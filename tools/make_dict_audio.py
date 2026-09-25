"""字典（字卡以外的字）的發音：每個詞一個 Nanami 音檔 audio/d/<JMdict 編號>.mp3。

2026-09-25 使用者：字典的字按了沒有聲音。原本用手機內建語音（speechSynthesis），iPhone 靜音鍵開著就不出聲；
改成跟字卡一樣的預錄音檔（<audio> 靜音鍵開著也會響）。約 2.3 萬個、32 kbps 單聲道（約 100 MB），
不放進離線下載包，點了才抓（離線時退回手機語音）。
朗讀文字：寫法的 Sudachi 讀音和字典讀音一致就念寫法（音調較自然），否則念假名（避免漢字念錯）。
朗讀文字沒變的不重做（hash 記在 build/dict-tts-manifest.json）。

用法：python3 tools/make_dict_audio.py [並行數，預設 12]
"""
import asyncio, hashlib, json, os, subprocess, sys, tempfile
import edge_tts

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "pipeline"))
from common import sudachi_tokens, kata2hira, has_kanji   # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.environ.get("TK_WORK", os.path.expanduser("~/Desktop/Claude code/workspace/work/jp-travel-vocab"))
MANIFEST = os.path.join(WORK, "build", "dict-tts-manifest.json")
VOICE = "ja-JP-NanamiNeural"
FFMPEG = "/opt/homebrew/bin/ffmpeg"


def tts_text(e):
    r = e["r"][0]
    if e.get("u") or not e.get("k"):
        return r
    k = e["k"][0]
    if not has_kanji(k):
        return k
    sud = "".join(kata2hira(t.reading_form()) for t in sudachi_tokens(k))
    return k if sud == kata2hira(r) else r


def trim(src, dst):
    af = ("silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.06,"
          "areverse,silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.18,areverse")
    subprocess.run([FFMPEG, "-v", "error", "-y", "-i", src, "-af", af, "-ac", "1", "-ar", "24000",
                    "-codec:a", "libmp3lame", "-b:a", "32k", dst], check=True)


async def synth(sem, text, dst, stats):
    async with sem:
        last = None
        for attempt in range(5):
            try:
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
                    raw = tmp.name
                await edge_tts.Communicate(text, VOICE).save(raw)
                if os.path.getsize(raw) < 600:
                    raise RuntimeError("音檔太小")
                await asyncio.to_thread(trim, raw, dst)
                os.unlink(raw)
                stats["ok"] += 1
                return True
            except Exception as ex:   # 網路錯誤或被限流：退避重試
                last = ex
                await asyncio.sleep(2 ** attempt)
        stats["fail"].append((dst, str(last)))
        return False


async def main(conc):
    entries = json.load(open(os.path.join(ROOT, "data", "dict.json"), encoding="utf-8"))["entries"]
    man = json.load(open(MANIFEST)) if os.path.exists(MANIFEST) else {}
    os.makedirs(os.path.join(ROOT, "audio", "d"), exist_ok=True)
    sem = asyncio.Semaphore(conc)
    stats = {"ok": 0, "fail": []}
    jobs = []
    for e in entries:
        text = tts_text(e)
        rel = f"audio/d/{e['i']}.mp3"
        h = hashlib.sha1(f"{VOICE}|{text}".encode()).hexdigest()[:16]
        if man.get(rel) == h and os.path.exists(os.path.join(ROOT, rel)):
            continue
        jobs.append((rel, h, text))
    print(f"要產生 {len(jobs)} 個音檔", flush=True)
    done = 0
    for i in range(0, len(jobs), 120):
        batch = jobs[i:i + 120]
        res = await asyncio.gather(*[synth(sem, t, os.path.join(ROOT, rel), stats) for rel, h, t in batch])
        for (rel, h, _), ok in zip(batch, res):
            if ok:
                man[rel] = h
        done += len(batch)
        json.dump(man, open(MANIFEST, "w"), indent=0)
        print(f"  {done}/{len(jobs)}", flush=True)
    print(f"完成 {stats['ok']}，失敗 {len(stats['fail'])}")
    for f in stats["fail"][:20]:
        print("  失敗", f)


if __name__ == "__main__":
    asyncio.run(main(int(sys.argv[1]) if len(sys.argv) > 1 else 12))

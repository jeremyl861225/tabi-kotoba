"""找出「語音把漢字念成別的讀音」的單字卡（2026-09-29 使用者：北念成ほく、南念成なん）。

build_data.word_tts 只在 Sudachi 讀音與字卡讀音相同時送漢字給語音，但 Edge 語音自己的判斷不一定跟 Sudachi 一樣
（單一個漢字常念成音讀）。這裡對每張「送漢字」的單字卡，用字卡讀音（假名）再合成一份，
跟現有的漢字版音檔比聲紋（MFCC＋DTW）：念法一樣距離小，念成別的音距離大。

用法（workspace 的 venv，要有 edge-tts、numpy）：
  python tools/tts_check.py synth   # 合成假名版到 workspace/build/ttscheck/{n,k}/<id>.mp3（可中斷續跑）
  python tools/tts_check.py score   # 比對，寫 build/ttscheck/scores.json（距離由大到小）
  python tools/tts_alt.py           # 單一漢字的卡再跟「其他讀音」比，寫 alt.json
判讀（2026-09-29 日文版的經驗）：距離 0＝念法完全一樣；4–9＝只差聲調；12 以上多半念錯。
單一漢字：alt.json 裡某個候選讀音比字卡讀音近很多（< 0.7 倍）＝念成那個音了。多字詞：12 以上的逐條用候選讀音驗證。
念錯的卡寫進 build/author/tts_kana.json（{編號: 寫法}），build_data 會改送假名，再跑 make_audio 重做、sw.js 的 AUDIO_REDO 加一批。
注意：單獨一個假名（し、ひ、ち）女聲會念成氣音，漢字念對的就不要改（市、氏、死、計…）。
"""
import asyncio, json, os, re, subprocess, sys, tempfile
import numpy as np

APP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.environ.get("TK_WORK", os.path.expanduser("~/Desktop/Claude code/workspace/work/jp-travel-vocab"))
HERE = os.path.join(WORK, "build", "ttscheck")
FFMPEG = "/opt/homebrew/bin/ffmpeg"
VOICES = {"n": "ja-JP-NanamiNeural", "k": "ja-JP-KeitaNeural"}
KANJI = re.compile(r"[㐀-鿿々〆]")


def targets():
    tts = json.load(open(os.path.join(WORK, "build", "tts.json"), encoding="utf-8"))
    cards = {c["id"]: c for c in json.load(open(os.path.join(APP, "data", "cards.json"), encoding="utf-8"))["cards"]}
    out = {}
    lo = os.environ.get("TK_MIN_ID", "")     # 只檢查新加的卡：TK_MIN_ID=4524
    for cid, v in tts.items():
        if lo and cid < lo:
            continue
        c = cards[cid]
        if c["k"] != "w" or not KANJI.search(v["w"]):
            continue
        kana = re.sub(r"^[〜～]+|[〜～]+$", "", c["r"]).replace("〜", "、").replace("～", "、")
        kana = re.sub(r"[（(]([^）)]*)[）)]", r"\1", kana)
        out[cid] = {"text": v["w"], "kana": kana, "w": c["w"], "r": c["r"]}
    return out


def trim(src, dst):
    af = ("silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.06,"
          "areverse,silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.18,areverse")
    subprocess.run([FFMPEG, "-v", "error", "-y", "-i", src, "-af", af, "-ac", "1", "-ar", "24000",
                    "-codec:a", "libmp3lame", "-b:a", "48k", dst], check=True)


async def synth_one(sem, voice, text, dst, stats):
    import edge_tts
    async with sem:
        last = None
        for attempt in range(5):
            try:
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
                    raw = tmp.name
                await edge_tts.Communicate(text, VOICES[voice]).save(raw)
                if os.path.getsize(raw) < 800:
                    raise RuntimeError("音檔太小")
                await asyncio.to_thread(trim, raw, dst)
                os.unlink(raw)
                stats["ok"] += 1
                return
            except Exception as e:
                last = e
                await asyncio.sleep(2 ** attempt)
        stats["fail"].append((dst, str(last)))


async def synth():
    t = targets()
    sem = asyncio.Semaphore(12)
    stats = {"ok": 0, "fail": []}
    jobs = []
    for cid, v in t.items():
        for voice in VOICES:
            dst = os.path.join(HERE, voice, f"{cid}.mp3")
            if os.path.exists(dst):
                continue
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            jobs.append(synth_one(sem, voice, v["kana"], dst, stats))
    print(f"要合成 {len(jobs)} 個", flush=True)
    for i in range(0, len(jobs), 120):
        await asyncio.gather(*jobs[i:i + 120])
        print(f"  {min(i + 120, len(jobs))}/{len(jobs)}", flush=True)
    print("完成", stats["ok"], "失敗", len(stats["fail"]), stats["fail"][:5])


# ---------- 聲紋比對 ----------
SR, NFFT, HOP, WIN = 16000, 512, 160, 400


def pcm(path):
    raw = subprocess.run([FFMPEG, "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32)


def mel_bank(n=26):
    mel = lambda f: 2595 * np.log10(1 + f / 700)
    imel = lambda m: 700 * (10 ** (m / 2595) - 1)
    pts = imel(np.linspace(mel(60), mel(7600), n + 2))
    bins = np.floor((NFFT + 1) * pts / SR).astype(int)
    fb = np.zeros((n, NFFT // 2 + 1))
    for i in range(1, n + 1):
        l, c, r = bins[i - 1], bins[i], bins[i + 1]
        fb[i - 1, l:c] = (np.arange(l, c) - l) / max(c - l, 1)
        fb[i - 1, c:r] = (r - np.arange(c, r)) / max(r - c, 1)
    return fb


FB = mel_bank()
DCT = np.cos(np.pi / 26 * (np.arange(26)[None, :] + 0.5) * np.arange(1, 13)[:, None])   # c1–c12


def mfcc(x):
    x = np.append(x[0], x[1:] - 0.97 * x[:-1])
    if len(x) < WIN:
        x = np.pad(x, (0, WIN - len(x)))
    n = 1 + (len(x) - WIN) // HOP
    idx = np.arange(WIN)[None, :] + HOP * np.arange(n)[:, None]
    frames = x[idx] * np.hamming(WIN)
    pw = np.abs(np.fft.rfft(frames, NFFT)) ** 2 / NFFT
    e = np.log(pw @ FB.T + 1e-10)
    keep = e.max(axis=1) > e.max() - 9          # 去掉幾乎無聲的格
    c = (e[keep] if keep.sum() > 5 else e) @ DCT.T
    return c - c.mean(axis=0)


def dtw(a, b):
    d = np.sqrt(((a[:, None, :] - b[None, :, :]) ** 2).sum(-1))
    n, m = d.shape
    acc = np.full((n + 1, m + 1), np.inf)
    acc[0, 0] = 0
    for i in range(1, n + 1):
        row, prev = acc[i], acc[i - 1]
        di = d[i - 1]
        # 先用上一列算「對角、正上」，再沿這一列累加「左邊」
        best = np.minimum(prev[:-1], prev[1:]) + di
        for j in range(1, m + 1):
            v = best[j - 1]
            if row[j - 1] + di[j - 1] < v:
                v = row[j - 1] + di[j - 1]
            row[j] = v
    return acc[n, m] / (n + m)


def score():
    t = targets()
    out = []
    for k, (cid, v) in enumerate(t.items()):
        rec = {"id": cid, **v}
        for voice in VOICES:
            a = os.path.join(APP, "audio", voice, f"{cid}.mp3")
            b = os.path.join(HERE, voice, f"{cid}.mp3")
            if not (os.path.exists(a) and os.path.exists(b)):
                continue
            xa, xb = pcm(a), pcm(b)
            rec[voice] = round(float(dtw(mfcc(xa), mfcc(xb))), 3)
            rec[voice + "_len"] = round(len(xa) / len(xb), 2)
        out.append(rec)
        if k % 300 == 0:
            print(k, flush=True)
    out.sort(key=lambda r: -max(r.get("n", 0), r.get("k", 0)))
    json.dump(out, open(os.path.join(HERE, "scores.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print("寫好", len(out))


if __name__ == "__main__":
    if sys.argv[1] == "synth":
        asyncio.run(synth())
    else:
        score()

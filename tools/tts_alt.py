"""單一漢字的卡：漢字版音檔比較像「字卡讀音」還是比較像「這個字的其他讀音」？

scores.json 的距離在 9–12 之間分不出是念錯還是只有聲調不同。這裡從 JmdictFurigana 統計每個漢字常見的讀音，
取字卡讀音以外最常見的 3 個當候選，合成出來跟漢字版比：候選比字卡讀音明顯更像 → 語音把它念成那個音了。
輸出 build/ttscheck/alt.json：{id: {"voice": {"kana": 距離, "候選": 距離…}}}
"""
import asyncio, collections, json, os, re
import tts_check as check

HERE = check.HERE
FURI = os.path.join(check.WORK, "dict", "JmdictFurigana.json")


def kata2hira(s):
    return "".join(chr(ord(c) - 0x60) if "ァ" <= c <= "ヶ" else c for c in s)


def readings():
    cnt = collections.defaultdict(collections.Counter)
    for e in json.load(open(FURI, encoding="utf-8-sig")):
        for seg in e["furigana"]:
            rb, rt = seg["ruby"], seg.get("rt")
            if rt and len(rb) == 1 and check.KANJI.match(rb):
                cnt[rb][kata2hira(rt)] += 1
    return cnt


DAKU = str.maketrans("かきくけこさしすせそたちつてとはひふへほ", "がぎぐげござじずぜぞだぢづでどばびぶべぼ")
HAN = str.maketrans("はひふへほ", "ぱぴぷぺぽ")


def candidates(ch, own, cnt, k=3):
    own = kata2hira(own)
    voiced = lambda x: {x[:1].translate(DAKU) + x[1:], x[:1].translate(HAN) + x[1:]}
    bad = {own} | voiced(own)
    out = []
    for r, _ in cnt[ch].most_common(12):
        if r in bad or r.endswith("っ") or len(r) < 1:
            continue
        if any(r in voiced(o) for o in out):   # 連濁形（ほく→ぼく）不另外試
            continue
        out.append(r)
        if len(out) == k:
            break
    return out


async def main():
    S = {r["id"]: r for r in json.load(open(os.path.join(HERE, "scores.json"), encoding="utf-8"))}
    cnt = readings()
    todo = {cid: r for cid, r in S.items() if len(r["text"]) == 1 and max(r.get("n", 0), r.get("k", 0)) > 0}
    alt_dir = os.path.join(HERE, "alt")
    sem = asyncio.Semaphore(12)
    stats = {"ok": 0, "fail": []}
    jobs, plan = [], {}
    for cid, r in todo.items():
        cands = candidates(r["text"], r["kana"], cnt)
        plan[cid] = cands
        for c in cands:
            for v in check.VOICES:
                dst = os.path.join(alt_dir, v, f"{c}.mp3")
                if os.path.exists(dst) or any(j[0] == dst for j in jobs):
                    continue
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                jobs.append((dst, check.synth_one(sem, v, c, dst, stats)))
    print(f"{len(todo)} 張卡、要合成 {len(jobs)} 個候選", flush=True)
    for i in range(0, len(jobs), 120):
        await asyncio.gather(*[j[1] for j in jobs[i:i + 120]])
        print(f"  {min(i + 120, len(jobs))}/{len(jobs)}", flush=True)
    feats = {}

    def mf(path):
        if path not in feats:
            feats[path] = check.mfcc(check.pcm(path))
        return feats[path]

    out = {}
    for cid, cands in plan.items():
        rec = {}
        for v in check.VOICES:
            a = mf(os.path.join(check.APP, "audio", v, f"{cid}.mp3"))
            d = {"kana": round(float(check.dtw(a, mf(os.path.join(HERE, v, f"{cid}.mp3")))), 2)}
            for c in cands:
                p = os.path.join(alt_dir, v, f"{c}.mp3")
                try:
                    d[c] = round(float(check.dtw(a, mf(p))), 2)
                except Exception:   # 單一假名（ほ）之類合成失敗的候選：跳過
                    pass
            rec[v] = d
        out[cid] = rec
    json.dump(out, open(os.path.join(HERE, "alt.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print("寫好", len(out))


if __name__ == "__main__":
    asyncio.run(main())

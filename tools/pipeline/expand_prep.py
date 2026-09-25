"""N3 擴充的候選：日檢 N5–N3 單字表（open-anki-jlpt-decks，MIT；資料源自 tanos.co.uk）對到 JMdict，扣掉已在字卡裡的字。

2026-09-25 使用者要求擴充到日檢 N3 程度（招牌、菜單、店員敬語都看得懂聽得懂），混進現有三條線。
輸入：dict/jlpt/n5.csv n4.csv n3.csv、build/selection.json（現有字卡）
輸出：build/expand/jlpt_candidates.json（每條：key、head、reading、jlpt、zipf、gloss、pos、in_deck）
"""
import csv, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
from wordfreq import zipf_frequency

by_id, kidx, ridx = jmdict()
JL = os.path.join(DICT, "jlpt")


def resolve(expr, reading, meaning):
    e = expr.strip("～〜")
    r = kata2hira(reading.strip("～〜"))
    cands = kidx.get(e, []) if has_kanji(e) else (ridx.get(e, []) or ridx.get(kata2hira(e), []))
    cands = list(dict.fromkeys(cands))
    if has_kanji(e) and len(cands) > 1:
        f = [c for c in cands if any(kata2hira(k["text"]) == r for k in by_id[c]["kana"])]
        cands = f or cands
    if len(cands) > 1:
        words = set(re.findall(r"[a-z]+", meaning.lower()))
        def score(c):
            w = by_id[c]
            s = 2 if (any(k.get("common") for k in w["kanji"]) or any(k.get("common") for k in w["kana"])) else 0
            g = " ".join(gl["text"].lower() for se in w["sense"] for gl in se["gloss"])
            return s + sum(1 for m in words if len(m) > 2 and m in g)
        cands.sort(key=score, reverse=True)
    return cands[0] if cands else None


def main():
    sel = json.load(open(os.path.join(BUILD, "selection.json"), encoding="utf-8"))
    deck_keys = {k for c in sel["cards"] for k in c.get("keys", [])}
    deck_forms = {(c["head"], kata2hira(c["reading"])) for c in sel["cards"]}
    seen, out = {}, []
    for lv in (5, 4, 3):                      # 先收較簡單的級數：同一個字出現在兩級時，算簡單那級
        rows = list(csv.DictReader(open(os.path.join(JL, f"n{lv}.csv"), encoding="utf-8")))
        for row in rows:
            expr, reading, meaning = row["expression"].strip(), row["reading"].strip(), row["meaning"].strip()
            if not expr:
                continue
            jid = resolve(expr, reading, meaning)
            key = f"w:{jid}" if jid else "p:" + re.sub(r"[\s～〜]", "", kata2hira(reading))
            if key in seen:
                continue
            seen[key] = lv
            rec = {"key": key, "head": expr, "reading": reading, "jlpt": lv, "meaning": meaning,
                   "zipf": zipf_frequency(expr.strip("～〜"), "ja")}
            if jid:
                e = entry_summary(by_id[jid])
                rec.update({"gloss": e["gloss"][:4], "pos": e["pos"], "jm_head": e["head"], "jm_reading": e["reading"]})
            rec["in_deck"] = key in deck_keys or (expr, kata2hira(reading)) in deck_forms
            out.append(rec)
    json.dump(out, open(os.path.join(BUILD, "expand", "jlpt_candidates.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    import collections
    c = collections.Counter((r["jlpt"], r["in_deck"]) for r in out)
    print("日檢候選", len(out), "；已在字卡裡", sum(1 for r in out if r["in_deck"]))
    for lv in (5, 4, 3):
        print(f"  N{lv}：新 {c[(lv, False)]}、已有 {c[(lv, True)]}")
    print("對不到字典", sum(1 for r in out if r["key"].startswith("p:")))


if __name__ == "__main__":
    main()

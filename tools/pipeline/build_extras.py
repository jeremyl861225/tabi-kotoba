"""三份補充清單 → build/expand/extras.json（給 select.py 的擴充模式）。

connectives.json → CJ 連接詞與句型；keigo.json → KG 敬語；signs_menus.json 依註記的地點關鍵字分主題（其餘 SN 招牌標示）。
單字盡量對到 JMdict（key 為 w:<id>），句型與對不到的用 x:<寫法>（〜そうだ（様態）與（伝聞）這種同讀音的才不會被合併）。
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

by_id, kidx, ridx = jmdict()
EXP = os.path.join(BUILD, "expand")
RULES = [("RS", r"菜單|點餐|餐廳|定食|拉麵|麵|份量|吃|飲料|酒"), ("TR", r"車站|月台|電車|列車|改札|新幹線"),
         ("DR", r"停車|道路|開車|駕駛|路口|高速|加油"), ("ON", r"溫泉|泡湯|浴池"), ("HT", r"飯店|旅館|房間|住宿"),
         ("CV", r"便利商店|超商|超市"), ("SG", r"寺|神社|景點|博物館|美術館|參觀"), ("MD", r"醫院|診所|看病"), ("DS", r"藥")]


def key_for(head, reading, kind):
    h = head.strip("〜～")
    if kind == "w" and "（" not in head:
        cands = kidx.get(h, []) if has_kanji(h) else (ridx.get(h, []) or ridx.get(kata2hira(h), []))
        r = kata2hira(reading)
        f = [c for c in cands if any(kata2hira(k["text"]) == r for k in by_id[c]["kana"])] or cands
        if len(f) == 1 or (f and has_kanji(h)):
            return f"w:{f[0]}"
    return f"x:{head}"


def main():
    out = []
    for fn, theme in (("connectives.json", "CJ"), ("keigo.json", "KG"), ("signs_menus.json", None)):
        for r in json.load(open(os.path.join(EXP, fn), encoding="utf-8")):
            th = theme
            if th is None:
                th = next((t for t, pat in RULES if re.search(pat, r.get("note", "") + r.get("zh", ""))), "SN")
            out.append({"key": key_for(r["head"], r["reading"], r.get("kind", "w")), "head": r["head"], "reading": r["reading"],
                        "level": r["level"], "theme": th, "kind": r.get("kind", "w"), "zh": r.get("zh", ""), "note": r.get("note", ""),
                        "src": fn.split(".")[0]})
    json.dump(out, open(os.path.join(EXP, "extras.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    import collections
    print(len(out), "條", collections.Counter((o["src"], o["theme"]) for o in out).most_common())
    print("對到字典", sum(1 for o in out if o["key"].startswith("w:")))


if __name__ == "__main__":
    main()

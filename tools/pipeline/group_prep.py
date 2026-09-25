"""擴充字的語意分組：替分組代理準備輸入（build/expand/group/）。

select.py 先照詞頻把擴充字切站（每 20 張一站，站內常是不相干的字、也取不出課名）；
這裡把每條擴充線（同級同主題）的字整理成 in-<級>-<主題>.json，給代理依意思分成 10–20 張一站並命名，
代理寫回 out-<級>-<主題>.json：[{"name": "來去與移動", "ids": ["1624", …]}, …]，select.py 重跑時就照分組切站。
另外列出「併進了新字的旅遊站」（select 把不到 8 張的小組併進同主題的旅遊站）給代理檢查課名是否還貼切：rename-in.json。
taken_names.json 是其餘旅遊站已用掉的課名（全 App 不可重複）。

用法：python3 tools/pipeline/group_prep.py
"""
import collections, glob, json, os, sys


def dump_rows(rows, path):
    """一張卡一行（代理讀起來省字數）"""
    with open(path, "w", encoding="utf-8") as f:
        f.write("[\n" + ",\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n]\n")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import BUILD   # noqa: E402

G = os.path.join(BUILD, "expand", "group")


def main():
    os.makedirs(G, exist_ok=True)
    sel = json.load(open(os.path.join(BUILD, "selection.json"), encoding="utf-8"))
    cards = {c["id"]: c for c in sel["cards"]}
    # 已寫好的中文（撰寫代理的輸出）比日檢表的英文好懂
    zh = {}
    for f in sorted(glob.glob(os.path.join(BUILD, "author", "out-*.json"))):
        for o in json.load(open(f, encoding="utf-8")):
            if o.get("zh"):
                zh[o["id"]] = o["zh"]

    def row(i):
        c = cards[i]
        m = c.get("meanings", {})
        r = {"id": i, "head": c["head"], "reading": c["reading"], "zipf": round(c.get("zipf", 0), 2)}
        z = zh.get(i) or "；".join(m.get("zh", [])[:2])
        if z:
            r["zh"] = z
        if m.get("en"):
            r["en"] = m["en"][0][:80]
        if c["theme"] != c.get("_lane"):
            r["theme"] = c["theme"]
        return r

    lanes = collections.OrderedDict()
    for u in sel["units"]:
        if "-x" in u["id"]:
            t, th, _ = u["id"].split("-")
            lanes.setdefault(f"{t}-{th}", []).extend(u["cards"])
    for f in glob.glob(os.path.join(G, "in-*.json")):
        os.remove(f)
    for k, ids in lanes.items():
        th = k.split("-")[1]
        for i in ids:
            cards[i]["_lane"] = th
        dump_rows([row(i) for i in ids], os.path.join(G, f"in-{k}.json"))

    names = json.load(open(os.path.join(BUILD, "unit_names.json"), encoding="utf-8"))
    grew = [u for u in sel["units"] if u.get("grew")]
    dump_rows([{"id": u["id"], "name": names.get(u["id"], ""), "cards": [f"{r['head']}（{r.get('zh') or r.get('en', '')}）" for r in map(row, u["cards"])]}
               for u in grew], os.path.join(G, "rename-in.json"))
    grew_ids = {u["id"] for u in grew}
    taken = sorted(v for k, v in names.items() if k not in grew_ids and any(u["id"] == k for u in sel["units"]))
    json.dump(taken, open(os.path.join(G, "taken_names.json"), "w", encoding="utf-8"), ensure_ascii=False)
    json.dump({k: len(v) for k, v in lanes.items()}, open(os.path.join(G, "lanes.json"), "w", encoding="utf-8"), ensure_ascii=False)
    print(f"{len(lanes)} 條擴充線、{sum(len(v) for v in lanes.values())} 張 → {G}")
    print("各線張數:", {k: len(v) for k, v in lanes.items()})
    print(f"要檢查課名的旅遊站 {len(grew)} 個；其餘旅遊站課名 {len(taken)} 個（不可重複）")


if __name__ == "__main__":
    main()

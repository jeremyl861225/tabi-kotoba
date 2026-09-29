"""料理字庫擴充（2026-09-29）：build/expand/food.txt → food.json（給 build_extras.py），並寫出語意分站 build/expand/group/out-<線>-<主題>.json。

food.txt 是人工整理的清單：「@主題 線 站名」開一站，每行「寫法|讀音|中文|說明|p」；行首「!」＝同讀音也照收（鯛 vs 泰國）。
一站整站放在同一條線（必備／常用／進階），站名就是課名；select 讀 extras.json 收字、讀分組檔照站切。
和既有字卡重複的（同寫法同讀音、或同讀音且其中一邊是假名寫法）不收，列出來給人看。
用法：python3 tools/pipeline/food_prep.py [--groups]   （--groups：select 跑完、卡片有編號後再寫分組檔）
"""
import json, os, re, sys, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import BUILD, kata2hira

EXP = os.path.join(BUILD, "expand")
SRC = os.path.join(EXP, "food.txt")


def parse():
    stations, cur = [], None
    for ln in open(SRC, encoding="utf-8"):
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        if ln.startswith("@"):
            th, tier, name = ln[1:].split(None, 2)
            cur = {"theme": th, "tier": int(tier), "name": name, "items": []}
            stations.append(cur)
            continue
        force = ln.startswith("!")
        f = ln.lstrip("!").split("|") + ["", "", "", ""]
        cur["items"].append({"head": f[0].strip(), "reading": f[1].strip(), "zh": f[2].strip(), "note": f[3].strip(),
                             "kind": "p" if f[4].strip() == "p" else "w", "force": force})
    return stations


def main():
    stations = parse()
    cards = json.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "cards.json"), encoding="utf-8"))["cards"]
    plain = lambda w: re.sub(r"\{([^|}]*)\|[^}]*\}", r"\1", w).replace("〜", "")
    have_form = {(plain(c["w"]), kata2hira(c["r"]).replace("〜", "")) for c in cards}
    have_read = collections.defaultdict(list)
    for c in cards:
        if "〜" not in c["w"]:   # 句型卡（〜たい、〜たら）不算：鯛、鱈 不是它們
            have_read[kata2hira(c["r"]).replace("〜", "")].append(plain(c["w"]))
    is_kana = lambda s: not re.search(r"[㐀-鿿々]", s)
    out, dup, seen = [], [], set()
    for st in stations:
        for it in st["items"]:
            fk = (it["head"], kata2hira(it["reading"]))
            same_read = have_read.get(kata2hira(it["reading"]), [])
            if fk in have_form or fk in seen:
                dup.append((st["name"], it["head"], "同寫法同讀音"))
                continue
            # 假名寫法的新字和既有的漢字字卡同讀音（まぐろ／鮪）、或反過來，多半是同一個字
            if same_read and not it["force"] and (is_kana(it["head"]) or any(is_kana(h) for h in same_read)):
                dup.append((st["name"], it["head"], f"同讀音：{'、'.join(same_read)}"))
                continue
            seen.add(fk)
            out.append({**{k: v for k, v in it.items() if k != "force"}, "theme": st["theme"], "tier": st["tier"], "station": st["name"]})
    json.dump(out, open(os.path.join(EXP, "food.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    size = collections.Counter((o["tier"], o["theme"], o["station"]) for o in out)
    print(f"{sum(len(s['items']) for s in stations)} 條 → 收 {len(out)}，重複 {len(dup)}")
    for d in dup:
        print("  重複", *d)
    print("各站：", ", ".join(f"{t}{th}{n}:{k}" for (t, th, n), k in size.items()))
    print("各線：", dict(collections.Counter(o["tier"] for o in out)))


def groups():
    """select 跑完以後：依站名寫分組檔（每條線一個檔），select 再跑一次就照站切"""
    sel = json.load(open(os.path.join(BUILD, "selection.json"), encoding="utf-8"))
    idof = {(c["head"], kata2hira(c["reading"])): c["id"] for c in sel["cards"]}
    lanes = collections.OrderedDict()
    for o in json.load(open(os.path.join(EXP, "food.json"), encoding="utf-8")):
        cid = idof.get((o["head"].replace("～", "〜"), kata2hira(o["reading"])))
        if not cid:
            print("找不到編號", o["head"]); continue
        lane = lanes.setdefault(f"{o['tier']}-{o['theme']}", collections.OrderedDict())
        lane.setdefault(o["station"], []).append(cid)
    for k, sts in lanes.items():
        p = os.path.join(EXP, "group", f"out-{k}.json")
        json.dump([{"name": n, "ids": ids} for n, ids in sts.items()], open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(p, [(n, len(ids)) for n, ids in sts.items()])


if __name__ == "__main__":
    groups() if "--groups" in sys.argv else main()

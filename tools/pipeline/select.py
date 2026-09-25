"""選字：候選詞條＋選字決定 → 依旅遊實用頻率排名、分級、分主題、切單元。

輸入：build/candidates.json、build/curate/out-*.json（代理的去留決定）、build/curate/manual.json（人工覆寫，可無）
輸出：build/selection.json（排名後的 1200 張卡骨架）、build/ids.json（卡片編號登記，讓編號跨版本穩定）
"""
import json, glob, os, re, sys, math, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import *
from themes import THEME_IDS
from wordfreq import zipf_frequency

TARGET = int(os.environ.get("TK_TARGET", 1200))
TIER_SIZES = (0.25, 0.375)          # 必備 25%、常用 37.5%、其餘進階
UNIT_MAX, UNIT_MIN = 20, 4
THEME_FLOOR = int(os.environ.get("TK_THEME_FLOOR", 30))
from themes import ASSIGN
FAMILY = {t: fam for t, (fam, _) in ASSIGN.items()}  # 太小的主題組併到同家族裡最大的一組（從 themes.py 推，新增主題不會 KeyError）


def split_units(g, tier, th, tag):
    """一組卡平均切成 ≤UNIT_MAX 張的站；tag 是 "x" 時為擴充站（id 1-VB-x1，和旅遊站 1-VB-1 分開，舊進度不亂）"""
    out = []
    k = math.ceil(len(g) / UNIT_MAX)
    size = math.ceil(len(g) / k)
    for p in range(k):
        part = g[p * size:(p + 1) * size]
        if not part:
            continue
        own = [x["no"] for x in part if x["theme"] == th]
        out.append({"id": f"{tier}-{th}-{tag}{p + 1}", "t": tier, "th": th, "part": p + 1, "parts": k,
                    "cards": [x["id"] for x in part],
                    "from": min(own) if own else part[0]["no"], "to": max(own) if own else part[-1]["no"]})
    return out


def load_decisions():
    dec = {}
    for f in sorted(glob.glob(os.path.join(BUILD, "curate", "out-*.json"))):
        for d in json.load(open(f, encoding="utf-8")):
            dec[d["key"]] = d
    man = os.path.join(BUILD, "curate", "manual.json")
    if os.path.exists(man):
        for d in json.load(open(man, encoding="utf-8")):
            dec[d["key"]] = {**dec.get(d["key"], {}), **d}
    return dec


EXP = os.path.join(BUILD, "expand")
LEVEL_TIER = {5: 1, 4: 2, 3: 3}   # 日檢 N5→必備線、N4→常用線、N3→進階線（2026-09-25 使用者：基礎字混進現有三條線）


def load_expansion():
    """擴充到日檢 N3 的新字：curate/in-NN.json＋out-NN.tsv（K 才收），以及 extras.json（連接詞、敬語等直接指定主題的清單）"""
    items = []
    ex = os.path.join(EXP, "extras.json")
    if os.path.exists(ex):   # 補充清單在前：連接詞、敬語、招牌菜單有專門整理的中文與說明，和日檢表重複時以它為準
        for r in json.load(open(ex, encoding="utf-8")):
            items.append({"key": r["key"], "head": r["head"], "reading": r["reading"], "jl": int(r["level"]), "theme": r["theme"],
                          "kind": r.get("kind", "w"), "meanings": {"zh": [r["zh"]]} if r.get("zh") else {}, "src_note": r.get("note", ""), "fix": ""})
    for inp in sorted(glob.glob(os.path.join(EXP, "curate", "in-*.json"))):
        outp = inp.replace("in-", "out-").replace(".json", ".tsv")
        if not os.path.exists(outp):
            continue
        rows = json.load(open(inp, encoding="utf-8"))
        dec = [ln.rstrip("\n").split("\t") for ln in open(outp, encoding="utf-8") if ln.strip()]
        for r, d in zip(rows, dec):
            if len(d) < 4 or d[0] != r["key"] or d[1] != "K" or d[2] not in THEME_IDS:
                continue
            # 日檢表有些一格放兩種寫法（いい; よい、足; 脚）：取第一種，其餘寫進參考說明
            hs = [x.strip() for x in r["head"].split(";") if x.strip()]
            rs = [x.strip() for x in r["reading"].split(";") if x.strip()] or [hs[0]]   # 讀音欄空白（片假名詞）就用寫法
            alt = "、".join(dict.fromkeys(hs[1:] + rs[1:]))
            r = {**r, "head": hs[0], "reading": rs[0], "note": (r.get("note", "") + (f"也寫作／也念作：{alt}" if alt else "")).strip()}
            items.append({"key": r["key"], "head": r["head"].strip(), "reading": r["reading"].strip(), "jl": int(r["jlpt"]),
                          "theme": d[2], "kind": "p" if d[3] == "p" else "w", "meanings": {k: v for k, v in (("en", [r.get("meaning", "")]), ("zh", r.get("zh", []))) if v and v != [""]},
                          "src_note": r.get("note", ""), "fix": d[4] if len(d) > 4 else ""})
    return items


def main():
    cands = {c["key"]: c for c in json.load(open(os.path.join(BUILD, "candidates.json"), encoding="utf-8"))}
    dec = load_decisions()
    missing = [k for k in cands if k not in dec]
    if missing:
        print(f"注意：{len(missing)} 個詞條還沒有選字決定（例：{missing[:5]}）")

    items = {}
    merges = []
    for key, d in dec.items():
        if key not in cands:
            if d.get("keep") and d.get("added"):   # 人工補的詞：來源段落有整組列出、但抽取只抓到部分（例如日期 1～10 日）
                cands[key] = {"key": key, "n": len(d.get("sources", [])), "sources": d.get("sources", []), "meanings": d.get("meanings", {}), "gloss": []}
            else:
                continue
        if d.get("keep"):
            th = d.get("theme")
            if th not in THEME_IDS:
                print("主題代碼錯誤", key, th)
                continue
            items[key] = {"key": key, "head": d["head"].strip(), "reading": d["reading"].strip(), "kind": d.get("kind", "w"),
                          "theme": th, "sources": set(cands[key]["sources"]), "fix": d.get("fix", ""),
                          "meanings": cands[key].get("meanings", {}), "gloss": cands[key].get("gloss", []), "keys": [key]}
        else:
            m = re.search(r"併入\s*([wp]:\S+)", d.get("why", ""))
            if m:
                merges.append((key, m.group(1)))
    for src, tgt in merges:
        if tgt in items and src in cands:
            items[tgt]["sources"] |= set(cands[src]["sources"])
            items[tgt]["keys"].append(src)
            for lang, v in cands[src].get("meanings", {}).items():
                items[tgt]["meanings"].setdefault(lang, [])
                items[tgt]["meanings"][lang] = list(dict.fromkeys(items[tgt]["meanings"][lang] + v))[:6]

    # 同寫法同讀音去重（不同分段的代理各自保留的）
    by_form = {}
    for it in items.values():
        fk = (it["head"], kata2hira(it["reading"]))
        if fk in by_form:
            a = by_form[fk]
            a["sources"] |= it["sources"]
            a["keys"] += it["keys"]
            for lang, v in it["meanings"].items():
                a["meanings"][lang] = list(dict.fromkeys(a["meanings"].get(lang, []) + v))[:6]
        else:
            by_form[fk] = it
    pool = list(by_form.values())
    for it in pool:
        it["n"] = len(it["sources"])
        it["zipf"] = zipf_frequency(it["head"].replace("〜", ""), "ja")
    pool.sort(key=lambda it: (-it["n"], -it["zipf"], it["reading"]))
    print(f"保留 {len(pool)} 個（去重後），目標 {TARGET}")
    sel = pool[:TARGET]
    # 主題保底：使用者指定要的主題（自駕、溫泉、藥妝…）常只有少數專題文章收錄，
    # 單看收錄數會整批落榜；每個主題至少收 THEME_FLOOR 個（不足就全收），補進來的仍依頻率排在後段
    have = collections.Counter(it["theme"] for it in sel)
    extra = []
    for th in THEME_IDS:
        need = THEME_FLOOR - have[th]
        if need > 0:
            more = [it for it in pool[TARGET:] if it["theme"] == th][:need]
            extra += more
            have[th] += len(more)
    if extra:
        drop, i = [], len(sel) - 1
        while len(drop) < len(extra) and i >= 0:
            th = sel[i]["theme"]
            if have[th] > THEME_FLOOR:
                drop.append(i)
                have[th] -= 1
            i -= 1
        sel = [it for k, it in enumerate(sel) if k not in set(drop)] + extra
        sel.sort(key=lambda it: (-it["n"], -it["zipf"], it["reading"]))
        print(f"主題保底補入 {len(extra)} 個：", collections.Counter(it["theme"] for it in extra).most_common())
    dist = collections.Counter(it["n"] for it in sel)
    print("入選的收錄數分佈:", sorted(dist.items(), reverse=True))

    # 分級
    n1 = round(len(sel) * TIER_SIZES[0])
    n2 = n1 + round(len(sel) * TIER_SIZES[1])
    for i, it in enumerate(sel):
        it["rank"] = i + 1
        it["tier"] = 1 if i < n1 else 2 if i < n2 else 3

    # ---- 擴充：日檢 N5–N3 的新字，依級數分到三條線（沒有旅遊排名，rank 為 None）----
    have_keys = {k for it in sel for k in it["keys"]}
    # 之前人工或撰寫代理判定刪掉的字（manual.json 的 keep:false），擴充時也不收回（例：箸 已有「お箸」）
    manp = os.path.join(BUILD, "curate", "manual.json")
    dropped_keys = {d["key"] for d in json.load(open(manp, encoding="utf-8")) if not d.get("keep")} if os.path.exists(manp) else set()
    have_keys |= dropped_keys
    have_forms = {(it["head"], kata2hira(it["reading"])) for it in sel}
    exp = []
    for it in load_expansion():
        fk = (it["head"], kata2hira(it["reading"]))
        if it["key"] in have_keys or fk in have_forms:
            continue
        have_keys.add(it["key"]); have_forms.add(fk)
        it.update({"sources": [], "n": 0, "zipf": zipf_frequency(it["head"].strip("〜～"), "ja"), "rank": None,
                   "tier": LEVEL_TIER.get(it["jl"], 3), "gloss": [], "keys": [it["key"]], "exp": True})
        exp.append(it)
    # 旅遊字也標上日檢級數（有在日檢表裡的）
    jl_map = {}
    jp = os.path.join(EXP, "jlpt_candidates.json")
    if os.path.exists(jp):
        for c in json.load(open(jp, encoding="utf-8")):
            jl_map[c["key"]] = max(jl_map.get(c["key"], 0), c["jlpt"])
    for it in sel:
        lv = [jl_map[k] for k in it["keys"] if k in jl_map]
        if lv:
            it["jl"] = max(lv)
    if exp:
        print(f"擴充新字 {len(exp)}：", dict(collections.Counter(("必備", "常用", "進階")[it["tier"] - 1] for it in exp)),
              collections.Counter(it["theme"] for it in exp).most_common(10))

    # 編號登記（跨版本穩定）
    ids_path = os.path.join(BUILD, "ids.json")
    ids = json.load(open(ids_path)) if os.path.exists(ids_path) else {}
    nxt = max([int(v) for v in ids.values()] + [0]) + 1
    for it in sel + exp:
        fk = f"{it['head']}|{kata2hira(it['reading'])}"
        if fk not in ids:
            ids[fk] = f"{nxt:04d}"
            nxt += 1
        it["id"] = ids[fk]
    json.dump(ids, open(ids_path, "w", encoding="utf-8"), ensure_ascii=False, indent=0)

    # 站號：同主題依排名 01, 02…（擴充字接在旅遊字後面，依級數、詞頻）
    exp.sort(key=lambda it: (it["tier"], -it["zipf"], it["reading"]))
    cnt = collections.Counter()
    for it in sel + exp:
        cnt[it["theme"]] += 1
        it["no"] = cnt[it["theme"]]

    # 單元：級內依主題分組，主題依該組最高排名排序；過大切段、過小併入同家族最大組
    units = []
    for tier in (1, 2, 3):
        groups = collections.OrderedDict()
        for it in sel:
            if it["tier"] == tier:
                groups.setdefault(it["theme"], []).append(it)
        small = [th for th, g in groups.items() if len(g) < UNIT_MIN]
        for th in small:
            fam = [t for t in groups if t != th and FAMILY[t] == FAMILY[th] and len(groups[t]) >= UNIT_MIN]
            if fam:
                host = max(fam, key=lambda t: len(groups[t]))
                groups[host].extend(groups.pop(th))
                groups[host].sort(key=lambda it: it["rank"])
        # 課的順序：整組的平均排名（比單看第一名穩定，必備線才不會從招牌開始）
        order = sorted(groups.items(), key=lambda kv: sum(x["rank"] for x in kv[1]) / len(kv[1]))
        T, E = [], []
        for th, g in order:
            T += split_units(g, tier, th, "")
        # 擴充字：同級同主題一組，切成 ≤20 張的站；各主題輪流排，再平均穿插到旅遊站之間
        eg = collections.OrderedDict()
        for it in exp:
            if it["tier"] == tier:
                eg.setdefault(it["theme"], []).append(it)
        small = [th for th, g in eg.items() if len(g) < UNIT_MIN]
        for th in small:
            fam = [t for t in eg if t != th and FAMILY[t] == FAMILY[th] and len(eg[t]) >= UNIT_MIN]
            if fam:
                host = max(fam, key=lambda t: len(eg[t]))
                eg[host].extend(eg.pop(th))
        # 輪流的順序：組句的核心（動詞、形容詞、連接詞、副詞）在前，其餘依字數
        PRIO = ["VB", "AJ", "CJ", "AV", "NM", "GR", "KG", "LF"]
        lanes = [split_units(g, tier, th, "x") for th, g in
                 sorted(eg.items(), key=lambda kv: (PRIO.index(kv[0]) if kv[0] in PRIO else len(PRIO), -len(kv[1])))]
        while any(lanes):
            for lane in lanes:
                if lane:
                    E.append(lane.pop(0))
        if E and T:
            # 平均穿插；旅遊站的位置用 i/T（第一站在 0）、擴充站用 (j+1)/(E+1)，每條線的第一站一定是旅遊站（必備線從打招呼開始）
            merged = sorted([(i / len(T), 0, i) for i in range(len(T))] + [((j + 1) / (len(E) + 1), 1, j) for j in range(len(E))])
            units += [T[i] if kind == 0 else E[i] for _, kind, i in merged]
        else:
            units += T + E
    out = [{k: (sorted(v) if isinstance(v, set) else v) for k, v in it.items()} for it in sel + exp]
    json.dump({"cards": out, "units": units}, open(os.path.join(BUILD, "selection.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    tiers = collections.Counter(it["tier"] for it in sel + exp)
    print("分級:", dict(tiers), " 單元數:", len(units), " 卡片:", len(sel) + len(exp))
    print("主題分佈:", collections.Counter(it["theme"] for it in sel + exp).most_common())
    print("各級單元大小:", [(u["id"], len(u["cards"])) for u in units][:80])


if __name__ == "__main__":
    main()

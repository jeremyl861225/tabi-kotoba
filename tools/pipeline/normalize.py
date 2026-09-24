"""把各來源詞表正規化成「詞條鍵」並計算收錄數（旅遊實用頻率）。

輸出 build/candidates.json：每個詞條（JMdict 詞條或常用句）被哪些來源收錄、各來源的寫法與意思、所在小標題。
"""
import json, glob, os, re, collections, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
import jaconv
from wordfreq import zipf_frequency

by_id, kidx, ridx = jmdict()

PAREN_RE = re.compile(r"[（(]([^）)]*)[）)]")
TRAIL_RE = re.compile(r"[。．.！!？?\s、,]+$")
MACRON = str.maketrans({"ā": "aa", "ī": "ii", "ū": "uu", "ē": "ee", "ō": "ou", "â": "aa", "î": "ii", "û": "uu", "ê": "ee", "ô": "ou",
                        "Ā": "aa", "Ī": "ii", "Ū": "uu", "Ē": "ee", "Ō": "ou"})
MACRON_KATA = str.maketrans({"ā": "a-", "ī": "i-", "ū": "u-", "ē": "e-", "ō": "o-"})


def romaji_variants(r):
    r = r.strip().lower()
    r = re.sub(r"[?!.,'’\"()（）]", "", r)
    r = r.replace("-", "").replace(" ", "")
    out = []
    h = jaconv.alphabet2kana(r.translate(MACRON))
    if h and not re.search(r"[a-z]", h):
        out.append(h)
    k = jaconv.alphabet2kana(r.translate(MACRON_KATA).replace("-", "ー"))
    if k and not re.search(r"[a-z]", k):
        out.append(hira2kata(k))
    return out


def clean(s):
    s = nfkc(s or "").strip()
    s = s.strip("「」『』\"“”'")
    return s


def split_forms(item):
    """一個來源詞條 → 可能的日文寫法清單（第一個是主要寫法）與讀音"""
    ja = clean(item.get("ja", ""))
    kana = clean(item.get("kana", ""))
    forms = []
    # 括號：讀音或可省略的部分
    m = PAREN_RE.search(ja)
    if m:
        inner = m.group(1).strip()
        base = PAREN_RE.sub("", ja).strip()
        if inner and is_kana(inner.replace(" ", "")) and has_kanji(base):
            kana = kana or inner.replace(" ", "")
        ja = base
    for alt in re.split(r"\s*[／/]\s*", ja):
        alt = TRAIL_RE.sub("", alt).strip()
        if alt:
            forms.append(alt)
    kana = TRAIL_RE.sub("", PAREN_RE.sub("", kana)).replace(" ", "")
    if not forms and item.get("romaji"):
        forms = romaji_variants(item["romaji"])[:1]
    return forms, kana


def lemma_if_single(text):
    """『乗り換えます』這種單一動詞加助動詞 → 辭書形"""
    toks = [t for t in sudachi_tokens(text)]
    content = [t for t in toks if t.part_of_speech()[0] not in ("助動詞", "補助記号", "助詞")]
    if len(content) == 1 and len(toks) <= 4:
        return content[0].dictionary_form()
    return None


def resolve(form, kana, meaning, lang):
    """回傳 ('w', jmdict_id) 或 ('p', 句子鍵) 或 None"""
    cands = []
    if has_kanji(form):
        cands = kidx.get(form, [])
        if not cands:
            lem = lemma_if_single(form)
            if lem and lem != form:
                cands = kidx.get(lem, []) or ridx.get(lem, [])
    else:
        cands = ridx.get(form, []) or ridx.get(kata2hira(form), [])
        if not cands:
            lem = lemma_if_single(form)
            if lem and lem != form:
                cands = ridx.get(lem, []) or kidx.get(lem, [])
    cands = list(dict.fromkeys(cands))
    if kana and len(cands) > 1:
        k2 = kata2hira(kana)
        f = [c for c in cands if any(kata2hira(r["text"]) == k2 for r in by_id[c]["kana"])]
        cands = f or cands
    if len(cands) > 1:
        cands = pick_best(cands, form, meaning, lang)
    if len(cands) == 1:
        return ("w", cands[0])
    if len(cands) == 0:
        # 句子或 JMdict 沒有的詞：用讀音當鍵
        r = reading_of(form) if has_kanji(form) else kata2hira(form)
        key = re.sub(r"[\s、。，,．.！!？?「」『』（）()〜～~・]", "", kata2hira(r))
        return ("p", key) if key else None
    return ("?", tuple(cands))


def pick_best(cands, form, meaning, lang):
    """多個同形詞條時：英文來源比對釋義；否則偏好把這個寫法當常用寫法的詞條"""
    scored = []
    mwords = set(re.findall(r"[a-z]+", (meaning or "").lower())) if lang == "en" else set()
    for c in cands:
        w = by_id[c]
        s = 0
        if any(k.get("common") for k in w["kanji"]) or any(r.get("common") for r in w["kana"]):
            s += 2
        if not has_kanji(form):
            uk = any("uk" in x.get("misc", []) for x in w["sense"][:1])
            if uk or not w["kanji"]:
                s += 3
        if mwords:
            g = " ".join(gl["text"].lower() for se in w["sense"] for gl in se["gloss"])
            s += len([m for m in mwords if len(m) > 2 and m in g])
        scored.append((s, c))
    scored.sort(reverse=True)
    top = scored[0][0]
    best = [c for s, c in scored if s == top]
    return best


def main():
    agg = {}
    unresolved = []
    src_meta = []
    for f in sorted(glob.glob(os.path.join(SOURCES, "*.json"))):
        d = json.load(open(f, encoding="utf-8"))
        sid, lang = d["id"], d.get("lang", "")
        src_meta.append({"id": sid, "lang": lang, "title": d.get("title", ""), "url": d.get("url", ""), "n_items": len(d["items"])})
        for it in d["items"]:
            forms, kana = split_forms(it)
            if not forms and kana:
                forms = [kana]
            for form in forms[:2]:
                res = resolve(form, kana, it.get("meaning", ""), lang)
                if not res:
                    continue
                kind, key = res
                if kind == "?":
                    unresolved.append({"src": sid, "form": form, "kana": kana, "meaning": it.get("meaning", ""), "cands": list(key)})
                    key = key[0]
                    kind = "w"
                k = f"{kind}:{key}"
                a = agg.setdefault(k, {"key": k, "kind": kind, "sources": set(), "forms": collections.Counter(),
                                       "kana": collections.Counter(), "meanings": {"zh": [], "en": [], "ja": []}, "sections": collections.Counter()})
                a["sources"].add(sid)
                a["forms"][form] += 1
                if kana:
                    a["kana"][kana] += 1
                if it.get("meaning"):
                    a["meanings"].setdefault(lang, []).append(it["meaning"])
                if it.get("section"):
                    a["sections"][f"{sid}:{it['section']}"] += 1
    out = []
    for a in agg.values():
        rec = {"key": a["key"], "kind": a["kind"], "n": len(a["sources"]), "sources": sorted(a["sources"]),
               "forms": [f for f, _ in a["forms"].most_common()], "kana": [k for k, _ in a["kana"].most_common()],
               "meanings": {k: list(dict.fromkeys(v))[:6] for k, v in a["meanings"].items() if v},
               "sections": [s for s, _ in a["sections"].most_common(8)]}
        if a["kind"] == "w":
            e = entry_summary(by_id[a["key"][2:]])
            rec.update({"jm": e["id"], "head": e["head"], "reading": e["reading"], "gloss": e["gloss"][:6], "pos": e["pos"], "jm_common": e["common"]})
            # 來源若多數用別的寫法（例如漢字寫法），以來源寫法為主
            top = rec["forms"][0]
            if top != e["head"] and (top in e["kanji"] or top in e["kana"]):
                rec["head_src"] = top
        else:
            rec["head"] = rec["forms"][0]
            rec["reading"] = rec["key"][2:]
        rec["zipf"] = zipf_frequency(rec.get("head_src", rec["head"]), "ja")
        out.append(rec)
    out.sort(key=lambda r: (-r["n"], -r["zipf"]))
    json.dump(out, open(os.path.join(BUILD, "candidates.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(unresolved, open(os.path.join(BUILD, "ambiguous.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(src_meta, open(os.path.join(BUILD, "sources_meta.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    dist = collections.Counter(r["n"] for r in out)
    print(f"{len(src_meta)} 份來源 → {len(out)} 個詞條（詞 {sum(1 for r in out if r['kind']=='w')}、句 {sum(1 for r in out if r['kind']=='p')}），多義待判 {len(unresolved)}")
    print("收錄數分佈:", sorted(dist.items(), reverse=True))


if __name__ == "__main__":
    main()

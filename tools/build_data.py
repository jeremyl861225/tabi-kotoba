"""組出 App 用的 data/cards.json，並做資料檢查。

輸入：workspace/build/selection.json（排名、分級、單元）、build/author/out-*.json（中文、例句）、
      build/author/fix.json（人工修正，可無）、build/sources_meta.json
輸出：data/cards.json、build/tts.json（朗讀文字，給 make_audio.py）、build/qa.json（檢查報告）
"""
import json, os, re, sys, glob, datetime, collections
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "pipeline"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
from rubytools import word_ruby, plain, reading, segments, uncovered_kanji, check_sentence, tts_text, romaji_for, RUBY_RE
from themes import theme_list
import opencc

TIERS = [{"id": 1, "name": "必備"}, {"id": 2, "name": "常用"}, {"id": 3, "name": "進階"}]
jp2t = opencc.OpenCC("jp2t")
s2t = opencc.OpenCC("s2t")


def phrase_ruby(head, read):
    """句子的標音：先用假名錨點對齊；對不上就逐詞用 Sudachi 讀音"""
    mk = word_ruby(head, read)
    if reading(mk) == read and not (mk.startswith("{") and mk.endswith("}") and len(plain(mk)) > 4):
        return mk
    out = []
    for t in sudachi_tokens(head):
        s = t.surface()
        if has_kanji(s):
            r = kata2hira(t.reading_form())
            out.append(word_ruby(s, r) if s != r else s)
        else:
            out.append(s)
    mk2 = "".join(out)
    return mk2 if kata2hira(reading(mk2)) == kata2hira(read) else mk


def clean_markup(mk):
    """拿掉標在假名上的 ruby、全形括號誤用"""
    def fix(m):
        base, rt = m.group(1), m.group(2)
        if not has_kanji(base):
            return base
        return "{" + base + "|" + rt + "}"
    return RUBY_RE.sub(fix, mk.replace("｛", "{").replace("｝", "}").replace("｜", "|"))


def same_as_chinese(head, zh):
    """日文漢字轉成繁體後幾乎就是中文意思（観光＝觀光）→ 測驗避開看字選意思"""
    kan = "".join(c for c in plain(head) if has_kanji(c))
    if len(kan) < 1:
        return False
    t = jp2t.convert(kan)
    first = re.split(r"[；;、，,（(／/]", zh)[0]
    return t in first or (len(t) >= 2 and sum(c in first for c in t) >= len(t) - 0)


def word_tts(head, read, kind, markup):
    if kind == "p":
        return tts_text(markup)
    if not has_kanji(head):
        return head
    toks = list(sudachi_tokens(head))
    sud = "".join(kata2hira(t.reading_form()) for t in toks)
    return head if sud == kata2hira(read) else read


def head_in_example(head, ex):
    """例句裡有沒有用到這個字（動詞形容詞可活用）"""
    p = plain(ex)
    h = head.replace("〜", "").replace("～", "")
    if h in p:
        return True
    lemmas = {t.dictionary_form() for t in sudachi_tokens(p)} | {t.normalized_form() for t in sudachi_tokens(p)}
    if h in lemmas:
        return True
    # 漢字詞幹（乗り換え→乗り換えます、乗換）
    stem = re.sub(r"[ぁ-ん]+$", "", h)
    return bool(stem) and len(stem) >= 1 and stem in p and has_kanji(stem)


def main():
    sel = json.load(open(os.path.join(BUILD, "selection.json"), encoding="utf-8"))
    authored = {}
    for f in sorted(glob.glob(os.path.join(BUILD, "author", "out-*.json"))):
        for d in json.load(open(f, encoding="utf-8")):
            authored[d["id"]] = d
    fixp = os.path.join(BUILD, "author", "fix.json")
    if os.path.exists(fixp):
        for d in json.load(open(fixp, encoding="utf-8")):
            authored.setdefault(d["id"], {}).update(d)
    themes = theme_list()
    tname = {t["id"]: t["name"] for t in themes}

    qa = collections.defaultdict(list)
    cards, tts = [], {}
    for c in sel["cards"]:
        a = authored.get(c["id"], {})
        head, read, kind = c["head"], c["reading"], c["kind"]
        if a.get("head"):
            head = a["head"]
        if a.get("reading"):
            read = a["reading"]
        w = phrase_ruby(head, read) if kind == "p" else word_ruby(head, read)
        if kata2hira(reading(w)) != kata2hira(read):
            qa["head_ruby_mismatch"].append([c["id"], head, read, w])
        ex = clean_markup(a.get("ex", "").strip())
        zh = a.get("zh", "").strip()
        card = {
            "id": c["id"], "w": w, "r": read, "zh": zh, "pos": a.get("pos", ""),
            "th": c["theme"], "t": c["tier"], "rank": c["rank"], "n": c["n"], "no": c["no"],
            "ex": ex, "exz": a.get("exz", "").strip(), "note": a.get("note", "").strip(), "k": kind,
        }
        verb_u = card["pos"].startswith("動詞")
        card["rm"] = romaji_for(head, read, kind, ("v5u",) if verb_u else ())
        if same_as_chinese(head, zh):
            card["sm"] = 1
        if not card["note"]:
            del card["note"]
        cards.append(card)
        tts[c["id"]] = {"w": word_tts(head, read, kind, w), "x": tts_text(ex) if ex else ""}

        # ---- 檢查 ----
        if not zh:
            qa["missing_zh"].append(c["id"])
        if not ex:
            qa["missing_ex"].append([c["id"], head])
            continue
        if s2t.convert(zh + card["exz"] + card.get("note", "")) != zh + card["exz"] + card.get("note", ""):
            qa["simplified_chinese"].append([c["id"], zh, card["exz"]])
        un = uncovered_kanji(ex)
        if un:
            qa["uncovered_kanji"].append([c["id"], ex, "".join(un)])
        bad = check_sentence(ex)
        if bad:
            qa["reading_mismatch"].append([c["id"], ex, [list(b) for b in bad]])
        if kind != "p" and not head_in_example(head, ex):
            qa["head_not_in_example"].append([c["id"], head, plain(ex)])
        if len(plain(ex)) > 40:
            qa["long_example"].append([c["id"], plain(ex)])

    # 單元標題
    units = []
    for u in sel["units"]:
        title = tname[u["th"]] + (f" {u['part']}" if u["parts"] > 1 else "")
        units.append({**u, "title": title})

    # 來源清單與音檔大小
    srcs = json.load(open(os.path.join(BUILD, "sources_meta.json"), encoding="utf-8"))
    audio_bytes = collections.Counter()
    for card in cards:
        for v in ("n", "k"):
            for suf in ("", "x"):
                p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "audio", v, f"{card['id']}{suf}.mp3")
                if os.path.exists(p):
                    audio_bytes[str(card["t"])] += os.path.getsize(p)
    data = {
        "meta": {"version": datetime.date.today().isoformat(), "count": len(cards),
                 "sources": [{"id": s["id"], "title": s["title"], "url": s["url"], "lang": s["lang"]} for s in srcs],
                 "audioBytes": dict(audio_bytes)},
        "tiers": TIERS, "themes": themes, "units": units, "cards": cards,
    }
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json.dump(data, open(os.path.join(root, "data", "cards.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    json.dump(tts, open(os.path.join(BUILD, "tts.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    json.dump(qa, open(os.path.join(BUILD, "qa.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    size = os.path.getsize(os.path.join(root, "data", "cards.json"))
    print(f"{len(cards)} 張卡、{len(units)} 課 → data/cards.json（{size / 1024:.0f} KB）")
    for k, v in qa.items():
        print(f"  檢查 {k}: {len(v)}")


if __name__ == "__main__":
    main()

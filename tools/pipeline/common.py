"""資料管線共用：路徑、JMdict 索引、假名工具、形態素分析。

原始來源（各網站的詞表）有著作權，只放在 workspace，不進 repo；
這裡的程式只讀它們、輸出詞條鍵與收錄數。
"""
import json, os, re, unicodedata, functools

WORK = os.environ.get("TK_WORK", os.path.expanduser("~/Desktop/Claude code/workspace/work/jp-travel-vocab"))
SOURCES = os.path.join(WORK, "sources")
DICT = os.path.join(WORK, "dict")
BUILD = os.path.join(WORK, "build")
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.makedirs(BUILD, exist_ok=True)

KANJI_RE = re.compile(r"[㐀-鿿豈-﫿々〆ヶ]")
KANA_ONLY_RE = re.compile(r"^[ぁ-ゖァ-ヺー・゛゜ー・]+$")


def has_kanji(s):
    return bool(KANJI_RE.search(s))


def kata2hira(s):
    return "".join(chr(ord(c) - 0x60) if "ァ" <= c <= "ヶ" else c for c in s)


def hira2kata(s):
    return "".join(chr(ord(c) + 0x60) if "ぁ" <= c <= "ゖ" else c for c in s)


def is_kana(s):
    return bool(KANA_ONLY_RE.match(s))


@functools.lru_cache(maxsize=1)
def jmdict():
    """回傳 (entries_by_id, kanji_index, kana_index)"""
    path = [f for f in os.listdir(DICT) if f.startswith("jmdict-eng") and f.endswith(".json")][0]
    data = json.load(open(os.path.join(DICT, path), encoding="utf-8"))
    by_id, kidx, ridx = {}, {}, {}
    for w in data["words"]:
        by_id[w["id"]] = w
        for k in w["kanji"]:
            kidx.setdefault(k["text"], []).append(w["id"])
        for r in w["kana"]:
            ridx.setdefault(r["text"], []).append(w["id"])
            h = kata2hira(r["text"])
            if h != r["text"]:
                ridx.setdefault(h, []).append(w["id"])
    return by_id, kidx, ridx


@functools.lru_cache(maxsize=1)
def furigana_index():
    """JmdictFurigana：(text, reading) -> [(ruby, rt)]"""
    data = json.load(open(os.path.join(DICT, "JmdictFurigana.json"), encoding="utf-8-sig"))
    idx = {}
    for e in data:
        idx[(e["text"], e["reading"])] = [(f["ruby"], f.get("rt", "")) for f in e["furigana"]]
    return idx


@functools.lru_cache(maxsize=1)
def sudachi():
    from sudachipy import dictionary
    return dictionary.Dictionary(dict="full").create()


def sudachi_tokens(text):
    from sudachipy import tokenizer
    return sudachi().tokenize(text, tokenizer.Tokenizer.SplitMode.C)


def reading_of(text):
    """整段文字的平假名讀音（Sudachi），標點照留"""
    out = []
    for m in sudachi_tokens(text):
        s = m.surface()
        r = m.reading_form()
        if not r or r == s and not is_kana(s):
            out.append(s)
        else:
            out.append(kata2hira(r))
    return "".join(out)


def entry_summary(w):
    """JMdict 詞條摘要：代表寫法、讀音、常用與否、英文釋義"""
    kanji = [k for k in w["kanji"]]
    kana = [r for r in w["kana"]]
    senses = w["sense"]
    uk = any("uk" in s.get("misc", []) for s in senses[:1])
    common_k = [k["text"] for k in kanji if k.get("common")]
    common_r = [r["text"] for r in kana if r.get("common")]
    head = None
    if uk or not kanji:
        head = (common_r or [kana[0]["text"]])[0]
    else:
        head = (common_k or [kanji[0]["text"]])[0]
    reading = (common_r or [kana[0]["text"]])[0]
    glosses = [g["text"] for s in senses[:3] for g in s["gloss"][:3]]
    pos = senses[0].get("partOfSpeech", []) if senses else []
    return {
        "id": w["id"], "head": head, "reading": reading, "uk": uk,
        "common": bool(common_k or common_r), "kanji": [k["text"] for k in kanji],
        "kana": [r["text"] for r in kana], "gloss": glosses, "pos": pos,
    }


def nfkc(s):
    return unicodedata.normalize("NFKC", s)

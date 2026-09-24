"""選字代理沒做完的分段，用規則補完：依來源小標題判主題、刪掉文法詞與長句、數字量詞用對照表修正。

輸出寫回 build/curate/out-N.json（接在代理已完成的部分後面），每條加 "auto": true，
撰寫階段的代理會再逐張確認寫法與讀音。
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

# 來源小標題（或來源本身）→ 主題；依序比對，先中先贏
SECTION_RULES = [
    ("LS", r"Phrases staff say|店員|接客|レジ|結帳時一定會聽到|怎麼回答才自然"),
    ("DR", r"道路|Driving|加油|ガソリン|満タン|軽油|自助加油|FAQ|〜でお願いします"),
    ("AP", r"機場|airport|Airport|Customs|immigration|baggage|Security|[Gg]ate|departure|Flight|Check-in|登機|入境|出國"),
    ("BT", r"Bus and train|バス|タクシー|[Tt]axi"),
    ("TR", r"車站|電車|IC卡|駅|公共交通|交通機関|購買車票"),
    ("DI", r"Directions|問路|道案内"),
    ("ON", r"Onsen|溫泉|錢湯|温泉|浴池|^[あかさたなはまやらわ]行$"),
    ("HT", r"宿泊|Lodging|ホテル|房型|住宿|入住|備品|用餐地點"),
    ("DK", r"Bars|飲料|Drinks"),
    ("CV", r"超商|コンビニ|スーパー"),
    ("DS", r"化妝|保養|藥品|軟膏|眼藥|成分|Pharmacy|薬の種類|唇妝|眼妝|底妝|感冒藥|胃腸藥"),
    ("MD", r"身體|症狀|symptoms|診療|診察|病院|Medical|不舒服|不適|Sentence Examples"),
    ("EM", r"危難|緊急|災害|Problems|Authority|困難|窘境|Extreme weather"),
    ("SG", r"観光地|美術館|博物館|自然公園|Tourism|景點"),
    ("RS", r"飲食店|レストラン|點餐|餐廳|Restaurant|人數|Allergies|Eating"),
    ("FD", r"美食|料理|餐點"),
    ("SH", r"購物|Shopping|服飾|Colors|アパレル|商店|賣場|Money"),
    ("NM", r"數字|Numbers|Time|量詞|時間|日期|Days|Months|Clock|幾點|幾分|念法"),
    ("SN", r"看板|禁止|Signs|Kanji|漢字|各分野共通|Shops, Stations"),
    ("SV", r"phone|Wi-?Fi|天氣|weather"),
    ("GR", r"Basics|Greeting|問候|打招呼|自我介紹|Typical Japanese|基本|Getting around"),
]
DROP_SECTIONS = r"Country and territory|Family|方言|Tips for Reading"
SOURCE_DEFAULT = {"ja-03": "ON", "en-11": "ON", "zh-11": "ON", "zh-05": "DR", "zh-07": "DS", "zh-08": "DS", "zh-06": "CV",
                  "zh-01": "AP", "en-08": "AP", "en-12": "AP", "zh-02": "TR", "en-02": "TR", "ja-07": "TR", "zh-03": "FD",
                  "zh-04": "SH", "ja-10": "MD", "zh-15": "EM", "zh-16": "NM", "en-04": "DS", "en-05": "LS", "en-06": "LS",
                  "ja-06": "SN", "en-09": "SN", "en-07": "SN", "zh-09": "ON", "ja-02": "RS", "ja-04": "LS"}

# 只寫假名的數字、量詞、日期時間 → 正確寫法
NUMERALS = {}
_n = ["一", "二", "三", "四", "五", "六", "七", "八", "九", "十"]
for k, v in {"いち": "一", "に": "二", "さん": "三", "よん": "四", "ご": "五", "ろく": "六", "なな": "七", "しち": "七", "はち": "八",
             "きゅう": "九", "じゅう": "十", "ひゃく": "百", "せん": "千", "まん": "万", "いちまん": "一万", "ぜろ": "ゼロ", "れい": "零"}.items():
    NUMERALS[k] = v
for r, h in zip(["ひとり", "ふたり", "さんにん", "よにん", "ごにん", "ろくにん", "しちにん", "ななにん", "はちにん", "きゅうにん", "じゅうにん"],
                ["一人", "二人", "三人", "四人", "五人", "六人", "七人", "七人", "八人", "九人", "十人"]):
    NUMERALS[r] = h
for r, h in zip(["ひとつ", "ふたつ", "みっつ", "よっつ", "いつつ", "むっつ", "ななつ", "やっつ", "ここのつ", "とお"],
                ["一つ", "二つ", "三つ", "四つ", "五つ", "六つ", "七つ", "八つ", "九つ", "十"]):
    NUMERALS[r] = h
for r, h in zip(["いっこ", "にこ", "さんこ", "よんこ", "ごこ", "ろっこ", "ななこ", "はっこ", "きゅうこ", "じゅっこ"],
                [f"{x}個" for x in _n]):
    NUMERALS[r] = h
for r, h in zip(["いちまい", "にまい", "さんまい", "よんまい", "ごまい"], [f"{x}枚" for x in _n[:5]]):
    NUMERALS[r] = h
for r, h in zip(["いっぽん", "にほん", "さんぼん", "よんほん", "ごほん"], [f"{x}本" for x in _n[:5]]):
    NUMERALS[r] = h
for r, h in zip(["ついたち", "ふつか", "みっか", "よっか", "いつか", "むいか", "なのか", "ようか", "ここのか", "とおか", "はつか"],
                ["一日", "二日", "三日", "四日", "五日", "六日", "七日", "八日", "九日", "十日", "二十日"]):
    NUMERALS[r] = h
for r, h in zip(["いちじ", "にじ", "さんじ", "よじ", "ごじ", "ろくじ", "しちじ", "はちじ", "くじ", "じゅうじ"], [f"{x}時" for x in _n]):
    NUMERALS[r] = h
for r, h in zip(["いっぷん", "にふん", "さんぷん", "よんぷん", "ごふん", "ろっぷん", "ななふん", "はっぷん", "きゅうふん", "じゅっぷん"], [f"{x}分" for x in _n]):
    NUMERALS[r] = h
for i, x in enumerate(_n[:10]):
    NUMERALS[["いちがつ", "にがつ", "さんがつ", "しがつ", "ごがつ", "ろくがつ", "しちがつ", "はちがつ", "くがつ", "じゅうがつ"][i]] = f"{x}月"
NUMERALS.update({"じゅういちがつ": "十一月", "じゅうにがつ": "十二月", "げつようび": "月曜日", "かようび": "火曜日", "すいようび": "水曜日",
                 "もくようび": "木曜日", "きんようび": "金曜日", "どようび": "土曜日", "にちようび": "日曜日"})

PARTICLES = set("はがをにでとへものやかねよ") | {"です", "ます", "から", "まで", "より", "だけ", "でも", "けど", "ので", "のに"}


def theme_for(r):
    for s in r["sections"]:
        sec = s.split(":", 1)[1] if ":" in s else s
        for th, pat in SECTION_RULES:
            if re.search(pat, sec):
                return th
    for sid in r["sources"]:
        if sid in SOURCE_DEFAULT:
            return SOURCE_DEFAULT[sid]
    pos = r.get("pos") or []
    if any(p.startswith("v") for p in pos) or any(p.startswith("adj") for p in pos):
        return "VB"
    return "SN" if "ja-01" in r["sources"] else "GR"


def decide(r):
    key = r["key"]
    head = r.get("head_src") or r["head"]
    reading = r.get("reading", "")
    form = r["forms"][0] if r["forms"] else head
    out = {"key": key, "auto": True}
    if any(re.search(DROP_SECTIONS, s) for s in r["sections"]) and head not in ("日本", "台湾"):
        return {**out, "keep": False, "why": "非旅遊情境（國名／親屬／方言）"}
    if re.search(r"[A-Za-z]", head) and not re.search(r"(Wi-?Fi|ATM|IC|ETC|SIM|WiFi|Suica|PASMO|JR)", head):
        return {**out, "keep": False, "why": "拼音轉換失敗"}
    if head in PARTICLES or (len(head) == 1 and is_kana(head)):
        return {**out, "keep": False, "why": "文法詞"}
    th = theme_for(r)
    kind = r["kind"]
    # 只寫假名的數字量詞：用對照表
    k2 = kata2hira(form) if is_kana(form) else None
    fix = ""
    if k2 and k2 in NUMERALS:
        head, reading, th, kind = NUMERALS[k2], k2, "NM", "w"
        fix = "數字量詞對照表"
    elif kind == "w" and is_kana(form) and has_kanji(head) and form not in (r.get("kana") or []):
        # 來源寫假名、字典卻對到漢字詞：先保留來源寫法，交給撰寫階段確認
        head, reading = form, kata2hira(form) if not re.search(r"[ァ-ヺ]", form) else form
        fix = "來源只有假名，先用來源寫法"
    if kind == "p":
        n = len(re.sub(r"[\s、。！？!?〜～]", "", reading))
        if th != "LS" and n > 12:
            return {**out, "keep": False, "why": "旅客自己說的長句"}
        if th == "LS" and n > 24:
            return {**out, "keep": False, "why": "句子太長"}
    d = {**out, "keep": True, "head": head, "reading": reading, "kind": kind, "theme": th}
    if fix:
        d["fix"] = fix
    return d


def main():
    cands = json.load(open(os.path.join(BUILD, "candidates.json"), encoding="utf-8"))
    by_key = {c["key"]: c for c in cands}
    total = 0
    for i in range(1, 7):
        inp = json.load(open(os.path.join(BUILD, "curate", f"in-{i}.json"), encoding="utf-8"))
        outp = os.path.join(BUILD, "curate", f"out-{i}.json")
        out = json.load(open(outp, encoding="utf-8")) if os.path.exists(outp) else []
        have = len(out)
        if have >= len(inp):
            continue
        for item in inp[have:]:
            out.append(decide(by_key[item["key"]]))
        json.dump(out, open(outp, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
        added = len(inp) - have
        total += added
        print(f"out-{i}.json：代理完成 {have} 條，規則補 {added} 條（保留 {sum(1 for d in out[have:] if d['keep'])}）")
    print("規則補完", total, "條")


if __name__ == "__main__":
    main()

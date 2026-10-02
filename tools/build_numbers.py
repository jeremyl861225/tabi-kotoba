"""數字與量詞專欄＋數字聽力測驗的資料（2026-10-02 使用者要求：「顯示各種量詞搭配數字時的變音，包含日期時間；
新增數字聽力測驗，聽金額、日期、時間等，填出正確的數字」）。

輸出：
- data/numbers.json：專欄（數字、量詞、日期、時間四段，每個詞有寫法、讀音、變音的位置、音檔）與聽力題庫
- build/numbers_tts.json（工作區）：要合成的音檔清單，給 tools/make_extra_audio.py

讀音全部寫成假名送給語音服務（數字寫法交給語音服務會念錯：一日、四時、何階…），所以念法一定照這裡的表。
變音的標示：拿「數字的念法＋量詞的基本念法」直接接起來比對，不一樣的部分標色（例：3本 さん＋ほん→さんぼん，標「ぼん」）。
題庫用固定亂數種子產生，重跑結果一樣；改了題目要重跑 make_extra_audio.py。"""
import difflib, json, os, random

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.environ.get("TK_WORK", os.path.expanduser("~/Desktop/Claude code/workspace/work/jp-travel-vocab"))

ONES = {1: "いち", 2: "に", 3: "さん", 4: "よん", 5: "ご", 6: "ろく", 7: "なな", 8: "はち", 9: "きゅう", 10: "じゅう"}
TENS = {1: "じゅう", 2: "にじゅう", 3: "さんじゅう", 4: "よんじゅう", 5: "ごじゅう", 6: "ろくじゅう", 7: "ななじゅう", 8: "はちじゅう", 9: "きゅうじゅう"}
HUNDREDS = {1: "ひゃく", 2: "にひゃく", 3: "さんびゃく", 4: "よんひゃく", 5: "ごひゃく", 6: "ろっぴゃく", 7: "ななひゃく", 8: "はっぴゃく", 9: "きゅうひゃく"}
THOUSANDS = {1: "せん", 2: "にせん", 3: "さんぜん", 4: "よんせん", 5: "ごせん", 6: "ろくせん", 7: "ななせん", 8: "はっせん", 9: "きゅうせん"}
KANJI_NUM = {1: "一", 2: "二", 3: "三", 4: "四", 5: "五", 6: "六", 7: "七", 8: "八", 9: "九", 10: "十"}


def under10000(n):
    out = ""
    for div, table in ((1000, THOUSANDS), (100, HUNDREDS), (10, TENS)):
        d = n // div % 10
        if d:
            out += table[d]
    if n % 10:
        out += ONES[n % 10]
    return out


def num_kana(n):
    """0～99,999,999 的念法（數數字的念法：4＝よん、7＝なな、9＝きゅう）"""
    if n == 0:
        return "ゼロ"
    man, rest = divmod(n, 10000)
    return (under10000(man) + "まん" if man else "") + under10000(rest)


def yen_kana(n):
    """金額：個位數是 4 時念 よえん（よんえん 不自然）"""
    k = num_kana(n)
    if n % 10 == 4:
        k = k[:-2] + "よ"
    return k + "えん"


MONTHS = {1: "いちがつ", 2: "にがつ", 3: "さんがつ", 4: "しがつ", 5: "ごがつ", 6: "ろくがつ", 7: "しちがつ", 8: "はちがつ",
          9: "くがつ", 10: "じゅうがつ", 11: "じゅういちがつ", 12: "じゅうにがつ"}
DAYS = {1: "ついたち", 2: "ふつか", 3: "みっか", 4: "よっか", 5: "いつか", 6: "むいか", 7: "なのか", 8: "ようか", 9: "ここのか",
        10: "とおか", 11: "じゅういちにち", 12: "じゅうににち", 13: "じゅうさんにち", 14: "じゅうよっか", 15: "じゅうごにち",
        16: "じゅうろくにち", 17: "じゅうしちにち", 18: "じゅうはちにち", 19: "じゅうくにち", 20: "はつか", 21: "にじゅういちにち",
        22: "にじゅうににち", 23: "にじゅうさんにち", 24: "にじゅうよっか", 25: "にじゅうごにち", 26: "にじゅうろくにち",
        27: "にじゅうしちにち", 28: "にじゅうはちにち", 29: "にじゅうくにち", 30: "さんじゅうにち", 31: "さんじゅういちにち"}
HOURS = {0: "れいじ", 1: "いちじ", 2: "にじ", 3: "さんじ", 4: "よじ", 5: "ごじ", 6: "ろくじ", 7: "しちじ", 8: "はちじ", 9: "くじ",
         10: "じゅうじ", 11: "じゅういちじ", 12: "じゅうにじ", 13: "じゅうさんじ", 14: "じゅうよじ", 15: "じゅうごじ",
         16: "じゅうろくじ", 17: "じゅうしちじ", 18: "じゅうはちじ", 19: "じゅうくじ", 20: "にじゅうじ", 21: "にじゅういちじ",
         22: "にじゅうにじ", 23: "にじゅうさんじ"}
MIN_ONES = {1: "いっぷん", 2: "にふん", 3: "さんぷん", 4: "よんぷん", 5: "ごふん", 6: "ろっぷん", 7: "ななふん", 8: "はっぷん", 9: "きゅうふん"}
MIN_TENS0 = {1: "じゅっぷん", 2: "にじゅっぷん", 3: "さんじゅっぷん", 4: "よんじゅっぷん", 5: "ごじゅっぷん"}
MIN_TENS = {1: "じゅう", 2: "にじゅう", 3: "さんじゅう", 4: "よんじゅう", 5: "ごじゅう"}


def min_kana(m):
    t, o = divmod(m, 10)
    if o == 0:
        return MIN_TENS0[t]
    return MIN_TENS.get(t, "") + MIN_ONES[o]


# ---------- 量詞：1～10＋「何」，不規則的整張表手寫 ----------
# (量詞, 基本念法, 用在哪, 說明, {數字: 念法}（只寫和直接接起來不同的）, 何的念法, {數字: 也可以這樣念})
COUNTERS = [
    ("つ", "つ", "一般的東西（不知道用哪個量詞時都可以用）、年齡（小孩）", "日本固有的數法，1～10 整套不同；11 以上改用「個」。問「幾個」說 いくつ。",
     {1: "ひとつ", 2: "ふたつ", 3: "みっつ", 4: "よっつ", 5: "いつつ", 6: "むっつ", 7: "ななつ", 8: "やっつ", 9: "ここのつ", 10: "とお"}, "いくつ", {}),
    ("個", "こ", "小東西：蛋、蛋糕、飯糰、行李", "1・6・8・10 變促音（いっこ、ろっこ、はっこ、じゅっこ）。",
     {1: "いっこ", 6: "ろっこ", 8: "はっこ", 10: "じゅっこ"}, "なんこ", {10: "じっこ"}),
    ("人", "にん", "人數", "1、2 是固有念法（ひとり、ふたり），4 是 よにん。點餐、訂位最常用。",
     {1: "ひとり", 2: "ふたり", 4: "よにん"}, "なんにん", {7: "しちにん"}),
    ("名", "めい", "人數（較正式：餐廳「何名様ですか」）", "全部規則。店員會說「〇名様」。",
     {}, "なんめい", {}),
    ("本", "ほん", "細長的東西：瓶裝飲料、傘、筆、香蕉；電車、公車的班次", "1・6・8・10 變 っぽん，3 與「何」變 ぼん。",
     {1: "いっぽん", 3: "さんぼん", 6: "ろっぽん", 8: "はっぽん", 10: "じゅっぽん"}, "なんぼん", {10: "じっぽん"}),
    ("杯", "はい", "一杯、一碗（飲料、湯、飯）", "1・6・8・10 變 っぱい，3 與「何」變 ばい。",
     {1: "いっぱい", 3: "さんばい", 6: "ろっぱい", 8: "はっぱい", 10: "じゅっぱい"}, "なんばい", {10: "じっぱい"}),
    ("枚", "まい", "薄平的東西：票、紙、盤子、襯衫、照片", "全部規則。",
     {}, "なんまい", {}),
    ("冊", "さつ", "書、雜誌、筆記本", "1・8・10 變促音（いっさつ、はっさつ、じゅっさつ）。",
     {1: "いっさつ", 8: "はっさつ", 10: "じゅっさつ"}, "なんさつ", {10: "じっさつ"}),
    ("匹", "ひき", "小動物、魚、蟲", "1・6・8・10 變 っぴき，3 與「何」變 びき。",
     {1: "いっぴき", 3: "さんびき", 6: "ろっぴき", 8: "はっぴき", 10: "じゅっぴき"}, "なんびき", {10: "じっぴき"}),
    ("台", "だい", "車、腳踏車、機器", "全部規則。",
     {}, "なんだい", {}),
    ("回", "かい", "次數（第幾次、幾次）", "1・6・8・10 變促音（いっかい、ろっかい、はっかい、じゅっかい）。",
     {1: "いっかい", 6: "ろっかい", 8: "はっかい", 10: "じゅっかい"}, "なんかい", {10: "じっかい"}),
    ("階", "かい", "樓層（〇樓）", "和「回」一樣促音化，另外 3 與「何」常念 がい（さんがい、なんがい）。",
     {1: "いっかい", 3: "さんがい", 6: "ろっかい", 8: "はっかい", 10: "じゅっかい"}, "なんがい", {3: "さんかい", 10: "じっかい"}),
    ("歳", "さい", "年齡", "1・8・10 變促音；20 歲特別念 はたち。",
     {1: "いっさい", 8: "はっさい", 10: "じゅっさい"}, "なんさい", {10: "じっさい"}),
    ("泊", "はく", "住幾晚（訂房）", "1・6・8・10 變 っぱく，3 與「何」變 ぱく。",
     {1: "いっぱく", 3: "さんぱく", 6: "ろっぱく", 8: "はっぱく", 10: "じゅっぱく"}, "なんぱく", {4: "よんぱく", 10: "じっぱく"}),
    ("足", "そく", "鞋子、襪子（一雙）", "1・8・10 變促音，3 與「何」變 ぞく。",
     {1: "いっそく", 3: "さんぞく", 8: "はっそく", 10: "じゅっそく"}, "なんぞく", {10: "じっそく"}),
    ("着", "ちゃく", "衣服（一套、一件）", "1・8・10 變促音。",
     {1: "いっちゃく", 8: "はっちゃく", 10: "じゅっちゃく"}, "なんちゃく", {10: "じっちゃく"}),
    ("軒", "けん", "房子、店家", "1・6・8・10 變促音，3 與「何」變 げん。",
     {1: "いっけん", 3: "さんげん", 6: "ろっけん", 8: "はっけん", 10: "じゅっけん"}, "なんげん", {10: "じっけん"}),
    ("番線", "ばんせん", "月台（〇號月台）", "全部規則；車站廣播常聽到。",
     {}, "なんばんせん", {}),
    ("円", "えん", "日圓", "4 念 よえん；其他規則。問價錢說 いくら。",
     {4: "よえん"}, "いくら", {}),
]
COUNTER_SLUG = {"つ": "tsu", "個": "ko", "人": "nin", "名": "mei", "本": "hon", "杯": "hai", "枚": "mai", "冊": "satsu", "匹": "hiki",
                "台": "dai", "回": "kai", "階": "kaii", "歳": "sai", "泊": "haku", "足": "soku", "着": "chaku", "軒": "ken", "番線": "bansen", "円": "en"}

TTS = []   # [{file, text, voice, rate}]


def tts(key, text, voice="n", rate=None):
    if rate is None:   # 短的詞放慢一點，單一音節才不會被念成氣音
        rate = "-45%" if len(text) <= 2 else "-25%" if len(text) <= 4 else "-10%"
    TTS.append({"file": f"audio/{key}.mp3", "text": text, "voice": voice, "rate": rate})
    return key


def mark(r, naive):
    """變音的位置：和直接接起來的念法逐字比對，回傳讀音裡變了的區段 [[起, 迄], …]
    （3本 さんほん→さんぼん 標「ぼ」；1本 いちほん→いっぽん 標「っぽ」；4時 よんじ→よじ 少了字就標前一個字「よ」）"""
    if r == naive:
        return None
    if naive == "*":
        return [[0, len(r)]]
    sm = difflib.SequenceMatcher(None, naive, r, autojunk=False)
    if sm.ratio() < 0.5:   # 幾乎整個不同（1日 ついたち、2人 ふたり）：整個標
        return [[0, len(r)]]
    out = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        a, b = (j1, j2) if j2 > j1 else (max(0, j1 - 1), max(1, j1))
        if out and a <= out[-1][1]:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return out or None


def item(w, r, key, naive=None, alt=None, note=None):
    d = {"w": w, "r": r, "a": tts(key, r)}
    hi = mark(r, naive) if naive else None
    if hi:
        d["hi"] = hi
    if alt:
        d["alt"] = alt
    if note:
        d["note"] = note
    return d


def section_numbers():
    g = []
    zero_ten = [item("0", "ゼロ", "c/n-0", alt="れい")]
    for n in range(1, 11):
        alt = {4: "し", 7: "しち", 9: "く"}.get(n)
        zero_ten.append(item(str(n), ONES[n], f"c/n-{n}", alt=alt))
    g.append({"title": "0～10", "note": "4、7、9 各有兩種念法：數數字、講價錢多用 よん、なな、きゅう；日期時間有固定念法（4 月＝しがつ、7 時＝しちじ、9 時＝くじ）。",
              "items": zero_ten})
    g.append({"title": "十位", "note": "十位數規則：數字＋じゅう。11＝じゅういち、25＝にじゅうご。",
              "items": [item(str(n * 10), TENS[n], f"c/n-{n * 10}") for n in range(1, 10)]})
    g.append({"title": "百位", "note": "300、600、800 會變音（びゃく、ぴゃく）。",
              "items": [item(str(n * 100), HUNDREDS[n], f"c/n-{n * 100}", naive=ONES[n] + "ひゃく" if n > 1 else "ひゃく") for n in range(1, 10)]})
    g.append({"title": "千位", "note": "3000、8000 會變音（ぜん、っせん）。1000 直接念 せん。",
              "items": [item(f"{n * 1000:,}", THOUSANDS[n], f"c/n-{n * 1000}", naive=ONES[n] + "せん" if n > 1 else "せん") for n in range(1, 10)]})
    big = [(10000, "いちまん"), (20000, "にまん"), (100000, "じゅうまん"), (1000000, "ひゃくまん"), (10000000, "いっせんまん")]
    g.append({"title": "萬位", "note": "日文以「萬」為單位，跟中文一樣四位一節：12,800＝いちまん・にせん・はっぴゃく。一萬要說 いちまん（不能省略 いち）。",
              "items": [item(f"{n:,}", r, f"c/n-{n}", naive=("いちせんまん" if n == 10000000 else None)) for n, r in big]})
    ex = [1980, 3500, 12800, 864, 1600]
    g.append({"title": "念念看", "note": "價錢的念法：從最大的位數往下念，0 不念。",
              "items": [item(f"{n:,}円", yen_kana(n), f"c/n-ex{n}") for n in ex]})
    return {"id": "num", "title": "數字", "lead": "先把 1～10、百、千、萬的變音記熟，價錢就聽得懂。", "groups": g}


def section_counters():
    out = []
    for c, base, use, note, irr, what, alts in COUNTERS:
        slug = COUNTER_SLUG[c]
        items = []
        for n in range(1, 11):
            naive = ONES[n] + base
            r = irr.get(n, naive)
            if c == "つ":
                naive = "*"   # 固有數法：整個都標
            items.append(item(f"{n}{c}" if c != "つ" else f"{n}つ" if n < 10 else "10", r, f"c/{slug}-{n}", naive=naive, alt=alts.get(n)))
        items.append(item(f"何{c}" if c not in ("つ", "円") else ("いくつ" if c == "つ" else "いくら"), what, f"c/{slug}-q",
                          naive=None if c in ("つ", "円") else "なん" + base))
        if c == "歳":
            items.append(item("20歳", "はたち", "c/sai-20", naive="にじゅっさい"))
        out.append({"c": c, "r": base, "use": use, "note": note, "items": items})
    return {"id": "cnt", "title": "量詞", "lead": "量詞前面的數字常會變音：1、6、8、10 容易變促音（っ），3 與「何」容易變濁音。點一下聽念法；標色的是變音的地方。",
            "counters": out}


def section_date():
    g = []
    months = []
    for m in range(1, 13):
        naive = (ONES[m] if m <= 10 else "じゅう" + ONES[m - 10]) + "がつ"
        months.append(item(f"{m}月", MONTHS[m], f"c/m-{m}", naive=naive))
    months.append(item("何月", "なんがつ", "c/m-q"))
    g.append({"title": "月", "note": "4 月＝しがつ、7 月＝しちがつ、9 月＝くがつ（不念 よんがつ、ななかつ、きゅうがつ）。", "items": months})
    days = []
    for d in range(1, 32):
        naive = num_kana(d) + "にち"
        days.append(item(f"{d}日", DAYS[d], f"c/d-{d}", naive=naive))
    days.append(item("何日", "なんにち", "c/d-q"))
    g.append({"title": "日", "note": "1～10 日、14 日、20 日、24 日是日本固有的念法；其他是 數字＋にち（17＝じゅうしちにち、19＝じゅうくにち）。", "items": days})
    wd = [("日曜日", "にちようび"), ("月曜日", "げつようび"), ("火曜日", "かようび"), ("水曜日", "すいようび"), ("木曜日", "もくようび"),
          ("金曜日", "きんようび"), ("土曜日", "どようび"), ("何曜日", "なんようび")]
    g.append({"title": "星期", "note": "日、月、火、水、木、金、土；口語常省略 日（月曜＝げつよう）。",
              "items": [item(w, r, f"c/w-{i}") for i, (w, r) in enumerate(wd)]})
    rel = [("今日", "きょう"), ("明日", "あした"), ("明後日", "あさって"), ("昨日", "きのう"), ("一昨日", "おととい"),
           ("今朝", "けさ"), ("今晩", "こんばん"), ("今週", "こんしゅう"), ("来週", "らいしゅう"), ("先週", "せんしゅう")]
    g.append({"title": "今天、明天", "note": "這幾個是特別念法，不是照字念。", "items": [item(w, r, f"c/rel-{i}") for i, (w, r) in enumerate(rel)]})
    dur = []
    for n in range(1, 11):
        if n == 1:
            dur.append(item("1日", "いちにち", "c/dd-1"))
        else:
            dur.append(item(f"{n}日間", DAYS[n] + "かん", f"c/dd-{n}", naive=num_kana(n) + "にちかん"))
    g.append({"title": "幾天（期間）", "note": "幾天的念法和日期一樣，只有 1 天是 いちにち；後面常加 かん（間）。", "items": dur})
    wk = {1: "いっしゅうかん", 8: "はっしゅうかん", 10: "じゅっしゅうかん"}
    g.append({"title": "幾週", "note": "1・8・10 變促音。", "items": [item(f"{n}週間", wk.get(n, ONES[n] + "しゅうかん"), f"c/wk-{n}", naive=ONES[n] + "しゅうかん") for n in range(1, 11)]})
    mo = {1: "いっかげつ", 6: "ろっかげつ", 8: "はっかげつ", 10: "じゅっかげつ"}
    g.append({"title": "幾個月", "note": "1・6・8・10 變促音。寫作 か月、ヶ月、カ月 都念 かげつ。", "items": [item(f"{n}か月", mo.get(n, ONES[n] + "かげつ"), f"c/mo-{n}", naive=ONES[n] + "かげつ") for n in range(1, 11)]})
    return {"id": "date", "title": "日期", "lead": "日期最容易念錯：1～10 日、14、20、24 日都有自己的念法。", "groups": g}


def section_time():
    g = []
    hrs = []
    for h in range(1, 13):
        naive = (ONES[h] if h <= 10 else "じゅう" + ONES[h - 10]) + "じ"
        hrs.append(item(f"{h}時", HOURS[h], f"c/h-{h}", naive=naive))
    hrs.append(item("何時", "なんじ", "c/h-q"))
    g.append({"title": "〇點（時）", "note": "4 點＝よじ、7 點＝しちじ、9 點＝くじ。", "items": hrs})
    h24 = [item(f"{h}時", HOURS[h], f"c/h-{h}", naive="じゅう" + ONES[h - 10] + "じ" if h < 20 else None) for h in range(13, 24)] + [item("0時", "れいじ", "c/h-0")]
    g.append({"title": "24 小時制", "note": "電車時刻、營業時間常用 24 小時制：14 時＝じゅうよじ、19 時＝じゅうくじ。", "items": h24})
    mins = []
    for m in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20, 30, 45):
        naive = num_kana(m) + "ふん"
        mins.append(item(f"{m}分", min_kana(m), f"c/mi-{m}", naive=naive, alt="じっぷん" if m == 10 else None))
    mins.append(item("半", "はん", "c/mi-half"))
    mins.append(item("何分", "なんぷん", "c/mi-q", naive="なんふん"))
    g.append({"title": "〇分", "note": "分 有 ふん、ぷん 兩種：1・3・4・6・8・10 念 ぷん（いっぷん、さんぷん、よんぷん、ろっぷん、はっぷん、じゅっぷん）。30 分也可以說 半（はん）。", "items": mins})
    hrs_d = {4: "よじかん", 7: "しちじかん", 9: "くじかん"}
    g.append({"title": "幾個小時", "note": "和〇點一樣：4＝よ、7＝しち、9＝く，後面加 かん。", "items": [item(f"{n}時間", hrs_d.get(n, ONES[n] + "じかん"), f"c/hd-{n}", naive=ONES[n] + "じかん") for n in range(1, 11)]})
    misc = [("午前", "ごぜん"), ("午後", "ごご"), ("朝", "あさ"), ("昼", "ひる"), ("夜", "よる"), ("〜前", "まえ"), ("〜過ぎ", "すぎ"), ("ちょうど", "ちょうど")]
    g.append({"title": "常一起出現的字", "note": "午前＝上午、午後＝下午；3時5分前＝差 5 分 3 點；3時過ぎ＝3 點多。", "items": [item(w, r, f"c/tm-{i}") for i, (w, r) in enumerate(misc)]})
    return {"id": "time", "title": "時間", "lead": "〇點用 時（じ）、〇分用 分（ふん／ぷん）；看電車時刻要會 24 小時制。", "groups": g}


# ---------- 數字聽力題庫 ----------
def build_quiz():
    rnd = random.Random(20261002)
    qs = []
    voice = ["n", "k"]

    def add(kind, say, show, ans, **kw):
        i = len(qs) + 1
        key = f"q/{kind[0]}{i:03d}"
        v = voice[i % 2]
        qs.append({"k": kind, "say": say, "show": show, "ans": ans, "a": key, "v": v, **kw})
        TTS.append({"file": f"audio/{key}.mp3", "text": say, "voice": v, "rate": "+0%"})

    # 金額：刻意多放 3／6／8 百、3／8 千、4／7／9 結尾
    prices = set()
    tricky = [300, 600, 800, 3000, 8000, 340, 680, 1800, 3600, 8300, 1400, 2700, 4900, 6800, 13800, 33000, 8800, 640, 980, 1980, 2980, 108, 384, 760, 9400]
    prices.update(tricky)
    while len(prices) < 110:
        kind = rnd.random()
        if kind < 0.3:
            n = rnd.randrange(10, 100) * 10
        elif kind < 0.75:
            n = rnd.randrange(10, 100) * 100 + (rnd.choice([0, 0, 0, 50, 80, 40]) if rnd.random() < 0.4 else 0)
        else:
            n = rnd.randrange(10, 100) * 1000 + rnd.choice([0, 0, 500, 800, 300, 600])
        prices.add(n)
    tmpl = [("ぜんぶで、{k}です。", "全部で{n}円です。"), ("{k}になります。", "{n}円になります。"), ("こちら、{k}です。", "こちら、{n}円です。"),
            ("おかえし、{k}です。", "お返し、{n}円です。"), ("おひとり、{k}です。", "お一人{n}円です。")]
    for n in sorted(prices, key=lambda x: rnd.random()):
        t = rnd.choice(tmpl)
        add("price", t[0].format(k=yen_kana(n)), t[1].format(n=f"{n:,}"), {"n": n}, unit="円")

    # 日期：每個特別的日子都至少出現一次
    dates = set()
    special = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 14, 20, 24]
    for d in special:
        dates.add((rnd.randint(1, 12), d))
    for m in (4, 7, 9):
        dates.add((m, rnd.randint(11, 28)))
    while len(dates) < 70:
        dates.add((rnd.randint(1, 12), rnd.randint(1, 28)))
    tmpl = [("{k}に、よやくしました。", "{m}月{d}日に予約しました。"), ("しゅっぱつは、{k}です。", "出発は{m}月{d}日です。"),
            ("チェックインは、{k}です。", "チェックインは{m}月{d}日です。"), ("{k}から、やすみです。", "{m}月{d}日から休みです。")]
    for m, d in sorted(dates, key=lambda x: rnd.random()):
        t = rnd.choice(tmpl)
        add("date", t[0].format(k=MONTHS[m] + " " + DAYS[d]), t[1].format(m=m, d=d), {"m": m, "d": d})

    # 時間：24 小時制（電車）、午前／午後、〇時半
    times = set()
    for h in (4, 7, 9, 14, 17, 19, 0):
        times.add((h, rnd.choice([1, 3, 4, 6, 8, 10, 20, 40, 45, 15])))
    while len(times) < 90:
        h = rnd.randint(5, 23)
        mi = rnd.choice([0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 1, 3, 4, 6, 8, 12, 16, 18, 24, 33, 47, 58])
        times.add((h, mi))
    for h, mi in sorted(times, key=lambda x: rnd.random()):
        style = rnd.random()
        if style < 0.45 or h in (0, 12):   # 24 小時制（0 點、12 點不用午前／午後，避免「午後 12 時」的歧義）
            k = HOURS[h] + (" " + min_kana(mi) if mi else "")
            say = rnd.choice([("でんしゃは、{k}に、でます。", "電車は{t}に出ます。"), ("つぎのバスは、{k}です。", "次のバスは{t}です。"), ("かいえんは、{k}です。", "開園は{t}です。")])
            show_t = f"{h}時" + (f"{mi}分" if mi else "")
        else:              # 午前／午後＋12 小時制
            ap = "ごぜん" if h < 12 else "ごご"
            h12 = h if h < 12 else h - 12
            hk = HOURS[h12]
            if mi == 30 and rnd.random() < 0.5:
                k, mt = ap + " " + hk + " はん", "半"
            else:
                k, mt = ap + " " + hk + (" " + min_kana(mi) if mi else ""), (f"{mi}分" if mi else "")
            say = rnd.choice([("{k}に、あいましょう。", "{t}に会いましょう。"), ("チェックアウトは、{k}です。", "チェックアウトは{t}です。"), ("よやくは、{k}です。", "予約は{t}です。")])
            show_t = ("午前" if h < 12 else "午後") + f"{h12}時" + mt
            if mt == "半":
                mi = 30
        add("time", say[0].format(k=k), say[1].format(t=show_t), {"h": h, "mi": mi})

    # 數量（量詞）：1～10，跟專欄的量詞表對應
    goods = [("つ", [("りんご", "りんご"), ("おにぎり", "おにぎり"), ("これ", "これ")], "{x}を、{k}ください。", "{x}を{w}ください。"),
             ("個", [("たまご", "卵"), ("ケーキ", "ケーキ"), ("にもつ", "荷物")], "{x}を、{k}ください。", "{x}を{w}ください。"),
             ("本", [("ビール", "ビール"), ("みず", "水"), ("かさ", "傘")], "{x}を、{k}ください。", "{x}を{w}ください。"),
             ("枚", [("きっぷ", "切符"), ("チケット", "チケット"), ("おさら", "お皿")], "{x}を、{k}ください。", "{x}を{w}ください。"),
             ("杯", [("コーヒー", "コーヒー"), ("ごはん", "ご飯"), ("なまビール", "生ビール")], "{x}を、{k}ください。", "{x}を{w}ください。"),
             ("人", [("おとな", "大人"), ("こども", "子供")], "{x}、{k}です。", "{x}{w}です。"),
             ("泊", [("", "")], "{k}、よやくしています。", "{w}予約しています。"),
             ("階", [("おてあらい", "お手洗い"), ("レストラン", "レストラン")], "{x}は、{k}です。", "{x}は{w}です。"),
             ("冊", [("ほん", "本")], "{x}を、{k}かいました。", "{x}を{w}買いました。"),
             ("台", [("タクシー", "タクシー")], "{x}を、{k}よびます。", "{x}を{w}呼びます。")]
    table = {c: (base, irr) for c, base, _, _, irr, _, _ in COUNTERS}
    per = {"つ": 12, "個": 10, "本": 14, "枚": 10, "杯": 12, "人": 12, "泊": 8, "階": 10, "冊": 6, "台": 6}
    for c, items_, say_t, show_t in goods:
        base, irr = table[c]
        nums = [1, 3, 6, 8, 10, 4] + [rnd.randint(1, 10) for _ in range(per[c] - 6)]
        for n in nums:
            x_say, x_show = rnd.choice(items_)
            k = irr.get(n, ONES[n] + base)
            w = (f"{KANJI_NUM[n]}つ" if n < 10 else "十") if c == "つ" else f"{n}{c}"
            add("count", say_t.format(x=x_say, k=k), show_t.format(x=x_show, w=w), {"n": n}, unit=c, item=x_show)
    return qs


def main():
    data = {"sections": [section_numbers(), section_counters(), section_date(), section_time()], "quiz": build_quiz()}
    os.makedirs(os.path.join(ROOT, "data"), exist_ok=True)
    with open(os.path.join(ROOT, "data", "numbers.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    seen, uniq = set(), []
    for t in TTS:
        if t["file"] not in seen:
            seen.add(t["file"]); uniq.append(t)
    os.makedirs(os.path.join(WORK, "build"), exist_ok=True)
    with open(os.path.join(WORK, "build", "numbers_tts.json"), "w", encoding="utf-8") as f:
        json.dump(uniq, f, ensure_ascii=False, indent=0)
    kinds = {}
    for q in data["quiz"]:
        kinds[q["k"]] = kinds.get(q["k"], 0) + 1
    print(f"專欄 {sum(1 for t in uniq if t['file'].startswith('audio/c/'))} 個音檔、聽力題 {len(data['quiz'])} 題 {kinds}")


if __name__ == "__main__":
    main()

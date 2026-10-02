"""五十音課程的資料（2026-10-02 使用者要求「日文增加五十音課程，由你發揮」）。

輸出：
- data/letters.json：課程（平假名 9 課、片假名 6 課）＋五十音表；js/letters.js 讀它畫課程、表格與練習
- build/letters_tts.json（工作區）：要合成的音檔清單，給 tools/make_extra_audio.py

每個假名：寫法、羅馬拼音（平文式）、音檔（單一假名用慢速，語音服務才不會把「し」念成氣音）、
例字（從字卡裡挑：讀音以這個假名開頭、兩到四拍、旅遊頻率最高的單字；播的是字卡本來的音檔）。
片假名和平假名同音，共用同一個音檔。促音・長音那課用「長短音／有無促音」的對照詞。"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.environ.get("TK_WORK", os.path.expanduser("~/Desktop/Claude code/workspace/work/jp-travel-vocab"))
RUBY = re.compile(r"\{([^|{}]+)\|[^{}]+\}")
SMALL = set("ゃゅょャュョぁぃぅぇぉァィゥェォ")

GOJUON = [  # (平假名, 羅馬拼音)；None＝表格裡的空格
    [("あ", "a"), ("い", "i"), ("う", "u"), ("え", "e"), ("お", "o")],
    [("か", "ka"), ("き", "ki"), ("く", "ku"), ("け", "ke"), ("こ", "ko")],
    [("さ", "sa"), ("し", "shi"), ("す", "su"), ("せ", "se"), ("そ", "so")],
    [("た", "ta"), ("ち", "chi"), ("つ", "tsu"), ("て", "te"), ("と", "to")],
    [("な", "na"), ("に", "ni"), ("ぬ", "nu"), ("ね", "ne"), ("の", "no")],
    [("は", "ha"), ("ひ", "hi"), ("ふ", "fu"), ("へ", "he"), ("ほ", "ho")],
    [("ま", "ma"), ("み", "mi"), ("む", "mu"), ("め", "me"), ("も", "mo")],
    [("や", "ya"), None, ("ゆ", "yu"), None, ("よ", "yo")],
    [("ら", "ra"), ("り", "ri"), ("る", "ru"), ("れ", "re"), ("ろ", "ro")],
    [("わ", "wa"), None, None, None, ("を", "o")],
    [("ん", "n"), None, None, None, None],
]
DAKUON = [
    [("が", "ga"), ("ぎ", "gi"), ("ぐ", "gu"), ("げ", "ge"), ("ご", "go")],
    [("ざ", "za"), ("じ", "ji"), ("ず", "zu"), ("ぜ", "ze"), ("ぞ", "zo")],
    [("だ", "da"), ("ぢ", "ji"), ("づ", "zu"), ("で", "de"), ("ど", "do")],
    [("ば", "ba"), ("び", "bi"), ("ぶ", "bu"), ("べ", "be"), ("ぼ", "bo")],
    [("ぱ", "pa"), ("ぴ", "pi"), ("ぷ", "pu"), ("ぺ", "pe"), ("ぽ", "po")],
]
YOON_ROWS = [("き", "k"), ("し", "sh"), ("ち", "ch"), ("に", "n"), ("ひ", "h"), ("み", "m"), ("り", "r"),
             ("ぎ", "g"), ("じ", "j"), ("び", "b"), ("ぴ", "p")]
FOREIGN = [("ティ", "ti"), ("ディ", "di"), ("トゥ", "tu"), ("ドゥ", "du"), ("ファ", "fa"), ("フィ", "fi"), ("フェ", "fe"), ("フォ", "fo"),
           ("ウィ", "wi"), ("ウェ", "we"), ("ウォ", "wo"), ("ヴァ", "va"), ("シェ", "she"), ("ジェ", "je"), ("チェ", "che"), ("ツァ", "tsa"),
           ("デュ", "dyu"), ("フュ", "fyu")]
PAIRS = [  # 促音・長音：對照詞（寫法, 讀音給語音服務, 羅馬拼音, 中文）
    ("きて", "きて", "kite", "來（来て）"), ("きって", "きって", "kitte", "郵票（切手）"),
    ("いえ", "いえ", "ie", "家"), ("いいえ", "いいえ", "iie", "不，不是"),
    ("とり", "とり", "tori", "鳥"), ("とおり", "とおり", "tōri", "街道（通り）"),
    ("ビル", "ビル", "biru", "大樓"), ("ビール", "ビール", "bīru", "啤酒"),
    ("おばさん", "おばさん", "obasan", "阿姨、伯母"), ("おばあさん", "おばあさん", "obāsan", "奶奶、老太太"),
    ("ちず", "ちず", "chizu", "地圖"), ("チーズ", "チーズ", "chīzu", "起司"),
]

TTS = []


def kata(s):
    return "".join(chr(ord(c) + 0x60) if "ぁ" <= c <= "ゖ" else c for c in s)


def yoon():
    out = []
    for base, cons in YOON_ROWS:
        row = []
        for small, v in (("ゃ", "a"), ("ゅ", "u"), ("ょ", "o")):
            r = cons + ("y" + v if cons in ("k", "n", "h", "m", "r", "g", "b", "p") else v)
            row.append((base + small, r))
        out.append(row)
    return out


def audio_key(roma, ch):
    k = {"ぢ": "di", "づ": "du", "を": "wo"}.get(ch, roma)   # 同音的假名分開存，念的字不同
    return f"l/{k}"


def add_tts(key, text, rate):
    TTS.append({"file": f"audio/{key}.mp3", "text": text, "voice": "n", "rate": rate})
    return key


class Examples:
    """從字卡挑例字：讀音（片假名看寫法）以這個假名開頭、後面不是小寫的ゃゅょ（避免 き 挑到 きょう）、兩到四拍"""
    def __init__(self, cards):
        self.cards = sorted((c for c in cards if c.get("k") == "w"), key=lambda c: (c.get("rank") or 99999, c.get("sq") or 99999))
        self.used = set()

    def pick(self, ch, katakana=False):
        n = len(ch)
        for c in self.cards:
            word = RUBY.sub(r"\1", c["w"])
            s = word if katakana else c["r"]
            if not s.startswith(ch) or c["id"] in self.used:
                continue
            if len(s) > n and s[n] in SMALL:
                continue
            if not (2 <= len(c["r"]) <= 4) or len(word) > 5:
                continue
            if katakana and not re.fullmatch(r"[ァ-ヺー]+", word):
                continue
            self.used.add(c["id"])
            return c["id"]
        return None


def cell(ch, roma, ex, katakana=False, slow="-55%"):
    shown = kata(ch) if katakana else ch
    key = audio_key(roma, ch)
    add_tts(key, ch, slow if len(ch) == 1 else "-45%")   # 片假名念起來一樣，共用平假名的音檔
    d = {"ch": shown, "roma": roma, "a": key}
    if katakana:
        d["hira"] = ch
    e = ex.pick(shown, katakana)
    if e:
        d["ex"] = e
    return d


def grid(rows, ex, katakana=False):
    return [[cell(c[0], c[1], ex, katakana) if c else None for c in row] for row in rows]


def main():
    cards = json.load(open(os.path.join(ROOT, "data", "cards.json"), encoding="utf-8"))["cards"]
    ex = Examples(cards)
    G = GOJUON
    hira = [
        {"id": "h1", "title": "あ行・か行", "sub": "母音與 k 開頭", "rows": grid(G[0:2], ex),
         "notes": ["日文的母音只有 あ（a）い（i）う（u）え（e）お（o）五個，每個假名都是一拍、念得一樣長。",
                   "う 嘴唇不要嘟：比中文的「ㄨ」扁一點。", "あ／お、き／さ 容易看錯：お 右邊多一點、き 比 さ 多一橫。"]},
        {"id": "h2", "title": "さ行・た行", "sub": "s、t 開頭", "rows": grid(G[2:4], ex),
         "notes": ["し 念 shi、ち 念 chi、つ 念 tsu，不是 si、ti、tu。", "さ 和 ち 左右相反，さ 開口朝右、ち 開口朝左。",
                   "す、つ 的 u 常常輕到幾乎聽不見（です 聽起來像 des）。"]},
        {"id": "h3", "title": "な行・は行", "sub": "n、h 開頭", "rows": grid(G[4:6], ex),
         "notes": ["ふ 念 fu，上排牙齒不碰嘴唇，比英文的 f 輕。", "ぬ／め：ぬ 的尾巴有一個圈。ね／れ／わ 的左半邊一樣，看右下怎麼收尾。",
                   "は、へ 當助詞時念 wa、e（こんにちは＝konnichiwa）。"]},
        {"id": "h4", "title": "ま行・や行", "sub": "m、y 開頭", "rows": grid(G[6:8], ex),
         "notes": ["や行只有 や、ゆ、よ 三個。", "ま／も：も 的勾在下面、橫線穿過去。", "ゆ 和 よ 縮小寫成 ゅ、ょ 時，用來組拗音（第 7 課）。"]},
        {"id": "h5", "title": "ら行・わ・を・ん", "sub": "r 開頭與最後幾個", "rows": grid(G[8:11], ex),
         "notes": ["ら行的 r 是舌尖輕彈一下，介於 l 和 d 之間，不捲舌。", "る／ろ：る 的尾巴有圈。わ／ね／れ 看右下。",
                   "を 只當助詞用，念 o。ん 是獨立的一拍鼻音，不會出現在字首。"]},
        {"id": "h6", "title": "濁音", "sub": "゛：g、z、d、b", "rows": grid(DAKUON[0:4], ex),
         "notes": ["右上加兩點（゛）就變成濁音：か→が、さ→ざ、た→だ、は→ば。", "ぢ 和 じ 同音、づ 和 ず 同音；平常幾乎都寫 じ、ず。",
                   "台灣人容易把 が 念成 ka：聲帶要震動。"]},
        {"id": "h7", "title": "半濁音・拗音（一）", "sub": "゜與 ゃゅょ", "rows": grid(DAKUON[4:5] + yoon()[0:4], ex),
         "notes": ["は行右上加圈（゜）變成 p 開頭：ぱ ぴ ぷ ぺ ぽ。", "拗音＝い段假名＋小寫的 ゃ ゅ ょ，合起來只算一拍：き＋ゃ＝きゃ（kya），不是 き・や 兩拍。",
                   "小字和大字意思不同：きゃく（客人）≠ きやく（規約）。"]},
        {"id": "h8", "title": "拗音（二）", "sub": "ひゃ～ぴゃ", "rows": grid(yoon()[4:], ex),
         "notes": ["じゃ、じゅ、じょ 很常見：じゅうしょ（住址）、じょうしゃけん（乘車券）。", "りゃ、りゅ、りょ 的 r 一樣是輕彈：りょかん（旅館）。"]},
        {"id": "h9", "title": "促音・長音", "sub": "っ與拉長的音", "kind": "pairs", "tip": "點一下聽，比較長短音、有沒有促音。",
         "rows": [[pair(*PAIRS[i]), pair(*PAIRS[i + 1])] for i in range(0, len(PAIRS), 2)],
         "notes": ["小寫的 っ（促音）：停一拍再發下一個子音，きって＝ki・t・te。", "長音：前一個音拉長一拍。あ段加 あ、い段加 い、う段加 う、え段加 い、お段加 う（おう 念 ō）；片假名一律用「ー」。",
                   "長短音、有沒有促音，意思都不同：ビル（大樓）≠ ビール（啤酒）、とり（鳥）≠ とおり（街道）。"]},
    ]
    kata_l = [
        {"id": "k1", "title": "ア行～サ行", "sub": "片假名 a、k、s", "rows": grid(G[0:3], ex, True),
         "notes": ["片假名用來寫外來語、外國地名與人名，菜單、招牌上很多。筆畫比較直、比較少。", "念法跟平假名完全一樣，只是寫法不同。",
                   "シ（shi）／ツ（tsu）最容易搞混：シ 的兩點橫著排、最後一筆由下往上；ツ 的兩點直著排、最後一筆由上往下。"]},
        {"id": "k2", "title": "タ行～ハ行", "sub": "片假名 t、n、h", "rows": grid(G[3:6], ex, True),
         "notes": ["チ／テ、ナ／メ、ヌ／ス 長得像，多看幾次。", "ホテル、タクシー、トイレ 都是旅遊必看的片假名。"]},
        {"id": "k3", "title": "マ行～ン", "sub": "片假名 m、y、r、w、n", "rows": grid(G[6:11], ex, True),
         "notes": ["ソ（so）／ン（n）：和 シ／ツ 同一個規則，ン 的最後一筆由下往上、ソ 由上往下。", "ワ／ウ、ラ／ヲ、ユ／コ 容易看錯。"]},
        {"id": "k4", "title": "濁音・半濁音", "sub": "片假名 ゛ ゜", "rows": grid(DAKUON, ex, True),
         "notes": ["跟平假名一樣，加 ゛ 或 ゜。", "バス（公車）、ビール（啤酒）、パン（麵包）、ポイント（點數）。"]},
        {"id": "k5", "title": "拗音", "sub": "片假名 ャュョ", "rows": grid(yoon(), ex, True),
         "notes": ["跟平假名的拗音一樣：キャ、シュ、チョ…", "シャツ（襯衫）、ジュース（果汁）、チョコレート（巧克力）。"]},
        {"id": "k6", "title": "外來語的特殊音", "sub": "ティ、ファ…", "rows": [[foreign(ch, r, ex) for ch, r in FOREIGN[i:i + 4]] for i in range(0, len(FOREIGN), 4)],
         "notes": ["為了寫外來語另外組出來的音，小寫的 ァィゥェォ 跟在前面的假名後面：ティ＝ti、ファ＝fa。",
                   "長音一律用「ー」：コーヒー（咖啡）、ビール（啤酒）、スーパー（超市）。", "看到不會念的片假名，先猜英文：チケット＝ticket、レシート＝receipt。"]},
    ]
    def chart_rows(rows, katakana=False):
        return [[{"ch": kata(c[0]) if katakana else c[0], "roma": c[1], "a": audio_key(c[1], c[0])} if c else None for c in row] for row in rows]
    chart = {"tabs": [
        {"title": "平假名", "sections": [{"title": "清音", "rows": chart_rows(GOJUON)}, {"title": "濁音・半濁音", "rows": chart_rows(DAKUON)},
                                       {"title": "拗音", "rows": chart_rows(yoon())}]},
        {"title": "片假名", "sections": [{"title": "清音", "rows": chart_rows(GOJUON, True)}, {"title": "濁音・半濁音", "rows": chart_rows(DAKUON, True)},
                                       {"title": "拗音", "rows": chart_rows(yoon(), True)}]},
    ]}
    data = {"kind": "kana", "title": "五十音", "lang": "ja", "sub": "平假名 9 課、片假名 6 課",
            "intro": "日文的字母叫「假名」，一個假名＝一拍。先學平假名（字卡的標音都是它），再學片假名（外來語、菜單、招牌）。每課先看表、點一下聽，再做練習。",
            "groups": [{"title": "平假名", "lessons": hira}, {"title": "片假名", "lessons": kata_l}], "chart": chart}
    with open(os.path.join(ROOT, "data", "letters.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    seen, uniq = set(), []
    for t in TTS:
        if t["file"] not in seen:
            seen.add(t["file"]); uniq.append(t)
    with open(os.path.join(WORK, "build", "letters_tts.json"), "w", encoding="utf-8") as f:
        json.dump(uniq, f, ensure_ascii=False, indent=0)
    n_items = sum(1 for g in data["groups"] for l in g["lessons"] for row in l["rows"] for c in row if c)
    n_ex = sum(1 for g in data["groups"] for l in g["lessons"] for row in l["rows"] for c in row if c and c.get("ex"))
    print(f"{sum(len(g['lessons']) for g in data['groups'])} 課、{n_items} 格（有例字 {n_ex}）、音檔 {len(uniq)} 個")


def pair(w, say, roma, zh):
    key = add_tts("l/w-" + roma.replace("ō", "oo").replace("ā", "aa").replace("ī", "ii"), say, "-10%")
    return {"ch": w, "roma": roma, "a": key, "zh": zh}


def foreign(ch, roma, ex):
    key = add_tts(f"l/f-{roma}", ch, "-45%")
    d = {"ch": ch, "roma": roma, "a": key}
    e = ex.pick(ch, True)
    if e:
        d["ex"] = e
    return d


if __name__ == "__main__":
    main()

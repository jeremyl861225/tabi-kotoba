"""文法專欄資料（2026-10-03，韓文版 yeohaengmal 同一套）：tools/grammar/*.py（內容手寫）→ data/grammar.json，並列出要合成的音檔。

輸出
- data/grammar.json：{ title, intro, groups: [{ title, lessons: [{ id, title, sub, summary, formula[], body[], table, ex[], notes[], quiz[] }] }] }
  - 日文都用 {漢字|かな} 標音（跟字卡一樣，設定頁的假名標音會生效）；body／notes／表格裡的 **粗體** 與日文由 js/grammar.js 轉成標記。
  - ex[]：{ ja, zh, a }；ja 裡的 [ ] 是這課要醒目標出的文法部分（朗讀時拿掉）；a 是音檔 key（audio/<a>.mp3）。
  - quiz[]：{ s, zh, o[], a, why, au }：s 有 ___ 是填空題（o 是選項，a 是正解的位置）；s 是 null 是「選出正確的句子」（o 是整句）。au 是正解整句的音檔 key。
- workspace/build/grammar_tts.json：給 tools/make_extra_audio.py 的音檔清單（女聲 Nanami，語速 -10%）。
- 朗讀文字＝標音的假名（畫面上的振假名＝語音念的，兩邊一致）。直接送漢字不行：2026-10-03 用聲紋比對抓到語音自己選讀法
  （「きれいな町」念成ちょう、「何も」念成なんも、「日本」念成にっぽん）；但全送假名也有兩個問題，這支程式處理掉了：
  (1) 助詞「は」「へ」：用 fugashi（UniDic）對**漢字原文**斷詞，判斷是助詞的 は→わ、へ→え（假名文字裡「ふくろはいります」分不出 は 是助詞）；
  (2) 助詞後面接 は 開頭的詞（日本語で｜話します、中に｜入って）：留一個空格，語音才不會斷成「では」「には」。
  句子照原樣的 prosody 會比真人平（全假名的缺點），但讀音與振假名一致。
- 音檔名是「朗讀文字＋聲音＋語速」的雜湊（audio/g/<10 碼>.mp3）：句子改了網址就變，手機快取的舊檔不會播錯句子。沒用到的舊檔會被刪掉。

用法：python tools/build_grammar.py（工作區 .venv）；之後 python tools/make_extra_audio.py build/grammar_tts.json（只做新增或改過的）。"""
import datetime, glob, hashlib, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.environ.get("TK_WORK", os.path.expanduser("~/Desktop/Claude code/workspace/work/jp-travel-vocab"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib   # noqa: E402

MODULES = [("a", "GROUP_A"), ("b", "GROUP_B"), ("c", "GROUP_C"), ("d", "GROUP_D"), ("e", "GROUP_E")]

VOICE, RATE = "n", "-10%"
RUBY = re.compile(r"\{([^|{}]+)\|([^{}]+)\}")
KANJI = re.compile(r"[㐀-鿿豈-﫿々〆ヶ]")
SPOKEN_OK = re.compile(r"[ぁ-んァ-ヶー。、？！ 〜]+")      # 朗讀文字可以有的字元（假名、標點、空格）
errors = []
tts = {}      # 音檔 key -> 朗讀文字
# 語音念不對的句子改送別的寫法：{原本的朗讀文字: 改送的}（2026-10-03 聲紋比對後填）
SAY_FIX = {}


def err(lid, msg):
    errors.append(f"[{lid}] {msg}")


def reading(markup):
    return RUBY.sub(r"\2", markup)


_tagger = None


def spoken(markup):
    """標音句 → 朗讀文字（假名；助詞は→わ、へ→え；助詞後面接 は 開頭的詞時留空格）"""
    global _tagger
    if _tagger is None:
        from fugashi import Tagger
        _tagger = Tagger()
    W, reads, pos = "", [], 0              # W：漢字原文；reads[i]：第 i 個字送出去的讀音（標音的詞只放在第一個字）
    for mo in RUBY.finditer(markup):
        for ch in markup[pos:mo.start()]:
            W += ch
            reads.append(ch)
        for k, ch in enumerate(mo.group(1)):
            W += ch
            reads.append(mo.group(2) if k == 0 else "")
        pos = mo.end()
    for ch in markup[pos:]:
        W += ch
        reads.append(ch)
    out, i = "", 0
    for w in _tagger(W):
        s = w.surface
        j = W.index(s, i)
        assert j == i, f"斷詞對不上原文：{W}"
        piece = "".join(reads[i:i + len(s)])
        if w.feature.pos1 == "助詞" and s == "は":
            piece = "わ"
        elif w.feature.pos1 == "助詞" and s == "へ":
            piece = "え"
        elif piece.startswith("は") and out.endswith(("で", "に", "と")):
            piece = " " + piece
        out += piece
        i += len(s)
    return out


def say(markup, lid):
    """標音句 → 朗讀文字（讀音）→ 音檔 key"""
    text = spoken(markup.replace("[", "").replace("]", ""))
    text = SAY_FIX.get(text, text)
    if not SPOKEN_OK.fullmatch(text):
        err(lid, f"朗讀文字有假名、漢字、標點以外的字元：{text}")
    key = "g/" + hashlib.sha1(f"{text}|{VOICE}|{RATE}".encode()).hexdigest()[:10]
    tts[key] = text
    return key


def check_markup(lid, s, what):
    """句子裡的漢字都要有標音，標音只能是假名"""
    for m in RUBY.finditer(s):
        if not re.fullmatch(r"[ぁ-んァ-ヶー]+", m.group(2)):
            err(lid, f"{what}的標音不是假名：{m.group(0)}")
    if KANJI.search(RUBY.sub("", s)):
        err(lid, f"{what}有漢字沒標音：{s}")
    if re.search(r"[0-9A-Za-z]", RUBY.sub("", s)):
        err(lid, f"{what}有數字或英文字母（語音念法不一定對，改寫成假名或漢字）：{s}")


def lesson_out(l):
    lid = l["id"]
    if not re.fullmatch(r"\w+", lid):
        err(lid, "id 只能用字母數字底線")
    for k in ("title", "sub", "summary", "formula", "body", "ex", "notes", "quiz"):
        if not l.get(k):
            err(lid, f"缺 {k}")
    t = l.get("table")
    if t:
        head, rows = t
        for r in rows:
            if len(r) != len(head):
                err(lid, f"表格欄數不符：{r}")
    ex = []
    for ja, zh in l["ex"]:
        if ja.count("[") != ja.count("]") or ja.count("[") < 1:
            err(lid, f"例句的 [ ] 沒成對或沒標出重點：{ja}")
        for seg in re.findall(r"\[([^\]]*)\]", ja):
            if seg.count("{") != seg.count("}"):
                err(lid, f"[ ] 不能切在標音中間：{ja}")
        check_markup(lid, ja.replace("[", "").replace("]", ""), "例句")
        if not zh:
            err(lid, f"例句缺中文：{ja}")
        ex.append({"ja": ja, "zh": zh, "a": say(ja, lid)})
    if len(ex) < 5 or len({e["zh"] for e in ex}) != len(ex):
        err(lid, "例句至少 5 句，中文不能重複（聽力題要用）")
    quiz = []
    for s, zh, opts, a, why in l["quiz"]:
        if not (2 <= len(opts) <= 4) or len(set(opts)) != len(opts):
            err(lid, f"選項要 2–4 個、不重複：{opts}")
        if not (0 <= a < len(opts)):
            err(lid, f"正解位置不對：{opts}")
        if not zh or not why:
            err(lid, f"題目缺中文或解釋：{opts}")
        if s is None:
            full = opts[a]
            for o in opts:
                if not o.endswith(("。", "？", "！")):
                    err(lid, f"整句選項要以句尾標點結束：{o}")
        else:
            if s.count("___") != 1:
                err(lid, f"填空題要剛好一個 ___：{s}")
            full = s.replace("___", opts[a])
            if len({s.replace("___", o) for o in opts}) != len(opts):
                err(lid, f"填空後有重複的句子：{s}")
        for o in opts:
            check_markup(lid, o, "選項")
        if len({RUBY.sub(r"\1", o) for o in opts}) != len(opts):
            err(lid, f"選項去掉標音後不能一樣（設定頁關掉假名標音就分不出來）：{opts}")
        check_markup(lid, full, "題目")
        quiz.append({"s": s, "zh": zh, "o": opts, "a": a, "why": why, "au": say(full, lid)})
    if len(quiz) < 5:
        err(lid, "練習題至少 5 題")
    return {"id": lid, "title": l["title"], "sub": l["sub"], "summary": l["summary"], "formula": l["formula"], "body": l["body"],
            "table": ({"head": t[0], "rows": t[1]} if t else None), "ex": ex, "notes": l["notes"], "quiz": quiz}


def main():
    groups = []
    ids = set()
    for mod, name in MODULES:
        try:
            m = importlib.import_module(f"grammar.{mod}")
        except ModuleNotFoundError:
            continue
        for g in ([getattr(m, name)] if hasattr(m, name) else []) + [getattr(m, n) for n in dir(m) if n.startswith("GROUP_") and n != name]:
            out = {"title": g["title"], "lessons": []}
            for l in g["lessons"]:
                if l["id"] in ids:
                    err(l["id"], "id 重複")
                ids.add(l["id"])
                out["lessons"].append(lesson_out(l))
            groups.append(out)
    if errors:
        print("\n".join(errors))
        sys.exit(f"{len(errors)} 個問題，沒有輸出")
    n = sum(len(g["lessons"]) for g in groups)
    data = {
        "version": datetime.date.today().isoformat(), "lang": "ja", "title": "文法",
        "intro": f"從語序、助詞、動詞變化到旅行最常用的句型，共 {n} 課。每課先看重點與例句（點一下就能聽），再做練習；答對八成算學完。",
        "groups": groups,
    }
    with open(os.path.join(ROOT, "data", "grammar.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    jobs = [{"file": f"audio/{k}.mp3", "text": t, "voice": VOICE, "rate": RATE} for k, t in sorted(tts.items())]
    os.makedirs(os.path.join(WORK, "build"), exist_ok=True)
    with open(os.path.join(WORK, "build", "grammar_tts.json"), "w", encoding="utf-8") as f:
        json.dump(jobs, f, ensure_ascii=False, indent=0)
    keep = {os.path.basename(j["file"]) for j in jobs}
    gone = [p for p in glob.glob(os.path.join(ROOT, "audio", "g", "*.mp3")) if os.path.basename(p) not in keep]
    for p in gone:
        os.remove(p)
    print(f"{n} 課、例句 {sum(len(l['ex']) for g in groups for l in g['lessons'])} 句、練習題 {sum(len(l['quiz']) for g in groups for l in g['lessons'])} 題；"
          f"音檔 {len(jobs)} 個（刪掉舊的 {len(gone)} 個）；data/grammar.json {os.path.getsize(os.path.join(ROOT, 'data', 'grammar.json')) / 1024:.0f} KB")


if __name__ == "__main__":
    main()

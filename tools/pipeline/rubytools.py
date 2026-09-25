"""假名標音、讀音比對、羅馬拼音、語音合成文字。

標記格式：{漢字|かな}，其餘文字原樣（與 App 的 js/ruby.js 相同）。
"""
import re, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

RUBY_RE = re.compile(r"\{([^|{}]+)\|([^{}]+)\}")
ZW = "​"


def plain(markup):
    return RUBY_RE.sub(r"\1", markup).replace(ZW, "")


def reading(markup):
    return RUBY_RE.sub(r"\2", markup).replace(ZW, "")


def segments(markup):
    """[(base, rt or None)]"""
    out, last = [], 0
    for m in RUBY_RE.finditer(markup):
        if m.start() > last:
            out.append((markup[last:m.start()], None))
        out.append((m.group(1), m.group(2)))
        last = m.end()
    if last < len(markup):
        out.append((markup[last:], None))
    return out


LATIN_RUN = r"[A-Za-z](?:[A-Za-z\-]*[A-Za-z])?"
KANJI_CLASS = "㐀-鿿豈-﫿々〆ヶ"
# 英文字母的日文念法（JR、ATM、X線這類縮寫）；對不上時退回一般對齊
LETTER = {"A": "エー|エイ", "B": "ビー", "C": "シー", "D": "ディー|デー", "E": "イー", "F": "エフ", "G": "ジー", "H": "エイチ|エッチ",
          "I": "アイ", "J": "ジェー|ジェイ", "K": "ケー|ケイ", "L": "エル", "M": "エム", "N": "エヌ", "O": "オー", "P": "ピー", "Q": "キュー",
          "R": "アール", "S": "エス", "T": "ティー|テー", "U": "ユー", "V": "ブイ|ヴィー", "W": "ダブリュー", "X": "エックス", "Y": "ワイ", "Z": "ゼット|ズィー"}


def _is_latin(r):
    return bool(re.match(r"[A-Za-z]", r))


def _runs(text):
    """把單字切成漢字段、英文字母段與其他（假名、標點）段"""
    return re.findall("[" + KANJI_CLASS + "]+|" + LATIN_RUN + "|[^" + KANJI_CLASS + "A-Za-z]+", text)


def _letters_pat(run):
    """全大寫縮寫（JR、ATM）照字母念法組 regex；不是縮寫回傳 None"""
    if not (run.isalpha() and run.isupper()):
        return None
    return "(" + "".join("(?:" + "|".join(kata2hira(x) for x in LETTER[ch].split("|")) + ")" for ch in run) + ")"


def align(head, read):
    """漢字段、英文字母段對讀音：用假名段當錨點做 regex 配對；配不上回傳 None。
    英文字母段的標音一律用片假名（{JR|ジェイアール}、{Wi-Fi|ワイファイ}）"""
    runs = _runs(head)
    m = None
    for strict in (True, False):
        pat = ""
        for r in runs:
            if has_kanji(r):
                pat += "(.+?)"
            elif _is_latin(r):
                pat += (_letters_pat(r) if strict else None) or "(.+?)"
            else:
                pat += re.escape(kata2hira(r))
        m = re.fullmatch(pat, kata2hira(read))
        if m:
            break
    if not m:
        return None
    out, gi = [], 0
    for r in runs:
        if has_kanji(r) or _is_latin(r):
            rt = m.group(gi + 1)
            gi += 1
            out.append((r, hira2kata(rt) if _is_latin(r) else rt))
        else:
            out.append((r, None))
    return out


def word_ruby(head, read):
    """單字的標音標記：優先用 JmdictFurigana 的逐字對應，其次用假名錨點對齊，最後整段標"""
    latin = bool(re.search(r"[A-Za-z]", head))
    if not has_kanji(head) and not latin:
        return head
    if not re.search(r"[ぁ-ゖァ-ヺ]", read):
        return head  # 讀音欄沒有假名（照抄英文），不標
    if not latin:
        fur = furigana_index()
        segs = fur.get((head, read)) or fur.get((head, kata2hira(read)))
        if segs:
            return "".join(f"{{{b}|{rt}}}" if rt else b for b, rt in segs)
    al = align(head, read)
    if al:
        # 讀音裡的片假名（生ビール的ビール）原樣保留；漢字段若查得到 JmdictFurigana 就再細分
        fur = furigana_index()
        out = []
        for b, rt in al:
            segs = (fur.get((b, rt)) or fur.get((b, kata2hira(rt)))) if rt and has_kanji(b) and len(b) > 1 else None
            if segs:
                out.append("".join(f"{{{x}|{y}}}" if y else x for x, y in segs))
            else:
                out.append(f"{{{b}|{rt}}}" if rt else b)
        return "".join(out)
    return f"{{{head}|{kata2hira(read)}}}"


def split_group_ruby(markup):
    """一段標音跨了好幾個詞時照 Sudachi 的詞切開：{一度言|いちどい}って → {一度|いちど}{言|い}って。
    （2026-09-25 使用者：「もう一度言ってください」的いちどい 整串標在「一度言」上，看起來標錯字）
    切開後的讀音要和原本一字不差才換，對不上就維持原樣。"""
    segs = segments(markup)
    text = "".join(b for b, _ in segs)
    if not any(rt and len(b) > 1 for b, rt in segs):
        return markup
    toks = [(m.begin(), m.end(), m.surface(), kata2hira(m.reading_form())) for m in sudachi_tokens(text)]
    out, pos = [], 0
    for base, rt in segs:
        s, e = pos, pos + len(base)
        pos = e
        inner = [t for t in toks if t[0] < e and t[1] > s] if rt and len(base) > 1 else []
        if len(inner) < 2:
            out.append((base, rt))
            continue
        pieces = []
        for ts, te, surf, rd in inner:
            # 全是漢字的詞整個標一段（{一度|いちど}、{大丈夫|だいじょうぶ}）：逐字標會把字距撐開（大 丈 夫）
            if all(re.match(f"[{KANJI_CLASS}]", ch) for ch in surf):
                wm = f"{{{surf}|{rd}}}"
            else:
                wm = word_ruby(surf, rd) if has_kanji(surf) else surf
            p = ts
            for b2, r2 in segments(wm):
                bs, be = p, p + len(b2)
                p = be
                if bs >= s and be <= e:
                    pieces.append((b2, r2))
                elif bs < e and be > s:   # 標音單位跨出這一段（詞的讀音對不齊），放棄
                    pieces = None
                    break
            if pieces is None:
                break
        fur = furigana_index()
        known = lambda b, r: len(b) == 1 or fur.get((b, r)) or fur.get((b, kata2hira(r)))   # 「日間／かかん」這種分析器的怪切法不要
        if (pieces and "".join(b for b, _ in pieces) == base and all(r for _, r in pieces)
                and all(known(b, r) for b, r in pieces)
                and "".join(kata2hira(r) for _, r in pieces) == kata2hira(rt)):
            out.extend(pieces)
        else:
            out.append((base, rt))
    return "".join(f"{{{b}|{r}}}" if r else b for b, r in out)


def insert_tildes(markup, head):
    """標音是用去掉〜的寫法算的；把〜放回 head 裡原本的位置（〜は{食|た}べられません、{私|わたし}の{名前|なまえ}は〜です）"""
    tpos = [i for i, ch in enumerate(head) if ch in "〜～"]
    if not tpos:
        return markup
    out, k, n = [], 0, 0   # k：已輸出的 head 字數（含〜）、n：下一個〜在 tpos 的位置
    def flush():
        nonlocal k, n
        while n < len(tpos) and tpos[n] == k:
            out.append("〜")
            k += 1
            n += 1
    for b, rt in segments(markup):
        if rt:
            flush()
            out.append(f"{{{b}|{rt}}}")
            k += len(b)
        else:
            for ch in b:
                flush()
                out.append(ch)
                k += 1
    flush()
    out.extend("〜" for _ in tpos[n:])
    return "".join(out)


def uncovered_kanji(markup):
    """ruby 以外還有沒有漏標的漢字"""
    bare = RUBY_RE.sub("", markup)
    return [c for c in bare if has_kanji(c)]


def sudachi_reading_spans(text):
    """[(start, end, surface, hira_reading)]"""
    out, pos = [], 0
    for t in sudachi_tokens(text):
        s = t.surface()
        r = t.reading_form()
        hr = kata2hira(r) if r else s
        out.append((pos, pos + len(s), s, hr))
        pos += len(s)
    return out


_ROW = {v: k for k, vs in {"a": "あかさたなはまやらわがざだばぱぁゃ", "i": "いきしちにひみりぎじぢびぴぃ", "u": "うくすつぬふむゆるぐずづぶぷぅゅ",
                            "e": "えけせてねへめれげぜでべぺぇ", "o": "おこそとのほもよろをごぞどぼぽぉょ"}.items() for v in vs}


def long_vowel_forms(s):
    """分析器的長音「ー」換回平假名寫法（ぎょーざ → ぎょうざ；e 段可寫い或え、o 段可寫う或お）"""
    outs = {"": ""}
    for ch in s:
        nxt = {}
        for k in outs:
            if ch == "ー" and k and _ROW.get(k[-1]):
                for v in {"a": "あ", "i": "い", "u": "う", "e": "いえ", "o": "うお"}[_ROW[k[-1]]]:
                    nxt[k + v] = ""
            else:
                nxt[k + ch] = ""
        outs = dict(list(nxt.items())[:16])
    return set(outs)


def check_sentence(markup):
    """比對標記的讀音與 Sudachi 的讀音；回傳不一致的片段 [(base, rt, sudachi)]"""
    text = plain(markup)
    toks = sudachi_reading_spans(text)
    # 把 ruby 片段換成字元位置
    spans, pos = [], 0
    for base, rt in segments(markup.replace(ZW, "")):
        if rt:
            spans.append((pos, pos + len(base), base, rt))
        pos += len(base)
    bad = []
    for s, e, base, rt in spans:
        cover = [t for t in toks if t[0] < e and t[1] > s]
        if not cover:
            continue
        cs, ce = cover[0][0], cover[-1][1]
        # 這些 token 範圍內，標記給的讀音 = ruby 的 rt + 範圍內非 ruby 文字
        marked = ""
        p2 = 0
        for b2, r2 in segments(markup.replace(ZW, "")):
            ln = len(b2)
            seg_s, seg_e = p2, p2 + ln
            if seg_e > cs and seg_s < ce:
                if r2:
                    marked += kata2hira(r2)
                else:
                    marked += kata2hira(b2[max(0, cs - seg_s):ce - seg_s])
            p2 += ln
        sud = "".join(kata2hira(t[3]) for t in cover)
        if marked != sud and ("ー" not in sud or marked not in long_vowel_forms(sud)):
            bad.append((base, rt, sud, text[cs:ce]))
    # 同一範圍只報一次
    seen, uniq = set(), []
    for b in bad:
        if b[3] not in seen:
            seen.add(b[3])
            uniq.append(b)
    return uniq


def tts_text(markup, force_kana=()):
    """語音合成用文字：分析器讀法與標記不同的漢字改成假名，避免念錯"""
    bad = {b[0] for b in check_sentence(markup)} | set(force_kana)
    out = []
    for base, rt in segments(markup.replace(ZW, "")):
        if rt and base in bad:
            out.append(rt)
        else:
            out.append(base)
    return "".join(out).replace("〜", "").replace("～", "")


# ---------- 羅馬拼音（修訂黑本式，長音加橫線） ----------
KANA = {}
_base = {
    "あ": "a", "い": "i", "う": "u", "え": "e", "お": "o",
    "か": "ka", "き": "ki", "く": "ku", "け": "ke", "こ": "ko",
    "さ": "sa", "し": "shi", "す": "su", "せ": "se", "そ": "so",
    "た": "ta", "ち": "chi", "つ": "tsu", "て": "te", "と": "to",
    "な": "na", "に": "ni", "ぬ": "nu", "ね": "ne", "の": "no",
    "は": "ha", "ひ": "hi", "ふ": "fu", "へ": "he", "ほ": "ho",
    "ま": "ma", "み": "mi", "む": "mu", "め": "me", "も": "mo",
    "や": "ya", "ゆ": "yu", "よ": "yo",
    "ら": "ra", "り": "ri", "る": "ru", "れ": "re", "ろ": "ro",
    "わ": "wa", "ゐ": "i", "ゑ": "e", "を": "o", "ん": "n",
    "が": "ga", "ぎ": "gi", "ぐ": "gu", "げ": "ge", "ご": "go",
    "ざ": "za", "じ": "ji", "ず": "zu", "ぜ": "ze", "ぞ": "zo",
    "だ": "da", "ぢ": "ji", "づ": "zu", "で": "de", "ど": "do",
    "ば": "ba", "び": "bi", "ぶ": "bu", "べ": "be", "ぼ": "bo",
    "ぱ": "pa", "ぴ": "pi", "ぷ": "pu", "ぺ": "pe", "ぽ": "po",
    "ぁ": "a", "ぃ": "i", "ぅ": "u", "ぇ": "e", "ぉ": "o", "ゔ": "vu",
}
KANA.update(_base)
_yoon = {"ゃ": "a", "ゅ": "u", "ょ": "o"}
for k, v in list(_base.items()):
    if k in "きぎしじちぢにひびぴみり":
        stem = {"し": "sh", "じ": "j", "ち": "ch", "ぢ": "j"}.get(k, v[:-1] + "y")
        for s, sv in _yoon.items():
            KANA[k + s] = stem + sv
# 外來語組合
KANA.update({"てぃ": "ti", "でぃ": "di", "とぅ": "tu", "どぅ": "du", "ふぁ": "fa", "ふぃ": "fi", "ふぇ": "fe", "ふぉ": "fo",
             "うぃ": "wi", "うぇ": "we", "うぉ": "wo", "しぇ": "she", "じぇ": "je", "ちぇ": "che", "ゔぁ": "va", "ゔぃ": "vi",
             "ゔぇ": "ve", "ゔぉ": "vo", "つぁ": "tsa", "つぇ": "tse", "つぉ": "tso", "でゅ": "dyu", "ふゅ": "fyu"})
MACRON = {"a": "ā", "i": "ī", "u": "ū", "e": "ē", "o": "ō"}


def to_romaji(kana, verb_final_u=False):
    h = kata2hira(kana)
    out, i = [], 0
    while i < len(h):
        two = h[i:i + 2]
        if two in KANA and len(two) == 2:
            out.append(KANA[two]); i += 2; continue
        c = h[i]
        if c == "っ":
            nxt = h[i + 1:i + 3]
            r = KANA.get(nxt) if nxt in KANA else KANA.get(h[i + 1:i + 2], "")
            out.append("t" if r.startswith("ch") else (r[:1] if r else ""))
            i += 1; continue
        if c == "ー":
            if out and out[-1] and out[-1][-1] in MACRON:
                out[-1] = out[-1][:-1] + MACRON[out[-1][-1]]
            i += 1; continue
        if c == "ん":
            nxt = KANA.get(h[i + 1:i + 2], "")
            out.append("n'" if nxt[:1] in ("a", "i", "u", "e", "o", "y") else "n")
            i += 1; continue
        out.append(KANA.get(c, c)); i += 1
    # 長音：ou、oo、uu、aa → 橫線（動詞字尾的う不併）
    s = "".join(out)
    end = len(s) - 1 if verb_final_u and s.endswith("u") else len(s)
    body, tail = s[:end], s[end:]
    body = re.sub(r"o[ou](?![aeiou])", "ō", body)
    body = re.sub(r"uu", "ū", body)
    body = re.sub(r"aa", "ā", body)
    body = re.sub(r"ee", "ē", body)
    return body + tail


def romaji_for(head, read, kind="w", pos=()):
    verb_u = any(p.startswith("v5u") or p == "v5u" for p in pos) and kata2hira(read).endswith("う")
    if kind == "p":
        toks = sudachi_tokens(plain(head).replace("〜", "").replace("～", ""))
        rs = [kata2hira(t.reading_form() or t.surface()) for t in toks]
        if "".join(rs) == kata2hira(read).replace("〜", "").replace("～", ""):
            parts = [to_romaji(r) for r, t in zip(rs, toks) if t.part_of_speech()[0] != "補助記号"]
            return " ".join(p for p in parts if p).replace(" ,", ",")
    return to_romaji(read, verb_final_u=verb_u)


if __name__ == "__main__":
    for h, r in [("乗り換え", "のりかえ"), ("入国審査", "にゅうこくしんさ"), ("生ビール", "なまビール"), ("一人", "ひとり"), ("お手洗い", "おてあらい"), ("山手線", "やまのてせん"), ("トイレ", "トイレ"), ("東京", "とうきょう")]:
        print(h, r, word_ruby(h, r), to_romaji(r))
    for s in ["{新宿|しんじゅく}で{山手線|やまのてせん}に{乗|の}り{換|か}えます。", "{市場|いちば}で{魚|さかな}を{買|か}いました。", "{今日|きょう}は{一日中|いちにちじゅう}{雨|あめ}です。"]:
        print(s, check_sentence(s), tts_text(s))
    print(to_romaji("かう", verb_final_u=True), to_romaji("おもう", verb_final_u=True), to_romaji("コーヒー"), to_romaji("きっぷ"), to_romaji("まっちゃ"), to_romaji("せんえん"), to_romaji("きんえん"))

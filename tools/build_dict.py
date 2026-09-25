"""離線字典：從 JMdict 常用詞版（jmdict-eng-common，約 2.2 萬詞）抽出寫法、讀音、詞性、英文釋義（搜尋用）與中文釋義（顯示用），
輸出 data/dict.json 給 App 查字卡以外的字。資料授權 CC BY-SA 4.0（EDRDG），衍生檔沿用同授權。
"""
import json, os, glob, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.environ.get("TK_WORK", os.path.expanduser("~/Desktop/Claude code/workspace/work/jp-travel-vocab"))
SRC = sorted(glob.glob(os.path.join(WORK, "dict", "jmdict-eng-common-*.json")))[-1]

POS = [("v5", "動詞"), ("v1", "動詞"), ("vk", "動詞"), ("vs-", "動詞"), ("vz", "動詞"), ("adj-i", "い形容詞"), ("adj-na", "な形容詞"),
       ("adv", "副詞"), ("int", "感嘆詞"), ("pn", "代名詞"), ("ctr", "量詞"), ("num", "數詞"), ("prt", "助詞"), ("exp", "連語"),
       ("suf", "接尾詞"), ("pref", "接頭詞"), ("aux", "助動詞"), ("conj", "接續詞"), ("adj-pn", "連體詞"), ("n", "名詞")]


def pos_label(codes):
    for c in codes:
        for k, v in POS:
            if c == k or c.startswith(k):
                if c == "vs":
                    return "名詞（する動詞）"
                return v
    return ""


# opencc s2tw 會把正確的台灣用字改錯，代理照著改就會出錯（2026-09-26 實際出現：干擾→幹擾、傢伙→傢夥、游擊手→遊擊手）
OPENCC_FIX = {"幹擾": "干擾", "幹涉": "干涉", "幹預": "干預", "若幹": "若干", "傢夥": "傢伙", "遊擊手": "游擊手", "遊擊隊": "游擊隊",
              # 代理漏掉的簡體與非台灣寫法（2026-09-26 全檔掃描）
              "要么": "要麼", "昵稱": "暱稱", "涂層": "塗層", "追踪": "追蹤", "橱窗": "櫥窗", "公衆": "公眾", "世界杯": "世界盃",
              "周日": "週日", "周一": "週一", "周二": "週二", "周三": "週三", "周四": "週四", "周五": "週五", "周六": "週六",
              "周末": "週末", "一周": "一週", "周刊": "週刊", "周年": "週年", "情欲": "情慾", "求知欲": "求知慾"}


def load_zh():
    """代理翻好的中文釋義：build/dictzh/out-NN.tsv（jmid<TAB>中文），見 pipeline/dict_zh_prep.py"""
    zh = {}
    # fix.tsv：人工改過的（放最後，蓋過代理的翻譯）
    for f in sorted(glob.glob(os.path.join(WORK, "build", "dictzh", "out-*.tsv"))) + glob.glob(os.path.join(WORK, "build", "dictzh", "fix.tsv")):
        for ln in open(f, encoding="utf-8"):
            p = ln.rstrip("\n").split("\t")
            # 佔位文字（代理偷懶寫的「翻譯待補」）不算
            # 只收「編號<TAB>中文」兩欄；「-」、英文單字、佔位文字（代理偷懶寫的「翻譯待補」）都不算
            if len(p) == 2 and p[1].strip() not in ("", "-") and not re.search(r"待補|待翻|^翻譯$|TODO|[A-Za-z]*[a-z]{3,}", p[1]):
                z = p[1]
                for a, b in OPENCC_FIX.items():   # 代理照 opencc 改錯的字改回來
                    z = z.replace(a, b)
                senses = list(dict.fromkeys(x.strip() for x in z.split("；") if x.strip()))   # 去掉空義項與重複（理想的；理想的）
                zh[p[0].strip()] = "；".join(senses)
    return zh


def main():
    data = json.load(open(SRC, encoding="utf-8"))
    zh = load_zh()
    out = []
    for w in data["words"]:
        kanji = [k["text"] for k in w["kanji"] if k.get("common")] or [k["text"] for k in w["kanji"]][:1]
        kana = [r["text"] for r in w["kana"] if r.get("common")] or [r["text"] for r in w["kana"]][:1]
        senses = w["sense"][:3]
        uk = any("uk" in s.get("misc", []) for s in senses[:1])
        gl = []
        for s in senses:
            g = ", ".join(x["text"] for x in s["gloss"][:3])
            if g and g not in gl:
                gl.append(g)
        gloss = "; ".join(gl)
        if len(gloss) > 90:
            gloss = gloss[:88].rsplit(",", 1)[0] + "…"
        # i：JMdict 編號（音檔 audio/d/<i>.mp3 用它，重建字典也不會變）；z：中文釋義（2026-09-25 使用者：字典只列中文）
        e = {"i": w["id"], "k": kanji[:2], "r": kana[:2], "g": gloss, "p": pos_label(senses[0].get("partOfSpeech", []) if senses else [])}
        if w["id"] in zh:
            e["z"] = zh[w["id"]]
        if uk:
            e["u"] = 1  # 平常寫假名
        if not e["k"]:
            del e["k"]
        out.append(e)
    dst = os.path.join(ROOT, "data", "dict.json")
    json.dump({"source": "JMdict (EDRDG), CC BY-SA 4.0, common entries", "entries": out}, open(dst, "w", encoding="utf-8"),
              ensure_ascii=False, separators=(",", ":"))
    print(f"{len(out)} 詞 → data/dict.json（{os.path.getsize(dst) / 1024:.0f} KB），中文釋義 {sum(1 for e in out if 'z' in e)} 詞")


if __name__ == "__main__":
    main()

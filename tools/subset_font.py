"""把 M PLUS 1（OFL）裁成只含本 App 用到的字，輸出 fonts/mplus1-sub.woff2。

字集＝字卡資料（單字、讀音、例句、羅馬拼音）＋介面程式裡的日文字串＋完整平假名片假名＋ASCII 與長音字母。
字卡資料一改就要重跑（build_data.py 最後會呼叫）。
原檔：https://github.com/google/fonts/tree/main/ofl/mplus1（放在 workspace，不進 repo）。
"""
import json, os, re, sys
from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.environ.get("MPLUS1_SRC", os.path.expanduser("~/Desktop/Claude code/workspace/work/jp-travel-vocab/fonts/MPLUS1-var.ttf"))
OUT = os.path.join(ROOT, "fonts", "mplus1-sub.woff2")


def charset():
    chars = set()
    data = json.load(open(os.path.join(ROOT, "data", "cards.json"), encoding="utf-8"))
    for c in data["cards"]:
        for k in ("w", "r", "ex", "rm"):
            chars.update(c.get(k) or "")
    for t in data["themes"]:
        chars.update(t.get("ja", ""))
    # 介面程式與頁面裡的日文字（平假名、片假名、漢字都收，中文介面字多收幾個無妨）
    for rel in ("index.html", "js/app.js", "js/quiz.js"):
        chars.update(open(os.path.join(ROOT, rel), encoding="utf-8").read())
    chars.update(chr(c) for c in range(0x3041, 0x3097))   # ひらがな
    chars.update(chr(c) for c in range(0x30A1, 0x30FB))   # カタカナ
    chars.update("ー・「」『』（）、。！？～…々〆〇　")
    chars.update(chr(c) for c in range(0x20, 0x7F))
    chars.update("āīūēōĀĪŪĒŌâîûêôÂÎÛÊÔ’‘“”–—×÷")
    return chars


def main():
    font = TTFont(SRC)
    cmap = font.getBestCmap()
    wanted = sorted(ord(ch) for ch in charset() if ord(ch) in cmap)
    opts = subset.Options()
    opts.layout_features = ["*"]
    opts.layout_features_remove = ["vert", "vrt2", "vkna", "vpal", "vhal"]  # 只排橫式
    opts.name_IDs = ["*"]
    opts.notdef_outline = True
    opts.drop_tables += ["DSIG"]
    sub = subset.Subsetter(opts)
    sub.populate(unicodes=wanted)
    sub.subset(font)
    # 只留 400–800 的字重範圍（先裁字再縮軸，順序反過來 gvar 會找不到直排字形）
    font = instancer.instantiateVariableFont(font, {"wght": (400, 800)})
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    font.flavor = "woff2"
    font.save(OUT)
    print(f"{len(wanted)} 字 → {OUT}（{os.path.getsize(OUT) / 1024:.0f} KB）")


if __name__ == "__main__":
    main()

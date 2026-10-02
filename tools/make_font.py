"""Zen Old Mincho（SIL OFL 1.1）子集 → fonts/zenold-500.woff2、fonts/zenold-900.woff2。
2026-10-01 第一次裁切時用的字表在工作區 fonts/zenold/chars-all.txt（App 與字典用到的字）；
2026-10-02 加了五十音課程與數字專欄，這支程式把字表和 App 現在的文字（data/*.json 除了字典、js/*.js、index.html）合起來重裁。
資料或介面文字改了要重跑，並升 sw.js 的 CACHE_VERSION。原始字型在工作區 fonts/zenold/ZenOldMincho-{Medium,Black}.ttf（不進 repo）。"""
import glob, os
from fontTools import subset
from fontTools.ttLib import TTFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.environ.get("TK_WORK", os.path.expanduser("~/Desktop/Claude code/workspace/work/jp-travel-vocab"))
SRC = os.path.join(WORK, "fonts", "zenold")


def chars():
    text = open(os.path.join(SRC, "chars-all.txt"), encoding="utf-8").read()
    files = [os.path.join(ROOT, "index.html")] + glob.glob(os.path.join(ROOT, "js", "*.js"))
    files += [p for p in glob.glob(os.path.join(ROOT, "data", "*.json")) if not p.endswith("dict.json")]
    for p in files:
        text += open(p, encoding="utf-8").read()
    return "".join(sorted(set(text)))


def build(src, text, out):
    font = TTFont(src)
    opts = subset.Options()
    opts.layout_features = ["kern", "ccmp", "locl", "liga", "calt", "palt"]   # 直排特徵會讓裁切出錯，橫排也用不到
    opts.name_IDs = ["*"]
    opts.notdef_outline = True
    sub = subset.Subsetter(opts)
    sub.populate(text=text)
    sub.subset(font)
    font.flavor = "woff2"
    font.save(out)
    return os.path.getsize(out)


def main():
    text = chars()
    a = build(os.path.join(SRC, "ZenOldMincho-Medium.ttf"), text, os.path.join(ROOT, "fonts", "zenold-500.woff2"))
    b = build(os.path.join(SRC, "ZenOldMincho-Black.ttf"), text, os.path.join(ROOT, "fonts", "zenold-900.woff2"))
    n = len(TTFont(os.path.join(ROOT, "fonts", "zenold-900.woff2")).getBestCmap())
    print(f"字表 {len(text)} 字（字型裡有的 {n} 字）；zenold-500 {a / 1024:.0f} KB、zenold-900 {b / 1024:.0f} KB")


if __name__ == "__main__":
    main()

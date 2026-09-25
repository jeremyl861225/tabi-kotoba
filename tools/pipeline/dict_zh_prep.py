"""離線字典的中文釋義：替翻譯代理切輸入檔（build/dictzh/in-NN.tsv，每檔 1,000 詞）。

2026-09-25 使用者：字典（字卡以外的字）要列中文意思，不要英文。JMdict 沒有中文，
由代理把英文釋義（含前三個義項）翻成台灣用語，寫回 out-NN.tsv（jmid<TAB>中文），build_dict.py 合併進 data/dict.json 的 z 欄。
依詞頻排序（常用的在前），每檔 500 詞。
每行：jmid、寫法（/ 分隔）、讀音（/ 分隔）、詞性、英文義項（義項之間用 ｜）。

用法：python3 tools/pipeline/dict_zh_prep.py
"""
import glob, json, os

WORK = os.environ.get("TK_WORK", os.path.expanduser("~/Desktop/Claude code/workspace/work/jp-travel-vocab"))
OUT = os.path.join(WORK, "build", "dictzh")
SRC = sorted(glob.glob(os.path.join(WORK, "dict", "jmdict-eng-common-*.json")))[-1]
CHUNK = 500


def main():
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from build_dict import pos_label
    from wordfreq import zipf_frequency
    os.makedirs(OUT, exist_ok=True)
    rows = []
    for w in json.load(open(SRC, encoding="utf-8"))["words"]:
        kanji = [k["text"] for k in w["kanji"] if k.get("common")] or [k["text"] for k in w["kanji"]][:1]
        kana = [r["text"] for r in w["kana"] if r.get("common")] or [r["text"] for r in w["kana"]][:1]
        senses = []
        for s in w["sense"][:3]:
            g = ", ".join(x["text"] for x in s["gloss"][:4])
            if g and g not in senses:
                senses.append(g)
        pos = pos_label(w["sense"][0].get("partOfSpeech", []) if w["sense"] else [])
        clean = lambda x: x.replace("\t", " ").replace("\n", " ")
        form = (kanji or kana)[0]
        rows.append((-zipf_frequency(form, "ja"), "\t".join([w["id"], "/".join(kanji[:2]) or "-", "/".join(kana[:2]), pos or "-", clean(" ｜ ".join(senses))])))
    # 常用的先翻（2026-09-25：分批上線時，最常被查到的詞先有中文）
    rows = [r for _, r in sorted(rows, key=lambda x: x[0])]
    for f in glob.glob(os.path.join(OUT, "in-*.tsv")):
        os.remove(f)
    n = 0
    for i in range(0, len(rows), CHUNK):
        n += 1
        with open(os.path.join(OUT, f"in-{n:02d}.tsv"), "w", encoding="utf-8") as f:
            f.write("\n".join(rows[i:i + CHUNK]) + "\n")
    print(f"{len(rows)} 詞 → {n} 個檔（{OUT}）")


if __name__ == "__main__":
    main()

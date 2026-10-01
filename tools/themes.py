"""主題（路線）定義：代碼、名稱、路線色，以及由路線色推算的色場、文字與線條色。"""

# 色票：一個主題家族一個顏色，只當點綴（線、站點、站號章、色點），不整片鋪色。
# 舊紀錄：2026-09-24 用 Colormind「ui」模型配的寶石灰調（workspace/palette/colormind/），2026-10-02 換成下面的天色系。
PALETTES = {
    # 2026-10-02 暮色玻璃：家族色改成「一天的天色」裡的日本傳統色（使用者要求類別顏色配合新設計）；
    # 以 OKLCH 定色相、亮度相近（0.47–0.64），五色＝淺底 LS、淺強調 LA、主色 M、深強調 DA、深字 DS 由主色推算
    "basic": ["#f0f5ff", "#6a7da6", "#44598b", "#2f3e64", "#141a29"],   # 紺 oklch(0.47 0.085 266)
    "move": ["#ebf8fc", "#60a3ba", "#1e809c", "#196176", "#091e25"],   # 浅葱 oklch(0.56 0.095 222)
    "stay": ["#fbf4ea", "#d4a965", "#b5811c", "#8e661e", "#22190a"],   # 山吹 oklch(0.64 0.125 78)
    "food": ["#fef2ed", "#e39066", "#c7632a", "#9a4e24", "#26160e"],   # 柿 oklch(0.61 0.145 47)
    "shop": ["#fef1f6", "#d67ea9", "#b94f87", "#8d3d67", "#25151d"],   # 紅梅 oklch(0.58 0.15 350)
    "care": ["#fff1f1", "#d26d6b", "#b63a3f", "#882a2e", "#271514"],   # 茜 oklch(0.53 0.16 22)
    "city": ["#edf8f1", "#6dab87", "#378a5f", "#2a6948", "#0e1f15"],   # 若竹 oklch(0.57 0.105 158)
    "listen": ["#f7f3fe", "#a087c7", "#7f5fab", "#5f4781", "#1d1726"],   # 藤 oklch(0.55 0.12 302)
}
ROLE = {"LS": 0, "LA": 1, "M": 2, "DA": 3, "DS": 4}
# 每條路線用所屬色票的哪個顏色（M+DA 表示兩色中間）
ASSIGN = {
    "GR": ("basic", "M"), "VB": ("basic", "DA"), "NM": ("basic", "LA"),
    "AP": ("move", "M"), "TR": ("move", "LA"), "BT": ("move", "DA"), "DR": ("move", "M+DA"), "DI": ("move", "M+LA"),
    "HT": ("stay", "M"), "ON": ("stay", "DA"),
    "FD": ("food", "M"), "RS": ("food", "DA"), "DK": ("food", "LA"),
    "SH": ("shop", "M"), "CV": ("shop", "DA"), "DS": ("shop", "LA"),
    "EM": ("care", "M"), "MD": ("care", "LA"),
    "SG": ("city", "M"), "SN": ("city", "DA"), "SV": ("city", "LA"),
    "LS": ("listen", "M"),
    # 2026-09-25 擴充到日檢 N3：基礎詞類與敬語
    "AJ": ("basic", "M"), "AV": ("basic", "M"), "CJ": ("basic", "M"),
    "LF": ("city", "M"), "KG": ("listen", "M"),
    # 2026-09-29 料理字庫擴充（使用者：居酒屋、料理、酒、懷石、魚貝、蔬菜）：都屬飲食家族
    "IZ": ("food", "DA"), "DN": ("food", "M"), "SU": ("food", "M"), "SK": ("food", "LA"), "KS": ("food", "M"), "VG": ("food", "M"),
}

# (id, 中文名稱, 日文路線名)；2026-09-24 名稱改成直白的說法（使用者覺得「聽懂對方說的話」莫名其妙）
THEMES = [
    ("GR", "寒暄與應答", "あいさつ線"),
    ("NM", "數字・時間・價錢", "かず線"),
    ("AP", "機場與入境", "くうこう線"),
    ("TR", "搭電車", "てつどう線"),
    ("BT", "巴士與計程車", "バス線"),
    ("DR", "自駕與加油", "ドライブ線"),
    ("DI", "問路與方向", "みちあんない線"),
    ("HT", "飯店住宿", "ホテル線"),
    ("ON", "溫泉旅館", "おんせん線"),
    ("RS", "餐廳點餐", "レストラン線"),
    ("FD", "料理與食材", "グルメ線"),
    ("DK", "飲料與甜點", "カフェ線"),
    ("IZ", "居酒屋", "いざかや線"),
    ("DN", "常見料理", "りょうり線"),
    ("SU", "壽司與海鮮", "すし線"),
    ("SK", "酒類", "おさけ線"),
    ("KS", "懷石與和食", "わしょく線"),
    ("VG", "蔬菜與調味料", "やさい線"),
    ("SH", "購物與結帳", "ショッピング線"),
    ("CV", "便利商店", "コンビニ線"),
    ("DS", "藥妝店", "くすり線"),
    ("MD", "看醫生", "びょういん線"),
    ("EM", "緊急求助", "きんきゅう線"),
    ("SG", "觀光景點", "かんこう線"),
    ("SN", "招牌與標示", "ひょうしき線"),
    ("SV", "網路・領錢・天氣", "せいかつ線"),
    ("LS", "店員與廣播常說的話", "きく線"),
    ("VB", "常用動詞", "どうし線"),
    ("AJ", "形容詞", "けいようし線"),
    ("AV", "副詞", "ふくし線"),
    ("CJ", "連接詞與句型", "つなぎ線"),
    ("LF", "生活用語", "くらし線"),
    ("KG", "敬語", "けいご線"),
]


N1 = "#e4e9f3"   # 淺色模式底：白天天空上的玻璃（2026-10-02 暮色玻璃；之前是米白 #f7f5f0）
N9 = "#141a36"   # 深色模式底／深色文字（傍晚的紺）
N8 = "#1f2650"   # 深色模式的玻璃面


def _rgb(h):
    return [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]


def _hex(rgb):
    return "#" + "".join(f"{max(0, min(255, round(c * 255))):02x}" for c in rgb)


def _lum(rgb):
    def ch(c):
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(x) for x in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    la, lb = _lum(a), _lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def _mix(a, b, t):
    """a 往 b 混 t（0..1）"""
    return [x + (y - x) * t for x, y in zip(a, b)]


def _toward(color, target, against, need):
    """把 color 往 target 推，直到與 against 的對比 ≥ need"""
    c = color
    for i in range(0, 101):
        c = _mix(color, target, i / 100)
        if contrast(c, against) >= need:
            break
    return c


def _alpha_for(ink, field, need, start=0.72):
    """ink 疊在 field 上最低要多少不透明度才達到 need 對比"""
    a = start
    while a < 1.0:
        if contrast(_mix(field, ink, a), field) >= need:
            return round(a, 2)
        a += 0.02
    return 1.0


def _pick(fam, role):
    pal = [_rgb(c) for c in PALETTES[fam]]
    if "+" in role:
        a, b = role.split("+")
        return _mix(pal[ROLE[a]], pal[ROLE[b]], 0.5)
    return pal[ROLE[role]]


def theme_list():
    white, n9, n1, n8 = [1, 1, 1], _rgb(N9), _rgb(N1), _rgb(N8)
    out = []
    for tid, name, ja in THEMES:
        fam, role = ASSIGN[tid]
        pal = PALETTES[fam]
        # 2026-09-25 使用者指出首頁「醫療緊急」色塊和下一站（看醫生）卡片顏色不同：同一家族的主題一律用家族主色 M，
        # 顏色＝分類。ASSIGN 裡的 role 保留作紀錄，不再決定顏色。
        c = _pick(fam, "M")
        dark = _rgb(pal[4])
        # 色場文字：白字或該色票的深字，取對比高者；都不到 4.5 就把色場往深字方向壓到白字過關
        cw, cd = contrast(c, white), contrast(c, dark)
        if max(cw, cd) >= 4.5:
            field, ink = c, (white if cw >= cd else dark)
        else:
            field, ink = _toward(c, dark, white, 4.5), white
        ink_rgb = ", ".join(str(round(x * 255)) for x in ink)
        a2 = _alpha_for(ink, field, 4.5)
        out.append({
            "id": tid, "code": tid, "name": name, "ja": ja, "family": fam,
            "color": _hex(c),
            "field": _hex(field),
            "on": _hex(ink),
            "on2": f"rgba({ink_rgb}, {a2})",
            "on3": f"rgba({ink_rgb}, 0.34)",
            "veil": f"rgba({ink_rgb}, {0.18 if ink == white else 0.1})",
            # 色場畫面裡的卡片：該色票的淺底與深字
            "paper": pal[0], "ink": pal[4],
            # 畫在淺底／深底上的線（非文字 ≥3:1）與文字（≥4.5:1）
            "lL": _hex(_toward(c, n9, n1, 3.0)),
            "lD": _hex(_toward(c, white, n9, 3.0)),
            "tL": _hex(_toward(c, n9, n1, 4.5)),
            "tD": _hex(_toward(c, white, n9, 4.5)),
            # 淡彩（首頁的下一站卡片）：白上 12% 的主題色、深色模式卡片面上 18%
            "bgL": _hex(_mix(white, c, 0.12)),
            "bgD": _hex(_mix(n8, c, 0.18)),
        })
    return out


THEME_IDS = [t[0] for t in THEMES]

# 首頁的主題家族分類（2026-09-25 使用者要求：首頁改依主題分類、以顏色區分）；
# 每個家族用色票主色（ASSIGN 裡 role 是 M 的主題）當代表色
FAMILY_NAMES = [("basic", "基本"), ("move", "交通"), ("stay", "住宿"), ("food", "飲食"), ("shop", "購物"),
                ("care", "醫療緊急"), ("city", "觀光生活"), ("listen", "店員廣播")]


def family_list():
    rep = {fam: tid for tid, (fam, role) in ASSIGN.items() if role == "M"}
    return [{"id": f, "name": n, "rep": rep[f]} for f, n in FAMILY_NAMES]

if __name__ == "__main__":
    for t in theme_list():
        print(t["id"], t["family"], "field", t["field"], "on", t["on"], t["on2"], "paper", t["paper"], "ink", t["ink"], "| lL", t["lL"], "lD", t["lD"])

"""主題（路線）定義：代碼、名稱、路線色。

路線色取材自東京實際的鐵道路線色（山手線黃綠、中央線橘、京濱東北線天藍、總武線黃……），
只拿來標示主題身分；文字色依對比度自動選黑或白。
"""

# (id, 中文名稱, 日文路線名, 路線色, 參考路線)
THEMES = [
    ("GR", "基本會話", "あいさつ線", "#80C241", "JR 山手線"),
    ("NM", "數字・時間・金額", "かず線", "#FF9500", "銀座線"),
    ("AP", "機場・入境", "くうこう線", "#00B2E5", "京濱東北線"),
    ("TR", "電車・車站", "てつどう線", "#FFD400", "中央・總武線"),
    ("BT", "巴士・計程車・船", "バス線", "#00AC9A", "埼京線"),
    ("DR", "自駕・加油", "ドライブ線", "#0079C2", "都營三田線"),
    ("DI", "問路・地點", "みちあんない線", "#8F76D6", "半藏門線"),
    ("HT", "住宿・飯店", "ホテル線", "#9C5E31", "副都心線"),
    ("ON", "溫泉・旅館", "おんせん線", "#EC6E65", "都營淺草線"),
    ("RS", "餐廳・點餐", "レストラン線", "#C1A470", "有樂町線"),
    ("FD", "料理・食材", "グルメ線", "#F15A22", "中央線快速"),
    ("DK", "飲料・甜點", "カフェ線", "#B6007A", "都營大江戶線"),
    ("SH", "購物・服飾", "ショッピング線", "#00BB85", "千代田線"),
    ("CV", "便利商店・超市", "コンビニ線", "#B5B5AC", "日比谷線"),
    ("DS", "藥妝・藥品", "くすり線", "#F59BBD", ""),
    ("MD", "身體・就醫", "びょういん線", "#A22041", ""),
    ("EM", "緊急・求助", "きんきゅう線", "#E60012", ""),
    ("SG", "觀光・景點", "かんこう線", "#2E8B57", ""),
    ("SN", "招牌・標示", "ひょうしき線", "#1B3A6B", ""),
    ("SV", "生活・通訊・天氣", "せいかつ線", "#5A6E7F", ""),
    ("LS", "聽懂對方說的話", "きく線", "#5E2D91", ""),
    ("VB", "常用動詞・形容詞", "ことば線", "#7A8B00", ""),
]


N1 = "#f3f4fa"   # 淺色模式底
N9 = "#121436"   # 深色模式底／深色文字


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


def theme_list():
    white, n9, n1 = [1, 1, 1], _rgb(N9), _rgb(N1)
    out = []
    for tid, name, ja, color, ref in THEMES:
        c = _rgb(color)
        # 色場：選白字或深靛字中對比較高者；兩者都不到 4.5 就把色場壓暗到白字過關
        cw, cd = contrast(c, white), contrast(c, n9)
        if max(cw, cd) >= 4.5:
            field, ink = c, (white if cw >= cd else n9)
        else:
            field, ink = _toward(c, n9, white, 4.5), white
        ink_rgba = "255, 255, 255" if ink == white else "18, 20, 54"
        a2 = _alpha_for(ink, field, 4.5)
        out.append({
            "id": tid, "code": tid, "name": name, "ja": ja,
            "color": color.lower(),
            "field": _hex(field),
            "on": _hex(ink),
            "on2": f"rgba({ink_rgba}, {a2})",
            "on3": f"rgba({ink_rgba}, 0.34)",
            "veil": f"rgba({ink_rgba}, {0.18 if ink == white else 0.1})",
            # 畫在淺底／深底上的線（非文字 ≥3:1）與文字（≥4.5:1）
            "lL": _hex(_toward(c, n9, n1, 3.0)),
            "lD": _hex(_toward(c, white, n9, 3.0)),
            "tL": _hex(_toward(c, n9, n1, 4.5)),
            "tD": _hex(_toward(c, white, n9, 4.5)),
        })
    return out


THEME_IDS = [t[0] for t in THEMES]

if __name__ == "__main__":
    for t in theme_list():
        print(t["id"], t["color"], "field", t["field"], "on", t["on"], t["on2"], "| lL", t["lL"], "lD", t["lD"], "tL", t["tL"], "tD", t["tD"])

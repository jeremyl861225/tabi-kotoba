"""App 圖示：深靛藍底、白色明朝體「旅」＋「たび」標音，下緣一條路線與站點（基本會話線的色）。
iOS 會自己切圓角，所以輸出滿版方形；maskable 版把內容縮進安全區。
字型用 macOS 內建的ヒラギノ明朝 ProN（只用來畫圖示，不隨 App 發佈）。"""
from PIL import Image, ImageDraw, ImageFont
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "icons")
FONT = "/System/Library/Fonts/ヒラギノ明朝 ProN.ttc"
NIGHT = (0x12, 0x14, 0x36)
LINE = (0x7B, 0x9C, 0xD6)   # 基本會話線的色，提亮一階讓深底上看得見
WHITE = (255, 255, 255)
RUBY = (0xA2, 0xA6, 0xC8)


def font(size, weight):
    # TTC 第 0 個是 ProN W3、第 2 個是 ProN W6
    return ImageFont.truetype(FONT, size, index=2 if weight >= 600 else 0)


def draw(size, scale=1.0):
    S = 1024
    img = Image.new("RGB", (S, S), NIGHT)
    d = ImageDraw.Draw(img)
    c = S / 2
    k = scale
    big = font(int(470 * k), 800)
    small = font(int(120 * k), 700)
    bb = d.textbbox((0, 0), "旅", font=big)
    sb = d.textbbox((0, 0), "たび", font=small)
    gap = int(26 * k)
    total = (sb[3] - sb[1]) + gap + (bb[3] - bb[1])
    top = c - total / 2 - int(70 * k)
    d.text((c - (sb[2] - sb[0]) / 2 - sb[0], top - sb[1]), "たび", font=small, fill=RUBY)
    d.text((c - (bb[2] - bb[0]) / 2 - bb[0], top + (sb[3] - sb[1]) + gap - bb[1]), "旅", font=big, fill=WHITE)
    # 路線與站點
    y = c + int(330 * k)
    x0, x1 = c - int(380 * k), c + int(380 * k)
    lw = int(40 * k)
    d.rounded_rectangle([x0, y - lw / 2, x1, y + lw / 2], radius=lw / 2, fill=LINE)
    for i, x in enumerate([x0 + lw / 2, c, x1 - lw / 2]):
        r = int(38 * k)
        d.ellipse([x - r, y - r, x + r, y + r], fill=WHITE if i < 2 else NIGHT, outline=LINE if i == 2 else None, width=int(16 * k))
        if i == 2:
            d.ellipse([x - r, y - r, x + r, y + r], outline=LINE, width=int(16 * k))
    return img.resize((size, size), Image.LANCZOS)


os.makedirs(OUT, exist_ok=True)
draw(192).save(os.path.join(OUT, "icon-192.png"))
draw(512).save(os.path.join(OUT, "icon-512.png"))
draw(180).save(os.path.join(OUT, "apple-touch-icon.png"))
draw(512, scale=0.8).save(os.path.join(OUT, "icon-maskable-512.png"))
print("icons written")

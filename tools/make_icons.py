"""App 圖示：一塊迷你站名牌——「たび」標在「旅」上方，下緣是山手線色帶。
iOS 會自己切圓角，所以輸出滿版方形；maskable 版把內容縮到安全區內。"""
from PIL import Image, ImageDraw, ImageFont
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "icons")
FONT_DIR = "/System/Library/Fonts/"
W7 = FONT_DIR + "ヒラギノ角ゴシック W7.ttc"
W6 = FONT_DIR + "ヒラギノ角ゴシック W6.ttc"
LINE = (0x80, 0xC2, 0x41)
PLATFORM = (0xE4, 0xE8, 0xE7)


def ink_box(draw, xy, text, font):
    return draw.textbbox(xy, text, font=font)


def draw_sign(size, scale=1.0):
    S = 1024
    img = Image.new("RGB", (S, S), PLATFORM if scale < 1 else (255, 255, 255))
    d = ImageDraw.Draw(img)
    # 內容區（maskable 時縮小置中）
    cw = int(S * scale)
    ox = (S - cw) // 2
    if scale < 1:
        d.rounded_rectangle([ox, ox, ox + cw, ox + cw], radius=int(cw * 0.06), fill=(255, 255, 255))
    band_h = int(cw * 0.085)
    band_y = ox + int(cw * 0.74)
    d.rectangle([ox, band_y, ox + cw, band_y + band_h], fill=LINE)
    notch = int(band_h * 0.9)
    d.polygon([(ox, band_y), (ox + notch, band_y + band_h / 2), (ox, band_y + band_h)], fill=(255, 255, 255))
    d.polygon([(ox + cw, band_y), (ox + cw - notch, band_y + band_h / 2), (ox + cw, band_y + band_h)], fill=(255, 255, 255))
    # 「旅」與「たび」：量墨跡框再堆疊（日文字型上下留白不對稱）
    f_big = ImageFont.truetype(W7, int(cw * 0.46))
    f_small = ImageFont.truetype(W6, int(cw * 0.13))
    bb = ink_box(d, (0, 0), "旅", f_big)
    sb = ink_box(d, (0, 0), "たび", f_small)
    big_h = bb[3] - bb[1]
    small_h = sb[3] - sb[1]
    gap = int(cw * 0.035)
    total = small_h + gap + big_h
    top = ox + (band_y - ox - total) // 2 + int(cw * 0.01)
    sx = ox + (cw - (sb[2] - sb[0])) // 2 - sb[0]
    d.text((sx, top - sb[1]), "たび", font=f_small, fill=(0x44, 0x4C, 0x4F))
    bx = ox + (cw - (bb[2] - bb[0])) // 2 - bb[0]
    d.text((bx, top + small_h + gap - bb[1]), "旅", font=f_big, fill=(0, 0, 0))
    return img.resize((size, size), Image.LANCZOS)


os.makedirs(OUT, exist_ok=True)
draw_sign(192).save(os.path.join(OUT, "icon-192.png"))
draw_sign(512).save(os.path.join(OUT, "icon-512.png"))
draw_sign(180).save(os.path.join(OUT, "apple-touch-icon.png"))
draw_sign(512, scale=0.78).save(os.path.join(OUT, "icon-maskable-512.png"))
print("icons written to", OUT)

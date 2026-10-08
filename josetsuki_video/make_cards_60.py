# ショート2本目(60cm YT660 vs HSS760nJ)用の縦画面カード(1080x1920)を images/ に描く。
# K0 = 写真の縦切り出し+冒頭の大見出し、K1〜K4 = 比較カード。字幕帯(y≈1400〜1680)には文字を置かない。
# usage: python3 prep_images.py && python3 make_cards_60.py
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

root = Path(__file__).parent
img_dir = root / "images"
W, H = 1080, 1920
NAVY = (0x0D, 0x2A, 0x47)
ORANGE = (0xF2, 0x6B, 0x0F)
ICE = (0xE8, 0xF1, 0xF8)
WHITE = (255, 255, 255)
FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"


def font(size):
    return ImageFont.truetype(FONT, size, index=0)


def snow_bg():
    """V1(雪の家)をぼかして白く飛ばした背景。"""
    bg = Image.open(img_dir / "V1.png").convert("RGB").resize((W, H))
    bg = bg.filter(ImageFilter.GaussianBlur(18))
    return Image.blend(bg, Image.new("RGB", (W, H), WHITE), 0.55)


def center(d, y, text, size, fill, stroke=0):
    d.text((W // 2, y), text, font=font(size), fill=fill, anchor="mm",
           stroke_width=stroke, stroke_fill=WHITE if stroke else None)


def mixed(d, y, parts, size):
    """色違いの文字列を中央揃えで1行に並べる。parts=[(text, color), ...]"""
    x = W / 2 - sum(font(size).getlength(t) for t, _ in parts) / 2
    for t, c in parts:
        d.text((x, y), t, font=font(size), fill=c, anchor="lm")
        x += font(size).getlength(t)


# K0: 冒頭。雪を飛ばす写真を縦に切り出し、上部に大見出し
photo = Image.open(img_dir / "P1_photo.png").convert("RGB")
cw = round(photo.height * W / H)
cx = 950
k0 = photo.crop((cx - cw // 2, 0, cx + cw // 2, photo.height)).resize((W, H), Image.LANCZOS)
ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
od = ImageDraw.Draw(ov)
for y in range(720):
    od.line([(0, y), (W, y)], fill=NAVY + (int(200 * (1 - y / 720)),))
k0 = Image.alpha_composite(k0.convert("RGBA"), ov)
d = ImageDraw.Draw(k0)
center(d, 230, "60cm除雪機", 132, WHITE)
mixed(d, 420, [("たった", WHITE), ("1.1万円", ORANGE), ("差", WHITE)], 120)
k0.convert("RGB").save(img_dir / "K0.png")


def two_col(d, top, rows, head_h=150, row_h=190):
    """2機種の比較表。rows=[(label, left, right, highlight_right)]"""
    left, mid, right = 60, W // 2, W - 60
    d.rounded_rectangle([left, top, right, top + head_h], radius=24, fill=NAVY)
    d.text(((left + mid) // 2, top + head_h // 2), "YT660", font=font(64), fill=WHITE, anchor="mm")
    d.text(((mid + right) // 2, top + head_h // 2), "HSS760nJ", font=font(64), fill=WHITE, anchor="mm")
    y = top + head_h + 16
    for label, a, b, hl in rows:
        d.rounded_rectangle([left, y, right, y + row_h], radius=20, fill=WHITE, outline=(0xC9, 0xD8, 0xE6), width=3)
        d.text((W // 2, y + 36), label, font=font(36), fill=(0x55, 0x6B, 0x80), anchor="mm")
        d.text(((left + mid) // 2, y + 118), a, font=font(76), fill=NAVY, anchor="mm")
        d.text(((mid + right) // 2, y + 118), b, font=font(76), fill=ORANGE if hl else NAVY, anchor="mm")
        y += row_h + 16
    return y


# K1: 価格と除雪幅
k1 = snow_bg()
d = ImageDraw.Draw(k1)
center(d, 250, "60cmクラス 2台", 88, NAVY)
y = two_col(d, 360, [("販売価格", "39.9万円", "41万円", False), ("除雪幅", "61.5cm", "60.5cm", False)])
d.rounded_rectangle([140, y + 30, W - 140, y + 170], radius=24, fill=NAVY)
mixed(d, y + 100, [("価格差 ", WHITE), ("たった1.1万円", ORANGE)], 64)
k1.save(img_dir / "K1.png")

# K2: 高い方が強くて軽い
k2 = snow_bg()
d = ImageDraw.Draw(k2)
mixed(d, 250, [("高い方が", NAVY)], 92)
mixed(d, 370, [("強くて", ORANGE), ("軽い", ORANGE)], 120)
y = two_col(d, 480, [("最大出力", "4.8PS", "5.8PS", True), ("重量", "112kg", "105kg", True)])
center(d, y + 70, "※メーカー公表値", 40, (0x55, 0x6B, 0x80))
k2.save(img_dir / "K2.png")

# K3: どっちを選ぶ
k3 = snow_bg()
d = ImageDraw.Draw(k3)
center(d, 250, "どっちを選ぶ？", 100, NAVY)
for i, (cond, model) in enumerate([("安さを重視", "YT660"), ("硬い雪が多い", "HSS760nJ"), ("物置への出し入れが多い", "HSS760nJ")]):
    top = 400 + i * 300
    d.rounded_rectangle([60, top, W - 60, top + 260], radius=24, fill=WHITE, outline=NAVY, width=4)
    d.rounded_rectangle([60, top, W - 60, top + 100], radius=24, fill=NAVY)
    d.rectangle([60, top + 70, W - 60, top + 100], fill=NAVY)
    d.text((W // 2, top + 52), cond, font=font(52), fill=WHITE, anchor="mm")
    d.text((W // 2, top + 182), "→ " + model, font=font(84), fill=ORANGE, anchor="mm")
k3.save(img_dir / "K3.png")

# K4: 締め(70cmへ)
k4 = snow_bg()
d = ImageDraw.Draw(k4)
center(d, 420, "駐車場が広いなら", 84, NAVY)
mixed(d, 560, [("70cm", ORANGE), ("クラスも候補", NAVY)], 96)
d.rounded_rectangle([90, 720, W - 90, 1000], radius=28, fill=NAVY)
center(d, 810, "3機種の比較は", 64, WHITE)
mixed(d, 910, [("関連動画", ORANGE), ("から", WHITE)], 80)
center(d, 1180, "北海道の除雪機選び", 56, NAVY)
k4.save(img_dir / "K4.png")
print("cards: K0〜K4")

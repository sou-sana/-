# 札幌に雪・入荷ショート（11/21）用の縦カード R0〜R4。在庫は販売ページの表示（11/21確認）。
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

root = Path(__file__).parent
img_dir = root / "images"
W, H = 1080, 1920
NAVY = (0x0D, 0x2A, 0x47)
ORANGE = (0xF2, 0x6B, 0x0F)
GRAY = (0x55, 0x6B, 0x80)
LINE = (0xC9, 0xD8, 0xE6)
WHITE = (255, 255, 255)
FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"


def font(size):
    return ImageFont.truetype(FONT, size, index=0)


def snow_bg():
    """V1(雪の家)をぼかして白く飛ばした背景。"""
    bg = Image.open(img_dir / "V1.png").convert("RGB").resize((W, H))
    bg = bg.filter(ImageFilter.GaussianBlur(18))
    return Image.blend(bg, Image.new("RGB", (W, H), WHITE), 0.55)


def center(d, y, text, size, fill):
    d.text((W // 2, y), text, font=font(size), fill=fill, anchor="mm")


def mixed(d, y, parts, size):
    """色違いの文字列を中央揃えで1行に並べる。parts=[(text, color), ...]"""
    x = W / 2 - sum(font(size).getlength(t) for t, _ in parts) / 2
    for t, c in parts:
        d.text((x, y), t, font=font(size), fill=c, anchor="lm")
        x += font(size).getlength(t)


def box(d, top, bottom, fill=WHITE):
    d.rounded_rectangle([60, top, W - 60, bottom], radius=26, fill=fill,
                        outline=None if fill == NAVY else LINE, width=3)




def shade(img, h, a0, a1):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    for y in range(h):
        od.line([(0, y), (W, y)], fill=NAVY + (int(a0 - (a0 - a1) * y / h),))
    return Image.alpha_composite(img.convert("RGBA"), ov)


def head(d, no, title, color=NAVY):
    d.rounded_rectangle([60, 170, 200, 310], radius=24, fill=ORANGE)
    d.text((130, 240), no, font=font(90), fill=WHITE, anchor="mm")
    d.text((240, 240), title, font=font(70), fill=color, anchor="lm")




ph = Image.open(img_dir / "Q4_v.png").convert("RGB").resize((W, H), Image.LANCZOS)
k0 = shade(ph, 760, 230, 60); d = ImageDraw.Draw(k0)
center(d, 250, "札幌に雪が積もった", 84, WHITE)
mixed(d, 410, [("今", WHITE), ("在庫がある", ORANGE), ("除雪機は？", WHITE)], 84)
k0.convert("RGB").save(img_dir / "R0.png")

k = snow_bg(); d = ImageDraw.Draw(k)
center(d, 260, "11月19日", 80, NAVY)
mixed(d, 390, [("ホンダ2機種が", NAVY), ("入荷", ORANGE)], 84)
box(d, 510, 1180)
for i, (a, b2) in enumerate([("HSS760nJ", "60cm・41万円"), ("HSS970nJ", "70cm・51万円")]):
    y = 640 + i * 260
    center(d, y, a, 100, NAVY)
    center(d, y + 110, b2, 60, GRAY)
center(d, 1260, "※通販店1店の掲載表示", 40, GRAY)
k.save(img_dir / "R1.png")

k = snow_bg(); d = ImageDraw.Draw(k)
center(d, 260, "70cmで今いちばん安い", 70, NAVY)
box(d, 380, 900, NAVY)
center(d, 490, "ホンダ", 60, WHITE)
center(d, 640, "HSS970nJ", 120, WHITE)
mixed(d, 800, [("51万円", ORANGE)], 100)
center(d, 1060, "札幌まで総額 約57万円", 64, NAVY)
center(d, 1160, "（営業所止めの例・概算）", 44, GRAY)
k.save(img_dir / "R2.png")

k = snow_bg(); d = ImageDraw.Draw(k)
center(d, 260, "ほかの機種は", 72, NAVY)
box(d, 380, 1180)
for i, (a, b2) in enumerate([("SXC1070H", "ラスト2台の表示"), ("ヤマハ系（YSF）", "納期は問い合わせ"), ("YT1070・SXC1380H", "売り切れ")]):
    y = 490 + i * 240
    center(d, y, a, 76, NAVY)
    center(d, y + 95, b2, 56, ORANGE if i == 2 else GRAY)
k.save(img_dir / "R3.png")

k = snow_bg(); d = ImageDraw.Draw(k)
center(d, 360, "注文の前に", 64, NAVY)
mixed(d, 490, [("届く日", ORANGE), ("を店に確認", NAVY)], 80)
d.rounded_rectangle([90, 640, W - 90, 1000], radius=28, fill=NAVY)
center(d, 740, "あなたの家の雪", 56, WHITE)
mixed(d, 860, [("今", WHITE), ("何cm", ORANGE), ("？", WHITE)], 84)
center(d, 1160, "70cmの比較は関連動画から", 54, NAVY)
k.save(img_dir / "R4.png")
print("cards: R0〜R4")

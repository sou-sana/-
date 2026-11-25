# 入荷したホンダが数日で売り切れショート（11/25）用の縦カード T0〜T4。在庫は Issue #70・#73 と販売ページ（11/25確認）。
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




ph = Image.open(img_dir / "Q16_v.png").convert("RGB").resize((W, H), Image.LANCZOS)
k0 = shade(ph, 760, 230, 60); d = ImageDraw.Draw(k0)
center(d, 250, "入荷したホンダの除雪機", 80, WHITE)
mixed(d, 410, [("もう", WHITE), ("売り切れ", ORANGE)], 116)
k0.convert("RGB").save(img_dir / "T0.png")

def one(date, after, model, sub, out):
    k = snow_bg(); d = ImageDraw.Draw(k)
    center(d, 260, date, 80, NAVY)
    box(d, 380, 860, NAVY)
    center(d, 480, "ホンダ", 60, WHITE)
    center(d, 630, model, 110, WHITE)
    center(d, 780, sub, 60, WHITE)
    mixed(d, 1040, [(after, NAVY), ("売り切れ", ORANGE)], 96)
    center(d, 1220, "※通販店1店の掲載表示（11月19日に入荷）", 40, GRAY)
    k.save(img_dir / out)
one("11月22日", "入荷から3日で", "HSS760nJ", "60cm・41万円", "T1.png")
one("11月24日", "入荷から5日で", "HSS970nJ", "70cm・51万円", "T2.png")

k = snow_bg(); d = ImageDraw.Draw(k)
center(d, 260, "これで70cmでいちばん安いのは", 58, NAVY)
box(d, 380, 900)
center(d, 490, "和同", 60, GRAY)
center(d, 640, "SXC1070H", 120, NAVY)
mixed(d, 800, [("58万円", ORANGE)], 100)
center(d, 1040, "商品名に「ラスト2台」", 64, NAVY)
center(d, 1150, "（11月25日時点）", 46, GRAY)
k.save(img_dir / "T3.png")

k = snow_bg(); d = ImageDraw.Draw(k)
center(d, 360, "雪が積もると在庫は早く動く", 60, NAVY)
mixed(d, 490, [("欲しい機種は", NAVY), ("早めに確認", ORANGE)], 72)
d.rounded_rectangle([90, 640, W - 90, 1000], radius=28, fill=NAVY)
center(d, 740, "あなたはもう", 56, WHITE)
mixed(d, 860, [("決めました", ORANGE), ("か？", WHITE)], 84)
center(d, 1160, "SXC1070Hの解説は関連動画から", 52, NAVY)
k.save(img_dir / "T4.png")
print("cards: T0〜T4")

# 今週売り切れた除雪機ショート（11/13〜15）用の縦カード X0〜X5。在庫は josetsuki_monitor（Issue #48・#50）と販売ページ（11/15）。
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




ph = Image.open(img_dir / "Q15_v.png").convert("RGB").resize((W, H), Image.LANCZOS)
k0 = shade(ph, 760, 230, 60); d = ImageDraw.Draw(k0)
center(d, 250, "今週", 96, WHITE)
mixed(d, 410, [("売り切れ", ORANGE), ("た除雪機", WHITE)], 110)
k0.convert("RGB").save(img_dir / "X0.png")

def one(name, date, maker, model, sub, out):
    k = snow_bg(); d = ImageDraw.Draw(k)
    center(d, 260, date, 80, NAVY)
    box(d, 380, 860, NAVY)
    center(d, 480, maker, 60, WHITE)
    center(d, 630, model, 110 if len(model) < 10 else 96, WHITE)
    center(d, 780, sub, 60, WHITE)
    mixed(d, 1040, [("売り切れ", ORANGE)], 110)
    center(d, 1220, "※通販店1店の掲載表示", 40, GRAY)
    k.save(img_dir / out)
one("", "11月13日", "ヤマハ", "YT1070", "70cm・48万円", "X1.png")
one("", "11月14日", "ホンダ（クロスオーガ）", "HSS1370iJX", "74万円", "X2.png")
one("", "11月15日", "和同", "SXC1380H", "80cm・79.8万円", "X3.png")

k = snow_bg(); d = ImageDraw.Draw(k)
center(d, 260, "こちらも", 72, NAVY)
mixed(d, 390, [("「残り僅か」", ORANGE), ("の表示", NAVY)], 80)
box(d, 510, 1100)
for i, (a, b) in enumerate([("SXC1070H", "70cm・電動旋回・58万円"), ("YSF1070T", "70cm・静音・68万円")]):
    y = 630 + i * 240
    center(d, y, a, 88, NAVY)
    center(d, y + 100, b, 52, GRAY)
center(d, 1180, "（11月15日時点）", 46, GRAY)
k.save(img_dir / "X4.png")

k = snow_bg(); d = ImageDraw.Draw(k)
center(d, 360, "欲しい機種があるなら", 64, NAVY)
mixed(d, 490, [("在庫", ORANGE), ("と", NAVY), ("届く時期", ORANGE), ("を早めに", NAVY)], 76)
d.rounded_rectangle([90, 640, W - 90, 1000], radius=28, fill=NAVY)
center(d, 740, "あなたはもう", 56, WHITE)
mixed(d, 860, [("決めました", ORANGE), ("か？", WHITE)], 84)
center(d, 1160, "70cmの比較は関連動画から", 54, NAVY)
k.save(img_dir / "X5.png")
print("cards: X0〜X5")

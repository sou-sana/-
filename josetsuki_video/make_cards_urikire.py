# ショート11本目(10月なのに、もう売り切れた除雪機)用の縦画面カード(1080x1920)を images/ に描く。
# Z0 = 写真+冒頭の大見出し、Z1〜Z4 = 説明カード。字幕帯(y≈1400〜1680)には文字を置かない。
# 在庫は除雪機ネットの掲載表示(josetsuki_monitor の記録、10/20時点)。
# usage: python3 prep_images.py && python3 make_cards_urikire.py
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


# Z0: 冒頭。歩道で作業する赤い機体(Q16_v)
ph = Image.open(img_dir / "Q16_v.png").convert("RGB").resize((W, H), Image.LANCZOS)
k0 = shade(ph, 760, 230, 60)
d = ImageDraw.Draw(k0)
center(d, 250, "10月なのに", 104, WHITE)
mixed(d, 410, [("もう", WHITE), ("売り切れ", ORANGE), ("た除雪機", WHITE)], 96)
k0.convert("RGB").save(img_dir / "Z0.png")

# Z1: 1枚目は冒頭と同じ写真を暗くした背景
k = shade(ph, H, 205, 170).convert("RGB")
d = ImageDraw.Draw(k)
center(d, 230, "10月5日の時点で", 64, WHITE)
mixed(d, 340, [("今シーズン", WHITE), ("完売", ORANGE)], 92)
box(d, 450, 1180)
for i, (a, b) in enumerate([("ホンダ HSM1390i", "90cm・ハイブリッド"),
                            ("ホンダ HSS960iJ", "小型ハイブリッド"),
                            ("ヤマハ YT1380・1380X", "80cm・サイドクラッチ")]):
    y = 560 + i * 220
    center(d, y, a, 66, NAVY)
    center(d, y + 85, b, 46, GRAY)
center(d, 1300, "※通販店1店の掲載表示（10月20日に確認）", 32, WHITE)
k.save(img_dir / "Z1.png")

# Z2: 10/17 静音タイプも
k = snow_bg(); d = ImageDraw.Draw(k)
center(d, 260, "10月17日", 80, NAVY)
box(d, 380, 760, NAVY)
center(d, 480, "静音タイプ", 60, WHITE)
center(d, 640, "Wado SXC1070SE", 84, WHITE)
mixed(d, 900, [("も", NAVY), ("売り切れ", ORANGE)], 110)
k.save(img_dir / "Z2.png")

# Z3: 残っているのは
k = snow_bg(); d = ImageDraw.Draw(k)
center(d, 260, "残っているのは", 72, NAVY)
mixed(d, 400, [("60cm・70cm", ORANGE), ("が中心", NAVY)], 88)
box(d, 520, 1180)
center(d, 610, "それでも「ラスト2台」の表示", 50, GRAY)
center(d, 760, "YSF1070T", 80, NAVY)
center(d, 900, "SXC1070H", 80, NAVY)
center(d, 1060, "（10月20日時点）", 46, GRAY)
k.save(img_dir / "Z3.png")

# Z4: 締め
k = snow_bg(); d = ImageDraw.Draw(k)
center(d, 400, "雪が降る前に", 72, NAVY)
mixed(d, 540, [("在庫", ORANGE), ("と", NAVY), ("届く時期", ORANGE), ("を確認", NAVY)], 80)
d.rounded_rectangle([90, 700, W - 90, 980], radius=28, fill=NAVY)
center(d, 790, "70cmクラスの比較は", 56, WHITE)
mixed(d, 890, [("関連動画", ORANGE), ("から", WHITE)], 80)
center(d, 1160, "北海道の除雪機選び", 56, NAVY)
k.save(img_dir / "Z4.png")
print("cards: Z0〜Z4")

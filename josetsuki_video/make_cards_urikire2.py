# 売り切れショート2（11/13 YT1070売り切れ）用の縦カード Y0〜Y4。在庫は josetsuki_monitor の記録（Issue #48）。
# usage: python3 make_cards_urikire2.py
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



# Y0: 冒頭（1メッセージ）
ph = Image.open(img_dir / "Q11_v.png").convert("RGB").resize((W, H), Image.LANCZOS)
k0 = shade(ph, 760, 230, 60)
d = ImageDraw.Draw(k0)
center(d, 250, "70cmで一番安い除雪機", 84, WHITE)
mixed(d, 410, [("売り切れ", ORANGE), ("ました", WHITE)], 110)
k0.convert("RGB").save(img_dir / "Y0.png")

# Y1: YT1070
k = snow_bg(); d = ImageDraw.Draw(k)
center(d, 260, "11月13日", 80, NAVY)
box(d, 380, 860, NAVY)
center(d, 480, "ヤマハ", 60, WHITE)
center(d, 620, "YT1070", 120, WHITE)
center(d, 770, "70cm・48万円", 64, WHITE)
mixed(d, 1060, [("在庫表示が", NAVY), ("0", ORANGE)], 100)
center(d, 1220, "※通販店1店の掲載表示", 40, GRAY)
k.save(img_dir / "Y1.png")

# Y2: 次に安い70cm
k = snow_bg(); d = ImageDraw.Draw(k)
center(d, 260, "これで70cmで一番安いのは", 60, NAVY)
box(d, 380, 1000)
center(d, 490, "ホンダ", 60, GRAY)
center(d, 630, "HSS970nJ", 120, NAVY)
mixed(d, 800, [("51万円", ORANGE)], 110)
center(d, 930, "予約受付中", 56, GRAY)
center(d, 1150, "（11月13日時点）", 46, GRAY)
k.save(img_dir / "Y2.png")

# Y3: 今季の売り切れ
k = snow_bg(); d = ImageDraw.Draw(k)
center(d, 260, "今シーズン", 72, NAVY)
mixed(d, 390, [("売り切れ", ORANGE), ("が続いている", NAVY)], 80)
box(d, 510, 1180)
for i, (a, b) in enumerate([("10月上旬", "ホンダ90cm・ヤマハ80cmほか"),
                            ("10月17日", "静音のWado SXC1070SE"),
                            ("11月13日", "ヤマハ YT1070")]):
    y = 610 + i * 200
    center(d, y, a, 56, ORANGE)
    center(d, y + 80, b, 58, NAVY)
k.save(img_dir / "Y3.png")

# Y4: 締め（質問）
k = snow_bg(); d = ImageDraw.Draw(k)
center(d, 360, "雪が本格的に降る前に", 64, NAVY)
mixed(d, 490, [("在庫", ORANGE), ("と", NAVY), ("届く時期", ORANGE), ("を確認", NAVY)], 80)
d.rounded_rectangle([90, 640, W - 90, 1000], radius=28, fill=NAVY)
center(d, 740, "あなたが考えているのは", 56, WHITE)
mixed(d, 860, [("何cm", ORANGE), ("の除雪機？", WHITE)], 84)
center(d, 1160, "70cmの比較は関連動画から", 54, NAVY)
k.save(img_dir / "Y4.png")
print("cards: Y0〜Y4")

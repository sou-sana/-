# ショート4本目(ヤマハ撤退・旧ヤマハモデル Willbe)用の縦画面カード(1080x1920)を images/ に描く。
# Y0 = 写真+冒頭の大見出し、Y1〜Y4 = 説明カード。字幕帯(y≈1400〜1680)には文字を置かない。
# usage: python3 prep_images.py && python3 make_cards_yamaha.py
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


# Y0: 冒頭。青い除雪機が雪を飛ばす写真(V4)に大見出し
k0 = Image.open(img_dir / "V4.png").convert("RGB").resize((W, H), Image.LANCZOS)
ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
od = ImageDraw.Draw(ov)
for y in range(760):
    od.line([(0, y), (W, y)], fill=NAVY + (int(215 * (1 - y / 760)),))
k0 = Image.alpha_composite(k0.convert("RGBA"), ov)
d = ImageDraw.Draw(k0)
mixed(d, 330, [("ヤマハ", ORANGE), ("の除雪機", WHITE)], 104)
center(d, 490, "もう買えない？", 112, WHITE)
k0.convert("RGB").save(img_dir / "Y0.png")

# Y1: 事業終了
k = snow_bg()
d = ImageDraw.Draw(k)
center(d, 240, "ヤマハの除雪機事業", 80, NAVY)
box(d, 340, 640, NAVY)
center(d, 440, "2026年3月末で", 72, WHITE)
center(d, 550, "終了", 110, ORANGE)
center(d, 720, "↓ 事業譲渡", 60, GRAY)
box(d, 800, 1100)
center(d, 890, "引き継いだのは", 52, GRAY)
center(d, 1000, "株式会社 Willbe", 84, NAVY)
center(d, 1200, "※ヤマハ発動機 公式サイトより", 38, GRAY)
k.save(img_dir / "Y1.png")

# Y2: 今のブランドと機種名
k = snow_bg()
d = ImageDraw.Draw(k)
center(d, 230, "今のブランドは", 76, NAVY)
center(d, 360, "Earth POWER", 116, ORANGE)
box(d, 470, 1150)
center(d, 550, "機種名は同じ系統", 56, GRAY)
for i, (cls, models) in enumerate([("6馬力帯", "YT660"), ("8馬力帯", "YSF860"),
                                   ("10馬力帯", "YSF1070T など"), ("13馬力帯", "YT1390X など")]):
    y = 680 + i * 120
    d.text((130, y), cls, font=font(48), fill=GRAY, anchor="lm")
    d.text((W - 130, y), models, font=font(62), fill=NAVY, anchor="rm")
center(d, 1240, "※区分名は最大出力の数値ではありません", 36, GRAY)
k.save(img_dir / "Y2.png")

# Y3: 使用中のヤマハ機の修理
k = snow_bg()
d = ImageDraw.Draw(k)
center(d, 230, "使っているヤマハ機の", 72, NAVY)
center(d, 340, "修理・部品は？", 96, ORANGE)
box(d, 450, 690)
center(d, 530, "①", 48, GRAY)
center(d, 620, "買った販売店", 76, NAVY)
box(d, 720, 960)
center(d, 800, "②", 48, GRAY)
center(d, 890, "サービスパートナー店", 72, NAVY)
box(d, 1000, 1220, NAVY)
center(d, 1070, "混む前に", 52, WHITE)
center(d, 1160, "雪が降る前に点検を", 64, ORANGE)
center(d, 1300, "※ヤマハ発動機 公式サイトの案内", 36, GRAY)
k.save(img_dir / "Y3.png")

# Y4: 締め
k = snow_bg()
d = ImageDraw.Draw(k)
center(d, 400, "旧ヤマハの", 84, NAVY)
mixed(d, 540, [("YT660", ORANGE), ("とホンダ", NAVY)], 96)
d.rounded_rectangle([90, 700, W - 90, 980], radius=28, fill=NAVY)
center(d, 790, "60cmクラスの比較は", 60, WHITE)
mixed(d, 890, [("関連動画", ORANGE), ("から", WHITE)], 80)
center(d, 1160, "北海道の除雪機選び", 56, NAVY)
k.save(img_dir / "Y4.png")
print("cards: Y0〜Y4")

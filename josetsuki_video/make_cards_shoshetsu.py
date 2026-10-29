# ショート14本目(札幌で初雪。除雪機、今注文していつ届く？)用の縦画面カード(1080x1920)を images/ に描く。
# N0 = 写真+冒頭の大見出し、N1〜N4 = 説明カード。字幕帯(y≈1400〜1680)には文字を置かない。
# 出典：除雪機ネットへの問い合わせ（10/23回答）、在庫監視の記録（10/27時点）
# usage: python3 prep_images.py && python3 make_cards_shoshetsu.py
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


# N0: 冒頭。雪の少ない住宅街と覆いをかけた機体(Q15_v)
ph = Image.open(img_dir / "Q15_v.png").convert("RGB").resize((W, H), Image.LANCZOS)
k0 = shade(ph, 760, 230, 60)
d = ImageDraw.Draw(k0)
center(d, 250, "札幌で初雪", 104, WHITE)
mixed(d, 410, [("除雪機、", WHITE), ("間に合う？", ORANGE)], 100)
k0.convert("RGB").save(img_dir / "N0.png")

# N1: 予約受付中は11月頃
k = shade(ph, H, 205, 170).convert("RGB")
d = ImageDraw.Draw(k)
center(d, 250, "通販店に聞いてみた", 64, WHITE)
box(d, 360, 760, NAVY)
center(d, 450, "「予約受付中」のホンダ3機種", 52, WHITE)
mixed(d, 600, [("入荷は", WHITE), ("11月頃", ORANGE), ("の予定", WHITE)], 84)
box(d, 810, 1180)
center(d, 900, "HSS760nJ・HSS970nJ", 60, NAVY)
center(d, 1010, "HSS960iJX", 60, NAVY)
center(d, 1110, "（10月23日の回答）", 44, GRAY)
k.save(img_dir / "N1.png")

# N2: もう完売
k = snow_bg(); d = ImageDraw.Draw(k)
mixed(d, 260, [("もう", NAVY), ("今シーズン完売", ORANGE)], 84)
box(d, 380, 1180)
for n, (a, b) in enumerate([("ホンダ HSM1390i", "90cm・ハイブリッド"), ("ホンダ HSS960iJ", "小型ハイブリッド"),
                            ("ヤマハ YT1380", "80cm・サイドクラッチ"), ("Wado SXC1070SE", "静音タイプ（10/17）")]):
    y = 470 + n * 180
    center(d, y, a, 60, NAVY)
    center(d, y + 70, b, 42, GRAY)
center(d, 1300, "※通販店1店の掲載表示（10月27日時点）", 32, GRAY)
k.save(img_dir / "N2.png")

# N3: ラスト2台
k = snow_bg(); d = ImageDraw.Draw(k)
center(d, 260, "70cmクラスは", 72, NAVY)
mixed(d, 400, [("「ラスト2台」", ORANGE), ("の表示", NAVY)], 84)
box(d, 520, 1060)
center(d, 650, "YSF1070T", 84, NAVY)
center(d, 800, "SXC1070H", 84, NAVY)
center(d, 950, "（10月27日時点）", 46, GRAY)
k.save(img_dir / "N3.png")

# N4: 締め
k = snow_bg(); d = ImageDraw.Draw(k)
center(d, 400, "注文の前に", 72, NAVY)
mixed(d, 540, [("届く時期", ORANGE), ("を店に確認", NAVY)], 84)
d.rounded_rectangle([90, 700, W - 90, 980], radius=28, fill=NAVY)
center(d, 790, "今買える機種と価格は", 56, WHITE)
mixed(d, 890, [("固定コメント", ORANGE), ("から", WHITE)], 80)
center(d, 1160, "北海道の除雪機選び", 56, NAVY)
k.save(img_dir / "N4.png")
print("cards: N0〜N4")

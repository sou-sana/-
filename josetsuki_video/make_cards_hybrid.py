# ショート3本目(ハイブリッド HSS960iJX vs HSS1370iJ)用の縦画面カード(1080x1920)を images/ に描く。
# H0 = 写真+冒頭の大見出し、H1〜H4 = 比較カード。字幕帯(y≈1400〜1680)には文字を置かない。
# usage: python3 prep_images.py && python3 make_cards_hybrid.py
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


# H0: 冒頭。深い雪を切り崩す除雪機(F1)に大見出し
k0 = Image.open(img_dir / "F1_v.png").convert("RGB").resize((W, H), Image.LANCZOS)
ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
od = ImageDraw.Draw(ov)
for y in range(760):
    od.line([(0, y), (W, y)], fill=NAVY + (int(210 * (1 - y / 760)),))
k0 = Image.alpha_composite(k0.convert("RGBA"), ov)
d = ImageDraw.Draw(k0)
mixed(d, 340, [("6.8万円", ORANGE), ("高いのに", WHITE)], 100)
center(d, 500, "パワーも幅も下？", 100, WHITE)
k0.convert("RGB").save(img_dir / "H0.png")


def two_col_named(d, top, left_name, right_name, rows):
    """two_col の見出し違い版。"""
    left, mid, right = 60, W // 2, W - 60
    d.rounded_rectangle([left, top, right, top + 150], radius=24, fill=NAVY)
    d.text(((left + mid) // 2, top + 75), left_name, font=font(58), fill=WHITE, anchor="mm")
    d.text(((mid + right) // 2, top + 75), right_name, font=font(58), fill=WHITE, anchor="mm")
    y = top + 166
    for label, a, b, hl in rows:
        d.rounded_rectangle([left, y, right, y + 190], radius=20, fill=WHITE, outline=(0xC9, 0xD8, 0xE6), width=3)
        d.text((W // 2, y + 36), label, font=font(36), fill=(0x55, 0x6B, 0x80), anchor="mm")
        d.text(((left + mid) // 2, y + 118), a, font=font(76), fill=NAVY, anchor="mm")
        d.text(((mid + right) // 2, y + 118), b, font=font(76), fill=ORANGE if hl else NAVY, anchor="mm")
        y += 206
    return y


# H1: 価格・出力・除雪幅
k = snow_bg()
d = ImageDraw.Draw(k)
center(d, 230, "ホンダ ハイブリッド2台", 80, NAVY)
y = two_col_named(d, 330, "HSS960iJX", "HSS1370iJ",
                  [("販売価格", "69.8万円", "63万円", True), ("最大出力", "8.6PS", "11.8PS", True), ("除雪幅", "62cm", "72cm", True)])
center(d, y + 50, "※仕様: Honda公式 / 価格: 10/5時点", 38, (0x55, 0x6B, 0x80))
k.save(img_dir / "H1.png")

# H2: 高い理由はクロスオーガ
k = snow_bg()
d = ImageDraw.Draw(k)
center(d, 260, "高い理由は", 92, NAVY)
center(d, 400, "クロスオーガ", 130, ORANGE)
d.rounded_rectangle([60, 520, W - 60, 900], radius=28, fill=NAVY)
center(d, 610, "HSS960iJX の「JX」は", 54, WHITE)
center(d, 700, "クロスオーガ搭載タイプ", 62, WHITE)
center(d, 810, "硬い雪への食い込みを助ける機構(Honda)", 40, WHITE)
d.rounded_rectangle([60, 940, W - 60, 1170], radius=24, fill=WHITE, outline=(0xC9, 0xD8, 0xE6), width=3)
center(d, 1010, "参考: 標準タイプ HSS960iJ", 44, (0x55, 0x6B, 0x80))
center(d, 1100, "58万円 → 完売", 60, NAVY)
k.save(img_dir / "H2.png")

# H3: どっちを選ぶ
k = snow_bg()
d = ImageDraw.Draw(k)
center(d, 250, "どっちを選ぶ？", 100, NAVY)
for i, (cond, model) in enumerate([("出力・除雪幅・価格", "HSS1370iJ"), ("硬い雪・クロスオーガ", "HSS960iJX"), ("狭い通路・新品で買う", "HSS960iJX")]):
    top = 400 + i * 300
    d.rounded_rectangle([60, top, W - 60, top + 260], radius=24, fill=WHITE, outline=NAVY, width=4)
    d.rounded_rectangle([60, top, W - 60, top + 100], radius=24, fill=NAVY)
    d.rectangle([60, top + 70, W - 60, top + 100], fill=NAVY)
    d.text((W // 2, top + 52), cond, font=font(52), fill=WHITE, anchor="mm")
    d.text((W // 2, top + 182), "→ " + model, font=font(84), fill=ORANGE, anchor="mm")
center(d, 1330, "※HSS1370iJは展示機1台のみ(10/5時点)", 38, (0x55, 0x6B, 0x80))
k.save(img_dir / "H3.png")

# H4: 締め
k = snow_bg()
d = ImageDraw.Draw(k)
center(d, 420, "70cmクラスの", 84, NAVY)
mixed(d, 560, [("ほかの機種", ORANGE), ("も比較中", NAVY)], 96)
d.rounded_rectangle([90, 720, W - 90, 1000], radius=28, fill=NAVY)
center(d, 810, "3機種の比較は", 64, WHITE)
mixed(d, 910, [("関連動画", ORANGE), ("から", WHITE)], 80)
center(d, 1180, "北海道の除雪機選び", 56, NAVY)
k.save(img_dir / "H4.png")
print("cards: H0〜H4")

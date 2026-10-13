# ショート5本目(買ってはいけない除雪機3つ)用の縦画面カード(1080x1920)を images/ に描く。
# B0 = 写真+冒頭の大見出し、B1〜B4 = 説明カード。字幕帯(y≈1400〜1680)には文字を置かない。
# usage: python3 prep_images.py && python3 make_cards_ng.py
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


# B0: 冒頭。押し固められた雪の山(F2_v)に大見出し
k0 = Image.open(img_dir / "F2_v.png").convert("RGB").resize((W, H), Image.LANCZOS)
ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
od = ImageDraw.Draw(ov)
for y in range(780):
    od.line([(0, y), (W, y)], fill=NAVY + (int(220 * (1 - y / 780)),))
k0 = Image.alpha_composite(k0.convert("RGBA"), ov)
d = ImageDraw.Draw(k0)
center(d, 320, "買ってはいけない", 108, WHITE)
mixed(d, 480, [("除雪機", WHITE), ("3つ", ORANGE)], 120)
k0.convert("RGB").save(img_dir / "B0.png")


def head(d, no, title):
    d.rounded_rectangle([60, 170, 200, 310], radius=24, fill=ORANGE)
    d.text((130, 240), no, font=font(90), fill=WHITE, anchor="mm")
    d.text((240, 240), title, font=font(70), fill=NAVY, anchor="lm")


# B1: 馬力の呼び名だけで選ぶ(Willbe公式の区分と公式の最大出力だけで比べる)
k = snow_bg()
d = ImageDraw.Draw(k)
head(d, "1", "馬力の呼び名で選ぶ")
d.rounded_rectangle([60, 380, W - 60, 480], radius=24, fill=NAVY)
d.text((290, 430), "公式の区分", font=font(48), fill=WHITE, anchor="mm")
d.text((800, 430), "公式の最大出力", font=font(48), fill=WHITE, anchor="mm")
for i, (model, cls, real, hl) in enumerate([("YT660", "6馬力帯", "4.8PS", False),
                                             ("YSF860", "8馬力帯", "9.3PS", True),
                                             ("YSF1070T", "10馬力帯", "9.4PS", True)]):
    top = 500 + i * 230
    box(d, top, top + 210)
    d.text((290, top + 65), model, font=font(46), fill=GRAY, anchor="mm")
    d.text((290, top + 145), cls, font=font(72), fill=NAVY, anchor="mm")
    d.text((800, top + 105), real, font=font(96), fill=ORANGE if hl else NAVY, anchor="mm")
center(d, 1240, "8馬力帯と10馬力帯がほぼ同じ", 52, NAVY)
center(d, 1320, "※区分・出力ともWillbe公式(YSF1070Tはヤマハ公式)", 34, GRAY)
k.save(img_dir / "B1.png")

# B2: 除雪高が足りない(棒グラフ)
k = snow_bg()
d = ImageDraw.Draw(k)
head(d, "2", "除雪高が足りない")
bars = [("通販の電動\n(多くは)", 30, GRAY, "30cm以下"), ("HSS760nJ", 42, NAVY, "42cm"),
        ("YT660", 44, NAVY, "44cm"), ("YSF1070T", 51, ORANGE, "51cm")]
base, scale, bw = 1180, 13, 170
for i, (name, v, col, lab) in enumerate(bars):
    x = 120 + i * 230
    d.rectangle([x, base - v * scale, x + bw, base], fill=col)
    d.text((x + bw // 2, base - v * scale - 45), lab, font=font(46), fill=col, anchor="mm")
    d.multiline_text((x + bw // 2, base + 60), name, font=font(34), fill=NAVY, anchor="mm", align="center")
d.line([(90, base), (W - 90, base)], fill=NAVY, width=4)
center(d, 1330, "※エンジン機は公式の除雪高(Willbe機は新雪時)。電動は比較サイト掲載値", 32, GRAY)
k.save(img_dir / "B2.png")

# B3: 近くに修理できる店がない
k = snow_bg()
d = ImageDraw.Draw(k)
head(d, "3", "修理先が遠い")
box(d, 400, 720, NAVY)
center(d, 490, "困るのは", 60, WHITE)
center(d, 620, "大雪の日に故障", 96, ORANGE)
box(d, 770, 1150)
center(d, 850, "買う前に確認", 56, GRAY)
center(d, 950, "近くのサービス店", 80, NAVY)
center(d, 1060, "点検・修理を受けてくれるか", 48, NAVY)
center(d, 1260, "※ヤマハ公式も修理は販売店・サービス店へと案内", 34, GRAY)
k.save(img_dir / "B3.png")

# B4: 締め
k = snow_bg()
d = ImageDraw.Draw(k)
center(d, 400, "今買える60cmクラス", 76, NAVY)
mixed(d, 540, [("YT660", ORANGE), ("とHSS760nJ", NAVY)], 88)
d.rounded_rectangle([90, 700, W - 90, 980], radius=28, fill=NAVY)
center(d, 790, "2台の比較は", 64, WHITE)
mixed(d, 890, [("関連動画", ORANGE), ("から", WHITE)], 80)
center(d, 1160, "北海道の除雪機選び", 56, NAVY)
k.save(img_dir / "B4.png")
print("cards: B0〜B4")

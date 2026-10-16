# ショート8本目(札幌の除雪機補助金は個人も使える？)用の縦画面カード(1080x1920)を images/ に描く。
# H0 = 写真+冒頭の大見出し、H1〜H4 = 説明カード。字幕帯(y≈1400〜1680)には文字を置かない。
# usage: python3 prep_images.py && python3 make_cards_hojokin.py
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


# H0: 冒頭。大雪の住宅地(Q2_v)に大見出し
k0 = Image.open(img_dir / "Q2_v.png").convert("RGB").resize((W, H), Image.LANCZOS)
ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
od = ImageDraw.Draw(ov)
for y in range(780):
    od.line([(0, y), (W, y)], fill=NAVY + (int(225 * (1 - y / 780)),))
k0 = Image.alpha_composite(k0.convert("RGBA"), ov)
d = ImageDraw.Draw(k0)
center(d, 300, "札幌の除雪機補助金", 88, WHITE)
mixed(d, 470, [("個人", ORANGE), ("も使える？", WHITE)], 104)
k0.convert("RGB").save(img_dir / "H0.png")

NOTE = "※札幌市公式「小型除雪機購入費の補助」(2026年10月確認)"


def card(title, top1, big, sub1, mid, sub2, note=NOTE):
    k = snow_bg()
    d = ImageDraw.Draw(k)
    d.text((W // 2, 240), title, font=font(70), fill=NAVY, anchor="mm")
    box(d, 400, 740, NAVY)
    center(d, 490, top1, 56, WHITE)
    center(d, 630, big, 92, ORANGE)
    box(d, 790, 1180)
    center(d, 860, sub1, 50, GRAY)
    center(d, 970, mid, 72, NAVY)
    center(d, 1075, sub2, 50, NAVY)
    center(d, 1300, note, 32, GRAY)
    return k


card("答え", "個人と企業は", "対象外", "対象は", "町内会", "と除雪ボランティアの団体").save(img_dir / "H1.png")
card("対象の機械", "安全装置付きの", "新品だけ", "販売業者から買う", "歩いて押す", "ハンドガイド型の小型除雪機").save(img_dir / "H2.png")
card("申し込み", "買う", "2週間以上前", "2026年度は9月中旬から受付予定", "予算で締め切り", "多いと抽選の場合も").save(img_dir / "H3.png")

# H4: 締め
k = snow_bg()
d = ImageDraw.Draw(k)
center(d, 400, "個人で買うなら", 76, NAVY)
mixed(d, 540, [("補助なし", ORANGE), ("で予算を", NAVY)], 88)
d.rounded_rectangle([90, 700, W - 90, 980], radius=28, fill=NAVY)
center(d, 790, "60cmクラスの比較は", 60, WHITE)
mixed(d, 890, [("関連動画", ORANGE), ("から", WHITE)], 80)
center(d, 1160, "北海道の除雪機選び", 56, NAVY)
k.save(img_dir / "H4.png")
print("cards: H0〜H4")

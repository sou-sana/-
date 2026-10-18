# ショート9本目(北海道まで送料いくら？聞いてみた)用の縦画面カード(1080x1920)を images/ に描く。
# P0 = 写真+冒頭の大見出し、P1〜P4 = 説明カード。字幕帯(y≈1400〜1680)には文字を置かない。
# usage: python3 prep_images.py && python3 make_cards_souryou.py
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


# 写真(Q3_h)を中央の帯に、上下はぼかした拡大で埋めた背景。P0とP1で同じ背景を使い、切り替えを目立たせない
ph = Image.open(img_dir / "Q3_h.png").convert("RGB")
bg = ph.resize((int(ph.width * H / ph.height), H), Image.LANCZOS)
x0 = (bg.width - W) // 2 - 250
bg = bg.crop((x0, 0, x0 + W, H)).filter(ImageFilter.GaussianBlur(22))
bg = Image.blend(bg, Image.new("RGB", (W, H), NAVY), 0.45)
fg = ph.resize((W, int(ph.height * W / ph.width)), Image.LANCZOS)
base = bg.copy()
base.paste(fg, (0, 760))


def top_shade(img, h=760, a0=235, a1=175):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    for y in range(h):
        od.line([(0, y), (W, y)], fill=NAVY + (int(a0 - (a0 - a1) * y / h),))
    return Image.alpha_composite(img.convert("RGBA"), ov)


k0 = top_shade(base)
d = ImageDraw.Draw(k0)
center(d, 250, "北海道まで", 84, WHITE)
center(d, 400, "除雪機の送料", 116, WHITE)
mixed(d, 560, [("いくら？", ORANGE), ("聞いてみた", WHITE)], 92)
k0.convert("RGB").save(img_dir / "P0.png")

NOTE = "※2026年10月16日、通販店(除雪機ネット)に問い合わせた概算"

# P1: 答え(同じ写真背景の上に箱)
k = top_shade(base, 1920, 200, 140).convert("RGB")
d = ImageDraw.Draw(k)
d.text((W // 2, 240), "札幌市まで（60cmクラス）", font=font(60), fill=WHITE, anchor="mm")
box(d, 400, 740)
center(d, 490, "営業所止め", 60, GRAY)
center(d, 630, "約6万円", 120, ORANGE)
box(d, 790, 1130)
center(d, 880, "自宅までのチャーター便", 56, GRAY)
center(d, 1010, "約8〜10万円", 100, NAVY)
center(d, 1300, NOTE, 32, WHITE)
k.save(img_dir / "P1.png")


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


card("総額にすると", "YT660 本体39.9万円", "約46万円", "営業所止めの送料を足すと", "本体の約15%", "が送料になる").save(img_dir / "P2.png")
card("だから", "近くの店の届け込み価格と", "総額で比べる", "通販が向くのは", "売り切れた機種や", "近くで扱いのない機種を探すとき",
     note="※送料は時期・地域・機種で変わる。注文前に必ず見積もりを").save(img_dir / "P3.png")

# P4: 締め
k = snow_bg()
d = ImageDraw.Draw(k)
center(d, 400, "本体価格だけで", 76, NAVY)
mixed(d, 540, [("決めない", ORANGE)], 96)
d.rounded_rectangle([90, 700, W - 90, 980], radius=28, fill=NAVY)
center(d, 790, "60cmクラスの比較は", 60, WHITE)
mixed(d, 890, [("関連動画", ORANGE), ("から", WHITE)], 80)
center(d, 1160, "北海道の除雪機選び", 56, NAVY)
k.save(img_dir / "P4.png")
print("cards: P0〜P4")

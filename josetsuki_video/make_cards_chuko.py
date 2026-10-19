# ショート10本目(中古の除雪機を買う前に売り手に聞く4つ)用の縦画面カード(1080x1920)を images/ に描く。
# U0 = 写真+冒頭の大見出し、U1〜U5 = 説明カード。字幕帯(y≈1400〜1680)には文字を置かない。
# usage: python3 prep_images.py && python3 make_cards_chuko.py
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


# U0: 冒頭。中古の赤い機体を点検する人(Q11_v)
ph = Image.open(img_dir / "Q11_v.png").convert("RGB").resize((W, H), Image.LANCZOS)


def shade(img, h, a0, a1):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    for y in range(h):
        od.line([(0, y), (W, y)], fill=NAVY + (int(a0 - (a0 - a1) * y / h),))
    return Image.alpha_composite(img.convert("RGBA"), ov)


k0 = shade(ph, 760, 230, 60)
d = ImageDraw.Draw(k0)
center(d, 250, "中古の除雪機", 104, WHITE)
mixed(d, 410, [("買う前に", WHITE), ("聞く4つ", ORANGE)], 104)
k0.convert("RGB").save(img_dir / "U0.png")


def head(d, no, title, color=NAVY):
    d.rounded_rectangle([60, 170, 200, 310], radius=24, fill=ORANGE)
    d.text((130, 240), no, font=font(90), fill=WHITE, anchor="mm")
    d.text((240, 240), title, font=font(70), fill=color, anchor="lm")


def qbody(d, q, a1, a2, a3):
    box(d, 400, 740, NAVY)
    center(d, 490, "売り手に聞く", 56, WHITE)
    center(d, 630, q, 80, ORANGE)
    box(d, 790, 1180)
    center(d, 860, a1, 50, GRAY)
    center(d, 970, a2, 72, NAVY)
    center(d, 1075, a3, 50, NAVY)


# U1: 1枚目は冒頭と同じ写真を暗くした背景(切り替えを目立たせない)
k = shade(ph, H, 205, 170).convert("RGB")
d = ImageDraw.Draw(k)
head(d, "1", "使った年数", WHITE)
qbody(d, "何年使った？", "年式と使った時間", "使い方を聞く", "保管は屋内か屋外か")
k.save(img_dir / "U1.png")

k = snow_bg(); d = ImageDraw.Draw(k)
head(d, "2", "整備の記録")
qbody(d, "点検・修理の記録は？", "オイル交換や部品交換", "いつ・どこで", "直したかを聞く")
k.save(img_dir / "U2.png")

k = snow_bg(); d = ImageDraw.Draw(k)
head(d, "3", "動かして確認")
qbody(d, "目の前で動かせる？", "エンジン・オーガ・走行", "非常停止も", "効くか見せてもらう")
center(d, 1300, "※確認は売り手に操作してもらい、回転部に近づかない", 32, GRAY)
k.save(img_dir / "U3.png")

k = snow_bg(); d = ImageDraw.Draw(k)
head(d, "4", "壊れたとき")
qbody(d, "保証と修理先は？", "中古は保証なしも多い", "近くで直せるか", "買う前に確かめる")
k.save(img_dir / "U4.png")

# U5: 締め
k = snow_bg(); d = ImageDraw.Draw(k)
center(d, 400, "答えがあいまいなら", 72, NAVY)
mixed(d, 540, [("新品", ORANGE), ("とも比べる", NAVY)], 92)
d.rounded_rectangle([90, 700, W - 90, 980], radius=28, fill=NAVY)
center(d, 790, "60cmクラスの新品比較は", 56, WHITE)
mixed(d, 890, [("関連動画", ORANGE), ("から", WHITE)], 80)
center(d, 1160, "北海道の除雪機選び", 56, NAVY)
k.save(img_dir / "U5.png")
print("cards: U0〜U5")

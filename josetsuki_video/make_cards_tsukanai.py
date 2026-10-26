# ショート13本目(除雪機のオーガに雪がくっつく：メーカーの対策)用の縦画面カード(1080x1920)を images/ に描く。
# G0 = 写真+冒頭の大見出し、G1〜G4 = 説明カード。字幕帯(y≈1400〜1680)には文字を置かない。
# 出典：Willbe YT660取扱説明書p39・p35、Honda FAQ（湿った雪）、除雪機ネットの販売ページ（つかない君）
# usage: python3 prep_images.py && python3 make_cards_tsukanai.py
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


def body(d, q, a1, a2, a3, src):
    box(d, 400, 740, NAVY)
    center(d, 490, "対策", 56, WHITE)
    center(d, 630, q, 76, ORANGE)
    box(d, 790, 1180)
    center(d, 860, a1, 50, GRAY)
    center(d, 970, a2, 68, NAVY)
    center(d, 1075, a3, 50, NAVY)
    center(d, 1300, src, 32, GRAY)


# G0: 冒頭。ベタ雪で詰まった青い機体(Q14_v)
ph = Image.open(img_dir / "Q14_v.png").convert("RGB").resize((W, H), Image.LANCZOS)
k0 = shade(ph, 760, 230, 60)
d = ImageDraw.Draw(k0)
center(d, 250, "除雪機の羽に", 104, WHITE)
mixed(d, 410, [("雪が", WHITE), ("くっつく", ORANGE)], 104)
k0.convert("RGB").save(img_dir / "G0.png")

k = shade(ph, H, 205, 170).convert("RGB")
d = ImageDraw.Draw(k)
head(d, "1", "使い終わったら", WHITE)
body(d, "オーガを空回し", "除雪をやめたら", "空回しで雪を飛ばす", "付いたまま放置→凍って故障も", "")
center(d, 1300, "出典：Willbe YT660 取扱説明書", 32, WHITE)
k.save(img_dir / "G1.png")

k = snow_bg(); d = ImageDraw.Draw(k)
head(d, "2", "湿った雪は")
body(d, "遅く・少しずつ", "速度を落とし", "雪幅を狭くして", "一度に取る量を少なく", "出典：Honda公式 よくある質問")
k.save(img_dir / "G2.png")

k = snow_bg(); d = ImageDraw.Draw(k)
head(d, "3", "軸に付ける用品")
body(d, "着雪を防ぐ部品も", "オーガの軸に付けるタイプ", "1個600円から", "軸の太さでサイズを選ぶ", "※効果は販売ページの説明。当チャンネルは未検証")
k.save(img_dir / "G3.png")

k = snow_bg(); d = ImageDraw.Draw(k)
center(d, 400, "詰まった雪は", 72, NAVY)
mixed(d, 540, [("エンジンを止めて", ORANGE)], 84)
center(d, 650, "キーを抜き、雪かき棒で", 60, NAVY)
d.rounded_rectangle([90, 760, W - 90, 1040], radius=28, fill=NAVY)
center(d, 850, "サイズの早見表は", 56, WHITE)
mixed(d, 950, [("固定コメント", ORANGE), ("から", WHITE)], 80)
center(d, 1180, "北海道の除雪機選び", 56, NAVY)
k.save(img_dir / "G4.png")
print("cards: G0〜G4")

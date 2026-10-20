# ショート12本目(初雪の前に除雪機で確認する4つ)用の縦画面カード(1080x1920)を images/ に描く。
# R0 = 写真+冒頭の大見出し、R1〜R5 = 説明カード。字幕帯(y≈1400〜1680)には文字を置かない。
# 出典：Honda・ヤマハ(Willbe)公式のよくある質問(josetsuki_research/公式FAQ_*.md)
# usage: python3 prep_images.py && python3 make_cards_shiunten.py
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
    center(d, 490, "確認すること", 56, WHITE)
    center(d, 630, q, 76, ORANGE)
    box(d, 790, 1180)
    center(d, 860, a1, 50, GRAY)
    center(d, 970, a2, 68, NAVY)
    center(d, 1075, a3, 50, NAVY)
    center(d, 1300, src, 32, GRAY)


# R0: 冒頭。ガレージでオイルを点検する人(Q12_v)
ph = Image.open(img_dir / "Q12_v.png").convert("RGB").resize((W, H), Image.LANCZOS)
k0 = shade(ph, 760, 230, 60)
d = ImageDraw.Draw(k0)
center(d, 250, "初雪の前に", 104, WHITE)
mixed(d, 410, [("除雪機で", WHITE), ("確認する4つ", ORANGE)], 96)
k0.convert("RGB").save(img_dir / "R0.png")

# R1: 1枚目は冒頭と同じ写真を暗くした背景
k = shade(ph, H, 205, 170).convert("RGB")
d = ImageDraw.Draw(k)
head(d, "1", "ガソリン", WHITE)
body(d, "去年の燃料、抜いた？", "抜いていないと", "燃料の詰まり", "の原因になることも", "")
center(d, 1300, "出典：ヤマハ（Willbe）公式 よくある質問", 32, WHITE)
k.save(img_dir / "R1.png")

k = snow_bg(); d = ImageDraw.Draw(k)
head(d, "2", "バッテリー")
body(d, "セルは回る？", "長く置くと放電する", "使う前に充電", "回らなければ充電不足かも", "出典：Honda・ヤマハ公式 よくある質問")
k.save(img_dir / "R2.png")

k = snow_bg(); d = ImageDraw.Draw(k)
head(d, "3", "オイル")
body(d, "量と汚れは？", "エンジンオイルを見る", "ウォームケースは", "シーズン初めに交換を推奨", "出典：ヤマハ（Willbe）公式 よくある質問")
k.save(img_dir / "R3.png")

k = snow_bg(); d = ImageDraw.Draw(k)
head(d, "4", "予備のボルト")
body(d, "シャーボルトはある？", "石をかむと折れて", "機械を守るボルト", "予備は純正を用意", "出典：Honda公式 よくある質問")
k.save(img_dir / "R4.png")

# R5: 締め
k = snow_bg(); d = ImageDraw.Draw(k)
center(d, 400, "かからなければ", 72, NAVY)
mixed(d, 540, [("雪の前に", ORANGE), ("販売店へ", NAVY)], 92)
d.rounded_rectangle([90, 700, W - 90, 980], radius=28, fill=NAVY)
center(d, 790, "買い替えなら60cmの比較を", 52, WHITE)
mixed(d, 890, [("関連動画", ORANGE), ("から", WHITE)], 80)
center(d, 1160, "北海道の除雪機選び", 56, NAVY)
k.save(img_dir / "R5.png")
print("cards: R0〜R5")

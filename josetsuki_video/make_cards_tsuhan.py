# ショート7本目(除雪機を通販で買う前に確認する4つ)用の縦画面カード(1080x1920)を images/ に描く。
# T0 = 写真+冒頭の大見出し、T1〜T5 = 説明カード。字幕帯(y≈1400〜1680)には文字を置かない。
# usage: python3 prep_images.py && python3 make_cards_tsuhan.py
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


# T0: 冒頭。配送トラックの横写真(Q8_h)を中央に、上下はぼかした拡大で埋める
ph = Image.open(img_dir / "Q8_h.png").convert("RGB")
bg = ph.resize((int(ph.width * H / ph.height), H), Image.LANCZOS)
x0 = (bg.width - W) // 2 + 120
bg = bg.crop((x0, 0, x0 + W, H)).filter(ImageFilter.GaussianBlur(22))
bg = Image.blend(bg, Image.new("RGB", (W, H), NAVY), 0.35)
fg = ph.resize((W, int(ph.height * W / ph.width)), Image.LANCZOS)
bg.paste(fg, (0, 760))
ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
od = ImageDraw.Draw(ov)
for y in range(760):
    od.line([(0, y), (W, y)], fill=NAVY + (int(235 - 60 * y / 760),))
k0 = Image.alpha_composite(bg.convert("RGBA"), ov)
d = ImageDraw.Draw(k0)
center(d, 250, "北海道で", 80, WHITE)
center(d, 400, "除雪機を通販で", 108, WHITE)
mixed(d, 560, [("買う前に", WHITE), ("確認する4つ", ORANGE)], 90)
k0.convert("RGB").save(img_dir / "T0.png")


def head(d, no, title):
    d.rounded_rectangle([60, 170, 200, 310], radius=24, fill=ORANGE)
    d.text((130, 240), no, font=font(90), fill=WHITE, anchor="mm")
    d.text((240, 240), title, font=font(70), fill=NAVY, anchor="lm")


NOTE = "※除雪機ネットの案内(2026年10月15日時点)"

# T1: 送料
k = snow_bg()
d = ImageDraw.Draw(k)
head(d, "1", "北海道への送料")
box(d, 400, 740, NAVY)
center(d, 490, "北海道は", 60, WHITE)
center(d, 630, "中継料が別", 104, ORANGE)
box(d, 790, 1150)
center(d, 870, "注文の前に", 56, GRAY)
center(d, 970, "送料を問い合わせ", 84, NAVY)
center(d, 1075, "早めだと安くなる場合も", 50, NAVY)
center(d, 1300, NOTE, 34, GRAY)
k.save(img_dir / "T1.png")

# T2: 荷下ろし
k = snow_bg()
d = ImageDraw.Draw(k)
head(d, "2", "荷下ろし")
box(d, 400, 740, NAVY)
center(d, 490, "荷降ろしに", 60, WHITE)
center(d, 630, "フォークリフト", 104, ORANGE)
box(d, 790, 1180)
center(d, 860, "無いときは", 52, GRAY)
center(d, 960, "営業所止め", 80, NAVY)
center(d, 1060, "か チャーター便(別見積)", 56, NAVY)
center(d, 1300, NOTE, 34, GRAY)
k.save(img_dir / "T2.png")

# T3: 初期不良
k = snow_bg()
d = ImageDraw.Draw(k)
head(d, "3", "初期不良の期限")
box(d, 400, 740, NAVY)
center(d, 490, "交換・修理は", 60, WHITE)
mixed(d, 630, [("到着後", WHITE), ("7日以内", ORANGE)], 104)
box(d, 790, 1180)
center(d, 860, "返品・返金はできない", 52, GRAY)
center(d, 970, "届いたらすぐ", 80, NAVY)
center(d, 1075, "エンジンをかけて確認", 56, NAVY)
center(d, 1300, NOTE, 34, GRAY)
k.save(img_dir / "T3.png")

# T4: 修理先
k = snow_bg()
d = ImageDraw.Draw(k)
head(d, "4", "修理先")
box(d, 400, 740, NAVY)
center(d, 490, "お店は長野県", 60, WHITE)
center(d, 630, "北海道は加盟店", 96, ORANGE)
box(d, 790, 1180)
center(d, 860, "買う前に確認", 52, GRAY)
center(d, 970, "近くで点検・修理", 80, NAVY)
center(d, 1075, "を受けられるか", 56, NAVY)
center(d, 1300, "※除雪機ネットは近くのメンテナンス加盟店を紹介と案内", 32, GRAY)
k.save(img_dir / "T4.png")

# T5: 締め
k = snow_bg()
d = ImageDraw.Draw(k)
center(d, 400, "支払いは", 70, NAVY)
mixed(d, 530, [("代金引換", ORANGE), ("が使えない", NAVY)], 84)
d.rounded_rectangle([90, 700, W - 90, 980], radius=28, fill=NAVY)
center(d, 790, "今買える機種の比較は", 60, WHITE)
mixed(d, 890, [("関連動画", ORANGE), ("から", WHITE)], 80)
center(d, 1160, "北海道の除雪機選び", 56, NAVY)
k.save(img_dir / "T5.png")
print("cards: T0〜T5")

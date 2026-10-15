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
mixed(d, 560, [("買う前に", WHITE), ("聞く4つ", ORANGE)], 100)
k0.convert("RGB").save(img_dir / "T0.png")


def head(d, no, title):
    d.rounded_rectangle([60, 170, 200, 310], radius=24, fill=ORANGE)
    d.text((130, 240), no, font=font(90), fill=WHITE, anchor="mm")
    d.text((240, 240), title, font=font(70), fill=NAVY, anchor="lm")


NOTE = "※例:除雪機ネットの案内(2026年10月)。条件は店ごとに違う"


def qcard(no, title, q, ans1, ans2, ans3):
    k = snow_bg()
    d = ImageDraw.Draw(k)
    head(d, no, title)
    box(d, 400, 740, NAVY)
    center(d, 490, "店に聞く", 56, WHITE)
    center(d, 630, q, 84, ORANGE)
    box(d, 790, 1180)
    center(d, 860, ans1, 50, GRAY)
    center(d, 970, ans2, 72, NAVY)
    center(d, 1075, ans3, 50, NAVY)
    center(d, 1300, NOTE, 32, GRAY)
    return k


qcard("1", "送料", "北海道までいくら？", "北海道は別料金の店も", "総額を注文前に", "早めだと安くなる場合も").save(img_dir / "T1.png")
qcard("2", "荷下ろし", "誰がどう降ろす？", "フォークリフトが要る店も", "営業所止めなら", "家まで運ぶ手段を決める").save(img_dir / "T2.png")
qcard("3", "初期不良", "何日以内に連絡？", "例:到着後7日以内", "届いたらすぐ", "エンジンをかけて確認").save(img_dir / "T3.png")
qcard("4", "修理先", "どこで直せる？", "大雪の日の故障が一番困る", "近くで点検・修理", "を受けられるか").save(img_dir / "T4.png")

# T5: 締め
k = snow_bg()
d = ImageDraw.Draw(k)
center(d, 400, "近くの店で買うか", 70, NAVY)
mixed(d, 530, [("通販", ORANGE), ("で買うか", NAVY)], 84)
d.rounded_rectangle([90, 700, W - 90, 980], radius=28, fill=NAVY)
center(d, 790, "機種の比較は", 60, WHITE)
mixed(d, 890, [("関連動画", ORANGE), ("から", WHITE)], 80)
center(d, 1160, "北海道の除雪機選び", 56, NAVY)
k.save(img_dir / "T5.png")
print("cards: T0〜T5")

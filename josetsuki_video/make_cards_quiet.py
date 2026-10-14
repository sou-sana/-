# ショート6本目(63万円の静音2台 YSF1070T vs SXC1070SE)用の縦画面カード(1080x1920)を images/ に描く。
# S0 = 写真+冒頭の大見出し、S1〜S4 = 説明カード。字幕帯(y≈1400〜1680)には文字を置かない。
# usage: python3 prep_images.py && python3 make_cards_quiet.py
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


# S0: 冒頭。夜明け前の住宅街で青い除雪機(Q1_v)に大見出し
k0 = Image.open(img_dir / "Q1_v.png").convert("RGB").resize((W, H), Image.LANCZOS)
ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
od = ImageDraw.Draw(ov)
for y in range(780):
    od.line([(0, y), (W, y)], fill=NAVY + (int(200 * (1 - y / 780)),))
k0 = Image.alpha_composite(k0.convert("RGBA"), ov)
d = ImageDraw.Draw(k0)
mixed(d, 330, [("同じ", WHITE), ("63万円", ORANGE), ("の", WHITE)], 100)
center(d, 480, "静音除雪機、どっち？", 96, WHITE)
k0.convert("RGB").save(img_dir / "S0.png")


def two_col(d, top, left_name, right_name, rows):
    left, mid, right = 60, W // 2, W - 60
    d.rounded_rectangle([left, top, right, top + 150], radius=24, fill=NAVY)
    d.text(((left + mid) // 2, top + 75), left_name, font=font(56), fill=WHITE, anchor="mm")
    d.text(((mid + right) // 2, top + 75), right_name, font=font(56), fill=WHITE, anchor="mm")
    y = top + 166
    for label, a, b in rows:
        d.rounded_rectangle([left, y, right, y + 180], radius=20, fill=WHITE, outline=LINE, width=3)
        d.text((W // 2, y + 34), label, font=font(36), fill=GRAY, anchor="mm")
        d.text(((left + mid) // 2, y + 112), a, font=font(68), fill=NAVY, anchor="mm")
        d.text(((mid + right) // 2, y + 112), b, font=font(68), fill=NAVY, anchor="mm")
        y += 196
    return y


# S1: ほぼ同じ数字
k = snow_bg()
d = ImageDraw.Draw(k)
center(d, 230, "数字はほぼ同じ", 88, NAVY)
y = two_col(d, 320, "YSF1070T", "SXC1070SE",
            [("販売価格", "63万円", "63万円"), ("除雪幅", "71.5cm", "71cm"), ("除雪高", "51cm", "51.8cm")])
center(d, y + 40, "※仕様: ヤマハ・Wado公式(除雪高はヤマハは新雪時)", 34, GRAY)
center(d, y + 90, "※価格: 除雪機ネット 10/14時点", 34, GRAY)
k.save(img_dir / "S1.png")

# S2: 違い1 静音の作り
k = snow_bg()
d = ImageDraw.Draw(k)
center(d, 230, "違い① 静音の作り", 84, NAVY)
box(d, 340, 700)
center(d, 410, "YSF1070T（ヤマハ）", 52, GRAY)
center(d, 520, "防音で運転音を軽減", 64, NAVY)
center(d, 620, "（数値の公表なし）", 44, GRAY)
box(d, 740, 1100)
center(d, 810, "SXC1070SE（Wado）", 52, GRAY)
center(d, 920, "通常モデルより約6dB低い", 60, ORANGE)
center(d, 1020, "エンジンカバー＋排雪部の改良", 44, NAVY)
center(d, 1200, "※どちらが静かかを比べた公式データはありません", 34, GRAY)
k.save(img_dir / "S2.png")

# S3: 違い2 操作
k = snow_bg()
d = ImageDraw.Draw(k)
center(d, 230, "違い② 操作のしかた", 84, NAVY)
box(d, 340, 700)
center(d, 410, "YSF1070T", 52, GRAY)
center(d, 520, "イージーターン", 80, ORANGE)
center(d, 620, "スイッチで旋回・電磁クラッチ", 44, NAVY)
box(d, 740, 1100)
center(d, 810, "SXC1070SE", 52, GRAY)
center(d, 920, "電動サイドクラッチ", 72, ORANGE)
center(d, 1020, "除雪部の高さも電動で調整", 44, NAVY)
center(d, 1200, "※ヤマハ・Wado公式の装備説明より", 34, GRAY)
k.save(img_dir / "S3.png")

# S4: 締め
k = snow_bg()
d = ImageDraw.Draw(k)
center(d, 400, "70cmクラスの", 84, NAVY)
mixed(d, 540, [("ほかの機種", ORANGE), ("も比較中", NAVY)], 96)
d.rounded_rectangle([90, 700, W - 90, 980], radius=28, fill=NAVY)
center(d, 790, "3機種の比較は", 64, WHITE)
mixed(d, 890, [("関連動画", ORANGE), ("から", WHITE)], 80)
center(d, 1160, "北海道の除雪機選び", 56, NAVY)
k.save(img_dir / "S4.png")
print("cards: S0〜S4")

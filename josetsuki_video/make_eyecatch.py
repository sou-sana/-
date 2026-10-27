# ブログ記事のアイキャッチ画像(1200x630)を outputs/eyecatch/ に作る。
# 写真の左側に紺のグラデーション、白の見出し2行(要所はオレンジ)、右下にサイト名。
# usage: python3 prep_images.py && python3 make_eyecatch.py
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

root = Path(__file__).parent
img_dir = root / "images"
out = root / "outputs" / "eyecatch"
out.mkdir(parents=True, exist_ok=True)
W, H = 1200, 630
NAVY = (0x0D, 0x2A, 0x47)
ORANGE = (0xF2, 0x6B, 0x0F)
WHITE = (255, 255, 255)
FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"


def font(size):
    return ImageFont.truetype(FONT, size, index=0)


def cover(path, ay=0.5):
    """ay: 縦長の写真で切り出す高さ(0=上端、1=下端)。"""
    im = Image.open(path).convert("RGB")
    r = max(W / im.width, H / im.height)
    im = im.resize((int(im.width * r) + 1, int(im.height * r) + 1), Image.LANCZOS)
    x, y = (im.width - W) // 2, int((im.height - H) * ay)
    return im.crop((x, y, x + W, y + H))


def make(name, photo, line1, line2, accent="", ay=0.5):
    im = cover(img_dir / photo, ay).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    for x in range(W):
        a = 235 if x < 480 else int(235 * max(0.0, 1 - (x - 480) / 520))
        od.line([(x, 0), (x, H)], fill=NAVY + (a,))
    im = Image.alpha_composite(im, ov)
    d = ImageDraw.Draw(im)
    size = 76
    while max(font(size).getlength(line1), font(size).getlength(line2)) > 700:
        size -= 2
    d.text((60, 200), line1, font=font(size), fill=WHITE, anchor="lm")
    d.text((60, 200 + size + 30), line2, font=font(size), fill=ORANGE, anchor="lm")
    if accent:
        d.rounded_rectangle([60, 70, 60 + font(36).getlength(accent) + 40, 126], radius=10, fill=ORANGE)
        d.text((80, 98), accent, font=font(36), fill=WHITE, anchor="lm")
    d.text((60, H - 60), "北海道の除雪機選び", font=font(34), fill=WHITE, anchor="lm")
    d.text((W - 24, H - 24), "※イメージ", font=font(22), fill=WHITE, anchor="rd")
    im.convert("RGB").save(out / f"{name}.jpg", quality=90)


ITEMS = [
    ("01_在庫まとめ", "Q10_h.png", "北海道の除雪機", "在庫・価格まとめ", "毎週更新"),
    ("02_買ってはいけない", "F2_h.png", "買ってはいけない", "除雪機3つ", "公式の数字で"),
    ("06_静音2台", "L5.png", "同じ63万円の静音機", "どっちを選ぶ？", "YSF1070T・SXC1070SE"),
    ("07_通販で店に聞く4つ", "Q8_h.png", "通販で買う前に", "店に聞く4つ", "札幌まで送料も"),
    ("08_札幌補助金", "F4b_h.png", "札幌の除雪機補助金", "個人も使える？", "2026年度"),
    ("09_ハイブリッド", "F4_h.png", "HSS960iJXと", "HSS1370iJの違い", "ホンダ"),
    ("10_何馬力必要", "L4.png", "家庭用除雪機は", "何馬力必要？", "北海道"),
    ("11_6・8・10馬力", "F5_h.png", "6・8・10馬力は", "何が違う？", "北海道"),
    ("12_60・70・80cm", "Q3_h.png", "除雪幅60・70・80cm", "どこまで違う？", "駐車場の広さで"),
    ("13_初雪前の確認4つ", "Q12_v.png", "初雪の前に除雪機で", "確認する4つ", "かからない原因も", 0.78),
    ("14_雪質で選ぶ機能", "Q14_v.png", "ベタ雪・固い雪に", "効く機能と機種", "公式の説明だけで", 0.6),
    ("15_オーガに雪がくっつく", "Q14_v.png", "除雪機の羽に", "雪がくっつく対策", "メーカー公式＋用品", 0.85),
    ("16_ヤマハとホンダ", "Q6_h.png", "除雪機 ヤマハとホンダ", "どっちがいい？", "60・70cmを公式の数字で"),
]
for it in ITEMS:
    make(*it)
print(len(ITEMS), "eyecatches ->", out)

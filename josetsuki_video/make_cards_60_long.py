# 60cm横動画(YT660 vs HSS760nJ)用の16:9カード KL1〜KL5 と、サムネイルを作る。
# usage: python3 prep_images.py && python3 make_cards_60_long.py
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

root = Path(__file__).parent
img_dir = root / "images"
W, H = 1920, 1080
NAVY = (0x0D, 0x2A, 0x47)
ORANGE = (0xF2, 0x6B, 0x0F)
GRAY = (0x55, 0x6B, 0x80)
LINE = (0xC9, 0xD8, 0xE6)
WHITE = (255, 255, 255)
FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
NOTE = "価格: 2026年10月5日時点・除雪機ネット掲載価格 / 仕様: メーカー公表値"


def font(size):
    return ImageFont.truetype(FONT, size, index=0)


def cover(path, w, h):
    im = Image.open(path).convert("RGB")
    s = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x, y = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))


def snow_bg():
    bg = cover(img_dir / "L4.png", W, H).filter(ImageFilter.GaussianBlur(16))
    return Image.blend(bg, Image.new("RGB", (W, H), WHITE), 0.72)


def mixed(d, x, y, parts, size, anchor="lm"):
    """色違いの文字列を1行に並べる。anchor="mm" なら x を中心にする。"""
    total = sum(font(size).getlength(t) for t, _ in parts)
    if anchor == "mm":
        x -= total / 2
    for t, c in parts:
        d.text((x, y), t, font=font(size), fill=c, anchor="lm")
        x += font(size).getlength(t)


def title(d, text):
    d.text((90, 110), text, font=font(92), fill=NAVY, anchor="lm")


# KL1: タイトル(背景はL5、左に文字)
k = cover(img_dir / "L5.png", W, H).convert("RGBA")
ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
od = ImageDraw.Draw(ov)
for x in range(W):
    a = max(0.0, min(1.0, (1250 - x) / 500))
    od.line([(x, 0), (x, H)], fill=(245, 249, 253, int(215 * a)))
k = Image.alpha_composite(k, ov)
d = ImageDraw.Draw(k)
d.text((90, 210), "60cm除雪機", font=font(150), fill=NAVY, anchor="lm", stroke_width=8, stroke_fill=WHITE)
d.text((96, 380), "YT660 vs HSS760nJ", font=font(84), fill=NAVY, anchor="lm", stroke_width=6, stroke_fill=WHITE)
d.rounded_rectangle([90, 500, 1190, 660], radius=24, fill=NAVY)
mixed(d, 640, 580, [("差額", WHITE), ("1.1万円", ORANGE), ("で何が変わる？", WHITE)], 70, "mm")
d.text((96, 1030), NOTE, font=font(28), fill=NAVY, anchor="ls", stroke_width=3, stroke_fill=WHITE)
d.text((W - 30, H - 24), "※イメージ", font=font(30), fill=WHITE, anchor="rs", stroke_width=3, stroke_fill=NAVY)
k.convert("RGB").save(img_dir / "KL1.png")

# KL2: 比較表
k = snow_bg()
d = ImageDraw.Draw(k)
title(d, "2台の比較表")
rows = [("販売価格", "39.9万円", "41万円", False), ("除雪幅", "61.5cm", "60.5cm", False),
        ("最大出力", "4.8PS", "5.8PS", True), ("重量", "112kg", "105kg", True), ("排気量", "171cm³", "196cm³", False)]
L0, L1_, L2_, R = 90, 470, 1195, 1830
d.rounded_rectangle([L1_, 210, R, 330], radius=20, fill=NAVY)
d.text(((L1_ + L2_) // 2, 270), "Willbe YT660", font=font(58), fill=WHITE, anchor="mm")
d.text(((L2_ + R) // 2, 270), "HONDA HSS760nJ", font=font(58), fill=WHITE, anchor="mm")
y = 345
for label, a, b, hl in rows:
    d.rounded_rectangle([L0, y, L1_ - 15, y + 120], radius=16, fill=NAVY)
    d.text(((L0 + L1_ - 15) // 2, y + 60), label, font=font(50), fill=WHITE, anchor="mm")
    d.rounded_rectangle([L1_, y, R, y + 120], radius=16, fill=WHITE, outline=LINE, width=3)
    d.text(((L1_ + L2_) // 2, y + 60), a, font=font(66), fill=NAVY, anchor="mm")
    d.text(((L2_ + R) // 2, y + 60), b, font=font(66), fill=ORANGE if hl else NAVY, anchor="mm")
    y += 135
d.text((90, 1052), NOTE, font=font(28), fill=GRAY, anchor="ls")
k.save(img_dir / "KL2.png")

# KL3: 差額1.1万円で変わること
k = snow_bg()
d = ImageDraw.Draw(k)
mixed(d, 90, 110, [("差額", NAVY), ("1.1万円", ORANGE), ("で変わること", NAVY)], 92)
items = [("最大出力", "4.8PS → 5.8PS", "＋1.0PS", ORANGE), ("重量", "112kg → 105kg", "−7kg", ORANGE),
         ("除雪幅", "61.5cm vs 60.5cm", "ほぼ同じ", GRAY)]
for i, (label, val, diff, c) in enumerate(items):
    top = 230 + i * 260
    d.rounded_rectangle([90, top, 1830, top + 220], radius=24, fill=WHITE, outline=LINE, width=3)
    d.rounded_rectangle([90, top, 470, top + 220], radius=24, fill=NAVY)
    d.rectangle([440, top, 470, top + 220], fill=NAVY)
    d.text((280, top + 110), label, font=font(60), fill=WHITE, anchor="mm")
    d.text((560, top + 110), val, font=font(72), fill=NAVY, anchor="lm")
    d.text((1780, top + 110), diff, font=font(84), fill=c, anchor="rm")
k.save(img_dir / "KL3.png")

# KL4: 迷ったときのチェック
k = snow_bg()
d = ImageDraw.Draw(k)
title(d, "迷ったときのチェック")
checks = [("予算をできるだけ抑えたい", "YT660"), ("出力を優先したい", "HSS760nJ"),
          ("本体の軽さを重視したい", "HSS760nJ"), ("駐車場が2台分・通路が長い", "70cmクラスも検討")]
for i, (cond, ans) in enumerate(checks):
    top = 220 + i * 200
    d.rounded_rectangle([90, top, 1830, top + 170], radius=20, fill=WHITE, outline=LINE, width=3)
    d.rounded_rectangle([90, top, 1080, top + 170], radius=20, fill=NAVY)
    d.rectangle([1050, top, 1080, top + 170], fill=NAVY)
    d.text((140, top + 85), cond, font=font(56), fill=WHITE, anchor="lm")
    d.text((1455, top + 85), "→ " + ans, font=font(64 if len(ans) < 9 else 54), fill=ORANGE, anchor="mm")
k.save(img_dir / "KL4.png")

# KL5: 締め
k = snow_bg()
d = ImageDraw.Draw(k)
mixed(d, W // 2, 300, [("安さ", NAVY), ("なら ", NAVY), ("YT660", ORANGE)], 96, "mm")
mixed(d, W // 2, 450, [("出力と軽さ", NAVY), ("なら ", NAVY), ("HSS760nJ", ORANGE)], 96, "mm")
d.rounded_rectangle([360, 600, 1560, 800], radius=28, fill=NAVY)
mixed(d, W // 2, 700, [("比較表と最新の在庫は ", WHITE), ("概要欄", ORANGE), ("の記事へ", WHITE)], 64, "mm")
d.text((W // 2, 900), "北海道の除雪機選び", font=font(52), fill=NAVY, anchor="mm")
k.save(img_dir / "KL5.png")

# サムネイル(1280x720)
t = cover(img_dir / "L5.png", 1280, 720).convert("RGBA")
ov = Image.new("RGBA", (1280, 720), (0, 0, 0, 0))
od = ImageDraw.Draw(ov)
for x in range(1280):
    a = max(0.0, min(1.0, (880 - x) / 330))
    od.line([(x, 0), (x, 720)], fill=(245, 249, 253, int(205 * a)))
t = Image.alpha_composite(t, ov)
d = ImageDraw.Draw(t)
d.text((44, 40), "60cm除雪機", font=font(124), fill=NAVY, stroke_width=8, stroke_fill=WHITE)
d.text((50, 200), "高い方が", font=font(80), fill=NAVY, stroke_width=7, stroke_fill=WHITE)
d.text((50, 300), "強くて軽い？", font=font(100), fill=ORANGE, stroke_width=8, stroke_fill=WHITE)
d.rounded_rectangle([44, 470, 800, 660], radius=16, fill=NAVY)
d.text((422, 525), "YT660 vs HSS760nJ", font=font(52), fill=WHITE, anchor="mm")
mixed(d, 422, 605, [("差額 ", WHITE), ("1.1万円", ORANGE)], 58, "mm")
d.rounded_rectangle([1280 - 104, 24, 1280 - 24, 70], radius=8, fill=NAVY)
d.text((1280 - 64, 47), "PR", font=font(26), fill=WHITE, anchor="mm")
d.text((1280 - 24, 700), "※イメージ", font=font(24), fill=WHITE, anchor="rs", stroke_width=3, stroke_fill=NAVY)
(root / "outputs").mkdir(exist_ok=True)
t.convert("RGB").save(root / "outputs" / "thumbnail_60cm横動画.jpg", quality=92)
print("cards: KL1〜KL5, thumbnail")

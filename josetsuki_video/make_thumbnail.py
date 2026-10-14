# 横動画のYouTubeサムネイル(1280x720)。背景=除雪機の写真(右下に機体)、左上に大きな文字、3機種の価格、差額の問いかけ
# usage: python3 make_thumbnail.py [背景画像]
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

root = Path(__file__).parent
W, H = 1280, 720
NAVY = (0x0D, 0x2A, 0x47)
ORANGE = (0xF2, 0x6B, 0x0F)
WHITE = (255, 255, 255)
FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
src = sys.argv[1] if len(sys.argv) > 1 else str(root / "images" / "P1_photo.png")


def font(size):
    return ImageFont.truetype(FONT, size, index=0)


bg = Image.open(src).convert("RGB")
s = max(W / bg.width, H / bg.height)
bg = bg.resize((round(bg.width * s), round(bg.height * s)), Image.LANCZOS)
bg = bg.crop((bg.width - W, bg.height - H, bg.width, bg.height))  # 右下(機体側)を残す

# 左側を白っぽくして文字を読みやすく
overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
od = ImageDraw.Draw(overlay)
for x in range(W):
    a = max(0.0, min(1.0, (860 - x) / 360))
    od.line([(x, 0), (x, H)], fill=(245, 249, 253, int(200 * a)))
img = Image.alpha_composite(bg.convert("RGBA"), overlay)
d = ImageDraw.Draw(img)

# メインコピー
d.text((44, 40), "70cm除雪機", font=font(128), fill=NAVY, stroke_width=8, stroke_fill=WHITE)
d.text((50, 200), "どれを買う？", font=font(76), fill=NAVY, stroke_width=7, stroke_fill=WHITE)

# 3機種の価格カード
x = 44
for name, price in [("HSS970nJ", "51"), ("SXC1070H", "58"), ("YSF1070T", "63")]:
    d.rounded_rectangle([x, 330, x + 240, 500], radius=14, fill=WHITE, outline=NAVY, width=4)
    d.rounded_rectangle([x, 330, x + 240, 382], radius=14, fill=NAVY)
    d.rectangle([x, 366, x + 240, 382], fill=NAVY)
    d.text((x + 120, 357), name, font=font(30), fill=WHITE, anchor="mm")
    d.text((x + 106, 448), price, font=font(88), fill=ORANGE, anchor="mm")
    d.text((x + 186, 466), "万円", font=font(30), fill=ORANGE, anchor="mm")
    x += 262

# 問いかけ帯
d.rounded_rectangle([44, 548, 830, 668], radius=16, fill=NAVY)
parts = [("差額", WHITE), ("12万円", ORANGE), ("の中身は？", WHITE)]
x = 437 - sum(font(62).getlength(t) for t, _ in parts) / 2
for t, color in parts:
    d.text((x, 608), t, font=font(62), fill=color, anchor="lm")
    x += font(62).getlength(t)

# PR(右上)と※イメージ(右下)
d.rounded_rectangle([W - 104, 24, W - 24, 70], radius=8, fill=NAVY)
d.text((W - 64, 47), "PR", font=font(26), fill=WHITE, anchor="mm")
d.text((W - 24, H - 20), "※イメージ", font=font(24), fill=WHITE, anchor="rs", stroke_width=3, stroke_fill=NAVY)

out = root / "outputs" / "thumbnail_横動画.jpg"
out.parent.mkdir(exist_ok=True)
img.convert("RGB").save(out, quality=92)
print(out, out.stat().st_size // 1024, "KB")

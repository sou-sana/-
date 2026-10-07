# YouTubeサムネイル(1280x720)を作る。背景=images_a/02(更衣室)、右側に大きな文字+小さな「PR」
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

root = Path(__file__).parent
W, H = 1280, 720
NAVY = (0x0F, 0x2A, 0x3D)
TEAL = (0x2A, 0x7F, 0x8C)
FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
FONT_B = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
src = sys.argv[1] if len(sys.argv) > 1 else str(root / "images_a" / "02.jpg")


def font(path, size):
    return ImageFont.truetype(path, size, index=0)


bg = Image.open(src).convert("RGB")
s = max(W / bg.width, H / bg.height)
bg = bg.resize((round(bg.width * s), round(bg.height * s)), Image.LANCZOS)
x0 = (bg.width - W) // 2
bg = bg.crop((x0, (bg.height - H) // 2, x0 + W, (bg.height - H) // 2 + H))

# 右側を白くぼかして文字を読みやすく
overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
od = ImageDraw.Draw(overlay)
for x in range(W):
    a = max(0, min(1, (x - 560) / 260))
    od.line([(x, 0), (x, H)], fill=(247, 251, 251, int(215 * a)))
img = Image.alpha_composite(bg.convert("RGBA"), overlay)
d = ImageDraw.Draw(img)

# メインコピー(2行)。白い縁取りで背景に負けないように
cx = 985
lines = [("“言い出せない”は、", 58, NAVY), ("弱さ", 150, NAVY), ("じゃない", 104, NAVY)]
y = 165
for text, size, color in lines:
    f = font(FONT, size)
    d.text((cx, y), text, font=f, fill=color, anchor="mt", stroke_width=6, stroke_fill=(255, 255, 255))
    y += int(size * 1.18)

# 下線アクセント
d.rounded_rectangle([cx - 150, y + 6, cx + 150, y + 16], radius=5, fill=TEAL)
# サブコピー
d.text((cx, y + 46), "辞めたいのに言い出せない看護師へ", font=font(FONT_B, 34), fill=NAVY, anchor="mt",
       stroke_width=4, stroke_fill=(255, 255, 255))

# PR(右上・小さく)
d.rounded_rectangle([W - 104, 24, W - 24, 70], radius=8, fill=NAVY + (230,))
d.text((W - 64, 47), "PR", font=font(FONT_B, 26), fill="white", anchor="mm")
# チャンネル名(左下・小さく)
d.text((32, H - 30), "げんばのカルテ", font=font(FONT_B, 28), fill="white", anchor="ls",
       stroke_width=4, stroke_fill=NAVY)

out = root / "thumbnail" / "thumbnail.jpg"
img.convert("RGB").save(out, quality=92)
print(out, out.stat().st_size // 1024, "KB")

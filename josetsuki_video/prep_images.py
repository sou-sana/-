# src/ の画像をコピーし、ロゴのように見える部分をぼかして images/ に置く。
# usage: python3 prep_images.py
from pathlib import Path

from PIL import Image, ImageFilter

root = Path(__file__).parent
src, dst = root / "src", root / "images"
dst.mkdir(exist_ok=True)

# (left, top, right, bottom) は元画像のピクセル座標
BLUR = {
    "V2.jpg": [(130, 845, 228, 908), (292, 855, 398, 918)],  # 車のエンブレム
    "V4.jpg": [(405, 768, 492, 820), (414, 840, 442, 862), (358, 836, 380, 857),
               (258, 872, 306, 892), (386, 940, 410, 962), (470, 815, 495, 835)],  # 除雪機の文字
}

for p in sorted(src.iterdir()):
    im = Image.open(p).convert("RGB")
    for box in BLUR.get(p.name, []):
        region = im.crop(box).filter(ImageFilter.GaussianBlur(8))
        im.paste(region, box)
    im.save(dst / (p.stem + ".png"))
    print(p.name, "->", p.stem + ".png", len(BLUR.get(p.name, [])), "blurred")

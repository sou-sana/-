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
    "F4b_h.jpg": [(478, 456, 500, 486)],  # シューターのラベル状の模様
    "Q4_v.jpg": [(262, 758, 302, 784)],  # 上着のロゴ状の模様
    "Q7_v.jpg": [(285, 1098, 337, 1137)],  # 操作パネルのラベル
    "Q10_h.jpg": [(183, 420, 214, 472), (78, 522, 114, 555)],  # 車のエンブレム・ナンバープレート
    "Q5_h.jpg": [(410, 450, 480, 490)],  # 電動機ハンドル下の銘板状の模様
    "Q6_h.jpg": [(1010, 175, 1140, 240)],  # 操作パネルの銘板状の模様
    "Q13_v.jpg": [(365, 748, 402, 772)],  # エンジンのラベル状の模様
    "Q15_v.jpg": [(430, 818, 482, 850), (668, 815, 718, 846)],  # 車のナンバープレート
}

for p in sorted(src.iterdir()):
    im = Image.open(p).convert("RGB")
    for box in BLUR.get(p.name, []):
        region = im.crop(box).filter(ImageFilter.GaussianBlur(8))
        im.paste(region, box)
    im.save(dst / (p.stem + ".png"))
    print(p.name, "->", p.stem + ".png", len(BLUR.get(p.name, [])), "blurred")

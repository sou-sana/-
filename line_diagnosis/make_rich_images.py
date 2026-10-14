# LINEリッチメッセージ用の画像(1040x1040)を作る。上半分=質問、下半分=はい/いいえ(左右)
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

NAVY = (0x0F, 0x2A, 0x3D)
TEAL = (0x2A, 0x7F, 0x8C)
BG = (0xF4, 0xFA, 0xFA)
FB = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
QUESTIONS = [
    ("質問 1 / 最大4問", ["ここ2週間で、", "「朝、体が動かない」", "「眠れない」「理由なく涙が出る」", "のどれかが何度もあった"]),
    ("質問 2", ["求人サイトを見たり、", "「辞めたあと」のことを", "考える時間が増えた"]),
    ("質問 3", ["前は楽しめていたことを、", "楽しいと感じにくくなった", "(笑う回数が減った など)"]),
    ("質問 4", ["仕事のあと、", "小さなモヤモヤが残る日が", "増えた"]),
]


def font(size):
    return ImageFont.truetype(FB, size, index=0)


out = Path(__file__).parent / "rich_images"
out.mkdir(exist_ok=True)
for i, (label, lines) in enumerate(QUESTIONS, 1):
    img = Image.new("RGB", (1040, 1040), BG)
    d = ImageDraw.Draw(img)
    d.text((520, 70), "辞めどき4段階チェック", font=font(36), fill=TEAL, anchor="mm")
    d.text((520, 128), label, font=font(30), fill=NAVY, anchor="mm")
    size = 50 if len(lines) <= 3 else 46
    y0 = 300 - (len(lines) - 1) * size * 0.75
    for k, line in enumerate(lines):
        d.text((520, y0 + k * size * 1.5), line, font=font(size), fill=NAVY, anchor="mm")
    # 下半分: はい(左) / いいえ(右)
    d.rectangle([0, 520, 519, 1039], fill=TEAL)
    d.rectangle([520, 520, 1039, 1039], fill=(0xE3, 0xEE, 0xF0))
    d.line([(520, 520), (520, 1040)], fill=(255, 255, 255), width=4)
    d.text((260, 760), "はい", font=font(96), fill="white", anchor="mm")
    d.text((780, 760), "いいえ", font=font(96), fill=NAVY, anchor="mm")
    d.text((260, 860), "タップ", font=font(32), fill=(220, 240, 240), anchor="mm")
    d.text((780, 860), "タップ", font=font(32), fill=TEAL, anchor="mm")
    img.save(out / f"Q{i}.png")
    print(out / f"Q{i}.png")

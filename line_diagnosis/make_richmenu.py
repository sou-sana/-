# LINEリッチメニュー画像(小・2500x843、1ボタン)を作る
from PIL import Image, ImageDraw, ImageFont

NAVY, TEAL = (0x0F, 0x2A, 0x3D), (0x2A, 0x7F, 0x8C)
FB = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
f = lambda s: ImageFont.truetype(FB, s, index=0)
img = Image.new("RGB", (2500, 843), (0xF4, 0xFA, 0xFA))
d = ImageDraw.Draw(img)
d.rounded_rectangle([120, 110, 2380, 733], radius=60, fill=TEAL)
d.text((1250, 330), "辞めどき4段階チェック", font=f(150), fill="white", anchor="mm")
d.text((1250, 540), "4つの質問・1分 ▶ タップして始める", font=f(84), fill=(0xE3, 0xF3, 0xF3), anchor="mm")
img.save("rich_images/richmenu_2500x843.png")

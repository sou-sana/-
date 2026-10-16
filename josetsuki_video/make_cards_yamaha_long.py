# ヤマハ撤退・旧ヤマハモデル(Willbe)の横動画用16:9カード YL1〜YL7 と、サムネイルを作る。
# usage: python3 prep_images.py && python3 make_cards_yamaha_long.py
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
NOTE = "情報: ヤマハ発動機・Willbe公式、PR TIMES（2026年10月確認）"


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


def photo_title(src, big, sub, box_parts):
    k = cover(img_dir / src, W, H).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    for x in range(W):
        a = max(0.0, min(1.0, (1300 - x) / 500))
        od.line([(x, 0), (x, H)], fill=(245, 249, 253, int(220 * a)))
    k = Image.alpha_composite(k, ov)
    d = ImageDraw.Draw(k)
    d.text((90, 210), big, font=font(130), fill=NAVY, anchor="lm", stroke_width=8, stroke_fill=WHITE)
    d.text((96, 370), sub, font=font(80), fill=NAVY, anchor="lm", stroke_width=6, stroke_fill=WHITE)
    d.rounded_rectangle([90, 490, 1240, 650], radius=24, fill=NAVY)
    mixed(d, 665, 570, box_parts, 64, "mm")
    d.text((96, 1030), NOTE, font=font(28), fill=NAVY, anchor="ls", stroke_width=3, stroke_fill=WHITE)
    d.text((W - 30, H - 24), "※イメージ", font=font(30), fill=WHITE, anchor="rs", stroke_width=3, stroke_fill=NAVY)
    return k


# YL1: タイトル
photo_title("Q6_h.png", "ヤマハの除雪機", "もう買えない？", [("修理・部品と", WHITE), ("今買える機種", ORANGE)]).convert("RGB").save(img_dir / "YL1.png")

# YL2: 何が起きたか(時系列)
k = snow_bg()
d = ImageDraw.Draw(k)
title(d, "何が起きたのか")
events = [("2025年11月", "Willbeが「Earth POWER」で先行販売（数量限定）"),
          ("2026年3月末", "ヤマハが除雪機事業を終了（事業譲渡）"),
          ("2026年8月", "Earth POWERの除雪機が本格販売")]
for i, (when, what) in enumerate(events):
    top = 250 + i * 240
    d.rounded_rectangle([90, top, 1830, top + 200], radius=24, fill=WHITE, outline=LINE, width=3)
    d.rounded_rectangle([90, top, 560, top + 200], radius=24, fill=NAVY if i != 1 else ORANGE)
    d.rectangle([530, top, 560, top + 200], fill=NAVY if i != 1 else ORANGE)
    d.text((325, top + 100), when, font=font(60), fill=WHITE, anchor="mm")
    d.text((620, top + 100), what, font=font(56), fill=NAVY, anchor="lm")
d.text((90, 1052), NOTE, font=font(28), fill=GRAY, anchor="ls")
k.save(img_dir / "YL2.png")

# YL3: ラインアップ
k = snow_bg()
d = ImageDraw.Draw(k)
title(d, "Earth POWERの機種（全12機種）")
rows = [("6馬力帯", "YT660・YT660-B"), ("8馬力帯", "YSF860・YSF860-B"),
        ("10馬力帯", "YT1070・YSF1070・YSF1070T・YSF1070T-B"), ("13馬力帯", "YT1380・YT1380X・YT1390X・YT1390XR")]
for i, (cls, models) in enumerate(rows):
    top = 230 + i * 175
    d.rounded_rectangle([90, top, 1830, top + 150], radius=20, fill=WHITE, outline=LINE, width=3)
    d.rounded_rectangle([90, top, 470, top + 150], radius=20, fill=NAVY)
    d.rectangle([440, top, 470, top + 150], fill=NAVY)
    d.text((280, top + 75), cls, font=font(56), fill=WHITE, anchor="mm")
    d.text((530, top + 75), models, font=font(54 if len(models) < 26 else 46), fill=NAVY, anchor="lm")
mixed(d, 90, 990, [("機種名はヤマハ時代と同じ系統。", NAVY), ("「〇馬力帯」は区分名で、最大出力の数値ではない", ORANGE)], 40)
k.save(img_dir / "YL3.png")

# YL4: 修理・部品の窓口
k = snow_bg()
d = ImageDraw.Draw(k)
title(d, "使っているヤマハ機の修理・部品")
for i, (no, who) in enumerate([("①", "購入した販売店"), ("②", "ヤマハ除雪機サービスパートナー店"), ("③", "ホームセンターで買った場合は、納入したサービス店")]):
    top = 240 + i * 190
    d.rounded_rectangle([90, top, 1830, top + 160], radius=20, fill=WHITE, outline=LINE, width=3)
    d.text((170, top + 80), no, font=font(72), fill=ORANGE, anchor="mm")
    d.text((260, top + 80), who, font=font(62 if len(who) < 16 else 52), fill=NAVY, anchor="lm")
d.rounded_rectangle([90, 830, 1830, 960], radius=20, fill=NAVY)
mixed(d, W // 2, 895, [("混む前に、", WHITE), ("雪が降る前の点検", ORANGE), ("を", WHITE)], 60, "mm")
d.text((90, 1052), "※ヤマハ発動機公式サイト「ご使用中のQ&A」の案内より", font=font(28), fill=GRAY, anchor="ls")
k.save(img_dir / "YL4.png")

# YL5: 買う前に確認する3つ
k = snow_bg()
d = ImageDraw.Draw(k)
title(d, "これから買う人が確認したい3つ")
for i, (t1, t2) in enumerate([("近くに修理・点検できる店があるか", "困るのは大雪の日の故障"),
                               ("保証と問い合わせの窓口", "ヤマハ表記の在庫品か、Willbeの新品か"),
                               ("在庫と納期", "ヤマハ表記の機種は在庫限り")]):
    top = 230 + i * 250
    d.rounded_rectangle([90, top, 1830, top + 220], radius=24, fill=WHITE, outline=LINE, width=3)
    d.text((150, top + 80), f"{i + 1}. {t1}", font=font(62), fill=NAVY, anchor="lm")
    d.text((210, top + 160), t2, font=font(44), fill=GRAY, anchor="lm")
k.save(img_dir / "YL5.png")

# YL6: 今買える旧ヤマハ系(除雪機ネット)
k = snow_bg()
d = ImageDraw.Draw(k)
title(d, "除雪機ネットで買える旧ヤマハ系")
L0, c1, c2, c3, R = 90, 520, 900, 1290, 1830
d.rounded_rectangle([L0, 210, R, 320], radius=20, fill=NAVY)
for x0, x1, h in [(L0, c1, "機種"), (c1, c2, "最大出力"), (c2, c3, "除雪幅"), (c3, R, "価格・在庫")]:
    d.text(((x0 + x1) // 2, 265), h, font=font(50), fill=WHITE, anchor="mm")
data = [("YT660", "4.8PS", "61.5cm", "39.9万円・早期予約"), ("YSF860", "9.3PS", "61.5cm", "54万円・要問い合わせ"),
        ("YSF1070T", "9.4PS", "71.5cm", "63万円・ラスト2台")]
for i, row in enumerate(data):
    top = 340 + i * 190
    d.rounded_rectangle([L0, top, R, top + 170], radius=20, fill=WHITE, outline=LINE, width=3)
    for (x0, x1), v in zip([(L0, c1), (c1, c2), (c2, c3), (c3, R)], row):
        d.text(((x0 + x1) // 2, top + 85), v, font=font(64 if len(v) < 9 else 44), fill=ORANGE if v == "9.3PS" else NAVY, anchor="mm")
d.text((90, 1000), "最大出力・除雪幅: Willbe・ヤマハ公式 / 価格・在庫: 除雪機ネット 10月14日時点（毎週変わります）", font=font(30), fill=GRAY, anchor="ls")
k.save(img_dir / "YL6.png")

# YL7: 締め
k = snow_bg()
d = ImageDraw.Draw(k)
mixed(d, W // 2, 260, [("予算なら ", NAVY), ("YT660", ORANGE)], 84, "mm")
mixed(d, W // 2, 390, [("60cmで出力と静音なら ", NAVY), ("YSF860", ORANGE)], 84, "mm")
mixed(d, W // 2, 520, [("70cmで静音・旋回なら ", NAVY), ("YSF1070T", ORANGE)], 84, "mm")
d.rounded_rectangle([360, 640, 1560, 840], radius=28, fill=NAVY)
mixed(d, W // 2, 740, [("最新の在庫と比較表は ", WHITE), ("概要欄", ORANGE), ("の記事へ", WHITE)], 62, "mm")
d.text((W // 2, 940), "北海道の除雪機選び", font=font(52), fill=NAVY, anchor="mm")
k.save(img_dir / "YL7.png")

# サムネイル(1280x720)
t = cover(img_dir / "Q6_h.png", 1280, 720).convert("RGBA")
ov = Image.new("RGBA", (1280, 720), (0, 0, 0, 0))
od = ImageDraw.Draw(ov)
for x in range(1280):
    a = max(0.0, min(1.0, (880 - x) / 330))
    od.line([(x, 0), (x, 720)], fill=(245, 249, 253, int(215 * a)))
t = Image.alpha_composite(t, ov)
d = ImageDraw.Draw(t)
d.text((44, 40), "ヤマハの除雪機", font=font(112), fill=NAVY, stroke_width=8, stroke_fill=WHITE)
d.text((50, 190), "もう買えない？", font=font(104), fill=ORANGE, stroke_width=8, stroke_fill=WHITE)
d.rounded_rectangle([44, 420, 820, 640], radius=16, fill=NAVY)
d.text((432, 485), "修理・部品はどこへ？", font=font(56), fill=WHITE, anchor="mm")
mixed(d, 432, 575, [("今買える ", WHITE), ("旧ヤマハ機", ORANGE)], 58, "mm")
d.rounded_rectangle([1280 - 104, 24, 1280 - 24, 70], radius=8, fill=NAVY)
d.text((1280 - 64, 47), "PR", font=font(26), fill=WHITE, anchor="mm")
d.text((1280 - 24, 700), "※イメージ", font=font(24), fill=WHITE, anchor="rs", stroke_width=3, stroke_fill=NAVY)
(root / "outputs").mkdir(exist_ok=True)
t.convert("RGB").save(root / "outputs" / "thumbnail_ヤマハ横動画.jpg", quality=92)
print("cards: YL1〜YL7, thumbnail")

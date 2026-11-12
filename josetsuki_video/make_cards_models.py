# 機種ページ（ブログ）を横動画にするための16:9カードとサムネイルを、機種ごとに作る。
# データは MODELS（ブログ記事と同じ公式の数字・11月の価格）。カード: <key>1〜<key>5、サムネ: outputs/thumb_<key>.jpg
# usage: python3 prep_images.py && python3 make_cards_models.py
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

root = Path(__file__).parent
img_dir = root / "images"
out_dir = root / "outputs"
out_dir.mkdir(exist_ok=True)
W, H = 1920, 1080
NAVY = (0x0D, 0x2A, 0x47)
ORANGE = (0xF2, 0x6B, 0x0F)
GRAY = (0x55, 0x6B, 0x80)
LINE = (0xC9, 0xD8, 0xE6)
WHITE = (255, 255, 255)
FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"

MODELS = {
    "MY": {  # YT1070
        "name": "YT1070", "maker": "ヤマハ（現ウィルビー）", "photo": "Q10_h.png",
        "big": "YT1070", "sub": "70cmで いちばん安い", "price": "48万円",
        "specs": [("除雪幅", "71.5cm"), ("最大出力", "9.5PS（3,600rpm）"), ("除雪高", "新雪51cm／固まった雪35cm"), ("機械の幅", "73cm")],
        "total": [("本体", "480,000円"), ("札幌までの送料（営業所止め）", "約6万円"), ("総額の目安", "約54万円")],
        "compare_title": "ホンダHSS970nJと比べると",
        "compare": [("価格", "48万円", "51万円"), ("除雪幅", "71.5cm", "71cm"), ("最大出力", "9.5PS", "8.6PS")],
        "cmp_heads": ("YT1070", "HSS970nJ"),
        "good": ["70cmをできるだけ安く", "除雪車が置く固い雪がある"],
        "bad": ["静かさ優先 → YSF860", "電動で楽に → SXC1070H"],
        "note": "仕様: Willbe公式（Earth POWER YT1070）、Honda公式／価格: 除雪機ネット 2026年11月",
    },
    "MS": {  # SXC1380H
        "name": "SXC1380H", "maker": "和同（Wado）", "photo": "L4.png",
        "big": "SXC1380H", "sub": "80cm・ホンダより6.2万円安い", "price": "79.8万円",
        "specs": [("除雪幅", "80cm"), ("最大出力", "11.8PS（3,600rpm）"), ("除雪高", "58cm"), ("機械の幅", "80cm")],
        "total": [("本体", "798,000円"), ("送料（80cm）", "店に確認"), ("メーカー希望小売価格", "877,800円")],
        "compare_title": "ホンダHSM1380iJNと比べると",
        "compare": [("価格", "79.8万円", "86万円"), ("除雪幅", "80cm", "80cm"), ("ローリング", "あり", "JRに付く")],
        "cmp_heads": ("SXC1380H", "HSM1380iJN"),
        "good": ["広い駐車場・敷地", "旋回や傾きを手元で楽に"],
        "bad": ["通り道が80cmより狭い", "予算60万円以下 → YT1070"],
        "note": "仕様: 和同産業・Honda公式／価格: 除雪機ネット 2026年11月",
    },
    "MF": {  # YSF860
        "name": "YSF860", "maker": "ウィルビー（旧ヤマハ）", "photo": "Q6_h.png",
        "big": "YSF860", "sub": "60cmの静音タイプ", "price": "54万円",
        "specs": [("除雪幅", "61.5cm"), ("最大出力", "9.3PS（3,400rpm）"), ("音量（公式）", "64.8dB(A)"), ("排気量", "296cm³")],
        "total": [("本体", "540,000円"), ("札幌までの送料（目安）", "約6万円"), ("総額の目安", "約60万円")],
        "compare_title": "同じ旧ヤマハ系と比べると",
        "compare": [("価格", "54万円", "68万円"), ("除雪幅", "61.5cm", "71.5cm"), ("音量", "64.8dB", "66.8dB")],
        "cmp_heads": ("YSF860", "YSF1070T"),
        "good": ["早朝の住宅街で使う", "通り道が狭く60cmにしたい"],
        "bad": ["予算40万円前後 → YT660", "広い駐車場 → 70cmクラス"],
        "note": "仕様・音量: Willbe・ヤマハ公式（音量は7m・4方向の平均）／価格: 除雪機ネット 2026年11月",
    },
    "MW": {  # SXC1070H
        "name": "SXC1070H", "maker": "和同（Wado）", "photo": "Q3_h.png",
        "big": "SXC1070H", "sub": "70cmで電動旋回", "price": "58万円",
        "specs": [("除雪幅", "71cm"), ("除雪高", "51.8cm"), ("旋回", "電動サイドクラッチ"), ("除雪部の高さ", "電動で調整")],
        "total": [("本体", "580,000円"), ("札幌までの送料（営業所止め）", "約6万円"), ("総額の目安", "約64万円")],
        "compare_title": "70cmクラスの価格",
        "compare": [("YT1070", "48万円", ""), ("HSS970nJ", "51万円", ""), ("SXC1070H", "58万円", "")],
        "cmp_heads": ("価格", ""),
        "good": ["旋回や上げ下げを手元で楽に", "高さも電動で変えたい"],
        "bad": ["できるだけ安く → YT1070", "静かさ優先 → YSF860"],
        "note": "仕様: 和同産業公式／価格: 除雪機ネット 2026年11月（ラスト2台の表示）",
    },
    "MT": {  # YSF1070T
        "name": "YSF1070T", "maker": "ウィルビー（旧ヤマハ）", "photo": "Q8_h.png",
        "big": "YSF1070T", "sub": "70cmの静音タイプ", "price": "68万円",
        "specs": [("除雪幅", "71.5cm"), ("音量（公式）", "66.8dB(A)"), ("除雪高", "新雪51cm／固まった雪35cm"), ("広さの目安", "車約6台分")],
        "total": [("本体", "680,000円"), ("札幌までの送料（営業所止め）", "約6万円"), ("総額の目安", "約74万円")],
        "compare_title": "同じ旧ヤマハ系と比べると",
        "compare": [("価格", "68万円", "54万円"), ("除雪幅", "71.5cm", "61.5cm"), ("音量", "66.8dB", "64.8dB")],
        "cmp_heads": ("YSF1070T", "YSF860"),
        "good": ["早朝の住宅街で70cm", "駐車場が広め"],
        "bad": ["安く70cm → YT1070", "通り道が狭い → YSF860"],
        "note": "仕様・音量・広さ: Willbe・ヤマハ公式／価格: 除雪機ネット 2026年11月（11月上旬に値上がり）",
    },
}


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


def fade_left(img, edge, width, alpha=220):
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    for x in range(img.width):
        a = max(0.0, min(1.0, (edge - x) / width))
        od.line([(x, 0), (x, img.height)], fill=(245, 249, 253, int(alpha * a)))
    return Image.alpha_composite(img.convert("RGBA"), ov)


def footer(d, note):
    d.text((90, H - 60), note, font=font(30), fill=GRAY, anchor="lm")


def card_title(m, key):
    k = fade_left(cover(img_dir / m["photo"], W, H), 1300, 500)
    d = ImageDraw.Draw(k)
    d.text((90, 150), m["maker"], font=font(64), fill=GRAY, anchor="lm", stroke_width=5, stroke_fill=WHITE)
    d.text((90, 300), m["big"], font=font(180), fill=NAVY, anchor="lm", stroke_width=9, stroke_fill=WHITE)
    d.text((96, 470), m["sub"], font=font(80), fill=NAVY, anchor="lm", stroke_width=6, stroke_fill=WHITE)
    d.rounded_rectangle((90, 560, 700, 700), 24, fill=ORANGE)
    d.text((395, 630), m["price"], font=font(96), fill=WHITE, anchor="mm")
    d.text((W - 40, H - 40), "※イメージ", font=font(30), fill=WHITE, anchor="rb", stroke_width=3, stroke_fill=NAVY)
    k.convert("RGB").save(img_dir / f"{key}1.png")


def rows_card(key, n, heading, rows, note, highlight_last=False):
    k = snow_bg()
    d = ImageDraw.Draw(k)
    d.text((90, 120), heading, font=font(84), fill=NAVY, anchor="lm")
    y = 270
    for i, (a, b) in enumerate(rows):
        last = highlight_last and i == len(rows) - 1
        d.rounded_rectangle((90, y - 70, W - 90, y + 70), 20, fill=ORANGE if last else WHITE, outline=LINE, width=3)
        d.text((140, y), a, font=font(60), fill=WHITE if last else GRAY, anchor="lm")
        d.text((W - 140, y), b, font=font(72), fill=WHITE if last else NAVY, anchor="rm")
        y += 170
    footer(d, note)
    k.save(img_dir / f"{key}{n}.png")


def compare_card(m, key):
    k = snow_bg()
    d = ImageDraw.Draw(k)
    d.text((90, 120), m["compare_title"], font=font(84), fill=NAVY, anchor="lm")
    h1, h2 = m["cmp_heads"]
    d.text((1150, 240), h1, font=font(60), fill=ORANGE, anchor="mm")
    if h2:
        d.text((1600, 240), h2, font=font(60), fill=GRAY, anchor="mm")
    y = 380
    for a, b, c in m["compare"]:
        d.rounded_rectangle((90, y - 70, W - 90, y + 70), 20, fill=WHITE, outline=LINE, width=3)
        d.text((140, y), a, font=font(60), fill=GRAY, anchor="lm")
        d.text((1150, y), b, font=font(72), fill=NAVY, anchor="mm")
        if c:
            d.text((1600, y), c, font=font(72), fill=GRAY, anchor="mm")
        y += 170
    footer(d, m["note"])
    k.save(img_dir / f"{key}4.png")


def fit_card(m, key):
    k = snow_bg()
    d = ImageDraw.Draw(k)
    d.text((90, 120), f"{m['name']}が向く人・向かない人", font=font(80), fill=NAVY, anchor="lm")
    for col, (head, items, color) in enumerate([("向く人", m["good"], ORANGE), ("ほかが候補", m["bad"], GRAY)]):
        x0 = 90 + col * 880
        d.rounded_rectangle((x0, 220, x0 + 840, 900), 28, fill=WHITE, outline=color, width=6)
        d.text((x0 + 420, 300), head, font=font(70), fill=color, anchor="mm")
        for i, t in enumerate(items):
            d.text((x0 + 50, 450 + i * 170), "・" + t, font=font(54), fill=NAVY, anchor="lm")
    d.text((W // 2, 990), "詳しい比較と最新の在庫は 概要欄の記事へ", font=font(56), fill=ORANGE, anchor="mm")
    k.save(img_dir / f"{key}5.png")


def thumb(m, key):
    tw, th = 1280, 720
    k = fade_left(cover(img_dir / m["photo"], tw, th), 860, 360, 200)
    d = ImageDraw.Draw(k)
    d.text((44, 60), m["big"], font=font(150), fill=NAVY, stroke_width=8, stroke_fill=WHITE)
    d.text((50, 250), m["sub"], font=font(64), fill=NAVY, stroke_width=6, stroke_fill=WHITE)
    d.rounded_rectangle((44, 380, 520, 500), 20, fill=ORANGE)
    d.text((282, 440), m["price"], font=font(84), fill=WHITE, anchor="mm")
    d.text((tw - 20, th - 20), "※イメージ", font=font(24), fill=WHITE, anchor="rb", stroke_width=2, stroke_fill=NAVY)
    k.convert("RGB").save(out_dir / f"thumb_{key}.jpg", quality=92)


for key, m in MODELS.items():
    card_title(m, key)
    rows_card(key, 2, f"{m['name']}の主な数字（公式）", m["specs"], m["note"])
    rows_card(key, 3, "北海道まで届けると", m["total"], "送料: 除雪機ネットへの問い合わせ（2026年10月、札幌市の例・概算）", highlight_last=True)
    compare_card(m, key)
    fit_card(m, key)
    thumb(m, key)
print("cards:", ", ".join(f"{k}1-5" for k in MODELS))

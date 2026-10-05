# 本編2用のフラットイラスト18枚(1920x1080 SVG)を生成する。
# 輪郭線のみ・顔なし・白/青/緑の淡い配色。下部(y>860)は字幕帯用の余白。
# スタイルA(表情あり半リアル)の画像を用意したら imgNN.png を差し替えれば build.py がそれを使う。
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "genba_karute_shorts"))
from make_images import INK, LINE, SCRUB, SKIN, TEAL, head, limb, plant, seated, shape, standing, window  # noqa: E402

W, H = 1920, 1080
FLOOR = 830
NAVY = "#0F2A3D"


def svg(body, top="#F5FAFA", bottom="#E3F0F0", floor="#D7E8E7", floor_y=FLOOR):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
            f'<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{top}"/>'
            f'<stop offset="1" stop-color="{bottom}"/></linearGradient>'
            f'<radialGradient id="glow"><stop offset="0" stop-color="#FFFFFF" stop-opacity=".85"/>'
            f'<stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/></radialGradient></defs>'
            f'<rect width="{W}" height="{H}" fill="url(#g)"/>'
            f'<rect y="{floor_y}" width="{W}" height="{H - floor_y}" fill="{floor}"/>'
            f'<line x1="0" y1="{floor_y}" x2="{W}" y2="{floor_y}" stroke="{INK}" stroke-width="4" opacity=".4"/>'
            f'{body}</svg>')


def shadow(x, y, rx=110):
    return f'<ellipse cx="{x}" cy="{y + 4}" rx="{rx}" ry="14" fill="{INK}" opacity=".08"/>'


def ghost(content, op=0.28):
    """ボケた人影(背景の忙しい人たち)。"""
    return f'<g opacity="{op}" filter="url(#blur)">{content}</g>'


BLUR = '<defs><filter id="blur"><feGaussianBlur stdDeviation="5"/></filter></defs>'


def rect(x, y, w, h, fill="#FFFFFF", rx=8, sw=LINE):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{INK}" stroke-width="{sw}"/>'


def figure_no_arms(x, fy, s, **kw):
    return standing(x, fy, s, arms="none", **kw)


def p(x, fy, s, dx, dy):
    return (x + dx * s, fy + dy * s)


# ---------- 1: ナースステーションの隅、立ち止まる看護師と流れる人影 ----------
def img1():
    b = BLUR
    b += rect(140, 300, 980, 60, "#EAF3F4") + rect(140, 360, 980, 200, "#F4F9F9")  # カウンター
    b += rect(220, 160, 240, 100, "#FFFFFF") + rect(520, 150, 180, 120, "#E2F0F2")
    for gx, op in [(300, .25), (520, .3), (760, .22), (980, .28)]:
        b += ghost(standing(gx, FLOOR, 0.78, arms="laugh", top="#CFE0E8"), op)
    b += plant(1700, 760, 1.0)
    b += shadow(1450, FLOOR)
    b += standing(1450, FLOOR, 0.98, droop=1.0, head_drop=34)
    return svg(b)


# ---------- 2: 更衣室のベンチに座り込む ----------
def img2():
    b = ""
    for i in range(7):
        x = 980 + i * 125
        b += rect(x, 150, 120, 640, "#E6F0F2", rx=4)
        b += f'<line x1="{x + 20}" y1="220" x2="{x + 100}" y2="220" stroke="{INK}" stroke-width="4" opacity=".5"/>'
        b += f'<circle cx="{x + 95}" cy="480" r="7" fill="{INK}"/>'
    b += rect(260, 170, 300, 220, "#DDEFF3")  # 小窓
    b += '<circle cx="410" cy="280" r="160" fill="url(#glow)"/>'
    b += shape("M500,660 h700 v34 h-700 z", fill="#D9E8EA")
    b += limb([(540, 694), (540, 820)], 16, "#D9E8EA") + limb([(1160, 694), (1160, 820)], 16, "#D9E8EA")
    b += seated(760, 660, 0.82, arms="lap", head_drop=34, lean=10)
    return svg(b)


# ---------- 3: 壁のようなシフト表を見上げる ----------
def img3():
    b = rect(520, 70, 1240, 740, "#FFFFFF", rx=6)
    cols, rows = 14, 12
    for r in range(rows):
        for c in range(cols):
            x, y = 560 + c * 85, 110 + r * 56
            fill = ["#DCEEF0", "#CFE6DD", "#E8F1F6", "#FFFFFF"][(r * 3 + c * 5) % 4]
            b += f'<rect x="{x}" y="{y}" width="78" height="48" rx="4" fill="{fill}" stroke="#B9D2D8" stroke-width="2"/>'
    b += plant(200, 760, 1.0)
    b += shadow(400, FLOOR, 70)
    s = 0.55
    b += figure_no_arms(400, FLOOR, s, head_drop=-14, head_tilt=-12)
    b += limb([p(400, FLOOR, s, -68, -536), p(400, FLOOR, s, -84, -420), p(400, FLOOR, s, -80, -300)], 34 * s, SCRUB)
    b += limb([p(400, FLOOR, s, 68, -536), p(400, FLOOR, s, 84, -420), p(400, FLOOR, s, 80, -300)], 34 * s, SCRUB)
    return svg(b)


# ---------- 4: 面談室、見えない圧 ----------
def img4():
    b = window(1500, 150, 300, 380, "#E2F1F4")
    b += seated(560, 640, 0.78, top="#C9D9E3", bottom="#9FB6C4", arms="gesture", lean=6)
    b += seated(1260, 640, 0.78, arms="lap", head_drop=26, facing=-1)
    b += shape("M720,600 h420 v26 h-420 z", fill="#F2F8F8")
    b += limb([(760, 626), (760, 820)], 14, "#E3EFF1") + limb([(1100, 626), (1100, 820)], 14, "#E3EFF1")
    # 圧の矢印(淡い)
    b += (f'<path d="M820,330 h170 v-46 l110,86 l-110,86 v-46 h-170 z" fill="{TEAL}" opacity=".18" '
          f'stroke="{TEAL}" stroke-width="4" stroke-dasharray="14 10" stroke-opacity=".5"/>')
    return svg(b)


# ---------- 5: 深夜、眠れずに天井を見る ----------
def img5():
    b = window(240, 150, 300, 340, "#5E7C8C",
               '<circle cx="470" cy="230" r="24" fill="#F2F6F2" opacity=".85"/>')
    b += shape("M640,560 h900 v120 h-900 z", fill="#B9CFD6")  # ベッド
    b += shape("M600,470 h50 v350 h-50 z", fill="#A9C1C9")
    b += shape("M640,520 q0,-40 40,-40 h150 q30,0 30,40 v40 h-220 z", fill="#E8F0F2")  # 枕
    b += head(750, 505, 44)  # 仰向けの頭(顔なし)
    b += shape("M800,520 q300,-50 720,10 v40 h-720 z", fill="#D3E3E6")  # 布団
    b += limb([(640, 680), (640, 820)], 18, "#A9C1C9") + limb([(1530, 680), (1530, 820)], 18, "#A9C1C9")
    b += rect(1620, 520, 130, 300, "#9FB8C0", rx=4)
    b += f'<circle cx="1685" cy="470" r="44" fill="#F4F8F8" stroke="{INK}" stroke-width="{LINE}"/>'
    b += f'<path d="M1685,470 v-30 M1685,470 l-6,-28" stroke="{INK}" stroke-width="5" stroke-linecap="round"/>'
    b += f'<line x1="1685" y1="470" x2="1700" y2="440" stroke="{INK}" stroke-width="5" stroke-linecap="round"/>'
    return svg(b, "#9FB4BE", "#8CA4AF", "#7E97A2")


# ---------- 6: 朝、ベッドの縁に座ったまま動けない ----------
def img6():
    b = window(1240, 120, 460, 480, "#F4FBFC")
    b += '<circle cx="1470" cy="360" r="330" fill="url(#glow)"/>'
    b += shape("M260,600 h760 v110 h-760 z", fill="#D3E3E6")
    b += shape("M260,540 q0,-30 30,-30 h160 q30,0 30,30 v60 h-220 z", fill="#EEF4F5")
    b += limb([(280, 710), (280, 820)], 16, "#C2D6DB") + limb([(1000, 710), (1000, 820)], 16, "#C2D6DB")
    b += seated(860, 610, 0.72, top="#E7EEF1", bottom="#C4D6DE", arms="lap", head_drop=24)
    return svg(b)


# ---------- 7: 言いかけてやめる、背後に人影 ----------
def img7():
    b = BLUR
    for gx, op in [(260, .26), (470, .3), (680, .24)]:
        b += ghost(standing(gx, FLOOR, 0.8, top="#CFE0E8", arms="down"), op)
    s = 0.98
    x = 1250
    b += shadow(x, FLOOR)
    b += standing(x, FLOOR, s, droop=0.5, head_drop=8, arms="none")
    b += limb([p(x, FLOOR, s, -68, -536 + 9), p(x, FLOOR, s, -84, -420), p(x, FLOOR, s, -80, -300)], 34 * s, SCRUB)
    b += limb([p(x, FLOOR, s, 68, -536 + 9), p(x, FLOOR, s, 110, -480), p(x, FLOOR, s, 40, -600)], 34 * s, SCRUB)
    return svg(b)


# ---------- 8: 抱えきれない書類 ----------
def img8():
    b = plant(1700, 760, 1.0)
    x, s = 960, 1.0
    b += shadow(x, FLOOR)
    b += standing(x, FLOOR, s, droop=0.3, head_drop=4, arms="none")
    stack = ""
    colors = ["#FFFFFF", "#DCEEF0", "#CFE6DD", "#E8F1F6"]
    for i in range(9):
        y = FLOOR - 400 * s - i * 34
        dx = (i % 3 - 1) * 12
        stack += rect(x - 120 + dx, y, 240, 32, colors[i % 4], rx=4, sw=5)
    b += stack
    b += limb([p(x, FLOOR, s, -68, -536), p(x, FLOOR, s, -110, -440), p(x, FLOOR, s, -110, -380)], 34 * s, SCRUB)
    b += limb([p(x, FLOOR, s, 68, -536), p(x, FLOOR, s, 110, -440), p(x, FLOOR, s, 110, -380)], 34 * s, SCRUB)
    # 落ちかけの1枚
    b += f'<g transform="rotate(18 1170 520)">{rect(1110, 500, 140, 26, "#FFFFFF", rx=4, sw=5)}</g>'
    return svg(b)


# ---------- 9: 夜の廊下に一人残る ----------
def img9():
    b = ""
    for i, x in enumerate([200, 620, 1040, 1460]):
        b += f'<rect x="{x}" y="250" width="220" height="440" rx="6" fill="#86A0AC" stroke="{INK}" stroke-width="{LINE}"/>'
        b += f'<ellipse cx="{x + 110}" cy="60" rx="90" ry="18" fill="#F3F8E8" opacity=".55"/>'
    b += '<ellipse cx="1180" cy="60" rx="110" ry="22" fill="#FFFFF0" opacity=".9"/>'
    b += '<path d="M1080,70 L940,830 H1420 L1280,70 Z" fill="#FFFFFF" opacity=".12"/>'
    b += shape("M1230,640 h220 v20 h-220 z", fill="#DDE7EA")  # ワゴン
    b += limb([(1250, 660), (1250, 800)], 10, "#DDE7EA") + limb([(1430, 660), (1430, 800)], 10, "#DDE7EA")
    b += rect(1260, 590, 80, 50, "#F4F8F8", rx=4, sw=5)
    s, x = 0.62, 1160
    b += shadow(x, FLOOR, 70)
    b += standing(x, FLOOR, s, droop=0.6, head_drop=20, arms="none")
    b += limb([p(x, FLOOR, s, 68, -530), p(x, FLOOR, s, 140, -420), p(x, FLOOR, s, 200, -360)], 34 * s, SCRUB)
    b += limb([p(x, FLOOR, s, -68, -530), p(x, FLOOR, s, -84, -420), p(x, FLOOR, s, -80, -300)], 34 * s, SCRUB)
    return svg(b, "#8DA6B2", "#7B95A1", "#6F8995")


# ---------- 10: 真新しい制服の新人と、足元の大きな影 ----------
def img10():
    b = window(220, 140, 320, 400, "#E2F1F4")
    x = 1080
    b += f'<path d="M{x - 90},{FLOOR + 6} L{x + 760},{FLOOR - 40} L{x + 820},{FLOOR + 140} L{x - 40},{FLOOR + 40} Z" fill="{INK}" opacity=".16"/>'
    b += standing(x, FLOOR, 0.95, droop=0.8, head_drop=30, top="#FFFFFF", bottom="#F2F7F8")
    return svg(b)


# ---------- 11: また面談室の扉の前、同じ場所を回る軌跡 ----------
def img11():
    b = rect(1180, 150, 360, 680, "#E6EEF0", rx=4)
    b += f'<circle cx="1490" cy="500" r="12" fill="{INK}"/>'
    b += rect(1260, 210, 200, 60, "#FFFFFF", rx=4, sw=5)
    b += (f'<ellipse cx="860" cy="{FLOOR + 60}" rx="300" ry="54" fill="none" stroke="{TEAL}" stroke-width="6" '
          f'stroke-dasharray="20 16" opacity=".45"/>')
    b += (f'<path d="M1150,{FLOOR + 50} l-30,-16 l4,34 z" fill="{TEAL}" opacity=".45"/>')
    b += shadow(900, FLOOR)
    b += standing(900, FLOOR, 0.96, droop=1.0, head_drop=26)
    return svg(b)


# ---------- 12: 受け取られない退職届 ----------
def img12():
    b = shape("M1100,560 h560 v28 h-560 z", fill="#F2F8F8")
    b += limb([(1140, 588), (1140, 820)], 14, "#E3EFF1") + limb([(1620, 588), (1620, 820)], 14, "#E3EFF1")
    b += f'<path d="M1380,560 v-8 h140 v8" fill="none" stroke="{INK}" stroke-width="5"/>'
    x, s = 720, 0.98
    b += shadow(x, FLOOR)
    b += standing(x, FLOOR, s, droop=0.6, head_drop=14, arms="none")
    b += limb([p(x, FLOOR, s, -68, -530), p(x, FLOOR, s, -84, -420), p(x, FLOOR, s, -80, -300)], 34 * s, SCRUB)
    hx, hy = p(x, FLOOR, s, 300, -470)
    b += limb([p(x, FLOOR, s, 68, -530), p(x, FLOOR, s, 180, -490), (hx, hy)], 34 * s, SCRUB)
    b += f'<g transform="rotate(-6 {hx + 60} {hy})">{rect(hx + 10, hy - 60, 130, 84, "#FFFFFF", rx=4, sw=6)}' \
         f'<path d="M{hx + 10},{hy - 60} l65,44 l65,-44" fill="none" stroke="{INK}" stroke-width="5"/></g>'
    return svg(b)


# ---------- 13: 肩の荷をそっと下ろす、差し込む光 ----------
def img13():
    b = '<path d="M1300,0 L1900,0 L1300,830 L700,830 Z" fill="#FFF8E8" opacity=".55"/>'
    b += window(1480, 120, 300, 380, "#FFF6E6")
    x, s = 860, 1.0
    b += shadow(x, FLOOR)
    b += standing(x, FLOOR, s, droop=0.1, head_drop=-4, head_tilt=-6, arms="none")
    b += rect(x + 150, FLOOR - 150, 210, 150, "#DCEBEE", rx=10)  # 下ろした荷物
    b += f'<path d="M{x + 210},{FLOOR - 150} q45,-60 90,0" fill="none" stroke="{INK}" stroke-width="{LINE}"/>'
    b += limb([p(x, FLOOR, s, -68, -536), p(x, FLOOR, s, -84, -420), p(x, FLOOR, s, -80, -300)], 34 * s, SCRUB)
    b += limb([p(x, FLOOR, s, 68, -536), p(x, FLOOR, s, 130, -420), p(x, FLOOR, s, 200, -300)], 34 * s, SCRUB)
    return svg(b, "#FBFCF8", "#EEF5F1", "#E2EEEA")


# ---------- 14: 本人と職場のあいだに立つ第三者(橋) ----------
def img14():
    b = ""
    # 職場(建物)
    b += rect(1420, 260, 340, 570, "#E6F0F2", rx=6)
    for r in range(4):
        for c in range(3):
            b += f'<rect x="{1460 + c * 100}" y="{300 + r * 110}" width="60" height="64" rx="4" fill="#CFE6EA" stroke="{INK}" stroke-width="4"/>'
    b += f'<path d="M1550,830 v-110 h80 v110" fill="#FFFFFF" stroke="{INK}" stroke-width="{LINE}"/>'
    b += f'<path d="M1520,250 l70,-60 l70,60" fill="none" stroke="{INK}" stroke-width="{LINE}"/>'
    b += f'<path d="M1590,190 v-30 m-14,15 h28" stroke="{TEAL}" stroke-width="8" stroke-linecap="round"/>'
    # 橋(アーチ)
    b += (f'<path d="M420,560 Q960,330 1420,560" fill="none" stroke="{TEAL}" stroke-width="10" '
          f'stroke-linecap="round" opacity=".55"/>')
    b += shadow(330, FLOOR, 80)
    b += standing(330, FLOOR, 0.72, droop=0.6, head_drop=14)
    b += shadow(960, FLOOR, 90)
    b += standing(960, FLOOR, 0.8, top="#DCEBDF", bottom="#BCD4C6")
    return svg(b)


# ---------- 15: 分かれ道(一人で行く道/誰かと並ぶ道) ----------
def img15():
    b = (f'<path d="M860,1080 C880,900 900,860 960,830 C1020,860 1040,900 1060,1080 Z" fill="#EEF5F2"/>')
    b += (f'<path d="M940,830 C760,700 520,600 180,560 L180,620 C500,660 740,750 920,860 Z" fill="#EEF5F2" '
          f'stroke="{INK}" stroke-width="3" opacity=".9"/>')
    b += (f'<path d="M980,830 C1160,700 1400,600 1740,560 L1740,620 C1420,660 1180,750 1000,860 Z" fill="#EEF5F2" '
          f'stroke="{INK}" stroke-width="3" opacity=".9"/>')
    b += '<circle cx="300" cy="300" r="200" fill="url(#glow)"/><circle cx="1620" cy="300" r="200" fill="url(#glow)"/>'
    b += standing(520, 640, 0.42)
    b += standing(1360, 640, 0.42)
    b += standing(1460, 630, 0.42, top="#DCEBDF", bottom="#BCD4C6")
    b += plant(960, 760, 0.8)
    return svg(b, "#F7FBFA", "#E9F3F0", "#DCEBE6", 830)


# ---------- 16: 机の上の3つのチェックと温かいお茶 ----------
def img16():
    b = shape("M260,640 h1400 v40 h-1400 z", fill="#EEF4F5")
    b += limb([(320, 680), (320, 830)], 18, "#E3EFF1") + limb([(1600, 680), (1600, 830)], 18, "#E3EFF1")
    for i in range(3):
        x = 520 + i * 260
        b += rect(x, 470, 200, 150, "#FFFFFF", rx=14)
        b += f'<path d="M{x + 55},{545} l35,35 l60,-70" fill="none" stroke="{TEAL}" stroke-width="14" stroke-linecap="round" stroke-linejoin="round"/>'
    b += shape("M1340,520 h150 v100 q0,30 -30,30 h-90 q-30,0 -30,-30 z", fill="#F7FBFB")
    b += f'<path d="M1490,545 q50,5 40,40 q-8,22 -40,20" fill="none" stroke="{INK}" stroke-width="{LINE}"/>'
    b += f'<path d="M1300,650 h230" stroke="{INK}" stroke-width="{LINE}" stroke-linecap="round"/>'
    for dx in (0, 40, 80):
        b += f'<path d="M{1375 + dx},500 q-16,-30 0,-60 q16,-30 0,-60" fill="none" stroke="#B9D2D8" stroke-width="6" stroke-linecap="round"/>'
    b += plant(180, 640, 0.8)
    return svg(b, "#FBFCF8", "#EEF5F2", "#E2EEEA")


# ---------- 17: 朝の窓辺で外を見る ----------
def img17():
    b = window(980, 110, 560, 600, "#F2FAFA",
               '<path d="M980,560 q140,-110 280,-20 q140,-90 280,0 v170 h-560 z" fill="#CFE6DD"/>')
    b += '<circle cx="1260" cy="380" r="420" fill="url(#glow)" opacity=".7"/>'
    b += plant(1700, 760, 1.0)
    b += shadow(760, FLOOR)
    b += standing(760, FLOOR, 1.0, droop=0.0, head_drop=-6, head_tilt=-8, top="#F3F8F8", bottom="#D4E4E6")
    return svg(b, "#FBFCF8", "#EEF6F3", "#E2EEEA")


# ---------- 18: エンドカード(文字は build.py で重ねる) ----------
def img18():
    b = f'<circle cx="960" cy="330" r="260" fill="url(#glow)"/>'
    b += standing(960, 560, 0.5, top="#F3F8F8", bottom="#D4E4E6")
    return svg(b, "#FFFFFF", "#F2F8F8", "#EDF5F4", 560)


if __name__ == "__main__":
    fns = [img1, img2, img3, img4, img5, img6, img7, img8, img9, img10, img11, img12, img13, img14, img15, img16, img17, img18]
    for i, fn in enumerate(fns, 1):
        Path(f"img{i:02d}.svg").write_text(fn())

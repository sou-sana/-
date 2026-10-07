# 差し替え集(episodes/*)の画像1〜4を SVG で描く。make_images.py と同じ画風・構図ルール
# (輪郭線のみ・顔なし・白/青/緑の淡い配色・文字なし・主役は字幕帯 y≈1300 より上)。
# usage: python3 episode_images.py [slug ...]   → episodes/<slug>/img1〜4.svg(続けて ./render.sh episodes/<slug>)
import math
import re
import sys
from pathlib import Path

from make_images import INK, LINE, SCRUB, SKIN, TEAL, bg_room, head, limb, plant, seated, shape, standing, svg, window

MINT = "#A8D2C6"
PALE = "#E9F1F3"
CARD = "#FFFFFF"
SOFT = "#B5D3DA"
SUNC = "#F6E7B0"
MOONC = "#EDEBC8"
CORAL = "#E9A28F"
TEAR = "#BFE3F0"


# ---------- 部品 ----------
def ln(x1, y1, x2, y2, w=LINE, c=INK, extra=""):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{c}" stroke-width="{w}" stroke-linecap="round" {extra}/>'


def circ(x, y, r, fill, sw=LINE, stroke=INK, extra=""):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>'


def box(x, y, w, h, fill, rx=8, sw=LINE, extra=""):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" '
            f'stroke="{INK}" stroke-width="{sw}" {extra}/>')


def glow(gid, x, y, r, color, op=0.55):
    return (f'<defs><radialGradient id="{gid}"><stop offset="0" stop-color="{color}" stop-opacity="{op}"/>'
            f'<stop offset="1" stop-color="{color}" stop-opacity="0"/></radialGradient></defs>'
            f'<circle cx="{x}" cy="{y}" r="{r}" fill="url(#{gid})"/>')


def tear(x, y, s=1.0):
    return (f'<path d="M{x},{y - 28 * s} C{x + 14 * s},{y - 6 * s} {x + 17 * s},{y + 12 * s} {x},{y + 17 * s} '
            f'C{x - 17 * s},{y + 12 * s} {x - 14 * s},{y - 6 * s} {x},{y - 28 * s} Z" fill="{TEAR}" '
            f'stroke="{INK}" stroke-width="{LINE * 0.6}"/>')


def moon(x, y, r, fill=MOONC, sw=LINE):
    return (f'<path d="M{x},{y - r} A{r},{r} 0 1 0 {x},{y + r} A{r * 0.62},{r} 0 1 1 {x},{y - r} Z" '
            f'fill="{fill}" stroke="{INK}" stroke-width="{sw}" stroke-linejoin="round"/>')


def sun(x, y, r, fill=SUNC, sw=LINE):
    rays = "".join(ln(x + math.cos(a) * r * 1.35, y + math.sin(a) * r * 1.35,
                      x + math.cos(a) * r * 1.7, y + math.sin(a) * r * 1.7, sw)
                   for a in [k * math.pi / 4 for k in range(8)])
    return rays + circ(x, y, r, fill, sw)


def coin(x, y, r, sw=LINE):
    return circ(x, y, r, "#F3E3A6", sw) + circ(x, y, r * 0.62, "none", sw * 0.6)


def person_icon(x, y, s=1.0, fill=SCRUB):
    """頭+肩だけの小さな人物アイコン(足元中心 x,y)。"""
    return (shape(f"M{x - 46 * s},{y} q0,{-78 * s} {46 * s},{-78 * s} q{46 * s},0 {46 * s},{78 * s} z", fill=fill, sw=LINE * 0.8)
            + circ(x, y - 108 * s, 30 * s, SKIN, LINE * 0.8))


def pair(x, y, s=1.0, conflict=False):
    out = person_icon(x - 52 * s, y, s, "#DCEBDF") + person_icon(x + 52 * s, y, s, "#E6EFF6")
    if conflict:  # 間にギザギザ
        out += (f'<path d="M{x - 14 * s},{y - 150 * s} l{14 * s},{18 * s} l{-12 * s},{16 * s} l{14 * s},{18 * s} '
                f'l{-12 * s},{16 * s}" fill="none" stroke="{CORAL}" stroke-width="{LINE}" stroke-linecap="round"/>')
    return out


def clock(x, y, r, sw=LINE):
    ticks = "".join(ln(x + math.cos(a) * r * 0.78, y + math.sin(a) * r * 0.78,
                       x + math.cos(a) * r * 0.9, y + math.sin(a) * r * 0.9, sw * 0.6)
                    for a in [k * math.pi / 2 for k in range(4)])
    return (circ(x, y, r, CARD, sw) + ticks + ln(x, y, x, y - r * 0.6, sw) + ln(x, y, x + r * 0.45, y + r * 0.1, sw)
            + circ(x, y, sw * 0.7, INK, 0))


def magnifier(x, y, r, angle=45, sw=LINE, lens="#EAF6F8", inner=""):
    a = math.radians(angle)
    hx1, hy1 = x + math.cos(a) * r, y + math.sin(a) * r
    hx2, hy2 = x + math.cos(a) * r * 2.1, y + math.sin(a) * r * 2.1
    return (limb([(hx1, hy1), (hx2, hy2)], r * 0.22, "#9FC3C2") + circ(x, y, r, lens, sw) + inner
            + circ(x, y, r, "none", sw))


def job_card(x, y, w, h, icon="", fill=CARD, sw=LINE, rot=0):
    """求人票カード(写真枠+罫線)。icon は右上に置く追加SVG。"""
    s = w / 200
    body = (box(x, y, w, h, fill, 10 * s, sw)
            + box(x + 20 * s, y + 22 * s, 56 * s, 56 * s, "#DCEBEA", 6 * s, sw * 0.7)
            + ln(x + 92 * s, y + 36 * s, x + w - 24 * s, y + 36 * s, 9 * s, SOFT)
            + ln(x + 92 * s, y + 64 * s, x + w - 60 * s, y + 64 * s, 9 * s, SOFT)
            + "".join(ln(x + 22 * s, y + (108 + 30 * k) * s, x + w - (24 + 30 * (k % 2)) * s, y + (108 + 30 * k) * s,
                         9 * s, SOFT) for k in range(int((h / s - 120) // 30))))
    if rot:
        body = f'<g transform="rotate({rot} {x + w / 2} {y + h / 2})">{body}{icon}</g>'
        return body
    return body + icon


def hospital(x, y, s=1.0, fill="#EEF4F5"):
    """病院の建物(底辺中央 x,y)。"""
    w, h = 220 * s, 200 * s
    out = shape(f"M{x - w / 2},{y} v{-h} h{w} v{h} z", fill=fill, sw=LINE * min(1, s + 0.3))
    out += shape(f"M{x - w * 0.22},{y - h} v{-60 * s} h{w * 0.44} v{60 * s} z", fill=fill, sw=LINE * min(1, s + 0.3))
    out += f'<path d="M{x - 8 * s},{y - h - 48 * s} h{16 * s} v{12 * s} h{12 * s} v{16 * s} h{-12 * s} v{12 * s} h{-16 * s} v{-12 * s} h{-12 * s} v{-16 * s} h{12 * s} z" fill="{CORAL}"/>'
    for row in range(2):
        for col in range(3):
            out += f'<rect x="{x - w / 2 + (24 + col * 66) * s}" y="{y - h + (26 + row * 70) * s}" width="{40 * s}" height="{40 * s}" rx="{4 * s}" fill="#CFE3EA"/>'
    out += f'<rect x="{x - 22 * s}" y="{y - 52 * s}" width="{44 * s}" height="{52 * s}" fill="#CFE3EA"/>'
    return out


def battery(x, y, level=0.18, op=0.8):
    return (f'<rect x="{x - 52}" y="{y - 26}" width="96" height="52" rx="9" fill="none" stroke="{TEAL}" stroke-width="7" opacity="{op}"/>'
            f'<rect x="{x + 46}" y="{y - 11}" width="10" height="22" rx="3" fill="{TEAL}" opacity="{op}"/>'
            f'<rect x="{x - 42}" y="{y - 16}" width="{max(10, 84 * level)}" height="32" rx="4" fill="{CORAL}" opacity=".85"/>')


def heart(x, y, s=1.0, fill=CORAL, op=1.0, sw=LINE):
    return (f'<path d="M{x},{y + 34 * s} C{x - 60 * s},{y - 4 * s} {x - 48 * s},{y - 54 * s} {x},{y - 26 * s} '
            f'C{x + 48 * s},{y - 54 * s} {x + 60 * s},{y - 4 * s} {x},{y + 34 * s} Z" fill="{fill}" opacity="{op}" '
            f'stroke="{INK}" stroke-width="{sw}" stroke-linejoin="round"/>')


def check(x, y, s=1.0, c=TEAL):
    return (f'<path d="M{x - 14 * s},{y} l{10 * s},{12 * s} l{20 * s},{-24 * s}" fill="none" stroke="{c}" '
            f'stroke-width="{LINE * s}" stroke-linecap="round" stroke-linejoin="round"/>')


def lying(fx, fy, s=1.0, **kw):
    """横たわる姿(standing を -90°回転。頭が左、足元 fx,fy)。"""
    return f'<g transform="rotate(-90 {fx} {fy})">{standing(fx, fy, s, **kw)}</g>'


def table(x1, x2, top, foot, fill="#EEF4F5"):
    return (limb([(x1 + 40, top + 20), (x1 + 40, foot)], 14, fill) + limb([(x2 - 40, top + 20), (x2 - 40, foot)], 14, fill)
            + shape(f"M{x1},{top} h{x2 - x1} v26 h{x1 - x2} z", fill=fill))


def sofa(x, y, w=780, fill="#9FC3C2", seat="#B4D3D1"):
    """ソファ(左端 x、座面上端 y)。"""
    return (shape(f"M{x + 40},{y - 140} q0,-60 60,-60 h{w - 120} q60,0 60,60 v200 h{-(w - 40)} z", fill=fill)
            + shape(f"M{x},{y - 60} q0,-40 40,-40 h40 v220 h-80 z", fill=fill)
            + shape(f"M{x + w - 40},{y - 100} h40 q40,0 40,40 v220 h-80 z", fill=fill)
            + shape(f"M{x + 80},{y} h{w - 120} v80 h{-(w - 120)} z", fill=seat)
            + limb([(x + 110, y + 80), (x + 110, y + 130)], 16, "#88A9AE")
            + limb([(x + w - 70, y + 80), (x + w - 70, y + 130)], 16, "#88A9AE"))


def door(x, y, w, h, fill="#E6EEF0", icon="", ajar=False):
    out = box(x, y, w, h, fill, 6)
    out += circ(x + w - 26, y + h * 0.55, 9, INK, 0)
    if ajar:
        out = (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#FFF8E6" stroke="{INK}" stroke-width="{LINE}"/>'
               + shape(f"M{x},{y} l{-w * 0.35},{-24} v{h + 48} l{w * 0.35},{-24} z", fill=fill))
    return out + icon


def nurse_hold(x, fy, s, target_r, target_l=None, top=SCRUB, **kw):
    """腕で物を持つ立ち姿。target_* は手の位置(胴の手前に描く)。"""
    def p(dx, dy):
        return (x + dx * s, fy + dy * s)
    out = standing(x, fy, s, top=top, arms="none", **kw)
    if target_r:
        out += limb([p(66, -530), p(110, -420), target_r], 34 * s, top)
    else:
        out = limb([p(68, -536), p(80, -420), p(80, -300)], 34 * s, top) + out
    if target_l:
        out += limb([p(-66, -530), p(-110, -420), target_l], 34 * s, top)
    else:
        out = limb([p(-68, -536), p(-80, -420), p(-80, -300)], 34 * s, top) + out
    return out


def ground_shadow(x, y, rx=110):
    return f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="16" fill="{INK}" opacity=".08"/>'


def sparkle(x, y, r, c="#FFFFFF", op=1.0):
    return (f'<path d="M{x},{y - r} Q{x + r * 0.18},{y - r * 0.18} {x + r},{y} Q{x + r * 0.18},{y + r * 0.18} {x},{y + r} '
            f'Q{x - r * 0.18},{y + r * 0.18} {x - r},{y} Q{x - r * 0.18},{y - r * 0.18} {x},{y - r} Z" fill="{c}" opacity="{op}" '
            f'stroke="{INK}" stroke-width="{LINE * 0.6}"/>')


def calm_room(top="#F6FBFB", bottom="#E6F2F1", floor="#DCEBEA"):
    return bg_room(top, bottom, floor, 1300)


# =====================================================================
# 感情3 休みの日に、何もする気が起きなかった
# =====================================================================
def k3_1():  # 白紙の手帳を見下ろす
    bg = calm_room()
    b = window(130, 280, 300, 400, "#E2F1F4", '<path d="M130,560 q80,-70 150,-10 q70,-60 150,0 v120 h-300 z" fill="#CFE6DD"/>')
    b += plant(900, 760, 0.8)
    b += box(760, 300, 180, 200, CARD) + ln(790, 350, 910, 350, 9, SOFT) + ln(790, 390, 880, 390, 9, SOFT)
    b += table(520, 1000, 900, 1296)
    # 開いた手帳(白紙の日付マス)
    pts = "M600,900 L650,720 L790,740 L770,900 Z"
    pts2 = "M770,900 L790,740 L930,720 L960,900 Z"
    b += shape(pts, fill=CARD) + shape(pts2, fill=CARD)
    for k in range(3):
        y = 770 + k * 40
        b += ln(650 - k * 8, y, 770 - k * 4, y + 6, 4, SOFT) + ln(795 + k * 4, y + 6, 925 + k * 8, y, 4, SOFT)
    b += ln(705, 732, 690, 892, 4, SOFT) + ln(870, 732, 885, 892, 4, SOFT)
    b += shape("M300,1040 h200 v24 h-200 z", fill="#D7E5E8") + limb([(320, 1064), (320, 1296)], 12, "#D7E5E8") + limb([(480, 1064), (480, 1296)], 12, "#D7E5E8")
    b += seated(340, 1040, 1.0, top="#EEF3F4", bottom="#C4D4DF", arms="lap", head_drop=26, head_tilt=10)
    return svg(b, bg)


def k3_2():  # 部屋の隅の趣味の道具、背を向ける
    bg = calm_room("#F2F7F7", "#E3EEEE", "#D8E6E6")
    # 棚
    b = shape("M640,520 h340 v24 h-340 z", fill="#E6EEF0") + shape("M640,760 h340 v24 h-340 z", fill="#E6EEF0")
    # 本(棚上段)
    for k, (w, h, c) in enumerate([(34, 150, "#CFE3EA"), (30, 130, "#DCEBDF"), (38, 160, "#E6EFF6"), (30, 120, "#CFE6DD")]):
        x = 670 + sum([34, 30, 38, 30][:k]) + k * 6
        b += box(x, 520 - h, w, h, c, 4, LINE * 0.7)
    # カメラ(棚上段)
    b += box(860, 440, 100, 70, "#E9F1F3", 10) + circ(910, 476, 22, "#CFE3EA", LINE * 0.8) + box(872, 426, 30, 16, "#E9F1F3", 4, LINE * 0.7)
    # 毛糸玉と編み棒(棚下段)
    b += circ(720, 712, 46, "#F1D9CF") + f'<path d="M686,690 q34,22 70,-6 M680,716 q40,24 82,-4 M690,742 q30,14 60,-2" fill="none" stroke="{INK}" stroke-width="4" opacity=".6"/>'
    b += ln(770, 650, 830, 740, 6) + ln(790, 646, 818, 744, 6)
    # ギター(床に立てかけ)
    b += f'<g transform="rotate(-12 860 1050)">' + limb([(860, 760), (860, 960)], 26, "#E6D7C4") + \
         box(836, 712, 48, 60, "#E6D7C4", 8, LINE * 0.8) + \
         f'<path d="M860,950 c-90,0 -100,70 -70,110 c-50,40 -40,170 70,170 c110,0 120,-130 70,-170 c30,-40 20,-110 -70,-110 z" fill="#E6D7C4" stroke="{INK}" stroke-width="{LINE}"/>' + \
         circ(860, 1070, 22, "#C9B49B", LINE * 0.7) + '</g>'
    # ほこり(小さな点)とクモの巣
    dust = "".join(f'<circle cx="{x}" cy="{y}" r="4" fill="#9FB3B9" opacity=".55"/>' for x, y in
                   [(700, 420), (760, 395), (905, 418), (930, 405), (690, 620), (850, 640), (900, 900), (820, 1010), (930, 1120)])
    b += dust + f'<path d="M980,300 q-40,30 -90,10 M980,330 q-30,30 -70,30 M980,300 v120" fill="none" stroke="#9FB3B9" stroke-width="3" opacity=".7"/>'
    b += ground_shadow(330, 1296)
    b += standing(330, 1290, 1.06, droop=0.8, head_drop=24, head_tilt=-14, top="#EEF3F4", bottom="#C4D4DF")
    return svg(b, bg)


def k3_3():  # ソファで横になったまま、日差しが移っていく
    bg = calm_room("#EEF4F4", "#E0ECEC", "#D3E3E3")
    b = window(620, 240, 340, 420, "#E2F1F4", sun(860, 340, 34))
    # 移ろう日差し(時間の経過)
    for k, op in enumerate([0.16, 0.28, 0.42]):
        x = 220 + k * 170
        b += f'<path d="M{x},700 l140,0 l120,560 l-140,0 z" fill="#FFF6D8" opacity="{op}"/>'
    b += clock(260, 360, 70)
    b += sofa(140, 1040, 800)
    b += lying(820, 970, 0.95, droop=0.0, top="#EEF3F4", bottom="#C4D4DF", head_tilt=0)
    b += shape("M200,960 q-10,-60 60,-60 h70 q40,0 40,40 v40 z", fill="#E6EFF6")  # クッション
    return svg(b, bg)


def k3_4():  # 胸の電池から細い糸が遠くの病院へ
    bg = calm_room()
    b = hospital(860, 520, 0.7)
    b += f'<path d="M560,780 C700,760 760,640 820,560" fill="none" stroke="{TEAL}" stroke-width="4" stroke-dasharray="4 14" stroke-linecap="round" opacity=".8"/>'
    b += plant(180, 1180, 0.9)
    b += ground_shadow(560, 1296, 120)
    b += standing(560, 1290, 1.12, droop=0.7, top="#F3F8F8", bottom="#D4E4E6", head_drop=10)
    b += glow("bglow", 560, 780, 120, "#9FD6CF")
    b += battery(560, 780, 0.1)
    return svg(b, bg)


# =====================================================================
# 感情4 些細なことで、涙が出るようになった
# =====================================================================
def train_bg(tone="#EAF3F5"):
    bg = bg_room("#F7FAF6", tone, "#C9D9DD", 1300)
    # 車窓(朝の空)とつり革
    b = '<defs><linearGradient id="am" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#D6EAF2"/><stop offset="1" stop-color="#F6EEDD"/></linearGradient></defs>'
    for x in (90, 420, 750):
        b += box(x, 420, 260, 300, "url(#am)", 18)
    b += shape("M40,240 h1000 v20 h-1000 z", fill="#D7E5E8")
    for x in (190, 400, 610, 820):
        b += ln(x, 260, x, 330, 5) + circ(x, 360, 28, "none", 7)
    b += shape("M40,1060 h1000 v40 h-1000 z", fill="#B9CDD3")  # 座席の背
    return bg, b


def k4_1():
    bg, b = train_bg()
    # まわりの乗客(うすい輪郭)
    b += f'<g opacity=".32">{standing(170, 1290, 0.9, top="#FFFFFF", bottom="#FFFFFF")}{standing(860, 1290, 0.92, top="#FFFFFF", bottom="#FFFFFF")}</g>'
    # 主人公: 右手でつり革
    x, fy, s = 520, 1290, 1.04
    b += limb([(x + 68 * s, fy - 540 * s), (x + 100 * s, fy - 680 * s), (610, 384)], 34 * s, "#E8EEF3")
    b += standing(x, fy, s, droop=0.4, top="#E8EEF3", bottom="#C4D4DF", head_drop=14, arms="none")
    b += limb([(x - 68 * s, fy - 536 * s), (x - 80 * s, fy - 420 * s), (x - 80 * s, fy - 300 * s)], 34 * s, "#E8EEF3")
    b += tear(x + 58, fy - 610 * s, 1.0)
    return svg(b, bg)


def bed(x, y, w=520, blanket="#DCEBF0", patient=True):
    """ベッド(左端 x、マットレス上端 y)。"""
    out = shape(f"M{x},{y - 120} v{330} M{x + w},{y - 40} v{250}", fill="none")
    out += limb([(x + 20, y - 120), (x + 20, y + 210)], 16, "#E6EEF0") + limb([(x + w - 20, y - 40), (x + w - 20, y + 210)], 16, "#E6EEF0")
    out += shape(f"M{x},{y} h{w} v60 h{-w} z", fill="#F3F8F8")
    out += shape(f"M{x + 30},{y - 54} q0,-24 24,-24 h110 q24,0 24,24 v54 h-158 z", fill=CARD)  # 枕
    if patient:
        out += head(x + 120, y - 66, 40)
        out += shape(f"M{x + 150},{y} q40,-90 160,-80 q160,0 {w - 330},40 v40 z", fill=blanket)
    return out


def k4_2():
    bg = calm_room("#F4FAFA", "#E4F1F1", "#D6E9E8")
    b = window(560, 260, 360, 380, "#DCEFF4", '<path d="M560,540 q100,-80 180,-10 q90,-60 180,10 v100 h-360 z" fill="#CFE6DD"/>')
    b += f'<path d="M520,240 q30,220 0,440 h30 q20,-220 0,-440 z" fill="#FFFFFF" stroke="{INK}" stroke-width="{LINE * 0.8}"/>'
    b += bed(460, 980, 520)
    x, fy, s = 290, 1290, 1.06
    b += ground_shadow(x, 1296)
    b += standing(x, fy, s, droop=0.3, head_drop=10, head_tilt=8, arms="none")
    b += limb([(x - 68 * s, fy - 536 * s), (x - 80 * s, fy - 420 * s), (x - 80 * s, fy - 300 * s)], 34 * s)
    b += limb([(x + 66 * s, fy - 530 * s), (x + 70 * s, fy - 440 * s), (x + 12 * s, fy - 520 * s)], 34 * s)  # 胸元に手
    return svg(b, bg)


def k4_3():
    bg = bg_room("#5E7387", "#4D6274", "#44586A", 1300)
    b = window(620, 250, 320, 380, "#33495E", moon(780, 390, 40, "#F2F1DA") +
               '<circle cx="680" cy="320" r="4" fill="#FFFFFF"/><circle cx="880" cy="480" r="3" fill="#FFFFFF"/>')
    b += glow("mglow", 560, 900, 360, "#BFD6E6", 0.18)
    x, y, w = 140, 1000, 800
    b += limb([(x + 20, y - 220), (x + 20, y + 230)], 18, "#90A7B6") + limb([(x + w - 20, y - 60), (x + w - 20, y + 230)], 18, "#90A7B6")
    b += shape(f"M{x},{y} h{w} v70 h{-w} z", fill="#A9BFCB")
    b += shape(f"M{x + 40},{y - 64} q0,-26 26,-26 h150 q26,0 26,26 v64 h-202 z", fill="#C8D8E0")
    b += lying(x + w - 60, y - 70, 0.92, top="#C8D8E0", bottom="#B3C6D1")
    b += shape(f"M{x + 230},{y + 10} q20,-140 220,-140 q300,-10 {w - 470},60 v80 z", fill="#9CB4C3")  # 掛け布団
    b += tear(x + 120, y - 150, 0.9)
    return svg(b, bg)


def k4_4():
    bg = calm_room()
    b = window(130, 300, 300, 460, "#E2F1F4", '<path d="M130,640 q80,-70 150,-10 q70,-60 150,0 v120 h-300 z" fill="#CFE6DD"/>')
    b += plant(900, 1180, 1.0)
    b += ground_shadow(560, 1296, 120)
    b += standing(560, 1290, 1.12, droop=0.5, top="#F3F8F8", bottom="#D4E4E6", head_drop=8)
    b += glow("cglow", 560, 770, 130, "#9FD6CF")
    # 胸元のコップ(あふれる水)
    cx, cy = 560, 790
    b += f'<path d="M{cx - 50},{cy - 50} q-6,28 -22,40 q-10,10 -6,26" fill="none" stroke="{TEAR}" stroke-width="10" stroke-linecap="round"/>'
    b += f'<path d="M{cx + 50},{cy - 50} q8,30 22,46 q10,12 4,30" fill="none" stroke="{TEAR}" stroke-width="10" stroke-linecap="round"/>'
    b += shape(f"M{cx - 56},{cy - 60} h112 l-14,120 h-84 z", fill="#EEF8FA")
    b += f'<path d="M{cx - 56},{cy - 60} q56,-26 112,0 z" fill="{TEAR}" stroke="{INK}" stroke-width="{LINE * 0.8}"/>'
    b += tear(cx - 86, cy + 20, 0.7) + tear(cx + 92, cy + 40, 0.6)
    return svg(b, bg)


# =====================================================================
# 感情5 好きだったものが、味気なく感じるようになった
# =====================================================================
def k5_1():
    bg = calm_room("#F4F8F8", "#E5EFEF", "#D9E7E7")
    b = window(620, 260, 320, 380, "#E2F1F4", '<path d="M620,540 q90,-70 160,-10 q80,-50 160,10 v100 h-320 z" fill="#CFE6DD"/>')
    b += shape("M300,1040 h200 v24 h-200 z", fill="#D7E5E8") + limb([(320, 1064), (320, 1296)], 12, "#D7E5E8") + limb([(480, 1064), (480, 1296)], 12, "#D7E5E8")
    b += seated(340, 1040, 1.0, top="#EEF3F4", bottom="#C4D4DF", arms="none", head_drop=20)
    b += table(500, 1000, 900, 1296)
    # 食器(輪郭だけ)
    b += f'<ellipse cx="760" cy="890" rx="140" ry="26" fill="{CARD}" stroke="{INK}" stroke-width="{LINE}"/>'
    b += f'<ellipse cx="760" cy="880" rx="80" ry="14" fill="#F1E8D8" stroke="{INK}" stroke-width="{LINE * 0.6}"/>'
    b += shape("M880,830 h80 l-10,70 h-60 z", fill="#E6F0F2")
    b += shape("M600,860 q0,40 50,40 q50,0 50,-40 z", fill="#EAF2F2")
    # 腕と箸(機械的に)
    b += limb([(400, 760), (470, 830), (600, 840)], 34, "#EEF3F4")
    b += ln(600, 846, 700, 800, 5) + ln(600, 836, 702, 788, 5)
    return svg(b, bg)


def k5_2():
    bg = calm_room("#F7FAF9", "#EAF1F0", "#DDE8E7")
    b = glow("wglow", 540, 560, 420, "#FFF6D8", 0.6)
    b += window(300, 220, 480, 560, "#EAF6FA", sun(660, 340, 40) + '<path d="M300,680 q120,-90 240,-20 q120,-70 240,10 v110 h-480 z" fill="#CFE6DD"/>')
    b += f'<path d="M260,200 q30,320 0,640 h36 q20,-320 0,-640 z" fill="#FFFFFF" stroke="{INK}" stroke-width="{LINE * 0.8}"/>'
    b += f'<path d="M820,200 q-30,320 0,640 h-36 q-20,-320 0,-640 z" fill="#FFFFFF" stroke="{INK}" stroke-width="{LINE * 0.8}"/>'
    b += f'<g opacity=".55">{plant(160, 1180, 0.9)}{box(870, 1000, 120, 180, "#E6EEF0")}</g>'
    b += ground_shadow(540, 1296, 120)
    b += standing(540, 1290, 1.1, droop=0.6, top="#EEF3F4", bottom="#C4D4DF", head_drop=4)
    return svg(b, bg)


def k5_3():
    bg = bg_room("#F2F7F8", "#E6EFF1", "#D0DEE1", 1300)
    b = ""
    shops = [(60, "#F3C9B8", "#CFE6DD"), (380, "#BFD9EE", "#F6E7B0"), (700, "#CFE6C9", "#F3C9B8")]
    for x, awn, item in shops:
        b += box(x, 380, 300, 700, "#F4F8F8", 6)
        b += "".join(shape(f"M{x + k * 50},{380} h50 l-6,70 q-19,18 -38,0 z", fill=awn if k % 2 == 0 else "#FFFFFF", sw=LINE * 0.7) for k in range(6))
        b += box(x + 30, 500, 240, 300, "#EAF6FA", 6)
        b += circ(x + 100, 700, 44, item) + box(x + 160, 620, 80, 120, awn, 8) + sparkle(x + 210, 560, 18)
    # 人物のまわりだけ色が抜ける
    b += ('<defs><radialGradient id="fade"><stop offset="0" stop-color="#DCE3E5" stop-opacity=".85"/>'
          '<stop offset=".6" stop-color="#DCE3E5" stop-opacity=".6"/><stop offset="1" stop-color="#DCE3E5" stop-opacity="0"/></radialGradient></defs>')
    b += '<ellipse cx="530" cy="760" rx="420" ry="620" fill="url(#fade)"/>'
    b += ground_shadow(530, 1296)
    x, fy, s = 530, 1290, 1.06
    # 歩く脚
    b += standing(x, fy, s, droop=0.5, top="#EEF3F4", bottom="#C4D4DF", head_drop=12, head_tilt=6)
    return svg(b, bg)


def k5_4():
    bg = calm_room("#F4F9F9", "#E4EFEF", "#D9E8E8")
    b = window(700, 300, 260, 420, "#E2F1F4", '<path d="M700,600 q70,-60 130,-10 q60,-50 130,0 v120 h-260 z" fill="#CFE6DD"/>')
    b += plant(180, 1180, 0.9)
    b += ground_shadow(540, 1296, 120)
    b += standing(540, 1290, 1.12, droop=0.6, top="#F3F8F8", bottom="#D4E4E6", head_drop=8)
    b += glow("hglow", 540, 780, 110, "#F3C9B8", 0.4)
    b += heart(540, 780, 1.0, "#F1C7BA", 0.75, LINE * 0.8)
    return svg(b, bg)


# =====================================================================
# 転職1 転職サイトは"選び方"で9割決まる
# =====================================================================
def t1_1():
    bg = calm_room("#F4F9F9", "#E6F1F1", "#D8E8E8")
    b = shape("M70,180 h940 v820 h-940 z", fill="#E3EEF0")
    for r in range(4):
        for c in range(5):
            b += job_card(100 + c * 180, 210 + r * 196, 160, 172, sw=LINE * 0.7)
    b += ground_shadow(540, 1296, 120)
    b += standing(540, 1290, 1.02, droop=0.7, head_drop=-10, head_tilt=-14)
    return svg(b, bg)


def t1_2():
    bg = calm_room()
    b = ln(540, 300, 540, 1260, 4, SOFT, 'stroke-dasharray="10 16"')
    # 左: 散らばるカードに囲まれて迷う
    for (x, y, r) in [(80, 380, -18), (290, 300, 12), (60, 640, 10), (340, 560, -8), (180, 470, 22)]:
        b += job_card(x, y, 130, 150, sw=LINE * 0.6, rot=r)
    b += ground_shadow(270, 1296, 100)
    b += standing(270, 1290, 0.92, droop=0.9, head_drop=24, head_tilt=-16)
    # 右: チェックリスト1枚を持って落ち着いている
    x, fy, s = 800, 1290, 0.95
    b += ground_shadow(x, 1296, 100)
    b += nurse_hold(x, fy, s, (x + 10, fy - 430 * s), (x - 30, fy - 430 * s), top="#DCEBDF")
    cx, cy = x - 70, fy - 560 * s
    b += box(cx, cy, 140, 180, CARD, 8) + box(cx + 46, cy - 14, 48, 22, "#DCEBEA", 5, LINE * 0.7)
    for k in range(3):
        b += check(cx + 34, cy + 50 + k * 44, 0.8) + ln(cx + 60, cy + 50 + k * 44, cx + 118, cy + 50 + k * 44, 7, SOFT)
    return svg(b, bg)


def t1_3():
    bg = calm_room("#F6FBFB", "#E8F3F2", "#DCEBEA")
    b = ""
    icons = [(220, moon(220, 560, 62)), (540, coin(540, 560, 64)), (860, pair(860, 620, 0.8))]
    for k, (x, ic) in enumerate(icons):
        chosen = k == 1
        b += circ(x, 560, 130, "#FFFFFF" if chosen else "#F1F6F7", LINE * (1.2 if chosen else 0.8),
                  TEAL if chosen else INK, 'opacity="1"' if chosen else 'opacity=".9"')
        if chosen:
            b = glow("pick", x, 560, 220, "#9FD6CF", 0.5) + b
        b += ic
    # 下から伸びる手(指さし)
    b += limb([(820, 1330), (660, 930)], 84, SCRUB)  # 袖
    b += limb([(586, 800), (566, 724)], 30, SKIN)  # 人さし指
    b += circ(626, 856, 58, SKIN)  # にぎった手
    b += limb([(586, 860), (566, 834)], 28, SKIN)  # 親指
    return svg(b, bg)


def t1_4():
    bg = calm_room()
    # 求人票の裏に隠れた現場の小さな景色
    sx, sy, sw_, sh = 340, 600, 520, 600
    b = box(sx, sy, sw_, sh, "#EAF5F4", 12)
    b += glow("rglow", sx + sw_ / 2, sy + sh / 2, 300, "#FFF6D8", 0.5)
    b += f'<g transform="translate({sx + 40},{sy + 80}) scale(0.42)">' + bed(0, 900, 520, patient=True) + \
         standing(800, 1150, 1.0, top="#DCEBDF", bottom="#C2D8CC") + standing(1000, 1150, 0.95) + '</g>'
    # めくり上げたカード(上端を軸に手前へ)
    b += f'<g transform="translate(0,0)">' + \
         f'<path d="M{sx},{sy} h{sw_} l40,-170 h{-sw_ - 80} z" fill="#FFFFFF" stroke="{INK}" stroke-width="{LINE}" stroke-linejoin="round"/>' + \
         ln(sx + 40, sy - 70, sx + sw_ - 40, sy - 70, 9, SOFT) + ln(sx + 40, sy - 120, sx + 300, sy - 120, 9, SOFT) + '</g>'
    x, fy, s = 200, 1290, 1.0
    b += ground_shadow(x, 1296, 100)
    b += nurse_hold(x, fy, s, (sx - 20, sy - 120), None)
    return svg(b, bg)


# =====================================================================
# 転職2 "夜勤なし"を本当に叶える看護師がやっていること
# =====================================================================
def t2_1():
    bg = calm_room("#F7FBF9", "#EAF3F1", "#DCEBEA")
    b = window(640, 260, 320, 400, "#E8F5F8", sun(800, 400, 44))
    b += plant(170, 1180, 0.9)
    x, fy, s = 470, 1290, 1.08
    b += ground_shadow(x, 1296)
    b += nurse_hold(x, fy, s, (x + 40, fy - 470 * s), (x - 10, fy - 470 * s), head_drop=-6)
    cx, cy = x - 90, fy - 560 * s
    b += job_card(cx, cy, 190, 210) + sun(cx + 150, cy + 50, 20, sw=LINE * 0.7)
    return svg(b, bg)


def t2_2():
    bg = bg_room("#9DB0BE", "#8CA1B1", "#7D93A3", 1300)
    # 夜の病棟廊下
    b = shape("M80,260 h920 v990 h-920 z", fill="#A9BCC8")
    for x in (130, 430, 730):
        b += door(x, 560, 200, 690, "#BFCED7")
    b += box(140, 300, 800, 120, "#B9C9D3", 10)
    b += glow("nglow", 760, 220, 200, "#F2F1DA", 0.35) + moon(760, 220, 54, "#F2F1DA")
    b += ground_shadow(500, 1296)
    b += standing(500, 1290, 1.06, droop=1.0, head_drop=-14, head_tilt=-18, top="#C9DCE2", bottom="#AFC5CE")
    return svg(b, bg)


def calendar(x, y, cols, rows, cell, marks):
    out = box(x, y - 60, cols * cell, rows * cell + 60, CARD, 12) + shape(f"M{x},{y - 60} h{cols * cell} v60 h{-cols * cell} z", fill="#CFE6DD")
    for c in range(1, cols):
        out += ln(x + c * cell, y, x + c * cell, y + rows * cell, 3, SOFT)
    for r in range(1, rows):
        out += ln(x, y + r * cell, x + cols * cell, y + r * cell, 3, SOFT)
    for k, m in enumerate(marks):
        cx, cy = x + (k % cols) * cell + cell / 2, y + (k // cols) * cell + cell / 2
        out += sun(cx, cy, cell * 0.17, sw=4) if m == "s" else moon(cx, cy, cell * 0.24, sw=4)
    return out


def t2_3():
    bg = calm_room()
    marks = "ssmsssmssmsssmssssmssmsss"[:20]
    b = calendar(180, 300, 5, 4, 140, marks)
    x, fy, s = 820, 1290, 1.0
    b += ground_shadow(x, 1296, 100)
    b += nurse_hold(x, fy, s, (650, 760), None, head_drop=8, head_tilt=-12)
    b += magnifier(560, 640, 110, 45, inner=moon(560, 640, 46) + "")
    return svg(b, bg)


def t2_4():
    bg = calm_room("#F6FBFB", "#E8F3F2", "#DCEBEA")
    b = ""
    icons = [lambda x, y: hospital(x, y + 40, 0.38), lambda x, y: sun(x, y, 34), lambda x, y: pair(x, y + 60, 0.55)]
    for k, x in enumerate((120, 420, 720)):
        y = 300 if k != 1 else 260
        b += (f'<rect x="{x}" y="{y}" width="240" height="330" rx="14" fill="{CARD if k == 1 else "#F1F6F7"}" '
              f'stroke="{TEAL if k == 1 else INK}" stroke-width="{LINE * (1.1 if k == 1 else 0.8)}"/>')
        b += icons[k](x + 120, y + 110)
        for j in range(3):
            b += ln(x + 40, y + 210 + j * 36, x + 200 - (j % 2) * 40, y + 210 + j * 36, 8, SOFT)
    b += magnifier(560, 470, 80, 50, lens="#FFFFFF", inner=check(540, 470, 1.2))
    x, fy, s = 540, 1290, 1.0
    b += ground_shadow(x, 1296)
    b += nurse_hold(x, fy, s, (x + 150, fy - 520), None, head_drop=-10, head_tilt=-6, top="#DCEBDF")
    return svg(b, bg)


# =====================================================================
# 転職3 転職で後悔する看護師の、たった1つの共通点
# =====================================================================
def t3_1():
    bg = calm_room("#F7FBF9", "#EAF3F1", "#DCEBEA")
    b = window(130, 300, 300, 400, "#E2F1F4", '<path d="M130,580 q80,-70 150,-10 q70,-60 150,0 v120 h-300 z" fill="#CFE6DD"/>')
    b += plant(900, 1180, 0.9)
    x, fy, s = 560, 1290, 1.08
    b += ground_shadow(x, 1296)
    b += nurse_hold(x, fy, s, (x + 40, fy - 470 * s), (x - 10, fy - 470 * s), head_drop=10)
    b += job_card(x - 90, fy - 560 * s, 190, 210) + sparkle(x + 130, fy - 570 * s, 22)
    return svg(b, bg)


def t3_2():
    bg = calm_room("#F2F6F7", "#E3ECEE", "#D6E2E4")
    # カードの裏(からまった線・対立する二人・時計)
    x, y, w, h = 190, 230, 700, 940
    b = box(x, y, w, h, "#F4F7F7", 18)
    b += f'<path d="M{x + 70},{y + 120} c120,-60 200,120 320,40 s160,-80 240,20 M{x + 90},{y + 820} c100,60 180,-90 300,-30 s180,70 230,-10" fill="none" stroke="{SOFT}" stroke-width="10" stroke-linecap="round"/>'
    b += f'<path d="M{x + 80},{y + 460} c60,-120 160,80 220,-30 c40,-80 120,60 180,-20 c50,-60 100,30 140,-10" fill="none" stroke="{SOFT}" stroke-width="8" stroke-linecap="round"/>'
    b += pair(x + 200, y + 400, 1.2, conflict=True)
    b += clock(x + 500, y + 600, 110)
    b += f'<path d="M{x + 610},{y + 470} q30,40 0,80" fill="none" stroke="{CORAL}" stroke-width="{LINE}" stroke-linecap="round"/>'
    # めくれた角
    b += shape(f"M{x + w},{y + h - 130} l-130,130 h110 q20,0 20,-20 z", fill="#E3ECEE")
    return svg(b, bg)


def t3_3():
    bg = calm_room()
    b = ln(540, 300, 540, 1260, 4, SOFT, 'stroke-dasharray="10 16"')
    # 左: 表だけ見る
    x, fy, s = 260, 1290, 0.95
    b += ground_shadow(x, 1296, 100)
    b += nurse_hold(x, fy, s, (x + 40, fy - 470 * s), (x - 10, fy - 470 * s), head_drop=8)
    b += job_card(x - 90, fy - 560 * s, 180, 200)
    # 右: 持ち上げて裏を見る
    x2 = 860
    cx, cy = 600, 640
    b += box(cx, cy, 300, 360, "#EAF5F4", 12) + pair(cx + 100, cy + 290, 0.6, conflict=True) + clock(cx + 230, cy + 120, 42)
    b += f'<path d="M{cx},{cy} h300 l30,-130 h-360 z" fill="#FFFFFF" stroke="{INK}" stroke-width="{LINE}" stroke-linejoin="round"/>'
    b += ln(cx + 10, cy - 70, cx + 290, cy - 70, 8, SOFT) + ln(cx + 10, cy - 110, cx + 180, cy - 110, 8, SOFT)
    b += ground_shadow(x2, 1296, 100)
    b += nurse_hold(x2, 1290, 0.95, (cx + 318, cy - 100), None, head_drop=-6, head_tilt=-14, top="#DCEBDF")
    return svg(b, bg)


def t3_4():
    bg = calm_room("#F6FBFB", "#E8F3F2", "#DCEBEA")
    b = window(700, 300, 260, 400, "#E2F1F4", '<path d="M700,600 q70,-60 130,-10 q60,-50 130,0 v100 h-260 z" fill="#CFE6DD"/>')
    b += job_card(150, 280, 360, 440, fill="#F7FAFA")
    inner = pair(400, 640, 0.6) + clock(470, 520, 30) + check(330, 520, 1.0)
    b += magnifier(400, 560, 140, 45, lens="#FFFFFF", inner=inner)
    x, fy, s = 760, 1290, 1.05
    b += ground_shadow(x, 1296)
    b += nurse_hold(x, fy, s, (560, 740), None, head_drop=-2, head_tilt=-10)
    return svg(b, bg)


# =====================================================================
# 副業1 夜勤に疲れた看護師の"次の道"
# =====================================================================
def bed_icon(x, y, s=1.0):
    return (shape(f"M{x - 50 * s},{y} v{-50 * s} h{100 * s} v{50 * s} M{x - 50 * s},{y - 20 * s} h{100 * s}", fill="none", sw=LINE * 0.8)
            + circ(x - 26 * s, y - 34 * s, 10 * s, "none", LINE * 0.6))


def f1_1():
    bg = calm_room("#EEF3F4", "#E1EAEC", "#D3E0E2")
    b = shape("M120,200 h840 v1060 h-840 z", fill="#DCE6E9")
    b += door(390, 420, 300, 840, "#E9F0F2", bed_icon(540, 600, 1.4))
    b += ground_shadow(540, 1296)
    b += standing(540, 1290, 1.0, droop=0.8, head_drop=6, top=SCRUB)
    return svg(b, bg)


def f1_2():
    bg = calm_room("#F6FBFB", "#E8F3F2", "#DCEBEA")
    b = glow("open", 540, 640, 520, "#FFF6D8", 0.55)
    # 開いた壁(両側)
    b += shape("M40,180 h120 v1080 h-120 z", fill="#D3DFE2") + shape("M920,180 h120 v1080 h-120 z", fill="#D3DFE2")
    icons = [
        lambda x, y: f'<path d="M{x - 12},{y - 40} h24 v28 h28 v24 h-28 v28 h-24 v-28 h-28 v-24 h28 z" fill="{CORAL}"/>',
        lambda x, y: box(x - 30, y - 40, 60, 80, CARD, 6, LINE * 0.7) + check(x, y - 6, 0.8) + ln(x - 14, y + 20, x + 16, y + 20, 5, SOFT),
        lambda x, y: box(x - 34, y - 50, 68, 100, "#E6EEF0", 4, LINE * 0.7) + "".join(f'<rect x="{x - 22 + c * 26}" y="{y - 38 + r * 26}" width="16" height="16" fill="#CFE3EA"/>' for r in range(3) for c in range(2)),
        lambda x, y: f'<path d="M{x - 30},{y + 34} L{x + 24},{y - 30}" stroke="{INK}" stroke-width="{LINE}" stroke-linecap="round"/><path d="M{x + 18},{y - 24} l14,-14 l8,8 l-14,14 z" fill="{TEAL}"/>' + sparkle(x + 30, y + 24, 12),
    ]
    xs = [200, 400, 600, 800]
    for k, x in enumerate(xs):
        top = 360 + abs(k - 1.5) * 50
        b += door(x - 80, top, 160, 760 - abs(k - 1.5) * 50, "#F3F8F8")
        b += circ(x, top + 130, 56, "#FFFFFF", LINE * 0.7) + icons[k](x, top + 130)
    b += shape("M0,1250 h1080 v20 h-1080 z", fill="#C8D9DC")
    return svg(b, bg)


def f1_3():
    bg = bg_room("#F4FAF8", "#E3F0EC", "#CFE3DA", 760)
    b = f'<path d="M0,760 q260,-80 540,-30 q280,-50 540,30 v40 h-1080 z" fill="#BFDDD3"/>'
    # 足元から広がる道(上から見下ろす)
    for ang, c in [(-62, "#F3F8F6"), (-32, "#F3F8F6"), (0, "#FFF8E6"), (32, "#F3F8F6"), (62, "#F3F8F6")]:
        a = math.radians(ang)
        ex, ey = 540 + math.sin(a) * 760, 1180 - math.cos(a) * 520
        nx, ny = math.cos(a), math.sin(a)
        b += (f'<path d="M{540 - 60},{1180} L{ex - nx * 22},{ey - ny * 22} L{ex + nx * 22},{ey + ny * 22} L{540 + 60},{1180} Z" '
              f'fill="{c}" stroke="{INK}" stroke-width="{LINE * 0.6}" stroke-linejoin="round"/>')
    b += sun(540, 420, 40) + plant(140, 1100, 0.7) + plant(940, 1100, 0.7)
    b += ground_shadow(540, 1296)
    b += standing(540, 1290, 0.95, droop=0.2, head_drop=-6, top=SCRUB)
    return svg(b, bg)


def f1_4():
    bg = bg_room("#FBFCF4", "#EEF6EE", "#D9EBE0", 1000)
    b = glow("sunglow", 820, 330, 340, "#FFF1C2", 0.7) + sun(820, 330, 64)
    b += hospital(170, 1010, 0.5, "#E1EAEC")
    b += f'<path d="M260,1300 L720,620 L860,620 L760,1300 Z" fill="#FFF8E6" stroke="{INK}" stroke-width="{LINE * 0.6}" stroke-linejoin="round"/>'
    b += plant(950, 1150, 0.8)
    b += ground_shadow(560, 1296)
    b += standing(560, 1290, 1.0, droop=0.0, head_drop=-10, head_tilt=10, top=SCRUB)
    return svg(b, bg)


# =====================================================================
# 副業2 アートメイク看護師のリアル
# =====================================================================
def s2_1():
    bg = calm_room("#F4F9FA", "#E6F0F2", "#D8E6E8")
    b = glow("star", 760, 330, 260, "#FFF1C2", 0.75) + sparkle(760, 330, 70, "#FFF4C8") + sparkle(620, 230, 20) + sparkle(900, 470, 24)
    b += plant(180, 1180, 0.9)
    b += ground_shadow(500, 1296)
    b += standing(500, 1290, 1.06, droop=0.0, head_drop=-24, head_tilt=22, arms="down")
    return svg(b, bg)


def s2_2():
    bg = calm_room("#F6FBFB", "#E8F3F2", "#DCEBEA")
    b = ln(160, 1160, 960, 1160, LINE) + ln(160, 1160, 160, 300, LINE)
    hs = [160, 280, 420, 560, 740]
    for k, h in enumerate(hs):
        x = 220 + k * 150
        b += box(x, 1160 - h, 100, h, ["#CFE6DD", "#BFDDD3", "#A8D2C6", "#93C6B8", "#7DBAA9"][k], 6)
    pts = [(270 + k * 150, 1160 - h - 60) for k, h in enumerate(hs)]
    b += '<path d="M' + " L".join(f"{x},{y}" for x, y in pts) + f'" fill="none" stroke="{TEAL}" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/>'
    b += "".join(circ(x, y, 14, "#FFFFFF", 6, TEAL) for x, y in pts)
    b += f'<path d="M{pts[-1][0] - 40},{pts[-1][1] - 30} l40,-30 l10,48" fill="none" stroke="{TEAL}" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/>'
    b += coin(330, 860, 40) + coin(400, 900, 34) + coin(860, 260, 44)
    return svg(b, bg)


def s2_3():
    bg = calm_room()
    # 2段の階段: 臨床経験(聴診器) → スクール(角帽)
    b = shape("M120,1290 v-240 h300 v240 z", fill="#E3EEF0") + shape("M420,1290 v-480 h300 v480 z", fill="#D6E8E8")
    b += shape("M720,1290 v-720 h260 v720 z", fill="#C6E0DA")
    # 聴診器
    b += f'<path d="M230,1170 q-40,-70 10,-90 M310,1170 q40,-70 -10,-90" fill="none" stroke="{INK}" stroke-width="6"/>' \
         f'<path d="M270,1170 v20 q0,40 40,40" fill="none" stroke="{INK}" stroke-width="6"/>' + circ(316, 1232, 16, TEAL, 5)
    # 角帽
    b += f'<path d="M570,920 l-80,-34 l80,-34 l80,34 z" fill="{INK}" opacity=".85"/>' + shape("M530,900 v40 q40,20 80,0 v-40", fill="#BFD6DD", sw=5) + ln(650, 886, 650, 940, 4)
    # 医師の管理(盾+十字)
    b += f'<path d="M850,380 l70,26 v60 q0,60 -70,90 q-70,-30 -70,-90 v-60 z" fill="#FFFFFF" stroke="{INK}" stroke-width="{LINE}" stroke-linejoin="round"/>'
    b += f'<path d="M842,430 h16 v16 h16 v16 h-16 v16 h-16 v-16 h-16 v-16 h16 z" fill="{CORAL}"/>'
    b += ground_shadow(560, 812, 90)
    x, fy, s = 560, 808, 0.72
    b += standing(x, fy, s, droop=0.0, head_drop=-6, head_tilt=12)
    return svg(b, bg)


def s2_4():
    bg = calm_room("#F6FBFB", "#E7F2F1", "#DCEBEA")
    b = f'<g opacity=".35">{moon(830, 320, 70)}{ln(740, 400, 920, 240, 10, CORAL)}</g>'
    b += window(130, 300, 280, 380, "#E2F1F4", sun(270, 420, 34))
    b += shape("M300,1040 h200 v24 h-200 z", fill="#D7E5E8") + limb([(320, 1064), (320, 1296)], 12, "#D7E5E8") + limb([(480, 1064), (480, 1296)], 12, "#D7E5E8")
    b += seated(340, 1040, 1.0, top="#F3F8F8", bottom="#C4D4DF", arms="none", head_drop=18, head_tilt=8)
    b += table(500, 1000, 900, 1296)
    # 手元の精密作業(細いペン型の道具と、なぞる曲線)
    b += box(620, 820, 280, 70, "#F3F8F8", 10)
    b += f'<path d="M660,860 q60,-30 120,-6 q50,20 90,-4" fill="none" stroke="{TEAL}" stroke-width="5" stroke-linecap="round" stroke-dasharray="2 10"/>'
    b += f'<path d="M660,860 q40,-22 80,-12" fill="none" stroke="{INK}" stroke-width="5" stroke-linecap="round"/>'
    b += limb([(400, 760), (480, 840), (620, 820)], 34, "#F3F8F8")
    b += ln(640, 820, 720, 740, 9) + ln(720, 740, 742, 718, 5, TEAL) + sparkle(748, 846, 14)
    b += glow("work", 720, 840, 140, "#9FD6CF", 0.35)
    return svg(b, bg)


# =====================================================================
# 橋渡しA 退職届を、書いては消していた
# =====================================================================
def back_view(fig):
    """standing() の V ネックを消して後ろ姿にする。"""
    return re.sub(r'<path d="M[^"]*" fill="none" stroke="#2B4A5E" stroke-width="5\.6[0-9]*" stroke-linecap="round"/>', "", fig)


def gear(cx, cy, r, teeth=10, fill="#D6E8E8"):
    pts = []
    for k in range(teeth * 4):
        a = 2 * math.pi * k / (teeth * 4)
        rr = r if (k % 4) in (1, 2) else r * 0.84
        pts.append(f"{cx + math.cos(a) * rr:.1f},{cy + math.sin(a) * rr:.1f}")
    return (f'<path d="M{" L".join(pts)} Z" fill="{fill}" stroke="{INK}" stroke-width="{LINE}" stroke-linejoin="round"/>'
            + circ(cx, cy, r * 0.32, "#F3F8F8") + circ(cx, cy, r * 0.12, "#C6DCDC", LINE * 0.8))


def bundle(cx, cy, w, h, inner=""):
    """風呂敷包みの大きな荷物(中心 cx,cy)。"""
    return (shape(f"M{cx - w / 2},{cy} q0,{-h / 2} {w / 2},{-h / 2} q{w / 2},0 {w / 2},{h / 2} q0,{h / 2} {-w / 2},{h / 2} "
                  f"q{-w / 2},0 {-w / 2},{-h / 2} z", fill="#CFE3E1") + inner
            + shape(f"M{cx - 50},{cy - h / 2 + 10} q50,-70 100,0 q-50,30 -100,0 z", fill="#BCD7D4"))


def a_1():  # スマホの下書きフォルダ(手元のアップ)
    bg = calm_room("#F2F7F8", "#E4EEF0", "#D9E6E8")
    b = glow("ph", 540, 700, 460, "#EFFFFF", 0.7)
    # 袖と手(左右から)
    b += limb([(60, 1330), (250, 1000)], 150, SCRUB) + limb([(1020, 1330), (830, 1000)], 150, SCRUB)
    b += limb([(250, 1000), (330, 860)], 110, SKIN) + limb([(830, 1000), (750, 860)], 110, SKIN)
    # スマホ
    px, py, pw, ph = 330, 240, 420, 820
    b += box(px, py, pw, ph, "#2F4B5C", 46) + box(px + 22, py + 60, pw - 44, ph - 120, "#F7FBFC", 18, LINE * 0.6)
    b += box(px + pw / 2 - 40, py + 26, 80, 14, "#4F6B7B", 7, 0)
    b += ln(px + 60, py + 120, px + 200, py + 120, 12, SOFT)
    for k in range(5):
        y = py + 180 + k * 120
        b += box(px + 50, y, pw - 100, 96, "#FFFFFF" if k else "#EAF5F4", 12, LINE * 0.6)
        ex, ey = px + 80, y + 26
        b += shape(f"M{ex},{ey} h56 v40 h-56 z", fill="#E6EFF6", sw=LINE * 0.6)
        b += f'<path d="M{ex},{ey} l28,22 l28,-22" fill="none" stroke="{INK}" stroke-width="{LINE * 0.6}" stroke-linejoin="round"/>'
        b += ln(ex + 84, ey + 8, px + pw - 80, ey + 8, 8, SOFT) + ln(ex + 84, ey + 34, px + pw - 140, ey + 34, 8, SOFT)
    # 親指(画面の手前)
    b += limb([(330, 880), (420, 800)], 46, SKIN) + limb([(750, 880), (660, 800)], 46, SKIN)
    return svg(b, bg)


def a_2():  # 師長の前で言葉を飲み込む
    bg = calm_room("#F4F8F8", "#E5EFEF", "#D9E7E7")
    b = window(620, 260, 320, 380, "#E2F1F4", '<path d="M620,540 q90,-70 160,-10 q80,-50 160,10 v100 h-320 z" fill="#CFE6DD"/>')
    b += box(140, 300, 260, 180, CARD) + ln(170, 350, 370, 350, 9, SOFT) + ln(170, 390, 320, 390, 9, SOFT)
    b += ground_shadow(770, 1296, 120)
    b += standing(770, 1290, 1.12, top="#BFD6DD", bottom="#A9C2CB", head_tilt=-6)  # 師長(背が高く、動かない)
    x, fy, s = 360, 1290, 0.98
    b += ground_shadow(x, 1296)
    b += standing(x, fy, s, droop=0.8, head_drop=18, head_tilt=8, arms="none")
    b += limb([(x + 68 * s, fy - 536 * s), (x + 80 * s, fy - 420 * s), (x + 80 * s, fy - 300 * s)], 34 * s)
    b += limb([(x - 66 * s, fy - 530 * s), (x - 70 * s, fy - 450 * s), (x - 6 * s, fy - 598 * s)], 34 * s)  # 口元に手
    # 飲み込んだ言葉(うすく消えていく吹き出し)
    b += f'<g opacity=".45"><path d="M470,470 q0,-50 60,-50 h90 q60,0 60,50 q0,50 -60,50 h-70 l-40,30 l6,-34 q-46,-6 -46,-46 z" fill="#FFFFFF" stroke="{INK}" stroke-width="{LINE * 0.7}" stroke-dasharray="6 12"/></g>'
    return svg(b, bg)


def a_3():  # 一人で大きな歯車を支える
    bg = calm_room("#F4F9F9", "#E6F0F0", "#D9E7E7")
    b = f'<g opacity=".5">{gear(220, 300, 90, 8, "#E3EEEE")}{gear(880, 330, 110, 9, "#E3EEEE")}</g>'
    b += gear(540, 380, 250, 12)
    x, fy, s = 540, 1290, 0.85
    b += limb([(x - 68 * s, fy - 536 * s), (x - 130 * s, fy - 650 * s), (x - 70, 650)], 34 * s, SCRUB)
    b += limb([(x + 68 * s, fy - 536 * s), (x + 130 * s, fy - 650 * s), (x + 70, 650)], 34 * s, SCRUB)
    b += ground_shadow(x, 1296)
    b += standing(x, fy, s, droop=0.3, head_drop=10, arms="none")
    b += f'<path d="M{x - 190},{820} q-20,-30 0,-60 M{x + 190},{820} q20,-30 0,-60" fill="none" stroke="{SOFT}" stroke-width="6" stroke-linecap="round"/>'
    return svg(b, bg)


def a_4():  # 肩の荷を下ろしかける後ろ姿
    bg = calm_room("#F7FBF9", "#EAF3F1", "#DCEBEA")
    b = glow("dawn", 540, 420, 420, "#FFF3D2", 0.65)
    b += window(330, 220, 420, 520, "#EEF7F8", '<path d="M330,620 q110,-90 210,-20 q110,-70 210,10 v130 h-420 z" fill="#CFE6DD"/>')
    x, fy, s = 520, 1290, 1.08
    b += ground_shadow(x, 1296, 140)
    b += back_view(standing(x, fy, s, droop=0.4, head_drop=-4, arms="none"))
    b += limb([(x - 68 * s, fy - 536 * s), (x - 80 * s, fy - 420 * s), (x - 80 * s, fy - 300 * s)], 34 * s)
    # 右肩からずり下ろすカバン
    b += f'<path d="M{x + 60 * s},{fy - 560 * s} Q{x + 160},{fy - 520} {x + 200},{fy - 330}" fill="none" stroke="{INK}" stroke-width="{LINE * 1.4}" stroke-linecap="round"/>'
    b += limb([(x + 68 * s, fy - 536 * s), (x + 130 * s, fy - 430 * s), (x + 190, fy - 330)], 34 * s)
    b += shape(f"M{x + 120},{fy - 330} h170 l-14,190 h-142 z", fill="#C8DCDF")
    b += sparkle(760, 520, 18) + sparkle(300, 640, 14)
    return svg(b, bg)


# =====================================================================
# 橋渡しB "私が辞めたら、回らない"が口癖になっていた
# =====================================================================
def b_1():  # 休日の部屋でシフト表を見つめてしまう
    bg = calm_room("#F5F9F8", "#E7F0EF", "#DAE8E7")
    b = calendar(520, 330, 5, 4, 96, "smsssmssmsssmssmssss")
    b += plant(140, 960, 0.7)
    b += sofa(100, 1040, 760)
    b += seated(330, 1040, 1.0, top="#F1E8DE", bottom="#C4D4DF", arms="lap", head_drop=-26, head_tilt=-14)
    return svg(b, bg)


def b_2():  # 「辞めたい」を飲み込んで笑う
    bg = calm_room("#F4FAFA", "#E4F1F1", "#D6E9E8")
    b = shape("M80,880 h920 v40 h-920 z", fill="#E3EEF0") + shape("M100,920 h880 v330 h-880 z", fill="#EEF4F5")
    b += box(700, 720, 200, 150, "#DCEBEA", 8) + ln(730, 770, 860, 770, 8, SOFT)
    b += f'<g opacity=".32">{standing(180, 1290, 0.9, top="#FFFFFF", bottom="#FFFFFF")}{standing(880, 1290, 0.9, top="#FFFFFF", bottom="#FFFFFF")}</g>'
    x, fy, s = 520, 1290, 1.04
    b += ground_shadow(x, 1296)
    b += standing(x, fy, s, droop=0.6, head_drop=4, head_tilt=12, arms="none")
    b += limb([(x - 66 * s, fy - 530 * s), (x - 80 * s, fy - 420 * s), (x - 6, fy - 380 * s)], 34 * s)
    b += limb([(x + 66 * s, fy - 530 * s), (x + 80 * s, fy - 420 * s), (x + 6, fy - 380 * s)], 34 * s)  # 前で手を組む
    b += f'<g opacity=".4"><path d="M600,470 q0,-44 54,-44 h70 q54,0 54,44 q0,44 -54,44 h-54 l-34,28 l4,-30 q-40,-6 -40,-42 z" fill="#FFFFFF" stroke="{INK}" stroke-width="{LINE * 0.7}" stroke-dasharray="6 12"/></g>'
    return svg(b, bg)


def b_3():  # 職場全体を一人で背負う
    bg = calm_room("#F2F7F8", "#E3EEF0", "#D6E3E5")
    inner = hospital(540, 600, 0.9, "#EEF4F5") + f'<g opacity=".8">{pair(330, 600, 0.5)}{pair(750, 600, 0.5)}</g>'
    b = bundle(540, 430, 720, 480, inner)
    x, fy, s = 540, 1290, 0.82
    b += limb([(x - 68 * s, fy - 536 * s), (x - 140 * s, fy - 640 * s), (x - 90, 676)], 34 * s, SCRUB)
    b += limb([(x + 68 * s, fy - 536 * s), (x + 140 * s, fy - 640 * s), (x + 90, 676)], 34 * s, SCRUB)
    b += ground_shadow(x, 1296)
    b += standing(x, fy, s, droop=0.9, head_drop=26, arms="none")
    return svg(b, bg)


def b_4():  # 荷物をそっと地面に置く後ろ姿
    bg = bg_room("#FBFCF6", "#EEF6F0", "#DCEDE3", 1300)
    b = glow("light", 540, 400, 480, "#FFF1C8", 0.7) + sun(540, 330, 54)
    b += f'<path d="M0,820 q260,-90 540,-40 q280,-50 540,40 v40 h-1080 z" fill="#CFE6DD"/>'
    b += bundle(800, 1170, 320, 240, hospital(800, 1230, 0.42, "#EEF4F5"))
    x, fy, s = 450, 1290, 1.06
    b += ground_shadow(x, 1296, 120) + ground_shadow(800, 1296, 170)
    b += back_view(standing(x, fy, s, droop=0.0, head_drop=-8, arms="none"))
    b += limb([(x - 68 * s, fy - 536 * s), (x - 80 * s, fy - 420 * s), (x - 80 * s, fy - 300 * s)], 34 * s)
    b += limb([(x + 68 * s, fy - 536 * s), (x + 150 * s, fy - 430 * s), (650, 1080)], 34 * s)
    b += sparkle(300, 560, 18) + sparkle(760, 640, 14) + sparkle(900, 480, 20)
    return svg(b, bg)


EPISODES = {
    "kanjo3_yasumi": [k3_1, k3_2, k3_3, k3_4],
    "kanjo4_namida": [k4_1, k4_2, k4_3, k4_4],
    "kanjo5_ajike": [k5_1, k5_2, k5_3, k5_4],
    "tenshoku1_erabikata": [t1_1, t1_2, t1_3, t1_4],
    "tenshoku2_yakin_nashi": [t2_1, t2_2, t2_3, t2_4],
    "tenshoku3_koukai": [t3_1, t3_2, t3_3, t3_4],
    "fukugyo1_tsugi_no_michi": [f1_1, f1_2, f1_3, f1_4],
    "fukugyo2_artmake": [s2_1, s2_2, s2_3, s2_4],
    "bridge_a_taishokutodoke": [a_1, a_2, a_3, a_4],
    "bridge_b_kuchiguse": [b_1, b_2, b_3, b_4],
}

if __name__ == "__main__":
    root = Path(__file__).parent / "episodes"
    for slug in sys.argv[1:] or EPISODES:
        for i, fn in enumerate(EPISODES[slug], 1):
            (root / slug / f"img{i}.svg").write_text(fn())

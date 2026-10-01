# 4枚のフラットイラスト(1080x1920 SVG)を生成する。
# 輪郭線のみ・顔なし・白/青/緑の淡い配色。字幕帯(y≈1300-1600)に主役が隠れない構図。
W, H = 1080, 1920
INK = "#2B4A5E"      # 輪郭線
SKIN = "#F7FBFB"     # 人物の塗り(ほぼ白)
SCRUB = "#CFE6EA"    # 看護師のスクラブ
TEAL = "#2A7F8C"
LINE = 7


def svg(body, bg):
    # 全体を1.1倍して少し上へ。人物の足元を y≈1330 に置き、下部を字幕用の余白にする
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
            f'<rect width="{W}" height="{H}" fill="#DCEBEA"/>'
            f'<g transform="translate(-54,-95) scale(1.1)">{bg}{body}</g></svg>')


def limb(pts, w, fill=SKIN):
    """輪郭つきの太い線(腕・脚)。外側に濃い線、内側に塗り色を重ねる。"""
    d = "M" + " L".join(f"{x},{y}" for x, y in pts)
    return (f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="{w + LINE * 2}" '
            f'stroke-linecap="round" stroke-linejoin="round"/>'
            f'<path d="{d}" fill="none" stroke="{fill}" stroke-width="{w}" '
            f'stroke-linecap="round" stroke-linejoin="round"/>')


def shape(d, fill=SKIN, sw=LINE, stroke=INK, extra=""):
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round" {extra}/>'


def head(x, y, r=46, tilt=0):
    return (f'<ellipse cx="{x}" cy="{y}" rx="{r * 0.9}" ry="{r}" transform="rotate({tilt} {x} {y})" '
            f'fill="{SKIN}" stroke="{INK}" stroke-width="{LINE}"/>')


def standing(x, fy, s=1.0, droop=0.0, top=SCRUB, bottom=SCRUB, head_tilt=0, head_drop=0,
             arms="down", bag=False):
    """立ち姿。fy=足元のy。droop=肩の落ち具合(0..1)。"""
    def p(dx, dy):
        return (x + dx * s, fy + dy * s)
    sh = 18 * droop  # 肩の下がり
    out = []
    # 脚
    out.append(limb([p(-28, -300), p(-30, -20)], 46 * s, bottom))
    out.append(limb([p(28, -300), p(30, -20)], 46 * s, bottom))
    out.append(shape(f"M{p(-58,-14)[0]},{p(-58,-14)[1]} h{50*s} v{18*s} h{-54*s} z", fill="#E9F1F3"))
    out.append(shape(f"M{p(8,-14)[0]},{p(8,-14)[1]} h{50*s} v{18*s} h{-46*s} z", fill="#E9F1F3"))
    # 腕(胴より後ろ側に一部隠れるよう先に描く)
    if arms == "down":
        out.append(limb([p(-68, -536 + sh * 2), p(-80 + 10 * droop, -420 + sh), p(-80, -300 + sh * 0.5)], 34 * s, top))
        out.append(limb([p(68, -536 + sh * 2), p(80 - 10 * droop, -420 + sh), p(80, -300 + sh * 0.5)], 34 * s, top))
    elif arms == "laugh":  # 片手を腹、片手を上げて笑う姿勢
        out.append(limb([p(-72, -540), p(-120, -470), p(-30, -420)], 34 * s, top))
        out.append(limb([p(72, -540), p(140, -620), p(150, -700)], 34 * s, top))
    # 胴
    # 肩を落とすほど外側が下がり、なで肩になる
    tx = [p(-76, -548 + sh * 2), p(76, -548 + sh * 2), p(64, -290), p(-64, -290)]
    out.append(shape(f"M{tx[0][0]},{tx[0][1]} Q{x},{p(0, -600)[1]} {tx[1][0]},{tx[1][1]} "
                     f"L{tx[2][0]},{tx[2][1]} L{tx[3][0]},{tx[3][1]} Z", fill=top))
    # Vネック
    out.append(f'<path d="M{p(-26,-574 + sh*0.8)[0]},{p(-26,-574 + sh*0.8)[1]} L{x},{p(0,-520+sh)[1]} '
               f'L{p(26,-574 + sh*0.8)[0]},{p(26,-574 + sh*0.8)[1]}" fill="none" stroke="{INK}" '
               f'stroke-width="{LINE*0.8}" stroke-linecap="round"/>')
    if bag:
        hx, hy = p(-80, -300 + sh * 0.5)
        out.append(f'<path d="M{hx-26*s},{hy+10*s} Q{hx},{hy-40*s} {hx+26*s},{hy+10*s}" fill="none" '
                   f'stroke="{INK}" stroke-width="{LINE}"/>')
        out.append(shape(f"M{hx-62*s},{hy+10*s} h{124*s} l{-10*s},{120*s} h{-104*s} z", fill="#DDEBEE"))
    # 首と頭
    out.append(limb([p(0, -585 + sh), p(0, -600 + sh + head_drop * 0.4)], 26 * s))
    out.append(head(p(0, -640 + sh + head_drop)[0], p(0, -640 + sh + head_drop)[1], 46 * s, head_tilt))
    return "".join(out)


def seated(x, sy, s=1.0, top=SCRUB, bottom="#B9D3DA", lean=0, arms="lap", head_tilt=0, head_drop=0,
           facing=1):
    """座り姿。sy=座面のy。facing=1で右向き(膝が右)。"""
    f = facing

    def p(dx, dy):
        return (x + dx * s * f, sy + dy * s)
    out = []
    # 脚: 太もも水平→すね垂直
    out.append(limb([p(-10, -24), p(150, -18), p(160, 240)], 48 * s, bottom))
    out.append(limb([p(20, -24), p(180, -12), p(196, 236)], 48 * s, bottom))
    # 胴
    tx = [p(-70 + lean, -300), p(70 + lean, -300), p(60, -20), p(-60, -20)]
    out.append(shape(f"M{tx[0][0]},{tx[0][1]} Q{p(lean, -326)[0]},{p(lean, -326)[1]} {tx[1][0]},{tx[1][1]} "
                     f"L{tx[2][0]},{tx[2][1]} L{tx[3][0]},{tx[3][1]} Z", fill=top))
    if arms == "lap":
        out.append(limb([p(60 + lean, -280), p(84, -150), p(150, -60)], 34 * s, top))
    elif arms == "laugh":
        out.append(limb([p(60 + lean, -280), p(120, -200), p(70, -140)], 34 * s, top))
    elif arms == "gesture":
        out.append(limb([p(60 + lean, -280), p(140, -220), p(210, -270)], 34 * s, top))
    hx, hy = p(lean * 1.4, -360 + head_drop)
    out.append(limb([p(lean, -310), (hx, hy + 30 * s)], 26 * s))
    out.append(head(hx, hy, 46 * s, head_tilt * f))
    return "".join(out)


def window(x, y, w, h, sky, extra=""):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{sky}" stroke="{INK}" stroke-width="{LINE}"/>'
            f'{extra}'
            f'<line x1="{x + w/2}" y1="{y}" x2="{x + w/2}" y2="{y + h}" stroke="{INK}" stroke-width="{LINE}"/>'
            f'<line x1="{x}" y1="{y + h*0.45}" x2="{x + w}" y2="{y + h*0.45}" stroke="{INK}" stroke-width="{LINE}"/>')


def plant(x, y, s=1.0, pot="#E3EFF1"):
    leaves = "".join(
        f'<path d="M{x},{y} q{dx*s},{-dy*s} {dx*1.6*s},{-dy*1.7*s} q{-dx*0.9*s},{dy*0.2*s} {-dx*1.6*s},{dy*1.7*s} z" '
        f'fill="#A8D2C6" stroke="{INK}" stroke-width="{LINE*0.7}"/>'
        for dx, dy in [(-40, 60), (40, 60), (-14, 90), (18, 84)])
    return leaves + shape(f"M{x-46*s},{y} h{92*s} l{-12*s},{86*s} h{-68*s} z", fill=pot)


def bg_room(top, bottom, floor, floor_y=1240):
    return (f'<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{top}"/><stop offset="1" stop-color="{bottom}"/></linearGradient></defs>'
            f'<rect width="{W}" height="{H}" fill="url(#g)"/>'
            f'<rect y="{floor_y}" width="{W}" height="{H}" fill="{floor}"/>'
            f'<line x1="0" y1="{floor_y}" x2="{W}" y2="{floor_y}" stroke="{INK}" stroke-width="{LINE*0.6}" opacity=".5"/>')


# ---------- 画像1: 休憩室、笑う同僚たちと、少し離れて立つ看護師 ----------
def img1():
    bg = bg_room("#F4FAFA", "#E4F1F1", "#D6E9E8", 1300)
    hills = (f'<path d="M110,560 q120,-110 230,-30 q90,-80 200,10 v120 h-430 z" fill="#BFDDD3"/>'
             f'<circle cx="460" cy="430" r="34" fill="#FFFFFF" opacity=".9"/>')
    b = window(110, 300, 430, 380, "#DCEFF4", hills)
    b += f'<rect x="680" y="330" width="230" height="160" rx="10" fill="#FFFFFF" stroke="{INK}" stroke-width="{LINE}"/>'
    b += f'<line x1="710" y1="380" x2="860" y2="380" stroke="#B5D3DA" stroke-width="10" stroke-linecap="round"/>'
    b += f'<line x1="710" y1="420" x2="820" y2="420" stroke="#B5D3DA" stroke-width="10" stroke-linecap="round"/>'
    b += plant(620, 1210, 0.9)
    # 立って笑い合う同僚3人
    b += standing(175, 1290, 0.92, top="#DCEBDF", bottom="#C2D8CC", arms="laugh", head_tilt=-18, head_drop=-8)
    b += standing(345, 1290, 0.95, top="#E6EFF6", bottom="#C9DBE6", arms="laugh", head_tilt=14, head_drop=-4)
    b += standing(510, 1290, 0.9, arms="laugh", head_tilt=-12, head_drop=-6)
    # 離れて立つ看護師(肩を落として硬い)
    b += f'<ellipse cx="880" cy="1296" rx="110" ry="16" fill="{INK}" opacity=".08"/>'
    b += standing(870, 1290, 1.02, droop=1.0, head_drop=30)
    return svg(b, bg)


# ---------- 画像2: 薄暗いリビング、ソファでスマホを持ったまま動かない ----------
def img2():
    bg = bg_room("#C7D9DE", "#AFC6CE", "#9DB6BE", 1300)
    night = (f'<circle cx="400" cy="380" r="26" fill="#F2F6F2" opacity=".85"/>'
             f'<circle cx="240" cy="330" r="4" fill="#FFFFFF"/><circle cx="330" cy="470" r="3" fill="#FFFFFF"/>')
    b = window(160, 260, 330, 420, "#5E7C8C", night)
    b += f'<path d="M120,240 q40,240 -10,480 h40 q30,-240 10,-480 z" fill="#D7E5E8" stroke="{INK}" stroke-width="{LINE*0.8}"/>'
    b += f'<path d="M920,500 l-50,0 l-40,90 h130 z" fill="#E8EFEA" stroke="{INK}" stroke-width="{LINE}"/>'
    b += limb([(895, 590), (895, 1200)], 10, "#DDE7EA")
    b += shape("M845,1200 h100 v20 h-100 z", fill="#DDE7EA")
    # ソファ
    b += shape("M150,880 q0,-60 60,-60 h660 q60,0 60,60 v200 h-780 z", fill="#9FC3C2")
    b += shape("M110,960 q0,-40 40,-40 h40 v220 h-80 z", fill="#9FC3C2")
    b += shape("M890,920 h40 q40,0 40,40 v180 h-80 z", fill="#9FC3C2")
    b += shape("M190,1020 h700 v80 h-700 z", fill="#B4D3D1")
    b += seated(400, 1020, 1.0, top="#E7EEF1", bottom="#B7CCD4", arms="lap", head_drop=22)
    b += limb([(220, 1100), (220, 1150)], 16, "#88A9AE") + limb([(860, 1100), (860, 1150)], 16, "#88A9AE")
    # 低いテーブル
    b += shape("M260,1210 h560 v24 h-560 z", fill="#E2ECEE")
    b += limb([(300, 1234), (300, 1300)], 14, "#E2ECEE") + limb([(780, 1234), (780, 1300)], 14, "#E2ECEE")
    # 右手にスマホ(小さく光る画面)
    b += '<defs><radialGradient id="glow"><stop offset="0" stop-color="#EFFFFF" stop-opacity=".8"/>' \
         '<stop offset="1" stop-color="#EFFFFF" stop-opacity="0"/></radialGradient></defs>'
    b += '<circle cx="548" cy="878" r="120" fill="url(#glow)"/>'
    b += limb([(456, 742), (500, 860), (540, 880)], 34, "#E7EEF1")
    b += f'<rect x="530" y="836" width="40" height="70" rx="7" transform="rotate(-12 550 870)" fill="#F4FFFF" stroke="{INK}" stroke-width="{LINE*0.8}"/>'
    return svg(b, bg)


# ---------- 画像3: 夕方の玄関、帰宅して肩を落とす ----------
def img3():
    bg = bg_room("#EEF3F4", "#E1ECEE", "#D2E1E3", 1260)
    sky = ('<defs><linearGradient id="eve" x1="0" y1="0" x2="0" y2="1">'
           '<stop offset="0" stop-color="#8FA7C2"/><stop offset=".65" stop-color="#C9C7D6"/>'
           '<stop offset="1" stop-color="#EBD9CF"/></linearGradient></defs>')
    b = sky
    # 開いたドア
    b += f'<rect x="120" y="300" width="340" height="960" fill="url(#eve)" stroke="{INK}" stroke-width="{LINE}"/>'
    b += f'<path d="M120,1150 q120,-60 340,-30 v140 h-340 z" fill="#9CB3B6" opacity=".7"/>'
    b += f'<path d="M460,300 l120,-40 v1060 l-120,-60 z" fill="#E6EEF0" stroke="{INK}" stroke-width="{LINE}"/>'
    b += f'<circle cx="560" cy="800" r="10" fill="{INK}"/>'
    # 靴箱と植物
    b += shape("M780,860 h220 v400 h-220 z", fill="#EEF4F5")
    b += f'<line x1="780" y1="1060" x2="1000" y2="1060" stroke="{INK}" stroke-width="{LINE*0.7}"/>'
    b += f'<line x1="890" y1="860" x2="890" y2="1260" stroke="{INK}" stroke-width="{LINE*0.7}"/>'
    b += plant(890, 860, 0.9)
    # 上がり框(段差)
    b += shape("M0,1260 h1080 v34 h-1080 z", fill="#E7EFF0")
    b += shape("M0,1294 h1080 v40 h-1080 z", fill="#C6D7DA")
    b += f'<ellipse cx="660" cy="1262" rx="130" ry="16" fill="{INK}" opacity=".08"/>'
    b += standing(660, 1258, 1.08, droop=1.0, top="#E8EEF3", bottom="#C4D4DF", head_drop=36, bag=True)
    return svg(b, bg)


# ---------- 画像4: 静かな部屋、胸のあたりに弱く光る電池マーク ----------
def img4():
    bg = bg_room("#F6FBFB", "#E6F2F1", "#DCEBEA", 1300)
    b = window(130, 300, 300, 460, "#E2F1F4", '<path d="M130,640 q80,-70 150,-10 q70,-60 150,0 v120 h-300 z" fill="#CFE6DD"/>')
    b += f'<path d="M100,280 q30,260 0,520 h40 q20,-260 0,-520 z" fill="#FFFFFF" stroke="{INK}" stroke-width="{LINE*0.8}"/>'
    b += plant(900, 1180, 1.0)
    b += f'<rect x="800" y="430" width="160" height="200" rx="8" fill="#FFFFFF" stroke="{INK}" stroke-width="{LINE}"/>'
    b += f'<path d="M820,600 l40,-60 l30,40 l20,-24 l30,44 z" fill="#CFE6DD"/>'
    b += f'<ellipse cx="560" cy="1296" rx="120" ry="16" fill="{INK}" opacity=".08"/>'
    b += standing(560, 1290, 1.12, droop=0.6, top="#F3F8F8", bottom="#D4E4E6", head_drop=6)
    # 電池マーク(残量わずか)とやわらかな光
    b += ('<defs><radialGradient id="bglow"><stop offset="0" stop-color="#9FD6CF" stop-opacity=".55"/>'
          '<stop offset="1" stop-color="#9FD6CF" stop-opacity="0"/></radialGradient></defs>')
    cx, cy = 560, 760
    b += f'<circle cx="{cx}" cy="{cy}" r="120" fill="url(#bglow)"/>'
    b += f'<rect x="{cx-52}" y="{cy-26}" width="96" height="52" rx="9" fill="none" stroke="{TEAL}" stroke-width="7" opacity=".75"/>'
    b += f'<rect x="{cx+46}" y="{cy-11}" width="10" height="22" rx="3" fill="{TEAL}" opacity=".75"/>'
    b += f'<rect x="{cx-42}" y="{cy-16}" width="18" height="32" rx="4" fill="#E9A28F" opacity=".85"/>'
    return svg(b, bg)


if __name__ == "__main__":
    for i, fn in enumerate([img1, img2, img3, img4], 1):
        open(f"img{i}.svg", "w").write(fn())

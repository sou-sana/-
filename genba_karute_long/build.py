# 本編(横 1920x1080)を storyboard.json + imgNN.png から書き出す。
# ナレーションは一文ずつTTSし、文間・シーン間に間を置く。字幕はシーンの「字幕」行を濃紺帯で表示。
# usage: python3 build.py
import json
import re
import subprocess
import sys
import wave
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from tts_vv import synthesize

root = Path(__file__).parent
sb = json.loads((root / "storyboard.json").read_text())
W, H = sb["size"]
FPS = 30
LEAD = 1.0          # 冒頭の無音(PRテロップ中)
XFADE = 0.8         # 画像切り替えのクロスフェード
ZOOM = 0.04         # 1枚あたりのごく緩いズーム量
SUB_FADE = 0.3
NAVY = (0x0F, 0x2A, 0x3D)
TEAL = (0x2A, 0x7F, 0x8C)
FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
FONT_SIZE, LINE_H, PAD_Y, MAX_TEXT_W = 52, 76, 26, 1700
BAND_BOTTOM = 1068
build = root / "build"
build.mkdir(exist_ok=True)


def run(cmd):
    subprocess.run(cmd, check=True)


def font(size):
    return ImageFont.truetype(FONT, size, index=0)


# 1) 一文ずつTTS
segs = sb["segments"]
sentences = []  # (seg_index, text)
for si, s in enumerate(segs):
    for x in re.split(r"(?<=。)", s["narration"]):
        if x.strip():
            sentences.append((si, x.strip()))
wavs = [build / f"s{i:03d}.wav" for i in range(len(sentences))]
synthesize([t for _, t in sentences], sb["voice"], wavs)

# 2) タイムライン組み立て+ナレーション連結
gap_s, gap_seg = sb["sentence_gap"], sb["segment_gap"]
pcm, t = [], 0.0
params = None


def silence(sec):
    return b"\x00" * (int(params.framerate * sec) * params.sampwidth * params.nchannels)


seg_start, seg_end, sent_times = {}, {}, []
for i, ((si, _), w) in enumerate(zip(sentences, wavs)):
    with wave.open(str(w)) as f:
        params = params or f.getparams()
        data = f.readframes(f.getnframes())
        sec = f.getnframes() / f.getframerate()
    if i == 0:
        pcm.append(silence(LEAD))
        t = LEAD
    seg_start.setdefault(si, t)
    sent_times.append((si, t, t + sec))
    pcm.append(data)
    t += sec
    last_in_seg = i == len(sentences) - 1 or sentences[i + 1][0] != si
    g = gap_seg if last_in_seg else gap_s
    pcm.append(silence(g))
    t += g
    if last_in_seg:
        seg_end[si] = t
narr_end = t
end = sb["endcard"]
total = narr_end + end["seconds"]
pcm.append(silence(end["seconds"]))
with wave.open(str(build / "voice.wav"), "wb") as f:
    f.setparams(params)
    f.writeframes(b"".join(pcm))

# 3) 画像の区間(複数画像のシーンは、中央に近い文の切れ目で切り替え)
shots = []  # [img, start, end]
for si, s in enumerate(segs):
    a, b = seg_start[si], seg_end[si]
    if si == 0:
        a = 0.0
    imgs = s["images"]
    cuts = [a]
    if len(imgs) > 1:
        bounds = [st for (k, st, _) in sent_times if k == si][1:]
        for j in range(1, len(imgs)):
            target = a + (b - a) * j / len(imgs)
            cuts.append(min(bounds, key=lambda x: abs(x - target)))
    cuts.append(b)
    for j, img in enumerate(imgs):
        if shots and shots[-1][0] == img:
            shots[-1][2] = cuts[j + 1]
        else:
            shots.append([img, cuts[j], cuts[j + 1]])
shots.append([end["image"], narr_end, total])

# 4) 字幕・テロップPNG
subs = []  # (png, x, y, start, dur)
for si, s in enumerate(segs):
    lines = s["subtitle"].split("\n")
    size = FONT_SIZE
    while max(font(size).getlength(l) for l in lines) > MAX_TEXT_W:
        size -= 2
    band_h = PAD_Y * 2 + LINE_H * len(lines)
    img = Image.new("RGBA", (W, band_h), NAVY + (222,))
    d = ImageDraw.Draw(img)
    for k, line in enumerate(lines):
        d.text((W // 2, PAD_Y + LINE_H * k + LINE_H // 2), line, font=font(size), fill="white", anchor="mm")
    path = build / f"sub_{si:02d}.png"
    img.save(path)
    st = seg_start[si] - 0.2
    subs.append((path, 0, BAND_BOTTOM - band_h, st, seg_end[si] - 0.4 - st))

pr = sb["pr_telop"]
img = Image.new("RGBA", (140, 72), (0, 0, 0, 0))
d = ImageDraw.Draw(img)
d.rounded_rectangle([0, 0, 139, 71], radius=12, fill=NAVY + (215,))
d.text((70, 36), pr["text"], font=font(40), fill="white", anchor="mm")
img.save(build / "pr.png")
subs.append((build / "pr.png", W - 140 - 48, 40, 0.0, pr["seconds"]))

img = Image.new("RGBA", (W, 300), (0, 0, 0, 0))
d = ImageDraw.Draw(img)
d.text((W // 2, 90), end["title"], font=font(84), fill=NAVY, anchor="mm")
d.text((W // 2, 210), end["text"], font=font(42), fill=TEAL, anchor="mm")
img.save(build / "endcard.png")
subs.append((build / "endcard.png", 0, 640, narr_end + 0.6, end["seconds"] - 0.6))

# 5) ffmpeg 合成
def image_path(num):
    """images_a/NN.(png|jpg|jpeg|webp) があればそれを優先(他サイトで作った半リアル画像)、なければフラット版。"""
    for ext in ("png", "jpg", "jpeg", "webp", "PNG", "JPG", "JPEG", "WEBP"):
        p = root / "images_a" / f"{num:02d}.{ext}"
        if p.exists():
            return p
    return root / f"img{num:02d}.png"


inputs, filters = [], []
n = len(shots)
for k, (img, a, b) in enumerate(shots):
    length = (b - a) + (XFADE / 2 if k > 0 else 0) + (XFADE / 2 if k < n - 1 else 0)
    frames = int(round(length * FPS))
    inputs += ["-i", str(image_path(img))]
    print("image", img, "->", image_path(img).name)
    filters.append(
        f"[{k}:v]scale={W * 2}:{H * 2}:force_original_aspect_ratio=increase,crop={W * 2}:{H * 2},"
        f"zoompan=z='1+{ZOOM}*on/{frames}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s={W}x{H}:fps={FPS},"
        f"setsar=1,format=yuv420p[s{k}]")
prev = "s0"
for k in range(1, n):
    filters.append(f"[{prev}][s{k}]xfade=transition=fade:duration={XFADE}:offset={shots[k][1] - XFADE / 2:.3f}[x{k}]")
    prev = f"x{k}"
base = n
for i, (png, x, y, st, du) in enumerate(subs):
    inputs += ["-loop", "1", "-framerate", str(FPS), "-t", f"{du:.3f}", "-i", str(png)]
    filters.append(f"[{base + i}:v]format=rgba,fade=in:st=0:d={SUB_FADE}:alpha=1,"
                   f"fade=out:st={du - SUB_FADE:.3f}:d={SUB_FADE}:alpha=1,setpts=PTS+{st:.3f}/TB[t{i}]")
    filters.append(f"[{prev}][t{i}]overlay={x}:{y}:eof_action=pass[o{i}]")
    prev = f"o{i}"
filters.append(f"[{prev}]format=yuv420p[vout]")

ai = base + len(subs)
inputs += ["-i", str(build / "voice.wav")]
voice_chain = "loudnorm=I=-16:TP=-2:LRA=11,aresample=48000,aformat=channel_layouts=stereo"
if sb.get("bgm"):
    run([sys.executable, str(root / "make_piano_bgm.py"), f"{total:.3f}", str(build / "bgm.wav")])
    inputs += ["-i", str(build / "bgm.wav")]
    filters.append(f"[{ai}:a]{voice_chain}[va]")
    filters.append(f"[{ai + 1}:a]loudnorm=I=-16:TP=-2,aresample=48000,volume={sb['bgm']['gain_db']}dB[ba]")
    filters.append("[va][ba]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.84[aout]")
else:
    filters.append(f"[{ai}:a]{voice_chain}[aout]")

out = root / "outputs" / f"{sb['title']}.mp4"
out.parent.mkdir(exist_ok=True)
run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", ";".join(filters),
     "-map", "[vout]", "-map", "[aout]", "-r", str(FPS),
     "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
     "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-t", f"{total:.3f}", "-movflags", "+faststart", str(out)])

timeline = {
    "total": round(total, 2),
    "shots": [{"image": i, "start": round(a, 2), "end": round(b, 2), "sec": round(b - a, 1)} for i, a, b in shots],
    "segments": [{"id": s["id"], "start": round(seg_start[k], 2), "end": round(seg_end[k], 2)} for k, s in enumerate(segs)],
}
(build / "timeline.json").write_text(json.dumps(timeline, ensure_ascii=False, indent=1))
print(f"total {total:.1f}s -> {out}")

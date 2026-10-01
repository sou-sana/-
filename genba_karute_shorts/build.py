# 絵コンテ(storyboard.json)+ img1〜4.png から縦型ショート動画(1080x1920 / 30fps / H.264+AAC)を書き出す。
# usage: python3 build.py [storyboard.json]
import json
import subprocess
import sys
import wave
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from tts_vv import synthesize

W, H, FPS = 1080, 1920, 30
TAIL = 0.5          # 各カットの余韻(秒)
END_HOLD = 1.5      # 最終カットだけ追加する余韻(秒)
XFADE = 0.3         # 画像切り替えのクロスフェード(秒)
SUB_FADE = 0.2      # 字幕のフェードイン/アウト(秒)
NAVY = (0x0F, 0x2A, 0x3D)
FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
FONT_INDEX = 0      # Noto Sans CJK JP
FONT_SIZE, LINE_H, PAD_Y, MAX_TEXT_W = 60, 90, 48, 940
BAND_CENTER_Y = 1540  # 画面下〜中央下(人物の足元 y≈1330 より下、Shorts下部UIより上)

root = Path(__file__).parent
sb = json.loads((root / (sys.argv[1] if len(sys.argv) > 1 else "storyboard.json")).read_text())
build = root / "build"
build.mkdir(exist_ok=True)
cuts = sb["cuts"]


def run(cmd):
    subprocess.run(cmd, check=True)


def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         check=True, capture_output=True, text=True).stdout
    return float(out)


# 1) ナレーション(カットごと)
wavs = [build / f"line{i}.wav" for i in range(1, len(cuts) + 1)]
synthesize([c["narration"] for c in cuts], sb["voice_style_id"], wavs)

# 2) 連結音声: 各カット = 音声 + 余韻の無音
starts, durs, frames = [], [], []
t = 0.0
for idx, w in enumerate(wavs):
    tail = TAIL + (END_HOLD if idx == len(wavs) - 1 else 0)
    with wave.open(str(w)) as f:
        params = f.getparams()
        data = f.readframes(f.getnframes())
        sec = f.getnframes() / f.getframerate()
    silence = b"\x00" * (int(params.framerate * tail) * params.sampwidth * params.nchannels)
    frames.append(data + silence)
    starts.append(t)
    durs.append(sec + tail)
    t += sec + tail
total = t
with wave.open(str(build / "voice.wav"), "wb") as f:
    f.setparams(params)
    f.writeframes(b"".join(frames))

# 3) 字幕PNG(全幅の濃紺半透明帯+白文字、中央寄せ)
for i, c in enumerate(cuts, 1):
    lines = c["subtitle"].split("\n")
    size = FONT_SIZE
    font = ImageFont.truetype(FONT, size, index=FONT_INDEX)
    while max(font.getlength(l) for l in lines) > MAX_TEXT_W:  # はみ出す場合のみ縮小
        size -= 2
        font = ImageFont.truetype(FONT, size, index=FONT_INDEX)
    band_h = PAD_Y * 2 + LINE_H * len(lines)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    top = BAND_CENTER_Y - band_h // 2
    d.rectangle([0, top, W, top + band_h], fill=NAVY + (222,))
    for k, line in enumerate(lines):
        cy = top + PAD_Y + LINE_H * k + LINE_H // 2
        d.text((W // 2, cy), line, font=font, fill=(255, 255, 255, 255), anchor="mm")
    img.save(build / f"sub{i}.png")

# 4) 画像セグメント(同じ画像が続くカットはまとめる)
segs = []  # (image, start, end)
for i, c in enumerate(cuts):
    if segs and segs[-1][0] == c["image"]:
        segs[-1][2] = starts[i] + durs[i]
    else:
        segs.append([c["image"], starts[i], starts[i] + durs[i]])

inputs, filters = [], []
n = len(segs)
for k, (img, s, e) in enumerate(segs):
    # 切り替え点を中心に XFADE 秒重ねるため、前後に半分ずつ延長
    length = (e - s) + (XFADE / 2 if k > 0 else 0) + (XFADE / 2 if k < n - 1 else 0)
    inputs += ["-loop", "1", "-framerate", str(FPS), "-t", f"{length:.3f}", "-i", str(root / f"img{img}.png")]
    filters.append(f"[{k}:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,format=yuv420p[s{k}]")
prev = "s0"
for k in range(1, n):
    off = segs[k][1] - XFADE / 2
    filters.append(f"[{prev}][s{k}]xfade=transition=fade:duration={XFADE}:offset={off:.3f}[x{k}]")
    prev = f"x{k}"

# 字幕を時間指定で重ねる(フェードイン/アウト付き)
base = n
for i in range(len(cuts)):
    s, d = starts[i], durs[i]
    inputs += ["-loop", "1", "-framerate", str(FPS), "-t", f"{d:.3f}", "-i", str(build / f"sub{i + 1}.png")]
    filters.append(f"[{base + i}:v]format=rgba,fade=in:st=0:d={SUB_FADE}:alpha=1,"
                   f"fade=out:st={d - SUB_FADE:.3f}:d={SUB_FADE}:alpha=1,setpts=PTS+{s:.3f}/TB[t{i}]")
    filters.append(f"[{prev}][t{i}]overlay=0:0:eof_action=pass[o{i}]")
    prev = f"o{i}"
filters.append(f"[{prev}]format=yuv420p[vout]")

audio_idx = base + len(cuts)
inputs += ["-i", str(build / "voice.wav")]
out = root / "outputs" / f"{sb['title']}.mp4"
out.parent.mkdir(exist_ok=True)
run(["ffmpeg", "-y", "-v", "error", *inputs,
     "-filter_complex", ";".join(filters),
     "-map", "[vout]", "-map", f"{audio_idx}:a",
     "-r", str(FPS), "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
     "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-t", f"{total:.3f}", "-movflags", "+faststart", str(out)])

# タイミング表を残す(字幕・音声の検証用)
timeline = [{"cut": i + 1, "start": round(starts[i], 3), "end": round(starts[i] + durs[i], 3),
             "image": cuts[i]["image"], "subtitle": cuts[i]["subtitle"]} for i in range(len(cuts))]
(build / "timeline.json").write_text(json.dumps(timeline, ensure_ascii=False, indent=1))
print(f"total {total:.2f}s -> {out}")

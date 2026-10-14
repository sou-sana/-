# 静かなピアノのアンビエントBGMを合成する(外部素材なし・著作権フリー)。
# ゆっくりした分散和音+まばらな旋律+柔らかい残響。
# usage: python3 make_piano_bgm.py <秒数> [out.wav]
import sys
import wave

import numpy as np
from scipy.signal import butter, fftconvolve, sosfilt

SR = 48000
dur = float(sys.argv[1]) if len(sys.argv) > 1 else 60.0
out = sys.argv[2] if len(sys.argv) > 2 else "bgm.wav"
rng = np.random.default_rng(11)
n = int(SR * (dur + 6))
buf = np.zeros((n, 2))


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def note(t0, midi, vel, length=4.0, pan=0.5):
    """減衰する倍音で作るピアノ風の音。"""
    i0 = int(t0 * SR)
    m = int(length * SR)
    if i0 + m > n:
        m = n - i0
    if m <= 0:
        return
    t = np.arange(m) / SR
    f0 = hz(midi)
    tone = np.zeros(m)
    for k, a in enumerate([1.0, 0.45, 0.22, 0.12, 0.06], 1):
        fk = f0 * k * (1 + 0.0004 * k * k)          # わずかな非調和性
        decay = 1.6 + 0.9 * k + f0 / 600
        tone += a * np.exp(-t * decay) * np.sin(2 * np.pi * fk * t)
    tone *= np.minimum(t / 0.006, 1) * vel
    buf[i0:i0 + m, 0] += tone * (1 - pan)
    buf[i0:i0 + m, 1] += tone * pan


# Fmaj7 → Em7 → Dm7 → Cmaj7/E → Bbmaj7 → Am7 → Gsus4 → Cmaj7 (各 4 拍, 1拍=1.0秒)
prog = [
    (41, [53, 57, 60, 64]), (40, [52, 55, 59, 62]), (38, [50, 53, 57, 60]), (40, [48, 52, 55, 59]),
    (46, [50, 53, 57, 62]), (45, [48, 52, 55, 60]), (43, [50, 55, 60, 62]), (36, [52, 55, 59, 64]),
]
scale = [60, 62, 64, 65, 67, 69, 71, 72, 74, 76]
beat = 1.0
t = 0.5
bar = 0
while t < dur:
    root, chord = prog[bar % len(prog)]
    note(t, root, 0.32, 6.0, 0.45)
    order = [0, 1, 2, 3, 2, 1] if bar % 2 == 0 else [0, 2, 1, 3, 1, 2]
    for j, idx in enumerate(order[:4 if bar % 3 else 6]):
        tj = t + j * beat * (4 / (4 if bar % 3 else 6)) + rng.normal(0, 0.01)
        note(tj, chord[idx], 0.16 + 0.04 * rng.random(), 4.0, 0.35 + 0.3 * rng.random())
    # まばらな旋律(2小節に1回程度)
    if rng.random() < 0.55:
        cands = [m for m in scale if (m % 12) in {c % 12 for c in chord}]
        note(t + rng.choice([1.0, 2.0]), rng.choice(cands) + 12, 0.13, 5.0, 0.6)
    t += 4 * beat
    bar += 1

# 残響: 指数減衰ノイズのインパルス応答
ir_len = int(2.8 * SR)
ir = rng.standard_normal((ir_len, 2)) * np.exp(-np.arange(ir_len) / SR * 2.2)[:, None]
ir = sosfilt(butter(2, 5000, "low", fs=SR, output="sos"), ir, axis=0)
wet = np.stack([fftconvolve(buf[:, c], ir[:, c])[:n] for c in range(2)], axis=1)
mix = buf / np.max(np.abs(buf)) + 0.6 * wet / np.max(np.abs(wet))
mix = sosfilt(butter(2, 6000, "low", fs=SR, output="sos"), mix, axis=0)[: int(SR * dur)]
tt = np.arange(len(mix)) / SR
env = np.clip(np.minimum(tt / 3.0, (dur - tt) / 4.0), 0, 1)
mix *= ((1 - np.cos(np.pi * env)) / 2)[:, None]
mix = mix / np.max(np.abs(mix)) * 0.5
with wave.open(out, "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((mix * 32767).astype("<i2").tobytes())
print(f"bgm {dur:.1f}s -> {out}")

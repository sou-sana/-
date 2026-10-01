# 静かなネイチャー系アンビエントBGMを合成する(外部素材なし・著作権フリー)。
# やわらかいパッド和音 + 小川/そよ風のノイズ + ごく稀なチャイム。
# usage: python3 make_bgm.py <秒数> [out.wav]
import sys
import wave

import numpy as np
from scipy.signal import butter, sosfilt

SR = 48000
dur = float(sys.argv[1]) if len(sys.argv) > 1 else 40.0
out = sys.argv[2] if len(sys.argv) > 2 else "bgm.wav"
rng = np.random.default_rng(7)
n = int(SR * dur)
t = np.arange(n) / SR


def hz(midi):
    return 440.0 * 2 ** ((midi - 69) / 12)


def smooth_lfo(rate, depth, seed):
    """ゆっくり揺れる乱数LFO(0中心)。"""
    r = np.random.default_rng(seed)
    pts = r.uniform(-1, 1, int(dur * rate) + 3)
    x = np.linspace(0, len(pts) - 3, n)
    i = x.astype(int)
    f = x - i
    f = (1 - np.cos(np.pi * f)) / 2
    return depth * (pts[i] * (1 - f) + pts[i + 1] * f)


# 1) パッド: Fmaj9 → Am7 → Dm9 → Bbmaj7(各10秒、ゆっくりクロスフェード)
chords = [[41, 53, 57, 60, 64, 67], [45, 52, 57, 60, 64, 67],
          [38, 53, 57, 60, 62, 64], [46, 50, 57, 62, 65, 69]]
step, fade = 10.0, 4.0
pad = np.zeros((n, 2))
k = 0
while k * step < dur:
    s0 = k * step - fade / 2
    seg = (t >= s0) & (t < s0 + step + fade)
    tt = t[seg] - s0
    L = step + fade
    env = np.clip(np.minimum(tt / fade, (L - tt) / fade), 0, 1)
    env = (1 - np.cos(np.pi * env)) / 2
    for j, m in enumerate(chords[k % len(chords)]):
        f0 = hz(m)
        amp = 0.5 if m < 48 else 0.22
        ph = rng.uniform(0, 2 * np.pi, 2)
        for ch, det in enumerate((-0.12, 0.12)):  # 左右でわずかにデチューン
            pad[seg, ch] += amp * env * np.sin(2 * np.pi * (f0 + det) * tt + ph[ch])
    k += 1
pad *= (1 + smooth_lfo(0.25, 0.15, 1))[:, None]
pad = sosfilt(butter(2, 1800, "low", fs=SR, output="sos"), pad, axis=0)

# 2) 小川/そよ風: ブラウンノイズを帯域制限し、ゆっくり強弱をつける
white = rng.standard_normal((n, 2))
brown = sosfilt(butter(1, 400, "low", fs=SR, output="sos"), white, axis=0)
stream = sosfilt(butter(2, [250, 2200], "band", fs=SR, output="sos"), white, axis=0) * 0.2
air = sosfilt(butter(2, 3500, "low", fs=SR, output="sos"), brown * 0.6 + stream, axis=0)  # シャー音を抑える
air *= (0.7 + smooth_lfo(0.15, 0.3, 2) + 0.08 * np.sin(2 * np.pi * 0.07 * t))[:, None]

# 3) ごく稀なチャイム(ペンタトニック、柔らかい減衰)
chime = np.zeros((n, 2))
notes = [72, 74, 77, 79, 81, 84]
tc = 3.0
while tc < dur - 3:
    f0 = hz(rng.choice(notes))
    m = (t >= tc) & (t < tc + 4)
    tt = t[m] - tc
    tone = np.sin(2 * np.pi * f0 * tt) + 0.3 * np.sin(2 * np.pi * f0 * 2.01 * tt)
    tone *= np.exp(-tt * 1.3) * np.minimum(tt / 0.01, 1)
    pan = rng.uniform(0.25, 0.75)
    chime[m, 0] += tone * (1 - pan)
    chime[m, 1] += tone * pan
    tc += rng.uniform(5.0, 9.0)


def rms(x):
    return np.sqrt(np.mean(x ** 2))


mix = pad / rms(pad) * 1.0 + air / rms(air) * 0.32 + chime / max(rms(chime), 1e-9) * 0.12
# 全体のフェードイン/アウト
env = np.minimum(np.minimum(t / 2.0, (dur - t) / 2.5), 1.0)
mix *= ((1 - np.cos(np.pi * np.clip(env, 0, 1))) / 2)[:, None]
mix = mix / np.max(np.abs(mix)) * 0.5
with wave.open(out, "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((mix * 32767).astype("<i2").tobytes())
print(f"bgm {dur:.2f}s -> {out}")

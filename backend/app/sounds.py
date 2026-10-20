"""Programmatic placeholder sound assets.

Every sound in `config.SOUNDS` is synthesised with numpy and written as a 16-bit mono WAV
into `ASSETS_DIR/<id>.wav`. Existing files are never overwritten, so real recordings can
replace the placeholders by dropping a WAV with the same name — no code changes needed.
Ambient beds are synthesised to loop seamlessly (modulation uses whole cycles per clip).
"""
from __future__ import annotations

import wave
import zlib
from pathlib import Path
from typing import Callable

import numpy as np

from . import config

SR = config.SAMPLE_RATE


def _rng(name: str) -> np.random.Generator:
    return np.random.default_rng(zlib.crc32(name.encode()))


def _t(seconds: float) -> np.ndarray:
    return np.arange(int(seconds * SR)) / SR


def _bandpass(x: np.ndarray, lo: float, hi: float) -> np.ndarray:
    spec = np.fft.rfft(x)
    freqs = np.fft.rfftfreq(len(x), 1 / SR)
    spec[(freqs < lo) | (freqs > hi)] = 0
    return np.fft.irfft(spec, len(x))


def _noise(rng, n: int, lo: float, hi: float) -> np.ndarray:
    y = _bandpass(rng.standard_normal(n), lo, hi)
    return y / (np.max(np.abs(y)) + 1e-9)


def _cycles(seconds: float, per_clip: float, phase: float = 0.0) -> np.ndarray:
    """Sine with a whole number of cycles per clip so the clip loops seamlessly."""
    t = _t(seconds)
    return np.sin(2 * np.pi * round(per_clip) * t / seconds + phase)


def _decay(n: int, tau: float) -> np.ndarray:
    return np.exp(-np.arange(n) / SR / tau)


def _fade(x: np.ndarray, ms: float = 8) -> np.ndarray:
    k = min(int(SR * ms / 1000), len(x) // 2)
    if k:
        ramp = np.linspace(0, 1, k)
        x = x.copy()
        x[:k] *= ramp
        x[-k:] *= ramp[::-1]
    return x


def _place(buf: np.ndarray, sig: np.ndarray, start_s: float) -> None:
    i = int(start_s * SR)
    j = min(len(buf), i + len(sig))
    if i < len(buf):
        buf[i:j] += sig[: j - i]


def _tone(freq, seconds: float, harmonics=(1.0,)) -> np.ndarray:
    """Tone; `freq` may be a scalar or an array (instantaneous frequency)."""
    t = _t(seconds)
    f = np.full_like(t, freq) if np.isscalar(freq) else freq
    phase = 2 * np.pi * np.cumsum(f) / SR
    return sum(a * np.sin((h + 1) * phase) for h, a in enumerate(harmonics))


# ----------------------------------------------------------------------- ambient beds
def _waves(s, r):
    n = len(_t(s))
    swell = 0.55 + 0.45 * _cycles(s, 1)
    foam = _noise(r, n, 2000, 7000) * 0.25 * np.clip(_cycles(s, 1, 1.2), 0, 1)
    return _noise(r, n, 80, 1400) * swell + foam


def _wind(s, r):
    n = len(_t(s))
    gust = 0.6 + 0.25 * _cycles(s, 1) + 0.15 * _cycles(s, 3, 1)
    return _noise(r, n, 120, 900) * gust


def _insects(s, r):
    t = _t(s)
    out = np.zeros_like(t)
    for f, am in [(4200, 40), (5100, 55), (4700, 32)]:
        out += np.sin(2 * np.pi * f * t) * (0.5 + 0.5 * _cycles(s, am * s))
    return out * 0.35 * (0.6 + 0.4 * _cycles(s, 2))


def _leaves(s, r):
    n = len(_t(s))
    out = _noise(r, n, 2000, 9000) * 0.15
    for _ in range(int(s * 14)):
        k = int(r.uniform(0.01, 0.05) * SR)
        burst = _noise(r, k, 3000, 10000) * _decay(k, 0.012) * r.uniform(0.3, 1)
        out = np.roll(out, 0)
        i = int(r.uniform(0, n - k))
        out[i:i + k] += burst
    return out


def _traffic(s, r):
    t = _t(s)
    rumble = _noise(r, len(t), 40, 450) * (0.7 + 0.3 * _cycles(s, 2))
    engine = 0.15 * np.sin(2 * np.pi * 70 * t) * (0.6 + 0.4 * _cycles(s, 1))
    return rumble + engine + 0.1 * _noise(r, len(t), 500, 2500) * (0.5 + 0.5 * _cycles(s, 3, 2))


def _voices(s, r, lo, hi, rate):
    n = len(_t(s))
    out = np.zeros(n)
    for _ in range(5):
        syl = 0.5 + 0.5 * np.abs(sum(_cycles(s, r.uniform(1, rate) * s, r.uniform(0, 6)) for _ in range(3)) / 3)
        out += _noise(r, n, r.uniform(lo, lo + 300), r.uniform(hi - 800, hi)) * syl
    return out


def _crowd(s, r):
    return _voices(s, r, 250, 3200, 6)


def _chatter(s, r):
    return _voices(s, r, 300, 3400, 5)


def _children(s, r):
    t = _t(s)
    out = _voices(s, r, 600, 5000, 7)
    for k in range(6):
        f0 = r.uniform(900, 1500)
        out += 0.2 * np.sin(2 * np.pi * f0 * t * (1 + 0.05 * _cycles(s, 3 + k))) * (
            np.clip(_cycles(s, 2 + k, k), 0, 1) ** 4)
    return out


def _cheering(s, r):
    swell = 0.5 + 0.5 * _cycles(s, 1, -1.5)
    return _voices(s, r, 300, 3600, 4) * (0.4 + 0.6 * swell)


def _rain(s, r):
    n = len(_t(s))
    out = _noise(r, n, 1200, 9500) * 0.6
    for _ in range(int(s * 60)):
        k = int(0.012 * SR)
        i = int(r.uniform(0, n - k))
        out[i:i + k] += _noise(r, k, 3000, 11000) * _decay(k, 0.003) * r.uniform(0.3, 0.9)
    return out


def _clock(s, r):
    n = len(_t(s))
    out = np.zeros(n)
    k = int(0.05 * SR)
    for i in range(int(s)):
        click = _noise(r, k, 1500, 6000) * _decay(k, 0.008) * (1.0 if i % 2 == 0 else 0.7)
        _place(out, click, i + 0.0)
    return out


def _cafe_music(s, r):
    scale = [261.63, 293.66, 329.63, 392.0, 440.0, 523.25]   # C major pentatonic
    out = np.zeros(len(_t(s)))
    step = 0.5
    for i in range(int(s / step)):
        f = scale[int(r.integers(0, len(scale)))]
        note = _tone(f, step * 1.5, (1.0, 0.4, 0.15)) * _decay(int(step * 1.5 * SR), 0.5)
        _place(out, _fade(note, 5), i * step)
    return out * 0.7


# ----------------------------------------------------------------------- effects
def _seagulls(s, r):
    out = np.zeros(len(_t(s)))
    for start in (0.05, 0.7):
        d = 0.5
        t = _t(d)
        f = 2000 - 1100 * (t / d) + 60 * np.sin(2 * np.pi * 25 * t)
        out_c = _tone(f, d, (1.0, 0.5, 0.25)) * np.sin(np.pi * t / d) ** 0.7
        _place(out, out_c, start)
    return out


def _footsteps(s, r):
    out = np.zeros(len(_t(s)))
    k = int(0.18 * SR)
    for i in range(4):
        step = _noise(r, k, 60, 500) * _decay(k, 0.045) * (0.8 + 0.2 * (i % 2))
        step += 0.4 * _noise(r, k, 800, 3000) * _decay(k, 0.01)
        _place(out, step, 0.1 + i * 0.55)
    return out


def _birds(s, r):
    out = np.zeros(len(_t(s)))
    for i in range(4):
        d = 0.12
        t = _t(d)
        f = r.uniform(2400, 3200) + r.uniform(1000, 1800) * (t / d)
        chirp = _tone(f, d, (1.0, 0.3)) * np.sin(np.pi * t / d)
        _place(out, chirp, 0.05 + i * 0.3)
    return out


def _horns(s, r):
    d = s * 0.85
    env = np.clip(np.minimum(np.arange(int(d * SR)) / (0.03 * SR), 1), 0, 1)
    sig = (_tone(440, d, (1.0, 0.5, 0.3, 0.2)) + _tone(554, d, (1.0, 0.5, 0.3))) * env
    out = np.zeros(len(_t(s)))
    _place(out, _fade(sig, 20), 0.05)
    return out


def _construction(s, r):
    out = np.zeros(len(_t(s)))
    k = int(0.15 * SR)
    for i in range(3):
        hit = _noise(r, k, 500, 4000) * _decay(k, 0.02) + _tone(180, 0.15) * _decay(k, 0.03)
        _place(out, hit, 0.05 + i * 0.35)
    return out


def _umbrella(s, r):
    n = len(_t(s))
    pop = _noise(r, n, 200, 3000) * _decay(n, 0.08)
    return pop + 0.3 * _noise(r, n, 3000, 7000) * np.sin(np.pi * np.arange(n) / n)


def _chalk(s, r):
    n = len(_t(s))
    scratch = _noise(r, n, 2500, 7000) * (0.5 + 0.5 * np.abs(np.sin(2 * np.pi * 14 * _t(s))))
    return scratch * np.sin(np.pi * np.arange(n) / n)


def _cups(s, r):
    t = _t(s)
    out = sum(a * np.sin(2 * np.pi * f * t) for f, a in [(3100, 1), (4300, 0.6), (5200, 0.4)])
    return out * _decay(len(t), 0.08)


def _espresso(s, r):
    n = len(_t(s))
    hiss = _noise(r, n, 800, 6500)
    return hiss * np.sin(np.pi * np.arange(n) / n) ** 0.5


def _whistle(s, r):
    t = _t(s)
    f = 2800 + 40 * np.sin(2 * np.pi * 30 * t)
    return _tone(f, s, (1.0, 0.15)) * np.sin(np.pi * t / s) ** 0.3


def _drums(s, r):
    out = np.zeros(len(_t(s)))
    k = int(0.4 * SR)
    for i, st in enumerate((0.05, 0.6, 1.1)):
        t = np.arange(k) / SR
        kick = np.sin(2 * np.pi * np.cumsum(130 - 90 * np.minimum(t / 0.3, 1)) / SR) * _decay(k, 0.12)
        snare = 0.5 * _noise(r, k, 1000, 6000) * _decay(k, 0.05) if i == 1 else 0
        _place(out, kick + snare, st)
    return out


def _barking(s, r):
    out = np.zeros(len(_t(s)))
    k = int(0.18 * SR)
    t = np.arange(k) / SR
    for st in (0.05, 0.45):
        bark = _tone(330 - 120 * t / 0.18, 0.18, (1.0, 0.6, 0.4)) * _decay(k, 0.07)
        bark += 0.4 * _noise(r, k, 500, 2500) * _decay(k, 0.05)
        _place(out, bark, st)
    return out


_RECIPES: dict[str, Callable] = {
    "waves": _waves, "wind": _wind, "insects": _insects, "leaves": _leaves,
    "traffic": _traffic, "crowd": _crowd, "rain": _rain, "chatter": _chatter,
    "cafe_music": _cafe_music, "clock": _clock, "cheering": _cheering, "children": _children,
    "seagulls": _seagulls, "footsteps": _footsteps, "birds": _birds, "horns": _horns,
    "construction": _construction, "umbrella": _umbrella, "chalk": _chalk, "cups": _cups,
    "espresso": _espresso, "whistle": _whistle, "drums": _drums, "barking": _barking,
}


def synthesize(sound_id: str) -> np.ndarray:
    """Return float samples in [-0.9, 0.9] for a sound id."""
    spec = config.SOUNDS[sound_id]
    sig = _RECIPES[sound_id](spec.clip_seconds, _rng(sound_id))
    sig = np.asarray(sig, dtype=np.float64)
    sig = sig / (np.max(np.abs(sig)) + 1e-9) * 0.9
    return _fade(sig, 4) if spec.kind == "effect" else sig


def write_wav(path: Path, samples: np.ndarray) -> None:
    pcm = (np.clip(samples, -1, 1) * 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def asset_path(sound_id: str, assets_dir: Path | None = None) -> Path:
    return (assets_dir or config.ASSETS_DIR) / f"{sound_id}.wav"


def ensure_assets(assets_dir: Path | None = None) -> list[str]:
    """Generate any missing placeholder WAVs. Returns ids that were created."""
    d = assets_dir or config.ASSETS_DIR
    d.mkdir(parents=True, exist_ok=True)
    created = []
    for sid in config.SOUNDS:
        p = asset_path(sid, d)
        if not p.exists():
            write_wav(p, synthesize(sid))
            created.append(sid)
    return created

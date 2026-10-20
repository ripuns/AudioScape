"""Audio processing and mixing.

Per layer: ambient sounds are looped to the full duration; effects are played once or
repeated sparingly (deterministic placement); a volume percentage is applied. All layers
are summed, then normalized so the mix never clips. The same normalization gain is applied
to each per-layer stem so the frontend can offer interactive layer control while the stems
still sum to exactly the delivered mix. Output: 30-second WAV.
"""
from __future__ import annotations

import math
import random
import shutil
import uuid
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from pydub import AudioSegment

from . import config, sounds
from .models import Layer


@dataclass
class RenderResult:
    id: str
    directory: Path
    mix_path: Path
    stem_paths: dict[str, Path]
    duration_ms: int
    normalization_gain_db: float


def _load(sound_id: str, assets_dir: Path) -> AudioSegment:
    seg = AudioSegment.from_wav(str(sounds.asset_path(sound_id, assets_dir)))
    return seg.set_channels(1).set_frame_rate(config.SAMPLE_RATE).set_sample_width(2)


def _to_float(seg: AudioSegment) -> np.ndarray:
    return np.asarray(seg.get_array_of_samples(), dtype=np.float64) / 32768.0


def _volume_gain_db(percent: int) -> float:
    return 20 * math.log10(max(percent, 1) / 100)


def loop_to_duration(seg: AudioSegment, duration_ms: int) -> AudioSegment:
    reps = math.ceil(duration_ms / len(seg))
    return (seg * reps)[:duration_ms].fade_in(30).fade_out(30)


def place_effect(seg: AudioSegment, repeats: int, duration_ms: int, seed: int) -> np.ndarray:
    """Place `repeats` copies of a short effect across the soundscape, one per slot with a
    deterministic random offset so repeats are spaced out ("sparingly")."""
    total = int(duration_ms * config.SAMPLE_RATE / 1000)
    out = np.zeros(total)
    clip = _to_float(seg)
    rng = random.Random(seed)
    slot = total // max(repeats, 1)
    for i in range(max(repeats, 1)):
        room = max(slot - len(clip), 0)
        start = i * slot + (rng.randrange(room) if room else 0)
        end = min(start + len(clip), total)
        out[start:end] += clip[: end - start]
    return out


def render_layer(layer: Layer, duration_ms: int, assets_dir: Path) -> np.ndarray:
    seg = _load(layer.sound, assets_dir)
    if layer.kind == "ambient":
        samples = _to_float(loop_to_duration(seg, duration_ms))
    else:
        seed = config.EFFECT_SEED + sum(map(ord, layer.sound))
        samples = place_effect(seg, layer.repeats, duration_ms, seed)
    return samples * 10 ** (_volume_gain_db(layer.volume) / 20)


def _write(path: Path, samples: np.ndarray) -> None:
    pcm = (np.clip(samples, -1, 1) * 32767).astype("<i2")
    seg = AudioSegment(data=pcm.tobytes(), sample_width=2,
                       frame_rate=config.SAMPLE_RATE, channels=1)
    seg.export(str(path), format="wav")


def _prune(output_dir: Path, keep: int) -> None:
    dirs = sorted((d for d in output_dir.iterdir() if d.is_dir()),
                  key=lambda d: d.stat().st_mtime)
    for d in dirs[: max(len(dirs) - keep, 0)]:
        shutil.rmtree(d, ignore_errors=True)


def render_soundscape(layers: list[Layer], output_dir: Path | None = None,
                      assets_dir: Path | None = None,
                      duration_ms: int = config.OUTPUT_DURATION_MS) -> RenderResult:
    if not layers:
        raise ValueError("at least one layer is required")
    output_dir = output_dir or config.OUTPUT_DIR
    assets_dir = assets_dir or config.ASSETS_DIR
    sounds.ensure_assets(assets_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    stems = {layer.sound: render_layer(layer, duration_ms, assets_dir) for layer in layers}
    mix = np.sum(list(stems.values()), axis=0)

    # normalize to prevent clipping: peak lands at -headroom dBFS
    peak = float(np.max(np.abs(mix))) or 1.0
    scale = 10 ** (-config.NORMALIZE_HEADROOM_DB / 20) / peak
    mix *= scale

    rid = uuid.uuid4().hex[:12]
    out = output_dir / rid
    out.mkdir()
    (out / "layers").mkdir()
    stem_paths = {}
    for sid, samples in stems.items():
        stem_paths[sid] = out / "layers" / f"{sid}.wav"
        _write(stem_paths[sid], samples * scale)
    mix_path = out / "soundscape.wav"
    _write(mix_path, mix)
    _prune(output_dir, config.MAX_STORED_OUTPUTS)
    return RenderResult(rid, out, mix_path, stem_paths, duration_ms, 20 * math.log10(scale))

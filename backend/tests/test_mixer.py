import wave

import numpy as np
from pydub import AudioSegment

from app import config
from app.mapping import select_layers
from app.mixer import loop_to_duration, place_effect, render_soundscape, _load
from app import sounds


def _samples(path):
    seg = AudioSegment.from_wav(str(path))
    return np.asarray(seg.get_array_of_samples(), dtype=np.float64) / 32768


def test_mix_is_30s_wav_and_not_clipping(tmp_path):
    layers = select_layers("city", [])
    res = render_soundscape(layers, tmp_path / "out", tmp_path / "assets")
    with wave.open(str(res.mix_path)) as w:
        assert abs(w.getnframes() / w.getframerate() - 30) < 0.01
    peak = np.max(np.abs(_samples(res.mix_path)))
    assert peak <= 10 ** (-config.NORMALIZE_HEADROOM_DB / 20) + 1e-3
    assert peak > 0.5


def test_stems_sum_to_mix(tmp_path):
    res = render_soundscape(select_layers("beach", []), tmp_path / "out", tmp_path / "assets")
    total = sum(_samples(p) for p in res.stem_paths.values())
    assert np.max(np.abs(total - _samples(res.mix_path))) < 0.01
    assert set(res.stem_paths) == {"waves", "wind", "seagulls", "footsteps"}


def test_volume_percentage_scales_layer(tmp_path):
    layers = select_layers("beach", [])
    layers[0].volume, layers[1].volume = 100, 25
    res = render_soundscape(layers, tmp_path / "out", tmp_path / "assets")
    loud = np.sqrt(np.mean(_samples(res.stem_paths["waves"]) ** 2))
    soft = np.sqrt(np.mean(_samples(res.stem_paths["wind"]) ** 2))
    assert loud > soft


def test_ambient_loops_and_effects_repeat_sparingly(tmp_path):
    sounds.ensure_assets(tmp_path)
    rain = _load("rain", tmp_path)
    assert len(loop_to_duration(rain, 30_000)) == 30_000
    clip = _load("footsteps", tmp_path)
    out = place_effect(clip, 5, 30_000, seed=1)
    assert len(out) == 30 * config.SAMPLE_RATE
    active = np.abs(out) > 1e-4
    # five hits, so some but far from all of the timeline is active
    assert 0.02 < active.mean() < 0.5
    # deterministic
    assert np.array_equal(out, place_effect(clip, 5, 30_000, seed=1))

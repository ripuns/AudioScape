import wave

from app import config, sounds


def test_all_sounds_generate(tmp_path):
    created = sounds.ensure_assets(tmp_path, use_bundled=False)
    assert set(created) == set(config.SOUNDS)
    for sid, spec in config.SOUNDS.items():
        with wave.open(str(sounds.asset_path(sid, tmp_path, use_bundled=False))) as w:
            assert w.getframerate() == config.SAMPLE_RATE
            assert w.getnchannels() == 1
            assert abs(w.getnframes() / w.getframerate() - spec.clip_seconds) < 0.05


def test_existing_assets_not_overwritten(tmp_path):
    sounds.ensure_assets(tmp_path, use_bundled=False)
    p = sounds.asset_path("waves", tmp_path, use_bundled=False)
    p.write_bytes(b"custom")
    assert sounds.ensure_assets(tmp_path, use_bundled=False) == []
    assert p.read_bytes() == b"custom"


def test_every_mapped_sound_exists():
    ids = set(config.SOUNDS)
    for rules in config.SCENE_SOUNDS.values():
        assert {r.sound for r in rules} <= ids
    for by_scene in config.OBJECT_SOUNDS.values():
        assert {r.sound for r in by_scene.values()} <= ids
    assert set(config.SCENE_SOUNDS) == set(config.ENVIRONMENTS)


def test_bundled_recordings_take_priority_and_are_valid(tmp_path):
    bundled = sorted(config.BUNDLED_DIR.glob("*.wav"))
    assert bundled, "real recordings should be committed in backend/assets/sounds"
    for p in bundled:
        assert p.stem in config.SOUNDS
        assert sounds.asset_path(p.stem, tmp_path) == p
        with wave.open(str(p)) as w:
            assert (w.getframerate(), w.getnchannels(), w.getsampwidth()) == (config.SAMPLE_RATE, 1, 2)
            seconds = w.getnframes() / w.getframerate()
            assert 0.5 < seconds <= config.OUTPUT_DURATION_MS / 1000
    # only sounds without a recording get synthesised
    created = sounds.ensure_assets(tmp_path)
    assert set(created) == set(config.SOUNDS) - {p.stem for p in bundled}

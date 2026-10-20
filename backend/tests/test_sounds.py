import wave

from app import config, sounds


def test_all_sounds_generate(tmp_path):
    created = sounds.ensure_assets(tmp_path)
    assert set(created) == set(config.SOUNDS)
    for sid, spec in config.SOUNDS.items():
        with wave.open(str(sounds.asset_path(sid, tmp_path))) as w:
            assert w.getframerate() == config.SAMPLE_RATE
            assert w.getnchannels() == 1
            assert abs(w.getnframes() / w.getframerate() - spec.clip_seconds) < 0.05


def test_existing_assets_not_overwritten(tmp_path):
    sounds.ensure_assets(tmp_path)
    p = sounds.asset_path("waves", tmp_path)
    p.write_bytes(b"custom")
    assert sounds.ensure_assets(tmp_path) == []
    assert p.read_bytes() == b"custom"


def test_every_mapped_sound_exists():
    ids = set(config.SOUNDS)
    for rules in config.SCENE_SOUNDS.values():
        assert {r.sound for r in rules} <= ids
    for by_scene in config.OBJECT_SOUNDS.values():
        assert {r.sound for r in by_scene.values()} <= ids
    assert set(config.SCENE_SOUNDS) == set(config.ENVIRONMENTS)

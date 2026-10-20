"""End-to-end pipeline: image bytes -> analysis -> sound mapping -> mixed soundscape."""
from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from . import config, mapping, mixer, preprocess, vision


def run(data: bytes, scorer: vision.Scorer, output_dir: Path | None = None,
        assets_dir: Path | None = None) -> dict:
    image = preprocess.load_image(data)                                   # image processing
    scene, detections = vision.analyze(image, scorer)                     # visual understanding
    layers = mapping.select_layers(scene.label, detections)               # sound mapping
    result = mixer.render_soundscape(layers, output_dir, assets_dir)      # audio mixing

    base = f"/api/soundscapes/{result.id}"
    payload = {
        "id": result.id,
        "scene": {
            "key": scene.label,
            "label": config.ENVIRONMENT_TITLES[scene.label],
            "confidence": round(scene.confidence, 4),
            "scores": {config.ENVIRONMENT_TITLES[k]: round(v, 4)
                       for k, v in sorted(scene.scores.items(), key=lambda kv: -kv[1])},
        },
        "objects": [{"label": d.label, "score": round(d.score, 4), "box": asdict(d.box)}
                    for d in detections],
        "layers": [{**layer.to_dict(), "url": f"{base}/layers/{layer.sound}.wav"}
                   for layer in layers],
        "mix_url": f"{base}/mix.wav",
        "duration_ms": result.duration_ms,
        "normalization_gain_db": round(result.normalization_gain_db, 2),
    }
    (result.directory / "meta.json").write_text(json.dumps(payload), encoding="utf-8")
    return payload

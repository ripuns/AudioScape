"""Sound mapping engine: detected scene + objects -> selected sound layers.

All rules come from `config` (SCENE_SOUNDS / OBJECT_SOUNDS)."""
from __future__ import annotations

from . import config
from .models import Detection, Layer


def _make_layer(rule: config.LayerRule, source: str, position=None) -> Layer:
    spec = config.SOUNDS[rule.sound]
    return Layer(sound=spec.id, label=spec.label, kind=spec.kind, volume=rule.volume,
                 repeats=spec.repeats if spec.kind == "effect" else 1,
                 sources=[source], position=position)


def select_layers(scene: str, detections: list[Detection]) -> list[Layer]:
    """Scene layers first, then one layer per detected object type.

    If an object maps to a sound already selected, the layers are merged (max volume,
    sources combined) so a sound never plays twice."""
    layers: dict[str, Layer] = {}
    for rule in config.SCENE_SOUNDS[scene]:
        layers[rule.sound] = _make_layer(rule, f"scene:{scene}")

    # strongest detection per object label drives its layer
    best: dict[str, Detection] = {}
    for d in detections:
        if d.label not in best or d.score > best[d.label].score:
            best[d.label] = d

    for label, det in best.items():
        by_scene = config.OBJECT_SOUNDS.get(label)
        if not by_scene:
            continue
        rule = by_scene.get(scene, by_scene["default"])
        source = f"object:{label}"
        pos = (round(det.box.cx, 3), round(det.box.cy, 3))
        if rule.sound in layers:
            existing = layers[rule.sound]
            existing.volume = max(existing.volume, rule.volume)
            existing.sources.append(source)
            existing.position = existing.position or pos
        else:
            layers[rule.sound] = _make_layer(rule, source, pos)
    return list(layers.values())

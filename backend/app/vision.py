"""Zero-shot visual understanding with CLIP (openai/clip-vit-base-patch32).

Two paths:
  * scene classification: the full image is scored against environment prompts;
  * tiled object detection: overlapping tiles are each scored against object prompts,
    detections above a threshold keep normalized coordinates and adjacent ones are merged.
CLIP is whole-image semantic scoring, not an object detector, so boxes are coarse.
"""
from __future__ import annotations

from typing import Protocol, Sequence

import numpy as np
from PIL import Image

from . import config
from .models import Box, Detection, SceneResult


class Scorer(Protocol):
    def score(self, images: Sequence[Image.Image], prompts: Sequence[str]) -> np.ndarray:
        """Return an (n_images, n_prompts) array of probabilities (softmax over prompts)."""


class ClipScorer:
    """CLIP zero-shot scorer. The model is loaded lazily on first use."""

    def __init__(self, model_id: str = config.CLIP_MODEL_ID):
        self.model_id = model_id
        self._model = None
        self._processor = None
        self._text_cache: dict[tuple[str, ...], object] = {}

    def _load(self):
        if self._model is None:
            import torch
            from transformers import CLIPModel, CLIPProcessor
            self._torch = torch
            self._model = CLIPModel.from_pretrained(self.model_id).eval()
            self._processor = CLIPProcessor.from_pretrained(self.model_id)

    def score(self, images, prompts):
        self._load()
        torch = self._torch
        key = tuple(prompts)
        with torch.no_grad():
            if key not in self._text_cache:
                tok = self._processor(text=list(prompts), return_tensors="pt", padding=True)
                t = self._model.get_text_features(**tok)
                self._text_cache[key] = t / t.norm(dim=-1, keepdim=True)
            px = self._processor(images=list(images), return_tensors="pt")
            v = self._model.get_image_features(**px)
            v = v / v.norm(dim=-1, keepdim=True)
            logits = self._model.logit_scale.exp() * v @ self._text_cache[key].T
            return logits.softmax(dim=-1).numpy()


def classify_scene(image: Image.Image, scorer: Scorer) -> SceneResult:
    keys = list(config.ENVIRONMENTS)
    prompts = [config.SCENE_PROMPT.format(config.ENVIRONMENTS[k]) for k in keys]
    probs = scorer.score([image], prompts)[0]
    scores = {k: float(p) for k, p in zip(keys, probs)}
    top = max(scores, key=scores.get)
    return SceneResult(label=top, confidence=scores[top], scores=scores)


def make_tiles(fraction: float = config.TILE_FRACTION,
               stride: float = config.TILE_STRIDE) -> list[Box]:
    """Overlapping tiles in normalized coordinates (default: 3x3 tiles of half size)."""
    starts, s = [], 0.0
    while s + fraction <= 1 + 1e-9:
        starts.append(round(s, 6))
        s += stride
    if starts[-1] + fraction < 1 - 1e-9:
        starts.append(round(1 - fraction, 6))
    return [Box(x, y, fraction, fraction) for y in starts for x in starts]


def _touching(a: Box, b: Box, eps: float = 1e-6) -> bool:
    return (a.x <= b.x + b.w + eps and b.x <= a.x + a.w + eps and
            a.y <= b.y + b.h + eps and b.y <= a.y + a.h + eps)


def _union(a: Box, b: Box) -> Box:
    x0, y0 = min(a.x, b.x), min(a.y, b.y)
    x1, y1 = max(a.x + a.w, b.x + b.w), max(a.y + a.h, b.y + b.h)
    return Box(x0, y0, x1 - x0, y1 - y0)


def merge_adjacent(dets: list[Detection]) -> list[Detection]:
    """Merge same-label detections whose boxes overlap or touch (score = max)."""
    merged: list[Detection] = []
    for label in {d.label for d in dets}:
        groups: list[Detection] = []
        for d in (x for x in dets if x.label == label):
            groups.append(Detection(d.label, d.score, Box(d.box.x, d.box.y, d.box.w, d.box.h)))
        changed = True
        while changed:
            changed = False
            for i in range(len(groups)):
                for j in range(i + 1, len(groups)):
                    if _touching(groups[i].box, groups[j].box):
                        a, b = groups[i], groups.pop(j)
                        groups[i] = Detection(label, max(a.score, b.score), _union(a.box, b.box))
                        changed = True
                        break
                if changed:
                    break
        merged.extend(groups)
    return sorted(merged, key=lambda d: -d.score)


def detect_objects(image: Image.Image, scorer: Scorer,
                   threshold: float = config.OBJECT_THRESHOLD) -> list[Detection]:
    keys = list(config.OBJECTS)
    prompts = [config.OBJECT_PROMPT.format(config.OBJECTS[k]) for k in keys]
    prompts += list(config.BACKGROUND_PROMPTS)
    tiles = make_tiles()
    w, h = image.size
    crops = [image.crop((int(t.x * w), int(t.y * h), int((t.x + t.w) * w), int((t.y + t.h) * h)))
             for t in tiles]
    probs = scorer.score(crops, prompts)
    found = []
    for tile, row in zip(tiles, probs):
        for i, key in enumerate(keys):
            if row[i] >= threshold:
                found.append(Detection(key, float(row[i]), tile))
    return merge_adjacent(found)


def analyze(image: Image.Image, scorer: Scorer) -> tuple[SceneResult, list[Detection]]:
    return classify_scene(image, scorer), detect_objects(image, scorer)

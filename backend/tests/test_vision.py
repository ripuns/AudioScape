import io

import numpy as np
import pytest
from PIL import Image

from app import config
from app.models import Box, Detection
from app.preprocess import load_image
from app.vision import analyze, classify_scene, detect_objects, make_tiles, merge_adjacent


class FakeScorer:
    """Scene prompts -> beach; tile prompts -> bird in top-right tile region, person bottom-left."""

    def score(self, images, prompts):
        n, k = len(images), len(prompts)
        out = np.full((n, k), 0.01)
        scene_keys = [config.SCENE_PROMPT.format(v) for v in config.ENVIRONMENTS.values()]
        if prompts[0] == scene_keys[0]:
            out[:, :] = 0.01
            out[:, 0] = 0.91
            return out
        obj_keys = list(config.OBJECTS)
        for i, im in enumerate(images):
            px = np.asarray(im).mean(axis=(0, 1))
            if px[0] > 200:      # red tile -> bird
                out[i, obj_keys.index("bird")] = 0.87
            if px[2] > 200:      # blue tile -> person
                out[i, obj_keys.index("person")] = 0.94
        return out


def png_bytes(size=(400, 300), color=(10, 10, 10)):
    buf = io.BytesIO()
    Image.new("RGB", size, color).save(buf, "PNG")
    return buf.getvalue()


def test_load_image_downscales_and_converts():
    img = load_image(png_bytes((3000, 1500)))
    assert img.mode == "RGB" and max(img.size) == config.MAX_IMAGE_SIDE


def test_load_image_rejects_garbage():
    with pytest.raises(ValueError):
        load_image(b"not an image")


def test_tiles_overlap_and_cover_image():
    tiles = make_tiles()
    assert len(tiles) == 9
    assert all(0 <= t.x and t.x + t.w <= 1 + 1e-9 for t in tiles)
    assert tiles[0].x + tiles[0].w > tiles[1].x   # overlapping
    assert max(t.x + t.w for t in tiles) == pytest.approx(1)


def test_scene_classification():
    res = classify_scene(Image.new("RGB", (64, 64)), FakeScorer())
    assert res.label == "beach" and res.confidence == pytest.approx(0.91)
    assert set(res.scores) == set(config.ENVIRONMENTS)


def test_merge_adjacent_same_label():
    a = Detection("bird", 0.6, Box(0, 0, 0.5, 0.5))
    b = Detection("bird", 0.9, Box(0.25, 0, 0.5, 0.5))
    far = Detection("bird", 0.7, Box(0.9, 0.9, 0.05, 0.05))
    other = Detection("person", 0.8, Box(0, 0, 0.5, 0.5))
    out = merge_adjacent([a, b, far, other])
    birds = [d for d in out if d.label == "bird"]
    assert len(birds) == 2 and len(out) == 3
    big = max(birds, key=lambda d: d.box.w)
    assert big.score == 0.9 and big.box.w == pytest.approx(0.75)


def test_detect_objects_keeps_normalized_boxes_above_threshold():
    img = Image.new("RGB", (300, 300), (255, 0, 0))  # every tile "red" -> bird everywhere
    dets = detect_objects(img, FakeScorer())
    assert [d.label for d in dets] == ["bird"]
    assert dets[0].score == pytest.approx(0.87)
    b = dets[0].box
    assert (b.x, b.y, b.w, b.h) == pytest.approx((0, 0, 1, 1))
    assert detect_objects(Image.new("RGB", (300, 300)), FakeScorer()) == []


def test_analyze_returns_both_paths():
    scene, dets = analyze(Image.new("RGB", (90, 90), (0, 0, 255)), FakeScorer())
    assert scene.label == "beach" and dets[0].label == "person"

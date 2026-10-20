import io

import numpy as np
from fastapi.testclient import TestClient
from PIL import Image

from app import config
from app.main import create_app


class BeachScorer:
    def score(self, images, prompts):
        out = np.full((len(images), len(prompts)), 0.01)
        if prompts[0] == config.SCENE_PROMPT.format(config.ENVIRONMENTS["beach"]):
            out[:, 0] = 0.91
        else:
            out[:, list(config.OBJECTS).index("bird")] = 0.87
        return out


def png(color=(120, 160, 200)):
    buf = io.BytesIO()
    Image.new("RGB", (320, 240), color).save(buf, "PNG")
    return buf.getvalue()


def client(tmp_path):
    return TestClient(create_app(BeachScorer(), tmp_path / "out", tmp_path / "assets"))


def test_health_and_config(tmp_path):
    c = client(tmp_path)
    assert c.get("/api/health").json()["status"] == "ok"
    cfg = c.get("/api/config").json()
    assert len(cfg["environments"]) == len(config.ENVIRONMENTS) >= 19
    assert sum(len(v) for v in cfg["groups"].values()) == len(config.ENVIRONMENTS)
    assert [r["sound"] for r in cfg["scene_sounds"]["beach"]] == [
        "waves", "wind", "seagulls", "footsteps"]


def test_beach_end_to_end(tmp_path):
    c = client(tmp_path)
    r = c.post("/api/soundscape", files={"image": ("beach.png", png(), "image/png")})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["scene"]["key"] == "beach" and body["scene"]["confidence"] == 0.91
    assert body["objects"][0]["label"] == "bird"
    sounds = {layer["sound"] for layer in body["layers"]}
    assert {"waves", "wind", "seagulls", "footsteps"} <= sounds and "birds" not in sounds
    assert body["duration_ms"] == 30000

    mix = c.get(body["mix_url"])
    assert mix.status_code == 200 and mix.headers["content-type"] == "audio/wav"
    assert mix.content[:4] == b"RIFF"
    layer = c.get(body["layers"][0]["url"])
    assert layer.status_code == 200
    assert c.get(f"/api/soundscapes/{body['id']}").json()["id"] == body["id"]


def test_rejects_non_image_and_unknown_ids(tmp_path):
    c = client(tmp_path)
    assert c.post("/api/soundscape", files={"image": ("x.png", b"nope", "image/png")}
                  ).status_code == 400
    assert c.get("/api/soundscapes/abcdefabcdef/mix.wav").status_code == 404
    assert c.get("/api/soundscapes/..%2f..%2fetc/mix.wav").status_code == 404

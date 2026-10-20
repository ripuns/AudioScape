"""FastAPI backend. No database, no authentication; files live on the local filesystem."""
from __future__ import annotations

import json
import re
from contextlib import asynccontextmanager
from dataclasses import asdict
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from . import config, pipeline, sounds
from .vision import ClipScorer, Scorer

_ID = re.compile(r"^[0-9a-f]{12}$")


def create_app(scorer: Scorer | None = None, output_dir: Path | None = None,
               assets_dir: Path | None = None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(_app):
        sounds.ensure_assets(asset_dir)
        yield

    app = FastAPI(title="AudioScape", version="1.0.0", lifespan=lifespan)
    app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173",
                                                      "http://127.0.0.1:5173"],
                       allow_methods=["*"], allow_headers=["*"])
    out_dir = output_dir or config.OUTPUT_DIR
    asset_dir = assets_dir or config.ASSETS_DIR
    clip = scorer or ClipScorer()

    @app.get("/api/health")
    def health():
        return {"status": "ok", "model": config.CLIP_MODEL_ID}

    @app.get("/api/config")
    def get_config():
        return {
            "environments": config.ENVIRONMENT_TITLES,
            "groups": {g: list(keys) for g, keys in config.ENVIRONMENT_GROUPS.items()},
            "objects": list(config.OBJECTS),
            "duration_ms": config.OUTPUT_DURATION_MS,
            "scene_sounds": {k: [asdict(r) for r in v] for k, v in config.SCENE_SOUNDS.items()},
            "object_sounds": {k: {s: asdict(r) for s, r in v.items()}
                              for k, v in config.OBJECT_SOUNDS.items()},
            "sounds": {k: asdict(v) for k, v in config.SOUNDS.items()},
        }

    @app.post("/api/soundscape")
    def create_soundscape(image: UploadFile = File(...)):
        data = image.file.read(config.MAX_UPLOAD_BYTES + 1)
        if len(data) > config.MAX_UPLOAD_BYTES:
            raise HTTPException(413, "image too large")
        try:
            return pipeline.run(data, clip, out_dir, asset_dir)
        except ValueError as exc:
            raise HTTPException(400, str(exc))

    def _dir(sid: str) -> Path:
        d = out_dir / sid
        if not _ID.match(sid) or not d.is_dir():
            raise HTTPException(404, "soundscape not found")
        return d

    @app.get("/api/soundscapes/{sid}")
    def get_soundscape(sid: str):
        return json.loads((_dir(sid) / "meta.json").read_text(encoding="utf-8"))

    @app.get("/api/soundscapes/{sid}/mix.wav")
    def get_mix(sid: str):
        return FileResponse(_dir(sid) / "soundscape.wav", media_type="audio/wav",
                            filename="audioscape-soundscape.wav")

    @app.get("/api/soundscapes/{sid}/layers/{sound}.wav")
    def get_layer(sid: str, sound: str):
        if sound not in config.SOUNDS:
            raise HTTPException(404, "unknown sound")
        path = _dir(sid) / "layers" / f"{sound}.wav"
        if not path.exists():
            raise HTTPException(404, "layer not in this soundscape")
        return FileResponse(path, media_type="audio/wav")

    return app


app = create_app()

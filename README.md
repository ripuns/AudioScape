# AudioScape

**Transforming visual scenes into interactive soundscapes — Image → Waveform → Audio**

Upload an image; AudioScape understands the scene, detects visual elements, maps them to
sound assets, mixes the layers and produces an interactive 30-second soundscape. A beach
photo evokes waves, wind, seagulls and footsteps — not just the label "beach".

Authors: Ripun Sethia (23BIT0421), Yash Joshi (23BIT0137), Lakshya Gupta (23BIT0103).

See [docs/SPEC.md](docs/SPEC.md) for the full specification and where each requirement lives.

## Stack
- Frontend: React + Vite + Web Audio API
- Backend: Python + FastAPI
- Vision: CLIP (`openai/clip-vit-base-patch32`), zero-shot
- Image: Pillow · Audio: pydub + FFmpeg
- Storage: local filesystem (no database, no auth)

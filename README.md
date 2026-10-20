# AudioScape

**Transforming visual scenes into interactive soundscapes — Image → Waveform → Audio**

Upload an image; AudioScape understands the scene, detects visual elements, maps them to
sound assets, mixes the audio layers and produces an interactive 30-second soundscape. A beach
photo evokes waves, wind, seagulls and footsteps — not just the label "beach".

Authors: Ripun Sethia (23BIT0421), Yash Joshi (23BIT0137), Lakshya Gupta (23BIT0103).

The full specification, and where each requirement lives in the code, is in
[docs/SPEC.md](docs/SPEC.md).

## How it works

```
Image Upload → Visual Understanding → Sound Mapping → Audio Mixing → Interactive Playback
   (React)     Pillow + CLIP (2 paths)   config-driven     pydub, normalize     Web Audio API
```

**Visual understanding (CLIP zero-shot, `openai/clip-vit-base-patch32`)**
- *Scene classification* — the full image is scored against the environment prompts. 19 are
  supported, in four groups: **Nature** (Beach, Forest, Park, Mountain, Lake, Countryside),
  **Urban** (City, Rainy Street, Market, Railway Station, Highway), **Home & indoor** (Classroom,
  Cafe, Kitchen, Library, Office) and **Other** (Stadium, Harbour, Place of Worship). The deck's
  original eight are included; the rest extend it, and adding more is a config-only change.
- *Tiled object detection* — the image is split into overlapping tiles (3×3 half-size tiles);
  each tile is scored against object prompts (person, bird, car, dog, umbrella, crowd, boat, train, cow) plus
  background prompts. Tiles above the threshold keep normalized coordinates and adjacent
  same-label tiles are merged. Boxes are coarse — this is not YOLO/COCO-precise, and no second
  detection model is used.

**Sound mapping** — [backend/app/config.py](backend/app/config.py) holds every mapping
(scene → sounds, object → sounds, volumes, repeats). Example: Beach → Waves + Wind + Seagulls +
Footsteps; a detected bird on a beach → Seagulls; a detected person → Footsteps. Object
positions are preserved on each layer for future spatial audio but are not used yet.

**Audio processing** — ambient sounds loop to 30 s; short effects play once or are repeated
sparingly with deterministic spacing; each layer gets a volume percentage; layers are summed and
normalized so the mix never clips. Output is a 30-second WAV. The same normalization gain is
applied to per-layer stems, so the player can offer a *Final mix* mode and a *Layers* mode where
each sound can be muted or rebalanced (stems sum to the mix).

**Playback** — Web Audio API player with play/pause/seek, a clickable waveform of the final mix,
a live frequency/waveform visualizer, per-layer controls and WAV download.

**Assets** — real recordings (Wikimedia Commons: CC0 / public domain / CC BY / CC BY-SA) are
bundled in [backend/assets/sounds/](backend/assets/sounds/) — see
[CREDITS.md](backend/assets/sounds/CREDITS.md) for authors and licences. Sounds without a
recording (rain, clock, cups) fall back to programmatic placeholder WAVs generated into
`backend/storage/assets/`. To swap any sound, drop a WAV named `<sound id>.wav` (e.g. `waves.wav`)
into `backend/assets/sounds/` — no code changes needed. Two tools help:
- `python tools/fetch_sounds.py [ids...]` — re-download and convert the bundled recordings
  (FFmpeg via `imageio-ffmpeg`; crossfades ambient beds into seamless loops, level-matches).
- `python tools/eval_scenes.py [n]` — downloads real Commons photos for every environment and reports
  scene-classification accuracy and confusions (about 75% top-1 / 87% top-3 over 19 scenes on
  auto-sourced, noisy photos; most errors are look-alikes such as lake vs. mountain or city vs. highway).
- `python tools/audit_sounds.py [dir|--synth]` — scores every sound with an AudioSet classifier
  (Audio Spectrogram Transformer) to check it is recognised as the right thing. The first
  synthetic placeholders scored near zero for most sounds (crowd/chatter/cheering/children read as
  "rain on surface"/"static"); the real recordings score 0.4–0.9 for 19 of 22 audited sounds.

## Stack
- Frontend: React + Vite + Web Audio API
- Backend: Python + FastAPI
- Vision: CLIP (`openai/clip-vit-base-patch32`) · Image: Pillow
- Audio: pydub (+ FFmpeg) · Storage: local filesystem — no database, no authentication

## Run it

Requirements: Python 3.10+, Node 18+. FFmpeg is only needed if you replace placeholders with
non-WAV files; the built-in WAV pipeline works without it.

```bash
# backend (http://127.0.0.1:8000)
cd backend
pip install -r requirements.txt
uvicorn app.main:app --port 8000        # first request downloads the CLIP model (~600 MB)

# frontend (http://localhost:5173, proxies /api to the backend)
cd frontend
npm install
npm run dev
```

Tests: `cd backend && python -m pytest`

## API
| Method | Path | Purpose |
|---|---|---|
| GET | `/api/health` | status |
| GET | `/api/config` | environments, mappings, sound catalog |
| POST | `/api/soundscape` | multipart `image` → scene, objects, layers, URLs |
| GET | `/api/soundscapes/{id}` | stored result metadata |
| GET | `/api/soundscapes/{id}/mix.wav` | final 30 s normalized mix |
| GET | `/api/soundscapes/{id}/layers/{sound}.wav` | one layer stem |

## Future scope — spatial audio (Level 3)
Bounding-box data is already kept per layer (`Layer.position`), so stereo panning from object
x-position, distance-based attenuation and binaural rendering can be added without redesign
(e.g. a bird at x=82% → seagulls panned right). Not implemented in the current level.

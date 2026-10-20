# AudioScape — Project Specification

*Transforming Visual Scenes into Interactive Soundscapes — Image → Waveform → Audio*

Team: Ripun Sethia (23BIT0421), Yash Joshi (23BIT0137), Lakshya Gupta (23BIT0103)

This document records the reference presentation, slide by slide, and where each
requirement lives in the codebase.

## 1. Problem
Images communicate only through the visual channel; existing apps display images,
apply effects, caption them or build slideshows. AudioScape asks whether the visual
information in an image can become an auditory representation of its environment.
A beach image should evoke waves, wind, birds and footsteps — not just the label "beach".

## 2. Pipeline
Image Upload → Visual Understanding → Sound Mapping → Audio Mixing → interactive soundscape.
Beach example: beach scene → waves + wind; bird detected → seagulls; person detected →
footsteps → final mixed soundscape.

| Stage | Code |
|---|---|
| Image Upload | `frontend/src/components/UploadPanel.jsx`, `POST /api/soundscape` |
| Visual Understanding | `backend/app/preprocess.py`, `vision.py` |
| Sound Mapping | `backend/app/mapping.py`, `config.py` |
| Audio Mixing | `backend/app/mixer.py` |

## 3. Multimedia integration
Core contribution is integration of visual and auditory media via coordinated processing:
image processing, semantic analysis, audio mixing, normalization, interactive playback,
audio visualization.

| Item | Code |
|---|---|
| Image processing | `preprocess.py` (Pillow) |
| Semantic analysis | `vision.py` (CLIP) |
| Audio mixing | `mixer.py` (pydub) |
| Normalization | `mixer.py` (`normalize`, applied to mix and stems) |
| Interactive playback | `frontend/src/components/Player.jsx` (Web Audio API) |
| Audio visualization | `frontend/src/components/Visualizer.jsx` (AnalyserNode) |

## 4. Architecture / stack
- Frontend: React + Vite + Web Audio API
- Backend: Python + FastAPI
- Vision: CLIP — `openai/clip-vit-base-patch32`
- Image: Pillow
- Audio: pydub + FFmpeg
- Storage: local filesystem; no database, no authentication
- Audio assets are programmatically generated placeholder WAV files (`backend/app/sounds.py`)

## 5. Computer vision approach
CLIP zero-shot mode: images scored against custom text prompts ("a photo of a beach",
"a photo of a bird", "a photo of a forest"). One model handles scene classification and
object presence; labels map directly to supported environments; no training data.
Limitation: CLIP is whole-image semantic scoring, not object detection, so tiled image
analysis is used for coarse localization.

## 6. Two-path analysis
- **Scene classification** — CLIP scores the full image against environment labels (e.g. Beach 91%).
- **Tiled object detection** — the image is divided into overlapping tiles; CLIP scores each
  tile against object labels (e.g. Bird 87%, Person 94%). Detections above a threshold are
  kept with normalized tile coordinates and merged where adjacent.
- Boxes are coarse, not YOLO/COCO-precise; no second detection model.

## 7. Controlled scope — 8 environments
Beach, Forest, Classroom, City, Cafe, Stadium, Park, Rainy Street.

| Environment | Sounds |
|---|---|
| Beach | Waves + Wind + Seagulls + Footsteps |
| Forest | Birds + Wind + Insects + Leaves |
| City | Traffic + Horns + Crowd + Construction |
| Rainy Street | Rain + Traffic + Umbrella + Footsteps |

Classroom, Cafe, Stadium and Park mappings are not given in the deck; they are defined in
`config.py` in the same style. Sounds started as generated placeholder WAVs; real recordings
(`backend/assets/sounds/`) now replace most of them without architectural changes, exactly as
the deck anticipates.

## 8. Visual information → audio
Detected scene & objects → mapping engine → selected sound layers.
- Mappings live centrally in configuration (`config.py`), not hard-coded across the app.
- Object position data from tiling is preserved for future scope; the current implementation
  does not use it.

Audio processing pipeline:
- Ambient sounds looped to 30 s
- Short effects played once or repeated sparingly
- Each layer has a volume percentage
- All layers mixed, then normalized to prevent clipping
- Output: 30-second WAV soundscape

## 9. Future scope — spatial audio (Level 3)
Preserved bounding-box data enables stereo panning by object x-position, distance-based
attenuation, and binaural/spatial rendering. Current: bird detected → seagull sound.
Future: bird at x=82% → seagulls panned right. (Not implemented; `Layer.position` carries the data.)

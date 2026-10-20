"""Central configuration for AudioScape.

All scene/object -> sound mappings, CLIP labels, thresholds and audio parameters live
here so nothing is hard-coded elsewhere in the application.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

# --------------------------------------------------------------------------- paths
BASE_DIR = Path(__file__).resolve().parent.parent
STORAGE_DIR = BASE_DIR / "storage"
ASSETS_DIR = STORAGE_DIR / "assets"      # generated placeholder WAVs (replaceable)
BUNDLED_DIR = BASE_DIR / "assets" / "sounds"   # real recordings (committed); override synthesised placeholders
OUTPUT_DIR = STORAGE_DIR / "outputs"     # rendered soundscapes
MAX_STORED_OUTPUTS = 50

# --------------------------------------------------------------------------- vision
CLIP_MODEL_ID = "openai/clip-vit-base-patch32"
MAX_IMAGE_SIDE = 1024            # Pillow preprocessing downscale limit
MAX_UPLOAD_BYTES = 15 * 1024 * 1024

SCENE_PROMPT = "a photo of a {}"
OBJECT_PROMPT = "a photo of a {}"

# Supported environments (8): key -> text used in the CLIP prompt
ENVIRONMENTS: dict[str, str] = {
    "beach": "beach",
    "forest": "forest",
    "classroom": "classroom",
    "city": "busy city street",
    "cafe": "cafe",
    "stadium": "stadium",
    "park": "park",
    "rainy_street": "rainy street",
}
ENVIRONMENT_TITLES: dict[str, str] = {
    "beach": "Beach", "forest": "Forest", "classroom": "Classroom", "city": "City",
    "cafe": "Cafe", "stadium": "Stadium", "park": "Park", "rainy_street": "Rainy Street",
}

# Object labels scored per tile: key -> CLIP prompt text
OBJECTS: dict[str, str] = {
    "person": "person",
    "bird": "bird",
    "car": "car",
    "dog": "dog",
    "umbrella": "umbrella",
    "crowd": "crowd of people",
}
# Negative / background prompts so a tile with no object does not force a match
BACKGROUND_PROMPTS: tuple[str, ...] = (
    "a photo of empty scenery",
    "a photo of sky",
    "a photo of the ground",
    "a photo of a wall",
    "a photo of water",
    "a photo of plants",
)

# Tiled analysis
TILE_FRACTION = 0.5        # tile edge as a fraction of the image edge
TILE_STRIDE = 0.25         # step between tiles (fraction) -> overlapping tiles
OBJECT_THRESHOLD = 0.5     # min tile probability for a detection to be kept

# --------------------------------------------------------------------------- audio
SAMPLE_RATE = 44100
OUTPUT_DURATION_MS = 30_000    # final soundscape length
NORMALIZE_HEADROOM_DB = 1.0
EFFECT_SEED = 7                # deterministic effect placement


@dataclass(frozen=True)
class SoundSpec:
    """A sound asset. `ambient` sounds are looped to full length; `effect` sounds are
    played once or repeated sparingly (`repeats` times across the soundscape)."""
    id: str
    label: str
    kind: str                  # "ambient" | "effect"
    repeats: int = 1           # effects only
    clip_seconds: float = 4.0  # length of generated placeholder


SOUNDS: dict[str, SoundSpec] = {s.id: s for s in [
    # ambient beds
    SoundSpec("waves", "Waves", "ambient", clip_seconds=6),
    SoundSpec("wind", "Wind", "ambient", clip_seconds=6),
    SoundSpec("insects", "Insects", "ambient", clip_seconds=4),
    SoundSpec("leaves", "Leaves", "ambient", clip_seconds=5),
    SoundSpec("traffic", "Traffic", "ambient", clip_seconds=6),
    SoundSpec("crowd", "Crowd", "ambient", clip_seconds=6),
    SoundSpec("rain", "Rain", "ambient", clip_seconds=5),
    SoundSpec("chatter", "Chatter", "ambient", clip_seconds=6),
    SoundSpec("cafe_music", "Cafe Music", "ambient", clip_seconds=8),
    SoundSpec("clock", "Clock Ticking", "ambient", clip_seconds=4),
    SoundSpec("cheering", "Cheering", "ambient", clip_seconds=6),
    SoundSpec("children", "Children Playing", "ambient", clip_seconds=6),
    SoundSpec("birds", "Birds", "ambient", clip_seconds=6),
    SoundSpec("umbrella", "Rain on Umbrella", "ambient", clip_seconds=5),
    SoundSpec("classroom", "Classroom Ambience", "ambient", clip_seconds=6),
    # one-shot / sparse effects
    SoundSpec("seagulls", "Seagulls", "effect", repeats=3, clip_seconds=1.6),
    SoundSpec("footsteps", "Footsteps", "effect", repeats=2, clip_seconds=2.4),
    SoundSpec("horns", "Horns", "effect", repeats=3, clip_seconds=1.0),
    SoundSpec("construction", "Construction", "effect", repeats=3, clip_seconds=1.2),
        SoundSpec("chalk", "Chalk on Board", "effect", repeats=3, clip_seconds=1.2),
    SoundSpec("cups", "Cups & Cutlery", "effect", repeats=5, clip_seconds=0.7),
    SoundSpec("espresso", "Espresso Machine", "effect", repeats=2, clip_seconds=2.5),
    SoundSpec("whistle", "Whistle", "effect", repeats=2, clip_seconds=1.0),
    SoundSpec("drums", "Drums", "effect", repeats=2, clip_seconds=2.0),
    SoundSpec("barking", "Dog Barking", "effect", repeats=3, clip_seconds=0.9),
]}


@dataclass(frozen=True)
class LayerRule:
    sound: str
    volume: int   # percent, 0-100


# Scene -> layers (slide: "Example Sound Mappings" + the four environments not listed there)
SCENE_SOUNDS: dict[str, tuple[LayerRule, ...]] = {
    "beach": (LayerRule("waves", 90), LayerRule("wind", 45),
              LayerRule("seagulls", 55), LayerRule("footsteps", 40)),
    "forest": (LayerRule("birds", 60), LayerRule("wind", 40),
               LayerRule("insects", 50), LayerRule("leaves", 55)),
    "city": (LayerRule("traffic", 85), LayerRule("horns", 50),
             LayerRule("crowd", 55), LayerRule("construction", 45)),
    "rainy_street": (LayerRule("rain", 90), LayerRule("traffic", 55),
                     LayerRule("umbrella", 35), LayerRule("footsteps", 40)),
    "classroom": (LayerRule("classroom", 70), LayerRule("chalk", 40),
                  LayerRule("clock", 35), LayerRule("footsteps", 30)),
    "cafe": (LayerRule("chatter", 60), LayerRule("cups", 45),
             LayerRule("espresso", 45), LayerRule("cafe_music", 35)),
    "stadium": (LayerRule("crowd", 80), LayerRule("cheering", 70),
                LayerRule("whistle", 45), LayerRule("drums", 50)),
    "park": (LayerRule("birds", 55), LayerRule("wind", 40),
             LayerRule("children", 50), LayerRule("footsteps", 35)),
}

# Object -> sound. Keyed by scene with "default" fallback (slide: bird -> seagulls on a beach).
OBJECT_SOUNDS: dict[str, dict[str, LayerRule]] = {
    "bird": {"beach": LayerRule("seagulls", 60), "default": LayerRule("birds", 60)},
    "person": {"default": LayerRule("footsteps", 45)},
    "car": {"default": LayerRule("horns", 45)},
    "dog": {"default": LayerRule("barking", 50)},
    "umbrella": {"default": LayerRule("umbrella", 40)},
    "crowd": {"default": LayerRule("crowd", 60)},
}

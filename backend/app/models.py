from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass
class Box:
    """Coarse region in normalized image coordinates (0-1). Not YOLO/COCO-precise."""
    x: float
    y: float
    w: float
    h: float

    @property
    def cx(self) -> float:
        return self.x + self.w / 2

    @property
    def cy(self) -> float:
        return self.y + self.h / 2


@dataclass
class Detection:
    label: str
    score: float
    box: Box


@dataclass
class SceneResult:
    label: str                      # top environment key
    confidence: float
    scores: dict[str, float]        # every environment -> probability


@dataclass
class Layer:
    sound: str
    label: str
    kind: str                       # ambient | effect
    volume: int                     # percent
    repeats: int = 1
    sources: list[str] = field(default_factory=list)   # e.g. ["scene:beach", "object:bird"]
    # Normalized (x, y) of the triggering object. Preserved for future spatial audio
    # (stereo panning / attenuation); the current mixer does not use it.
    position: tuple[float, float] | None = None

    def to_dict(self) -> dict:
        return asdict(self)

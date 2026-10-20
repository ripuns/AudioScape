"""Download real sound recordings from Wikimedia Commons (CC0 / public domain / CC BY / CC BY-SA)
and convert them into AudioScape assets in backend/assets/sounds/.

Each entry is resolved by a Commons search + title match, downloaded (only the byte range
needed for long files), cut to the chosen excerpt, converted to 44.1 kHz mono 16-bit WAV and
level-matched. Ambient beds are crossfaded so they loop seamlessly. A CREDITS.md with the
author and licence of every file is written alongside.

    python tools/fetch_sounds.py            # fetch everything
    python tools/fetch_sounds.py waves wind # fetch only these ids

Needs FFmpeg (`pip install imageio-ffmpeg` provides a binary).
"""
from __future__ import annotations

import html
import json
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request
import wave
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app import config, sounds  # noqa: E402

API = "https://commons.wikimedia.org/w/api.php"
UA = {"User-Agent": "AudioScapeStudentProject/1.0 (https://github.com/ripuns/AudioScape)"}
SR = config.SAMPLE_RATE
LOOP_XFADE_S = 1.0

# id, search query, title substring, extension (optional), start s, duration s, kind
MANIFEST = [
    ("waves", "ocean waves", "Oceanwavescrushing", None, 10, 25, "ambient"),
    ("wind", "Wind sounds 2020-05-10", "Wind sounds 2020-05-10 1625", None, 20, 22, "ambient"),
    ("insects", "Grillenzirpen", "Grillenzirpen - nachts um 3", ".ogg", 3, 25, "ambient"),
    ("leaves", "rustling", "Rustling leaves (Gravity Sound)", None, 0, 17, "ambient"),
    ("traffic", "road traffic", "street traffic Berlin", None, 0, 28, "ambient"),
    ("crowd", "crowd", "large-crowd-medium-distance", None, 5, 25, "ambient"),
    ("chatter", "Cafe ambiance", "Cafe ambiance", None, 60, 28, "ambient"),
    ("classroom", "Ambient classroom mono", "Ambient classroom mono", None, 5, 28, "ambient"),
    ("cafe_music", "Jazz at the park", "Jazz at the park", None, 10, 28, "ambient"),
    ("cheering", "football match", "Match amical France-USA", None, 0, 28, "ambient"),
    ("children", "children laughing", "children playing in a park", None, 0, 28, "ambient"),
    ("umbrella", "rain on roof", "Dion-Bouton, regen", None, 10, 25, "ambient"),
    ("birds", "forest birds", "Birds forest.ogg", None, 0, 14, "ambient"),
    ("seagulls", "seagull", "Gull 1.ogg", None, 0, 6, "effect"),
    ("footsteps", "steps running", "Forest track 4", None, 0, 9, "effect"),
    ("horns", "car horn", "Car Horn", None, 0, 2.5, "effect"),
    ("construction", "construction noise", "Baustelle am", None, 10, 8, "effect"),
    ("barking", "dog bark", "Barking of a dog 2.ogg", None, 0, 3.8, "effect"),
    ("whistle", "whistle referee", "referee-whistle-blow", None, 0, 3.0, "effect"),
    ("drums", "drum kit", "Drum beat.ogg", None, 0, 8, "effect"),
    ("chalk", "chalk blackboard", "Chalkboard-writing", None, 4, 6, "effect"),
    ("espresso", "espresso", "Espresso machine.ogg", None, 2, 10, "effect"),
    ("stream", "stream water", "433589 jackthemurray", None, 5, 25, "ambient"),
    ("lapping", "lake", "Escucha desde la orilla", None, 0, 30, "ambient"),
    ("frogs", "frogs", "Chorus of Frogs", None, 0, 24, "ambient"),
    ("rooster", "rooster", "Small rooster crowing", None, 0, 6, "effect"),
    ("cows", "cattle", "Single Cow Moo", None, 0, 3.5, "effect"),
    ("train", "train arriving", "Tielingxi", None, 0, 20, "effect"),
    ("station", "city ambience", "TheStationTunnelOfTheTampereStation", None, 5, 28, "ambient"),
    ("market", "market", "Pantami Market", None, 30, 28, "ambient"),
    ("highway", "road traffic", "De una calle tranquila a una avenida", None, 60, 28, "ambient"),
    ("kitchen", "kitchen", "Kitchen sounds recorded while cooking", None, 20, 28, "ambient"),
    ("tap", "kitchen", "Kitchen sink draining", None, 0, 28, "ambient"),
    ("library", "library", "Biblioteca", None, 5, 28, "ambient"),
    ("typing", "typing keyboard", "Keyboard noise", None, 0, 22, "ambient"),
    ("phone", "telephone ringing", "Model 500 Telephone", None, 0, 8, "effect"),
    ("ship_horn", "ship horn", "Cruise ship Albatros", None, 0, 6, "effect"),
    ("bells", "church bell", "Samariter Church Bell I (Es).ogg", None, 0, 14, "effect"),
    ("chant", "gregorian chant", "Veni.sancte.spiritus", None, 5, 28, "ambient"),
]


def _api(**p) -> dict:
    p.update(format="json", action="query")
    req = urllib.request.Request(API + "?" + urllib.parse.urlencode(p), headers=UA)
    return json.load(urllib.request.urlopen(req, timeout=60))


def resolve(query: str, match: str, ext: str | None) -> dict:
    d = _api(generator="search", gsrsearch=f"{query} filetype:audio", gsrnamespace=6, gsrlimit=30,
             prop="imageinfo", iiprop="url|size|extmetadata|metadata")
    for pg in d.get("query", {}).get("pages", {}).values():
        if match in pg["title"] and (ext is None or pg["title"].endswith(ext)):
            ii = pg["imageinfo"][0]
            md = {m["name"]: m["value"] for m in (ii.get("metadata") or []) if isinstance(m, dict)}
            em = ii.get("extmetadata", {})
            clean = lambda k: re.sub(r"<[^>]+>", "", html.unescape(em.get(k, {}).get("value", ""))).strip()
            return {"title": pg["title"], "url": ii["url"], "size": ii["size"],
                    "length": float(md.get("length") or 0), "license": clean("LicenseShortName"),
                    "author": clean("Artist") or "unknown", "page": ii["descriptionurl"]}
    raise LookupError(f"no Commons file matching {match!r} for query {query!r}")


def download(info: dict, start: float, dur: float, dest: Path) -> None:
    need = info["size"]
    if info["length"] and info["size"] > 20_000_000:
        need = min(info["size"], int(info["size"] * (start + dur + 5) / info["length"] * 1.2) + 65536)
    req = urllib.request.Request(info["url"], headers={**UA, "Range": f"bytes=0-{need - 1}"})
    with urllib.request.urlopen(req, timeout=300) as r, open(dest, "wb") as f:
        shutil.copyfileobj(r, f)


def ffmpeg_exe() -> str:
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        return "ffmpeg"


def decode(src: Path, start: float, dur: float, dest: Path) -> np.ndarray:
    subprocess.run([ffmpeg_exe(), "-y", "-loglevel", "error", "-ss", str(start), "-t", str(dur),
                    "-i", str(src), "-ac", "1", "-ar", str(SR), "-f", "wav", str(dest)], check=True)
    with wave.open(str(dest)) as w:
        return np.frombuffer(w.readframes(w.getnframes()), dtype="<i2").astype(np.float64) / 32768


def make_loop(x: np.ndarray) -> np.ndarray:
    """Equal-power crossfade of the tail into the head so the clip loops without a click."""
    n = int(LOOP_XFADE_S * SR)
    if len(x) < 4 * n:
        return x
    t = np.linspace(0, np.pi / 2, n)
    head, tail = x[:n], x[-n:]
    body = x[n:-n].copy()
    body = np.concatenate([tail * np.cos(t) + head * np.sin(t), body[: len(body)]])
    return body


def level(x: np.ndarray, kind: str) -> np.ndarray:
    if kind == "ambient":          # RMS-match beds so config volume percentages mean the same thing
        rms = np.sqrt(np.mean(x ** 2)) or 1e-9
        x = x * (10 ** (-20 / 20) / rms)
        peak = np.max(np.abs(x))
        return x * (0.95 / peak) if peak > 0.95 else x
    x = x / (np.max(np.abs(x)) or 1) * 0.9
    k = int(0.01 * SR)
    ramp = np.linspace(0, 1, k)
    x[:k] *= ramp
    x[-k:] *= ramp[::-1]
    return x


def main() -> None:
    wanted = set(sys.argv[1:])
    out_dir = config.BUNDLED_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    credits_path = out_dir / "sources.json"
    credits = json.loads(credits_path.read_text(encoding="utf-8")) if credits_path.exists() else {}
    tmp = Path(tempfile.mkdtemp())
    failed = []
    for sid, query, match, ext, start, dur, kind in MANIFEST:
        if wanted and sid not in wanted:
            continue
        try:
            info = resolve(query, match, ext)
            src = tmp / f"{sid}{Path(info['title']).suffix}"
            download(info, start, dur, src)
            x = decode(src, start, dur, tmp / f"{sid}_dec.wav")
            if len(x) < SR:
                raise ValueError("decoded audio is too short")
            if kind == "ambient":
                x = make_loop(x)
            sounds.write_wav(sounds.asset_path(sid, out_dir, use_bundled=False), level(x, kind))
            credits[sid] = {k: info[k] for k in ("title", "author", "license", "page")} | {
                "excerpt": f"{start}s + {dur}s", "kind": kind}
            print(f"ok   {sid:13s} {len(x) / SR:5.1f}s  {info['license']:12s} {info['title'][:60]}")
        except Exception as exc:  # keep going; report at the end
            failed.append(sid)
            print(f"FAIL {sid:13s} {exc}")
    credits_path.write_text(json.dumps(credits, indent=2, ensure_ascii=False), encoding="utf-8")
    write_credits_md(out_dir, credits)
    shutil.rmtree(tmp, ignore_errors=True)
    if failed:
        sys.exit(f"failed: {', '.join(failed)}")


def write_credits_md(out_dir: Path, credits: dict) -> None:
    lines = ["# Sound credits", "",
             "Recordings are from Wikimedia Commons, cut/converted to mono 44.1 kHz WAV and "
             "level-matched. Licences: CC0 / Public domain need no attribution; CC BY and CC BY-SA "
             "require the attribution below (CC BY-SA also requires derivatives be shared alike).", "",
             "| Sound | Source file | Author | Licence |", "|---|---|---|---|"]
    for sid in config.SOUNDS:
        c = credits.get(sid)
        if c:
            lines.append(f"| {sid} | [{c['title'].removeprefix('File:')}]({c['page']}) | "
                         f"{c['author'].replace('|', '/')} | {c['license']} |")
    synth = [s for s in config.SOUNDS if s not in credits]
    lines += ["", "Synthesised placeholders (generated by `app/sounds.py`, no third-party licence): "
              + (", ".join(synth) or "none") + "."]
    (out_dir / "CREDITS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

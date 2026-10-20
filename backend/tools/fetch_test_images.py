"""Download licence-free test photos for every environment into backend/test_images/ (gitignored).

Only photos whose Wikimedia Commons licence is CC0 or Public Domain are kept, so they carry no
attribution or royalty obligations. Layout:

    backend/test_images/<environment>/<nn>_<slug>.jpg
    backend/test_images/manifest.json      title, author, licence and source page of every file

    python tools/fetch_test_images.py [per_environment]     # default 30
    python tools/fetch_test_images.py 20 beach forest       # only some environments
"""
from __future__ import annotations

import html
import io
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app import config  # noqa: E402

API = "https://commons.wikimedia.org/w/api.php"
UA = {"User-Agent": "AudioScapeStudentProject/1.0 (https://github.com/ripuns/AudioScape)"}
OUT = config.BASE_DIR / "test_images"
THUMB_W = 1024
MIN_SIDE = 480
OK_LICENSES = ("cc0", "public domain", "pd", "cc-zero")

QUERIES = {
    "beach": ["beach", "sandy beach sea", "tropical beach palm", "seashore waves sand", "coast shore"],
    "forest": ["forest", "forest path trees", "woodland trail", "pine forest", "rainforest trees"],
    "classroom": ["classroom", "classroom students desks", "school classroom", "lecture hall students"],
    "city": ["city street", "downtown street traffic", "urban street cars", "city skyline street", "busy street pedestrians"],
    "cafe": ["cafe interior", "coffee shop", "cafe tables customers", "restaurant interior", "coffeehouse"],
    "stadium": ["stadium", "football stadium crowd", "stadium match fans", "sports arena crowd", "cricket stadium"],
    "park": ["city park", "public park lawn", "park people picnic", "park benches trees", "botanical garden park"],
    "rainy_street": ["rainy street", "rain umbrella street", "wet street rain", "rainy day city", "rain pavement umbrellas"],
    "mountain": ["mountain landscape", "mountain peaks snow", "alpine mountains", "mountain range", "mountain valley"],
    "lake": ["lake landscape", "lake shore water", "mountain lake reflection", "calm lake", "lakeside"],
    "countryside": ["countryside", "farmland field", "farm pasture cows", "rural landscape", "meadow farm"],
    "market": ["market stalls", "outdoor market", "street market vendors", "bazaar", "farmers market"],
    "railway_station": ["railway station", "train station platform", "railway platform train", "station concourse", "metro station",
                        "train", "locomotive railway", "railway", "tram station", "subway platform", "railroad depot"],
    "highway": ["highway", "motorway traffic", "freeway cars", "expressway", "highway interchange"],
    "kitchen": ["kitchen", "kitchen interior", "home kitchen", "restaurant kitchen cooking", "kitchen stove"],
    "library": ["library interior", "library bookshelves", "reading room library", "public library", "university library"],
    "office": ["office interior", "office desks computers", "open plan office", "workplace office", "conference room office"],
    "harbour": ["harbour boats", "harbor ships", "port harbour", "marina boats", "fishing harbour",
                "port", "docks ships", "wharf boats", "boats moored", "pier boats", "lighthouse harbor", "sailboats"],
    "worship": ["church interior", "temple interior", "cathedral interior", "mosque interior", "temple",
                "church", "chapel interior", "synagogue", "altar", "pagoda", "buddhist temple", "hindu temple", "abbey interior"],
}


def _api(**p) -> dict:
    p.update(format="json", action="query")
    req = urllib.request.Request(API + "?" + urllib.parse.urlencode(p), headers=UA)
    for attempt in range(4):
        try:
            return json.load(urllib.request.urlopen(req, timeout=60))
        except Exception:
            time.sleep(1.5 * (attempt + 1))
    return {}


def _clean(v: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", html.unescape(v or ""))).strip()


def candidates(query: str, pages: int = 3):
    """Yield (title, thumb_url, page_url, license, author) for licence-free JPEG photos."""
    for page in range(pages):
        d = _api(generator="search", gsrsearch=f"{query} filetype:bitmap", gsrnamespace=6, gsrlimit=50,
                 gsroffset=page * 50, prop="imageinfo", iiprop="url|mime|size|extmetadata", iiurlwidth=THUMB_W)
        found = d.get("query", {}).get("pages", {})
        if not found:
            return
        for pg in found.values():
            ii = pg["imageinfo"][0]
            if ii["mime"] != "image/jpeg" or min(ii["width"], ii["height"]) < MIN_SIDE:
                continue
            em = ii.get("extmetadata", {})
            lic = _clean(em.get("LicenseShortName", {}).get("value", ""))
            if not any(lic.lower().startswith(k) for k in OK_LICENSES):
                continue
            yield (pg["title"], ii.get("thumburl") or ii["url"], ii["descriptionurl"], lic,
                   _clean(em.get("Artist", {}).get("value", "")) or "unknown")


def slug(title: str) -> str:
    name = re.sub(r"^File:", "", title).rsplit(".", 1)[0]
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")[:50] or "image"


def main() -> None:
    args = sys.argv[1:]
    per = int(args[0]) if args and args[0].isdigit() else 30
    only = [a for a in args if not a.isdigit()]
    envs = [e for e in config.ENVIRONMENTS if not only or e in only]

    OUT.mkdir(exist_ok=True)
    mpath = OUT / "manifest.json"
    manifest = json.loads(mpath.read_text(encoding="utf-8")) if mpath.exists() else {}
    for env in envs:
        folder = OUT / env
        folder.mkdir(exist_ok=True)
        entries = manifest.setdefault(env, [])
        seen = {e["title"] for e in entries}
        for q in QUERIES.get(env, [env]):
            for title, url, page, lic, author in candidates(q):
                if len(entries) >= per:
                    break
                if title in seen:
                    continue
                try:
                    raw = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()
                    img = Image.open(io.BytesIO(raw))
                    img.verify()
                except Exception:
                    continue
                seen.add(title)
                fname = f"{len(entries) + 1:02d}_{slug(title)}.jpg"
                (folder / fname).write_bytes(raw)
                entries.append({"file": fname, "title": title, "license": lic, "author": author,
                                "page": page, "query": q})
            if len(entries) >= per:
                break
        mpath.write_text(json.dumps(manifest, indent=1, ensure_ascii=False), encoding="utf-8")
        print(f"{env:16s} {len(entries):3d} photos", flush=True)
    total = sum(len(v) for v in manifest.values())
    mb = sum(f.stat().st_size for f in OUT.rglob("*.jpg")) / 1e6
    print(f"\n{total} photos, {mb:.0f} MB in {OUT}")


if __name__ == "__main__":
    main()

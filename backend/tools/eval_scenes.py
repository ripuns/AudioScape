"""Evaluate scene classification on real photos from Wikimedia Commons.

For every environment in config.ENVIRONMENTS, downloads a few photos matching a search query,
runs the CLIP scene classifier and reports top-1 / top-3 accuracy plus the confusions.

    python tools/eval_scenes.py [photos_per_scene]    # default 4
"""
from __future__ import annotations

import io
import json
import sys
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app import config, preprocess, vision  # noqa: E402

API = "https://commons.wikimedia.org/w/api.php"
UA = {"User-Agent": "AudioScapeStudentProject/1.0 (https://github.com/ripuns/AudioScape)"}

QUERIES = {
    "beach": ["sandy beach sea", "tropical beach"], "forest": ["forest path trees", "woodland"],
    "classroom": ["classroom interior desks", "school classroom students"],
    "city": ["city street traffic buildings", "downtown street cars"],
    "cafe": ["cafe interior tables", "coffee shop interior"],
    "stadium": ["football stadium crowd", "stadium match"], "park": ["city park lawn people", "public park"],
    "rainy_street": ["rainy street umbrellas", "wet street rain"],
    "mountain": ["mountain landscape peaks", "alpine mountains"], "lake": ["lake landscape water", "mountain lake"],
    "countryside": ["countryside farmland field", "farm cows pasture"],
    "market": ["market stalls people", "outdoor market vendors"],
    "railway_station": ["railway station platform", "train station interior"],
    "highway": ["highway traffic cars", "motorway"], "kitchen": ["kitchen interior", "home kitchen cooking"],
    "library": ["library interior bookshelves", "reading room library"],
    "office": ["office interior desks computers", "open plan office"],
    "harbour": ["harbour boats", "port harbor ships"], "worship": ["church interior", "temple interior"],
}


def _api(**p) -> dict:
    p.update(format="json", action="query")
    req = urllib.request.Request(API + "?" + urllib.parse.urlencode(p), headers=UA)
    return json.load(urllib.request.urlopen(req, timeout=60))


def photos(query: str, n: int) -> list[tuple[str, bytes]]:
    d = _api(generator="search", gsrsearch=f"{query} filetype:bitmap", gsrnamespace=6, gsrlimit=25,
             prop="imageinfo", iiprop="url|mime", iiurlwidth=640)
    out = []
    for pg in d.get("query", {}).get("pages", {}).values():
        ii = pg["imageinfo"][0]
        if ii["mime"] != "image/jpeg":
            continue
        try:
            req = urllib.request.Request(ii.get("thumburl") or ii["url"], headers=UA)
            out.append((pg["title"], urllib.request.urlopen(req, timeout=60).read()))
        except Exception:
            continue
        if len(out) == n:
            break
    return out


def main() -> None:
    per = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    scorer = vision.ClipScorer()
    top1 = top3 = total = 0
    confusions: Counter = Counter()
    per_scene = {}
    for env in config.ENVIRONMENTS:
        qs = QUERIES.get(env, [env])
        imgs = [b for q in qs for b in photos(q, per // len(qs) or 1)][:per]
        hit = 0
        for title, raw in imgs:
            res = vision.classify_scene(preprocess.load_image(raw), scorer)
            ranked = sorted(res.scores, key=res.scores.get, reverse=True)
            total += 1
            if ranked[0] == env:
                top1 += 1; hit += 1
            else:
                confusions[(env, ranked[0])] += 1
                print(f"    miss: {title[5:70]!r} -> {ranked[0]}")
            top3 += env in ranked[:3]
        per_scene[env] = (hit, len(imgs))
        print(f"{env:16s} {hit}/{len(imgs)}", flush=True)
    print(f"\ntop-1 {top1}/{total} = {top1 / total:.0%}   top-3 {top3}/{total} = {top3 / total:.0%}")
    for (truth, pred), c in confusions.most_common(12):
        print(f"  {truth} -> {pred}  x{c}")


if __name__ == "__main__":
    main()

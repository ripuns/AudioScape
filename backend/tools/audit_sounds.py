"""Objective audit of sound assets with an AudioSet classifier (Audio Spectrogram Transformer).

For every sound in config.SOUNDS, scores how strongly the clip is recognised as the thing it is
meant to be (max probability over the expected AudioSet labels below) and prints the model's
top labels. Use it after swapping in real recordings to sanity-check them without listening.

    python tools/audit_sounds.py [assets_dir]      # default: bundled assets dir
    python tools/audit_sounds.py --synth           # audit the synthesised placeholders
"""
from __future__ import annotations

import sys
import tempfile
import wave
from pathlib import Path

import numpy as np
from scipy.signal import resample_poly

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app import config, sounds  # noqa: E402

MODEL = "MIT/ast-finetuned-audioset-10-10-0.4593"

EXPECTED: dict[str, list[str]] = {
    "waves": ["Waves, surf", "Ocean", "Water", "Sea"],
    "wind": ["Wind", "Wind noise (microphone)", "Rustling leaves"],
    "insects": ["Cricket", "Insect", "Mosquito", "Fly, housefly"],
    "leaves": ["Rustling leaves", "Rustle", "Crackle", "Wind"],
    "traffic": ["Traffic noise, roadway noise", "Vehicle", "Car", "Motor vehicle (road)", "Engine"],
    "crowd": ["Speech", "Crowd", "Hubbub, speech noise, speech babble", "Cheering", "Chatter"],
    "rain": ["Rain", "Raindrop", "Rain on surface"],
    "chatter": ["Speech", "Hubbub, speech noise, speech babble", "Chatter", "Conversation", "Crowd"],
    "classroom": ["Speech", "Hubbub, speech noise, speech babble", "Chatter", "Conversation", "Child speech, kid speaking"],
    "cafe_music": ["Music", "Jazz", "Musical instrument", "Piano"],
    "clock": ["Tick", "Tick-tock", "Clock"],
    "cheering": ["Speech", "Cheering", "Crowd", "Applause", "Clapping"],
    "children": ["Speech", "Children playing", "Child speech, kid speaking", "Yell", "Crowd", "Laughter"],
    "seagulls": ["Bird", "Bird vocalization, bird call, bird song", "Chirp, tweet", "Animal"],
    "footsteps": ["Walk, footsteps", "Crunch", "Footsteps"],
    "birds": ["Bird", "Bird vocalization, bird call, bird song", "Chirp, tweet"],
    "horns": ["Vehicle horn, car horn, honking", "Car", "Honk", "Beep, bleep"],
    "construction": ["Jackhammer", "Hammer", "Drill", "Power tool", "Sawing", "Tools", "Engine", "Machine gun"],
    "umbrella": ["Rain", "Raindrop", "Rain on surface", "Patter"],
    "chalk": ["Scratch", "Writing", "Scrape", "Pencil", "Rub"],
    "cups": ["Dishes, pots, and pans", "Cutlery, silverware", "Glass", "Clink", "Tableware", "Ding"],
    "espresso": ["Steam", "Hiss", "Boiling", "Spray", "Water", "Liquid"],
    "whistle": ["Whistle", "Whistling", "Referee whistle"],
    "drums": ["Drum", "Snare drum", "Drum kit", "Bass drum", "Percussion"],
    "barking": ["Dog", "Bark", "Animal", "Domestic animals, pets"],
    "stream": ["Stream", "Water", "Trickle, dribble", "Gurgling", "Liquid"],
    "lapping": ["Water", "Waves, surf", "Ocean", "Slosh", "Splash, splatter", "Boat, Water vehicle", "Stream"],
    "frogs": ["Frog", "Croak", "Animal", "Insect"],
    "rooster": ["Rooster", "Crowing, cock-a-doodle-doo", "Chicken, rooster", "Fowl"],
    "cows": ["Cattle, bovinae", "Moo", "Livestock, farm animals, working animals", "Animal"],
    "train": ["Train", "Rail transport", "Railroad car, train wagon", "Train horn", "Vehicle"],
    "station": ["Inside, public space", "Hubbub, speech noise, speech babble", "Speech", "Train", "Rail transport", "Echo"],
    "market": ["Hubbub, speech noise, speech babble", "Speech", "Crowd", "Inside, public space", "Outside, urban or manmade"],
    "highway": ["Traffic noise, roadway noise", "Vehicle", "Car", "Motor vehicle (road)", "Truck"],
    "kitchen": ["Dishes, pots, and pans", "Cutlery, silverware", "Frying (food)", "Water tap, faucet", "Sink (filling or washing)", "Speech", "Inside, small room"],
    "library": ["Inside, small room", "Inside, large room or hall", "Silence", "Speech", "Hubbub, speech noise, speech babble", "Inside, public space"],
    "tap": ["Water", "Liquid", "Fill (with liquid)", "Water tap, faucet", "Sink (filling or washing)", "Drip"],
    "typing": ["Typing", "Computer keyboard", "Typewriter", "Typewriter", "Tap"],
    "phone": ["Telephone bell ringing", "Ringtone", "Telephone", "Alarm"],
    "ship_horn": ["Foghorn", "Ship", "Boat, Water vehicle", "Vehicle horn, car horn, honking", "Air horn, truck horn"],
    "bells": ["Bell", "Church bell", "Chime", "Ding", "Tubular bells", "Gong"],
    "chant": ["Chant", "Choir", "Singing", "Male singing", "Music", "Mantra"],
}


def load_16k(path: Path) -> np.ndarray:
    with wave.open(str(path)) as w:
        sr, ch = w.getframerate(), w.getnchannels()
        x = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2").astype(np.float32) / 32768
    if ch > 1:
        x = x.reshape(-1, ch).mean(axis=1)
    return resample_poly(x, 16000, sr).astype(np.float32)


def main() -> None:
    from transformers import ASTFeatureExtractor, ASTForAudioClassification
    import torch

    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if "--synth" in sys.argv:
        d = Path(tempfile.mkdtemp())
        for sid in config.SOUNDS:
            sounds.write_wav(sounds.asset_path(sid, d), sounds.synthesize(sid))
    else:
        d = Path(args[0]) if args else config.BUNDLED_DIR

    fe = ASTFeatureExtractor.from_pretrained(MODEL)
    model = ASTForAudioClassification.from_pretrained(MODEL).eval()
    id2label = model.config.id2label
    label2id = {v: k for k, v in id2label.items()}

    print(f"{'sound':13s} {'score':>6s}  verdict   top labels")
    rows = []
    for sid in config.SOUNDS:
        p = sounds.asset_path(sid, d)
        if not p.exists():
            continue
        x = load_16k(p)[: 16000 * 10]
        with torch.no_grad():
            probs = torch.sigmoid(model(**fe(x, sampling_rate=16000, return_tensors="pt")).logits)[0]
        exp = [label2id[l] for l in EXPECTED[sid] if l in label2id]
        score = max(float(probs[i]) for i in exp)
        top = [f"{id2label[int(i)]} {float(probs[i]):.2f}" for i in probs.argsort(descending=True)[:3]]
        verdict = "good" if score >= 0.35 else "weak" if score >= 0.15 else "POOR"
        rows.append((score, sid))
        print(f"{sid:13s} {score:6.2f}  {verdict:8s}  {'; '.join(top)}")


if __name__ == "__main__":
    main()

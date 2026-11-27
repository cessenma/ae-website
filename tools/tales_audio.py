#!/usr/bin/env python3
"""Read-aloud audio for the classic-tale pages: one MP3 per scene (the readers' voice and settings, ae-readers
tools/readalong.py), checked by transcription so a dropped last sentence is caught and re-made.
Output: assets/audio/tales/<slug>-<n>.mp3. Ledgered in ae-readers/spend.jsonl.
"""
import os, re, sys
from concurrent.futures import ThreadPoolExecutor
SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.expanduser("~/Documents/GitHub/ae-readers/tools"))
sys.path.insert(0, os.path.join(SITE, "tools"))
from readalong import tts, transcribe
from tales_data import TALES
OUT = os.path.join(SITE, "assets", "audio", "tales")
os.makedirs(OUT, exist_ok=True)
norm = lambda s: re.findall(r"[a-z']+", s.lower().replace("’", "'"))

def one(job):
    slug, i, text = job
    path = os.path.join(OUT, f"{slug}-{i}.mp3")
    if os.path.exists(path):
        return f"kept {slug}-{i}"
    want = norm(text)
    for attempt in range(3):
        tts("tale-" + slug, text, path)
        heard, _ = transcribe("tale-" + slug, path)
        got = norm(" ".join(w["word"] for w in heard))
        if abs(len(got) - len(want)) <= max(2, len(want) // 12) and got[-2:] == want[-2:]:
            return f"ok {slug}-{i} ({len(got)}/{len(want)} words)"
    return f"CHECK {slug}-{i}: heard {len(got)} of {len(want)} words, ends {' '.join(got[-4:])!r}"

jobs = [(t["slug"], i, s["en"]) for t in TALES for i, s in enumerate(t["scenes"], 1)]
with ThreadPoolExecutor(6) as ex:
    for r in ex.map(one, jobs):
        print(r, flush=True)

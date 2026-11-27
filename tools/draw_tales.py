#!/usr/bin/env python3
"""Pictures for the classic-tale pages (tools/tales_data.py), in the Chris and Cora art style (ae-readers STYLE C).
Scene 1 of a tale is generated; scenes 2-6 are drawn with scene 1 as the reference so the characters stay the same.
Masters: ~/Downloads/AE-tales-art/<slug>-<n>.png; site copies: assets/img/tales/<slug>-<n>.webp (1000 px).
Every call is ledgered in ae-readers/spend.jsonl (imgapi). Chris approved about US$2 on 2026-11-26.
    python3 tools/draw_tales.py [slug ...] [--redo slug-n]
"""
import os, sys, io
from concurrent.futures import ThreadPoolExecutor
SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.expanduser("~/Documents/GitHub/ae-readers/tools"))
sys.path.insert(0, os.path.join(SITE, "tools"))
from imgapi import gen, edit
from draw_refs import STYLES
from tales_data import TALES
from PIL import Image
OUT = os.path.expanduser("~/Downloads/AE-tales-art")
WEB = os.path.join(SITE, "assets", "img", "tales")
STYLE = STYLES["C"]
RULES = ("Storybook scene for a classic children's tale. NO text, letters, numbers, logos or signs anywhere. One scene, one "
         "perspective, every character complete and inside the frame with a margin all round. Gentle and friendly, nothing gory or frightening. ")
redo = {a for i, a in enumerate(sys.argv) if i and sys.argv[i - 1] == "--redo"}
want = [a for a in sys.argv[1:] if not a.startswith("--") and a not in redo]

def web(png, name):
    os.makedirs(WEB, exist_ok=True)
    im = Image.open(png).convert("RGB"); im.thumbnail((1000, 1000)); im.save(os.path.join(WEB, name + ".webp"), "WEBP", quality=82, method=6)

def tale(t):
    first = os.path.join(OUT, f"{t['slug']}-1.png")
    for i, s in enumerate(t["scenes"], 1):
        name = f"{t['slug']}-{i}"; png = os.path.join(OUT, name + ".png")
        if os.path.exists(png) and name not in redo:
            web(png, name); continue
        base = f"{STYLE} {RULES}Characters in this tale: {t['cast']}. Scene: {s['art']}"
        try:
            if i == 1:
                data, _ = gen(base, size="1536x1024", quality="medium", job="tale-" + t["slug"])
            else:
                data, _ = edit([first], base + " Draw the characters exactly as in the reference image: same shapes, colours and clothes. "
                               "A new scene, not a copy of the reference.", size="1536x1024", quality="medium", job="tale-" + t["slug"])
            open(png, "wb").write(data); web(png, name); print("drew", name, flush=True)
        except Exception as e:
            print("FAILED", name, str(e)[:200], flush=True)

ts = [t for t in TALES if not want or t["slug"] in want]
with ThreadPoolExecutor(5) as ex:
    list(ex.map(tale, ts))
print("done")

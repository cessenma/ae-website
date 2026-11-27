#!/usr/bin/env python3
"""Second pass on tale pictures whose content contradicted the text (review 2026-11-27): each is redrawn from the tale's
scene 1 as reference with an explicit list of who may and may not appear. Old files are kept as *-v1.png."""
import os, sys, shutil
from concurrent.futures import ThreadPoolExecutor
SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.expanduser("~/Documents/GitHub/ae-readers/tools")); sys.path.insert(0, os.path.join(SITE, "tools"))
from imgapi import edit
from draw_refs import STYLES
from tales_data import TALES
from draw_tales import RULES, OUT, web
T = {t["slug"]: t for t in TALES}
FIX = {  # (slug, scene): extra instruction
 ("three-little-pigs", 3): "ONLY the third pig (green overalls) is in this scene, building alone. The other two pigs and the wolf are NOT in the picture.",
 ("three-little-pigs", 4): "Inside the stick house doorway there is ONLY the second pig (blue cap). The third pig (green overalls) is NOT in this picture.",
 ("tortoise-and-hare", 3): "ONLY the hare is in this scene. The tortoise is NOT in the picture: the path behind the hare is empty.",
 ("boy-who-cried-wolf", 1): "There is NO wolf anywhere in this picture: only the boy and the sheep on the hill.",
 ("boy-who-cried-wolf", 2): "There is NO wolf anywhere in this picture.",
 ("boy-who-cried-wolf", 3): "There is NO wolf anywhere in this picture.",
 ("boy-who-cried-wolf", 4): "There is NO wolf anywhere in this picture.",
 ("boy-who-cried-wolf", 6): "There is NO wolf in this picture and no farmers: only the boy alone, and a few sheep far away.",
 ("cinderella", 3): "ONLY Cinderella and the fairy godmother are in this scene (plus the horses and carriage). The prince is NOT in the picture.",
 ("cinderella", 4): "ONLY Cinderella (running down the stairs) and the prince (at the top) are in this scene. The fairy godmother is NOT in the picture.",
 ("cinderella", 5): "In this scene: the prince, the two stepsisters, the stepmother, and Cinderella in her grey dress at the doorway. The fairy godmother is NOT in the picture.",
 ("cinderella", 6): "In this scene: Cinderella in her grey dress, the kneeling prince, and the two surprised stepsisters. The fairy godmother is NOT in the picture.",
 ("nian-monster", 1): "The old man with the long white beard and red coat is NOT in this picture: only ordinary villagers (parents and children) look out of the windows.",
 ("nian-monster", 2): "The monster Nian is NOT in this picture, and the old man with the white beard is NOT in this picture: only village families walking up the mountain path.",
 ("nian-monster", 3): "Late afternoon, before dark. The monster Nian is NOT in this picture.",
 ("nian-monster", 4): "The village is empty: the ONLY person is the old man, seen through the window inside the bright house. NO other villagers, no children, nobody at the door. Red paper strips beside the red door.",
 ("nian-monster", 6): "Bright morning. The monster Nian is NOT in this picture at all: it has gone. Only happy villagers and the old man, putting red paper on the doors, with firecrackers and red lanterns.",
 ("nian-monster", 5): "The ONLY person is the old man with the firecrackers. NO other villagers and no children in this picture.",
}
def one(item):
    (slug, i), extra = item
    t = T[slug]; name = f"{slug}-{i}"; png = os.path.join(OUT, name + ".png"); old = os.path.join(OUT, name + "-v1.png")
    ref = os.path.join(OUT, f"{slug}-1-v1.png") if os.path.exists(os.path.join(OUT, f"{slug}-1-v1.png")) else os.path.join(OUT, f"{slug}-1.png")
    if os.path.exists(old) and i != 1 and os.path.getmtime(png) > os.path.getmtime(old) + 5: return "kept " + name
    if not os.path.exists(old): shutil.copy2(png, old)
    if i == 1: ref = old
    p = (f"{STYLES['C']} {RULES}Characters in this tale: {t['cast']}. Scene: {t['scenes'][i-1]['art']} IMPORTANT: {extra} "
         "Draw the characters that do appear exactly as in the reference image: same shapes, colours and clothes. A new scene, not a copy of the reference.")
    try:
        data, _ = edit([ref], p, size="1536x1024", quality="medium", job="tale-" + slug)
        open(png, "wb").write(data); web(png, name); return "redrew " + name
    except Exception as e:
        return f"FAILED {name} {str(e)[:160]}"
ONLY = set(sys.argv[1:])  # optional: names like nian-monster-6, to redo just those
ITEMS = [(k, v) for k, v in FIX.items() if not ONLY or f"{k[0]}-{k[1]}" in ONLY]
with ThreadPoolExecutor(6) as ex:
    for r in ex.map(one, ITEMS): print(r, flush=True)

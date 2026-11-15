#!/usr/bin/env python3
"""
Data for the AE:NEXTLEVEL blocks that seo_build.py injects (2026-11-15).

Why: a plain book card on /phonics-rules-chart/ got 0 taps from 212 visitors in five days and 2 of 253 on
/english-alphabet-worksheet/. So the sound pages get the book itself: four real pages of the free reader
This Is Bobo! (1a) to read aloud — on KK pages printed in KK first, on phonics pages in plain English —
then the picture, the sentence and the recording. The grammar books get a grade picker that shows that
grade's real free sample page.

Writes data/next_level.json and the pictures in assets/img/readers/try/. Reads:
  ~/Documents/GitHub/ae-readers/data/books/1a.json   the book's text (viewer page = 2 × book page − 2)
  assets/kk/<xx>.json                                the site's own KK spellings (tools/kk_lookup.py)
  chris-and-cora-readers/read/1a/pages/NN.jpg        text page NN, its picture on NN+1; audio/pNN.mp3
Usage:  python3 tools/build_next_level.py   then   /usr/bin/python3 tools/seo_build.py --strict
"""
import os, re, json, subprocess, tempfile

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOOK = os.path.expanduser("~/Documents/GitHub/ae-readers/data/books/1a.json")
PAGES = [6, 7, 8, 12]                 # book pages: This is Bobo. / Look at Bobo! / Bobo is a dog… / Bobo is in a box…
NAMES = {"bobo": "ˈbobo", "chris": "krɪs", "cora": "ˈkorə"}
WEAK = {"a": "ə", "the": "ðə", "and": "ənd", "has": "hæz"}      # the form said inside a sentence
GRADES = [("G3", "三年級"), ("G4", "四年級"), ("G5", "五年級"), ("G6", "六年級"), ("G7-1", "國一"), ("G8-1", "國二"),
          ("G9-1", "國三"), ("G10-1", "高一"), ("G11-1", "高二"), ("G12-1", "高三")]

def kk(word):
    w = word.lower()
    if w in NAMES: return NAMES[w]
    if w in WEAK: return WEAK[w]
    shard = json.load(open(os.path.join(SITE, "assets/kk", (w[:2] if len(w) > 1 else w + "_") + ".json"), encoding="utf-8"))
    return shard[w].split("|")[0]

def main():
    book = {p["n"]: p["text"] for p in json.load(open(BOOK, encoding="utf-8"))["pages"]}
    out_dir = os.path.join(SITE, "assets/img/readers/try")
    os.makedirs(out_dir, exist_ok=True)
    cards = []
    for n in PAGES:
        v = 2 * n - 2
        sents = re.findall(r"[^.!?]+[.!?]", book[n])
        src = os.path.join(SITE, f"chris-and-cora-readers/read/1a/pages/{v + 1:02d}.jpg")
        assert os.path.exists(src) and os.path.exists(os.path.join(SITE, f"chris-and-cora-readers/read/1a/audio/p{v:02d}.mp3"))
        dst = os.path.join(out_dir, f"1a-{v + 1:02d}.webp")
        with tempfile.NamedTemporaryFile(suffix=".png") as t:
            subprocess.run(["sips", "-s", "format", "png", "-Z", "720", src, "--out", t.name], check=True, capture_output=True)
            subprocess.run(["cwebp", "-quiet", "-q", "78", t.name, "-o", dst], check=True)
        cards.append({"text": [s.strip() for s in sents],
                      "kk": [" ".join(kk(w) for w in re.findall(r"[A-Za-z]+", s)) for s in sents],
                      "img": f"/assets/img/readers/try/1a-{v + 1:02d}.webp", "audio": f"/chris-and-cora-readers/read/1a/audio/p{v:02d}.mp3"})
    grades = []
    for code, zh in GRADES:
        img, pdf = f"assets/img/grammar-books/free/{code}-sample.webp", f"assets/downloads/ae-grammar-{code.lower()}-sample.pdf"
        assert os.path.exists(os.path.join(SITE, img)) and os.path.exists(os.path.join(SITE, pdf)), code
        grades.append({"code": code, "zh": zh, "img": "/" + img, "pdf": "/" + pdf})
    json.dump({"_note": "written by tools/build_next_level.py; read by seo_build.next_level", "book": "This Is Bobo!",
               "cards": cards, "grades": grades},
              open(os.path.join(SITE, "data/next_level.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for c in cards: print(c["text"], c["kk"])

if __name__ == "__main__":
    main()

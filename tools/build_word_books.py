#!/usr/bin/env python3
"""
Data for the AE:WORDBOOK strip on the per-word pronunciation pages (2026-11-18).

Why: the 1,166 word pages had 1,078 visitors in a week (11-11 → 11-17) and 2 of them reached the readers page.
The Chris and Cora books are written from the same MOE list, so each word page shows one real sentence from the
books with that word in it, the page's picture, where the word starts and how often it is read in the 36 books.

Writes data/word_books.json and assets/img/readers/in-story/<book>-<page>.webp. Reads:
  tools/data/words/pilot.json + content.json           the word pages
  ~/Documents/GitHub/ae-readers/data/ladder.json        every list word with its written forms
  ~/Documents/GitHub/ae-readers/data/books/*.json       the 36 manuscripts (story page n → flip page 2n−2, picture 2n−1)
  ~/Downloads/AE-readers-out/flip/<book>/pages/NN.jpg   the page pictures
Rules:
  - a sentence with the word exactly as the page spells it is preferred; an inflected form (apples) is the fallback
  - a word that is also another list word's inflection (left = past of leave, saw = past of see) gets no strip:
    the sentence could be the other word
  - the earliest such sentence in the series is the one shown (reusing later pages saved only 24 of 422 pictures);
    pictures are 300 px wide, a preview and not the book's page
Usage:  python3 tools/build_word_books.py   then   /usr/bin/python3 tools/seo_build.py --strict
"""
import os, re, sys, json, glob, subprocess, tempfile, collections

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
READERS = os.path.expanduser("~/Documents/GitHub/ae-readers")
FLIP = os.path.expanduser("~/Downloads/AE-readers-out/flip")
OUT_IMG = os.path.join(SITE, "assets/img/readers/in-story")
MAX_LEN = 140          # longest sentence shown

def order(code):
    m = re.match(r"(\d+)([abc])$", code)
    return (int(m.group(1)), m.group(2))

def main():
    ladder = json.load(open(os.path.join(READERS, "data/ladder.json"), encoding="utf-8"))["words"]
    forms = {w["word"].lower(): sorted({f.lower() for f in (w.get("forms") or {})} | {w["word"].lower()}) for w in ladder}
    owner = collections.defaultdict(set)                     # written form → the list words it can be
    for w, fs in forms.items():
        for f in fs:
            owner[f].add(w)
    pilot = json.load(open(os.path.join(SITE, "tools/data/words/pilot.json"), encoding="utf-8"))
    content = json.load(open(os.path.join(SITE, "tools/data/words/content.json"), encoding="utf-8"))
    pages_words = {d["slug"]: d["word"] for d in pilot if d["slug"] in content}

    books = sorted((os.path.basename(f)[:-5] for f in glob.glob(os.path.join(READERS, "data/books/*.json"))), key=order)
    sents, titles = [], {}                                   # (book, n, sentence)
    for b in books:
        d = json.load(open(os.path.join(READERS, f"data/books/{b}.json"), encoding="utf-8"))
        titles[b] = d["title"]
        for p in d["pages"]:
            for s in re.findall(r"[^.!?]+[.!?]+[\"”’']*", p.get("text") or ""):
                sents.append((b, p["n"], s.strip()))

    def rx(alts):
        return re.compile(r"(?<![A-Za-z'’])(" + "|".join(re.escape(a) for a in sorted(alts, key=len, reverse=True)) + r")(?![A-Za-z])", re.I)

    cand, skipped = {}, {"not-in-books": [], "other-word's-form": []}
    for slug, word in pages_words.items():
        w = word.lower()
        if w not in forms:
            skipped["not-in-books"].append(word); continue
        if len(owner[w]) > 1:                                # left / saw / rose: could be the other word
            skipped["other-word's-form"].append(word); continue
        exact, anyform = rx([w]), rx(forms[w])
        hits = [(b, n, s, bool(exact.search(s))) for b, n, s in sents if anyform.search(s)]
        if not hits:
            skipped["not-in-books"].append(word); continue
        count = sum(len(anyform.findall(s)) for _, _, s, _ in hits)
        cand[slug] = dict(word=word, hits=hits, count=count, first=order(hits[0][0])[0], rx=anyform,
                          inflected=any(m.lower() != w for _, _, s, _ in hits for m in anyform.findall(s)))

    chosen_pages, out = set(), {}
    def key(h):                                              # exact spelling first, short enough, then earliest
        b, n, s, ex = h
        return (not ex, len(s) > MAX_LEN, order(b), n, len(s))
    for slug in sorted(cand, key=lambda s: (order(cand[s]["hits"][0][0]), cand[s]["hits"][0][1])):
        c = cand[slug]
        ok = [h for h in c["hits"] if len(h[2]) <= MAX_LEN] or c["hits"]
        b, n, s, ex = min(ok, key=key)
        chosen_pages.add((b, n))
        marks = [[m.start(1), m.end(1)] for m in c["rx"].finditer(s)]
        out[slug] = dict(word=c["word"], book=b, level=order(b)[0], title=titles[b], sentence=s, marks=marks,
                         img=f"/assets/img/readers/in-story/{b}-{2 * n - 1:02d}.webp", first_level=c["first"],
                         count=c["count"], inflected=c["inflected"])

    os.makedirs(OUT_IMG, exist_ok=True)
    made = 0
    for b, n in sorted(chosen_pages, key=lambda k: (order(k[0]), k[1])):
        src = os.path.join(FLIP, b, "pages", f"{2 * n - 1:02d}.jpg")
        dst = os.path.join(OUT_IMG, f"{b}-{2 * n - 1:02d}.webp")
        assert os.path.exists(src), src
        if not os.path.exists(dst):
            with tempfile.NamedTemporaryFile(suffix=".png") as t:
                subprocess.run(["sips", "-s", "format", "png", "--resampleWidth", "300", src, "--out", t.name], check=True, capture_output=True)
                subprocess.run(["cwebp", "-quiet", "-q", "76", t.name, "-o", dst], check=True)
            made += 1
    keep = {os.path.basename(v["img"]) for v in out.values()}
    for f in os.listdir(OUT_IMG):
        if f not in keep:
            os.remove(os.path.join(OUT_IMG, f))
    json.dump({"_note": "written by tools/build_word_books.py; read by seo_build.word_book", "words": out},
              open(os.path.join(SITE, "data/word_books.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    size = sum(os.path.getsize(os.path.join(OUT_IMG, f)) for f in os.listdir(OUT_IMG))
    print(f"word pages {len(pages_words)} · with a strip {len(out)} · pictures {len(chosen_pages)} ({made} new, {size / 1e6:.1f} MB)")
    print("per level:", dict(sorted(collections.Counter(v["level"] for v in out.values()).items())))
    for k, v in skipped.items():
        print(f"no strip ({k}): {len(v)}", ", ".join(sorted(v))[:400])
    if "--show" in sys.argv:
        for s in ("apple", "eraser", "doll", "through", "able", "a", "the", "watch", "read", "ice-cream"):
            if s in out: print(s, "→", out[s]["book"], out[s]["title"], "|", out[s]["sentence"], out[s]["marks"], out[s]["count"], out[s]["first_level"])

if __name__ == "__main__":
    main()

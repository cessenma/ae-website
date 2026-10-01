#!/usr/bin/env python3
"""Bake the practice questions into the served HTML.

The Cambridge / YLE practice pages and the vocabulary drills ship their questions as data
inside a <script> and build the question cards in the browser. A reader sees the full page;
a crawler that does not run scripts (most AI crawlers, link previewers) gets the passage
but none of the questions, options or explanations — on /ket-rw-practice-part1/ that was
59% of the page's text.

This runs each page once in headless Chromium, lets the page's OWN engine draw the cards,
and writes that markup back into the empty containers in the source. In the browser the
engine still draws over it on load with the same markup, so nothing changes for a reader.

It also:
  - converts the YLE practice pictures to WebP, points the pages at them, and gives the
    static <img> tags an alt text and their pixel size
  - adds a Quiz JSON-LD block built from the same question data

Idempotent. Run after any generator that rewrites these pages and before seo_build.py:

    ~/.claude/skills/seo/.venv/bin/python3 tools/prerender_practice.py            # all
    ~/.claude/skills/seo/.venv/bin/python3 tools/prerender_practice.py ket-rw-practice-part1
"""
import functools, glob, http.server, json, os, re, sys, threading

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIGIN = "https://americanenglish.com.tw"
ORG_ID, PERSON_ID = ORIGIN + "/#organization", ORIGIN + "/#christopher"
PRE_A, PRE_B = "<!--AE:PRE-->", "<!--/AE:PRE-->"
QUIZ_A, QUIZ_B = "<!-- AE:QUIZ-LD start -->", "<!-- AE:QUIZ-LD end -->"

CONTAINER = re.compile(r'<form\b[^>]*(?:class="(?:prx-form|gd-form)[^"]*"|id="prx")[^>]*>|<div class="prx-slot"[^>]*>')

GRAB = """() => {
  const out = [];
  document.querySelectorAll('form.prx-form, form#prx, form.gd-form').forEach(f => {
    const slots = f.querySelectorAll('.prx-slot');
    if (slots.length) slots.forEach(s => out.push(s.innerHTML));
    else out.push(f.innerHTML);
  });
  let prx = null, gd = null;
  try { prx = (typeof PRX !== 'undefined') ? PRX : null } catch (e) {}
  try { gd = (typeof GDRILLS !== 'undefined') ? GDRILLS : null } catch (e) {}
  return {out, prx, gd};
}"""

LEVEL = {"starters": ("CEFR Pre-A1", "Cambridge English: Pre A1 Starters"), "movers": ("CEFR A1", "Cambridge English: A1 Movers"),
         "flyers": ("CEFR A2", "Cambridge English: A2 Flyers"), "ket": ("CEFR A2", "Cambridge English: A2 Key for Schools (KET)"),
         "a2": ("CEFR A2", "Cambridge English: A2 Key for Schools (KET)"), "pet": ("CEFR B1", "Cambridge English: B1 Preliminary for Schools (PET)"),
         "b1": ("CEFR B1", "Cambridge English: B1 Preliminary for Schools (PET)"), "fce": ("CEFR B2", "Cambridge English: B2 First for Schools (FCE)"),
         "b2": ("CEFR B2", "Cambridge English: B2 First for Schools (FCE)")}
PAPER = {"listening": "Listening", "reading": "Reading", "rw": "Reading and Writing", "ruoe": "Reading and Use of English",
         "vocabulary": "Vocabulary"}


def jd(o):
    return json.dumps(o, ensure_ascii=False, separators=(",", ":"))


def plain(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", str(s or ""))).strip()


# ---------------------------------------------------------------- YLE pictures
_SIZE = {}
def _dims(url):
    from PIL import Image
    if url not in _SIZE:
        f = os.path.join(SITE, url.lstrip("/"))
        try:
            if f.endswith(".svg"):          # PIL cannot open SVG: its own width/height (or viewBox) says the size
                head = open(f, encoding="utf-8").read(600) if os.path.exists(f) else ""
                m = re.search(r'<svg[^>]*\bwidth="([\d.]+)"[^>]*\bheight="([\d.]+)"', head) or \
                    re.search(r'<svg[^>]*\bviewBox="[\d.]+ [\d.]+ ([\d.]+) ([\d.]+)"', head)
                _SIZE[url] = (int(float(m.group(1))), int(float(m.group(2)))) if m else None
            else:
                _SIZE[url] = Image.open(f).size if os.path.exists(f) else None
        except Exception:
            _SIZE[url] = None
    return _SIZE[url]

_LV = {"starters": "Starters", "movers": "Movers", "flyers": "Flyers"}
_PART = {"l": "聽力", "rw": "閱讀與寫作", "sp": "口說"}

def fix_yle_imgs(html):
    """WebP paths, an alt where the tag has none, and the pixel size, on every YLE <img>."""
    html = re.sub(r'(/assets/img/(?:yle|pics)/[^"\'\s)]+?)\.png', lambda m: m.group(1) + ".webp"
                  if os.path.exists(os.path.join(SITE, m.group(1).lstrip("/") + ".webp")) else m.group(0), html)
    n = [0]
    def tag(m):
        t = m.group(0)
        src = re.search(r'src="([^"]+)"', t).group(1)
        mm = re.search(r"/yle/(\w+)/\w+?-(l|rw|sp)(\d*)", src)
        if 'alt=""' in t and mm:
            n[0] += 1
            part = f" Part {mm.group(3)}" if mm.group(3) else ""
            kind = "場景圖" if "scene" in src else "圖片"
            t = t.replace('alt=""', f'alt="{_LV[mm.group(1)]} {_PART[mm.group(2)]}{part} 題目{kind} {n[0]}"')
        d = _dims(src)
        if d and "width=" not in t:
            t = t[:-1].rstrip("/").rstrip() + f' width="{d[0]}" height="{d[1]}">'
        return t
    return re.sub(r'<img\b[^>]*src="/assets/img/(?:yle|pics)/[^"]+"[^>]*>', tag, html)


def yle_pictures(pages):
    """PNG -> WebP, references rewritten, alt + dimensions on the static tags."""
    from PIL import Image
    made = 0
    pngs = glob.glob(os.path.join(SITE, "assets/img/yle/*/*.png")) + glob.glob(os.path.join(SITE, "assets/img/pics/*.png"))
    for png in pngs:
        webp = png[:-4] + ".webp"
        if not os.path.exists(webp) or os.path.getmtime(webp) < os.path.getmtime(png):
            Image.open(png).convert("RGB").save(webp, "WEBP", quality=82, method=6)
            made += 1
    changed = 0
    for p in pages:
        s = o = open(p, encoding="utf-8").read()
        # leave the baked blocks alone here: they are rewritten from the browser's output below
        parts = re.split("(" + re.escape(PRE_A) + r".*?" + re.escape(PRE_B) + ")", s, flags=re.S)
        s = "".join(x if x.startswith(PRE_A) else fix_yle_imgs(x) for x in parts)
        if s != o:
            open(p, "w", encoding="utf-8").write(s)
            changed += 1
    # drop the PNGs once nothing in the site points at them any more
    refs = set()
    for f in glob.glob(os.path.join(SITE, "**/*.html"), recursive=True) + [os.path.join(SITE, "sitemap.xml"), os.path.join(SITE, "llms.txt")]:
        if os.path.exists(f):
            refs.update(re.findall(r'/assets/img/(?:yle|pics)/[^"\'\s)<]+?\.png', open(f, encoding="utf-8").read()))
    gone = 0
    for png in pngs:
        if "/" + os.path.relpath(png, SITE) not in refs and os.path.exists(png[:-4] + ".webp"):
            os.remove(png)
            gone += 1
    print(f"practice pictures: {made} converted to WebP, {changed} pages updated, {gone} unreferenced PNGs removed")


# ---------------------------------------------------------------- Quiz JSON-LD
def question(it):
    q = plain(it.get("q")) or plain(it.get("stem")) or f"Question {it.get('n')}"
    why = it.get("why")
    if it.get("accept"):
        node = {"@type": "Question", "name": q, "eduQuestionType": "Short answer",
                "acceptedAnswer": {"@type": "Answer", "text": str(it["accept"][0])}}
        exp = plain(why if isinstance(why, str) else " ".join(why or []))
    elif isinstance(it.get("opts"), list) and isinstance(it.get("a"), int) and it["a"] < len(it["opts"]):
        opts = [plain(o) for o in it["opts"]]
        node = {"@type": "Question", "name": q, "eduQuestionType": "Multiple choice",
                "acceptedAnswer": {"@type": "Answer", "text": opts[it["a"]]},
                "suggestedAnswer": [{"@type": "Answer", "text": o} for k, o in enumerate(opts) if k != it["a"]]}
        exp = plain(why[it["a"]] if isinstance(why, list) and len(why) > it["a"] else (why if isinstance(why, str) else ""))
    else:
        return None
    if exp:
        node["acceptedAnswer"]["answerExplanation"] = {"@type": "Comment", "text": exp}
    return node


def quiz_ld(slug, html, data):
    items = []
    if data.get("prx"):
        prx = data["prx"]
        for s in (prx.get("sets") or [{"items": prx.get("items") or []}]):
            items += s.get("items") or []
    elif data.get("gd"):
        for v in data["gd"].values():
            items += v
    parts = [x for x in (question(it) for it in items) if x]
    if not parts:
        return None
    lv = LEVEL.get(slug.split("-")[0], ("", ""))
    paper = next((v for k, v in PAPER.items() if f"-{k}-" in slug), "")
    t = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.S)
    d = re.search(r'<meta name="description" content="([^"]*)"', html)
    ld = {"@context": "https://schema.org", "@type": "Quiz", "name": plain(t.group(1)) if t else slug,
          "description": d.group(1) if d else "", "url": f"{ORIGIN}/{slug}/", "inLanguage": ["en", "zh-Hant-TW"],
          "isAccessibleForFree": True, "learningResourceType": "Practice test", "educationalUse": "practice",
          "author": {"@type": "Person", "@id": PERSON_ID, "name": "Christopher", "url": ORIGIN + "/certified-american-teacher-banqiao/"},
          "publisher": {"@id": ORG_ID}, "hasPart": parts}
    if lv[0]:
        ld["educationalLevel"] = lv[0]
        ld["about"] = {"@type": "Thing", "name": lv[1]}
    if paper:
        ld["assesses"] = paper
    return ld


# ---------------------------------------------------------------- injection
def inject(src, chunks):
    """Put each captured chunk into its container, in document order. None if the page's
    containers do not line up with what the browser drew."""
    marks = list(CONTAINER.finditer(src))
    conts, i = [], 0
    while i < len(marks):
        m = marks[i]
        if m.group(0).startswith("<form"):
            end = src.find("</form>", m.end())
            slots = [x for x in marks[i + 1:] if x.group(0).startswith("<div") and x.start() < end]
            if slots:
                conts += [(x.end(), "</div>") for x in slots]
                i += 1 + len(slots)
            else:
                conts.append((m.end(), "</form>"))
                i += 1
        else:
            i += 1          # a stray slot outside a form: ignored
    if len(conts) != len(chunks):
        return None
    for (pos, close), html in reversed(list(zip(conts, chunks))):
        block = PRE_A + html.strip() + PRE_B
        if src.startswith(PRE_A, pos):
            end = src.index(PRE_B, pos) + len(PRE_B)
            src = src[:pos] + block + src[end:]
        elif src[pos:].lstrip().startswith(close):
            src = src[:pos] + block + src[pos:]
        else:
            return None
    return src


def main():
    only = set(sys.argv[1:])
    pages = sorted(p for p in glob.glob(os.path.join(SITE, "*/index.html"))
                   if re.search(r"const PRX\b|const GDRILLS\b", open(p, encoding="utf-8").read())
                   and not os.path.basename(os.path.dirname(p)).startswith("gept"))
    if only:
        pages = [p for p in pages if os.path.basename(os.path.dirname(p)) in only]
    yle_pages = sorted(glob.glob(os.path.join(SITE, "*/index.html")))
    yle_pictures([p for p in yle_pages if re.search(r"/assets/img/(?:yle|pics)/", open(p, encoding="utf-8").read())])

    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a, **k):
            pass
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=SITE))
    srv.handle_error = lambda *a, **k: None       # the browser drops blocked requests mid-flight
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{srv.server_address[1]}"

    from bs4 import BeautifulSoup
    from playwright.sync_api import sync_playwright
    done = skipped = 0
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        ctx = br.new_context()
        # the page only needs its own files: tracking and fonts would just slow the run
        ctx.route(re.compile(r"^https?://(?!127\.0\.0\.1)"), lambda r: r.abort())
        pg = ctx.new_page()
        for p in pages:
            slug = os.path.basename(os.path.dirname(p))
            pg.goto(f"{base}/{slug}/", wait_until="domcontentloaded")
            data = pg.evaluate(GRAB)
            chunks = []
            for h in data["out"]:
                if 'class="pane-stim"' in h:        # the stimulus is already on the page above the form
                    frag = BeautifulSoup(h, "html.parser")
                    for x in frag.select(".pane-stim"):
                        x.decompose()
                    h = str(frag)
                chunks.append(fix_yle_imgs(h))
            src = open(p, encoding="utf-8").read()
            new = inject(src, chunks)
            if new is None or not any(c.strip() for c in chunks):
                print(f"  SKIP {slug}: containers do not match ({len(chunks)} drawn)")
                skipped += 1
                continue
            ld = quiz_ld(slug, new, data)
            new = re.sub(re.escape(QUIZ_A) + r".*?" + re.escape(QUIZ_B) + r"\n?", "", new, flags=re.S)
            if ld:
                new = new.replace("</head>", f'{QUIZ_A}\n<script type="application/ld+json">{jd(ld)}</script>\n{QUIZ_B}\n</head>', 1)
            if new != src:
                open(p, "w", encoding="utf-8").write(new)
            done += 1
        br.close()
    srv.shutdown()
    print(f"pre-rendered {done} pages, skipped {skipped}")


if __name__ == "__main__":
    main()

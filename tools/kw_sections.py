#!/usr/bin/env python3
"""
Keyword sections (2026-10-19). One short section per page, written around the search phrase
that brings the page most of its impressions but few clicks, lives in data/kw_sections.json;
seo_build.process_page inserts it on every build, so a generator re-run cannot drop it.

Why: the 10-19 CTR audit found 104 pages below a healthy click rate for their position.
Most of them rank for a phrase the page never answers in so many words (「12pm是幾點」,
「萬聖節快樂英文」, 「英文補習班費用」). The section answers that phrase first, in one or two
sentences, then adds what the page was missing.

Entry: {"id": "...", "h2": "...", "html": "<p>…</p>…", "at": "faq" | "after:<h2 id>"}
  at = "faq" (default): before the FAQ section (or before the last section if there is none);
  at = "after:<id>": after the section that holds the heading with that id.
The block is real content: content_signature() counts it, so adding or editing one moves the
page's sitemap date once. Remove an entry and the next build removes the section.
"""
import os, re, json

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(SITE, "data", "kw_sections.json")
START, END = "<!-- AE:KW start -->", "<!-- AE:KW end -->"
_data = None

def data():
    global _data
    if _data is None:
        _data = json.load(open(DATA, encoding="utf-8")) if os.path.exists(DATA) else {}
    return _data

def strip(html):
    return re.sub(r"\n?" + re.escape(START) + r".*?" + re.escape(END) + r"\n?", "", html, flags=re.S)

def block(e):
    return (f'{START}<section class="section kw-sec"><div class="wrap">'
            f'<div class="center stack reveal"><h2 id="{e["id"]}">{e["h2"]}</h2></div>'
            f'<div class="kw-card prose reveal">{e["html"]}</div></div></section>{END}')

def _section_bounds(main, pos):
    """(start, end) of the outermost <section> of <main> that contains position pos."""
    depth, start = 0, None
    for m in re.finditer(r"<(/?)section\b[^>]*>", main):
        if not m.group(1):
            if depth == 0:
                start = m.start()
            depth += 1
        else:
            depth -= 1
            if depth == 0 and start is not None and start <= pos < m.end():
                return start, m.end()
    return None

def apply(html, rel):
    html = strip(html)
    slug = os.path.dirname(rel).replace(os.sep, "/")
    e = data().get(slug)
    if not e:
        return html
    mm = re.search(r"<main\b[^>]*>(.*)</main>", html, re.S)
    if not mm:
        return html
    main, off = mm.group(1), mm.start(1)
    at = e.get("at", "faq")
    where = None
    if at.startswith("after:"):
        h = re.search(r'<h[23][^>]*\bid="%s"' % re.escape(at[6:]), main)
        b = _section_bounds(main, h.start()) if h else None
        where = b[1] if b else None
    if where is None:
        f = re.search(r'<div class="faq"', main)
        b = _section_bounds(main, f.start()) if f else None
        if b:
            where = b[0]
        else:                                   # no FAQ: before the closing call-to-action section
            secs = [m.start() for m in re.finditer(r"<section\b", main)]
            where = secs[-1] if len(secs) > 1 else len(main)
    if at.startswith("after:") and where is None:
        raise SystemExit(f"kw_sections: {slug}: no heading id {at[6:]!r}")
    return html[:off + where] + "\n" + block(e) + "\n" + html[off + where:]

if __name__ == "__main__":                       # list what is configured and where it lands
    import glob
    for slug, e in sorted(data().items()):
        f = os.path.join(SITE, slug, "index.html")
        ok = os.path.exists(f)
        print(f"{'ok ' if ok else 'MISSING'} {slug:44} at={e.get('at','faq'):28} {e['h2'][:40]}")

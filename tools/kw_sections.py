#!/usr/bin/env python3
"""
Keyword sections (2026-10-19). One short section per page, written around the search phrase
that brings the page most of its impressions but few clicks, lives in data/kw_sections.json;
seo_build.process_page inserts it on every build, so a generator re-run cannot drop it.

Why: the 10-19 CTR audit found 104 pages below a healthy click rate for their position.
Most of them rank for a phrase the page never answers in so many words (「12pm是幾點」,
「萬聖節快樂英文」, 「英文補習班費用」). The section answers that phrase first, in one or two
sentences, then adds what the page was missing.

Entry: {"id": "...", "h2": "...", "html": "<p>…</p>…", "at": "faq" | "after:<h2 id>", "lead": true?}
  lead = true: the box's first sentence also appears as a 「快速解答」 (quick answer) line under the page intro.
  at = "faq" (default): before the FAQ section (or before the last section if there is none);
  at = "after:<id>": after the section that holds the heading with that id.
The block is real content: content_signature() counts it, so adding or editing one moves the
page's sitemap date once. Remove an entry and the next build removes the section.
"""
import os, re, json

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(SITE, "data", "kw_sections.json")
START, END = "<!-- AE:KW start -->", "<!-- AE:KW end -->"
LSTART, LEND = "<!-- AE:KWLEAD start -->", "<!-- AE:KWLEAD end -->"
_data = None

def data():
    global _data
    if _data is None:
        _data = json.load(open(DATA, encoding="utf-8")) if os.path.exists(DATA) else {}
    return _data

def strip(html):
    html = re.sub(r"\n?[ \t]*" + re.escape(LSTART) + r".*?" + re.escape(LEND), "", html, flags=re.S)   # lead() inserts "\n    "
    return re.sub(r"\n?" + re.escape(START) + r".*?" + re.escape(END) + r"\n?", "", html, flags=re.S)

def lead_sentence(e):
    """The box's own first sentence, as plain text: the quick answer shown under the page intro."""
    if isinstance(e.get("lead"), str):          # an entry may word its own quick answer
        return e["lead"]
    m = re.search(r"<p>(.*?)</p>", e["html"], re.S)
    t = re.sub(r"<[^>]+>", "", m.group(1)) if m else ""
    cut = t.find("。")
    return (t[:cut + 1] if cut > 0 else t).strip()

def lead(html, e):
    """'lead': true → a one-line quick answer right after the page-hero intro paragraph, linking down to
    the full section. The 10-20 audit found the boxes 23–76% down long pages (the 12pm answer at 6,279 px
    on a phone): Google reads them, but a parent who lands from the search did not see the answer first."""
    h = re.search(r'<section class="page-hero.*?</section>', html, re.S)
    if not h:
        return html
    pe = html.find("</p>", h.start(), h.end())
    if pe < 0:
        return html
    pe += 4
    strip_ = (f'{LSTART}<p class="kw-lead reveal d2"><span class="kw-lead-tag">快速解答</span>{lead_sentence(e)}'
              f'<a href="#{e["id"]}">看完整說明 ↓</a></p>{LEND}')
    return html[:pe] + "\n    " + strip_ + html[pe:]

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
    html = html[:off + where] + "\n" + block(e) + "\n" + html[off + where:]
    return lead(html, e) if e.get("lead") else html

if __name__ == "__main__":                       # list what is configured and where it lands
    import glob
    for slug, e in sorted(data().items()):
        f = os.path.join(SITE, slug, "index.html")
        ok = os.path.exists(f)
        print(f"{'ok ' if ok else 'MISSING'} {slug:44} at={e.get('at','faq'):28} {e['h2'][:40]}")

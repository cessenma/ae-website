#!/usr/bin/env python3
"""
Site-wide in-text links (2026-10-19). Rules live in data/autolinks.json; seo_build.py calls
apply() on every page, so the links survive any generator re-run.

Why: internal links tell Google which page is the main one for a topic, and links inside
the article text count for more than a "read next" box. A scan on 10-19 found the words
already on the site but the links missing — 48 pages say 複數 and 2 link to the plurals
page; 52 say 卡片 and 3 link to the card page; the worksheet maker had 0 of 19.

Rules for a link (all must hold):
  - inside <main>, in a paragraph or list item (also FAQ answers), never in a heading, table,
    button, label, the page hero, a download box, a widget or any tool-injected block;
  - the page does not already link the target in its own text, and is not the target;
  - first eligible mention only (longest keyword wins at a position), Latin keywords on word
    boundaries; one link per paragraph; at most max_per_page links, chosen by rule priority;
  - not on practice-test pages, the sales/contact pages, or the title-test pages before their
    hold date (they start linking automatically after it).
Links carry data-al="1": every build removes them first and re-applies, so changing a rule
changes the site, and content_signature() ignores them (no sitemap date churn).
"""
import os, re, json, datetime

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = os.path.join(SITE, "data", "autolinks.json")
_cfg = None

BANNED_TAGS = {"a", "button", "h1", "h2", "h3", "h4", "h5", "h6", "script", "style", "label", "th", "td",
               "table", "figcaption", "figure", "summary", "select", "option", "textarea", "code", "pre",
               "nav", "header", "footer", "svg", "title", "form", "blockquote"}
BANNED_CLASSES = {"page-hero", "magnet-box", "ae-cta", "breadcrumb", "pg-toc", "chart-fig", "kkl", "wsm", "cw",
                  "compare", "hubcard", "region-cta", "byl", "page-meta", "faq-q", "kkl-note", "wsm-hint",
                  "post-hero", "cta-box", "season-strip", "eyebrow",
                  "tcard", "pr-quoteband", "stars", "who"}          # parents' testimonials stay as written
BLOCKS = {"p", "li"}
VOID = {"br", "img", "input", "meta", "link", "hr", "source", "wbr", "col", "area", "base", "embed", "track"}
INJECTED = [("<!-- AE:ROUTE -->", "<!-- /AE:ROUTE -->"), ("<!-- AE:READNEXT", "<!-- AE:READNEXT end -->"),
            ("<!-- AE:REGION -->", "<!-- /AE:REGION -->"), ("<!-- AE:TOC -->", "<!-- /AE:TOC -->"),
            ("<!-- AE:NEXT start", "<!-- AE:NEXT end -->"), ("<!-- AE:SEASON", "<!-- AE:SEASON end -->"),
            ("<!-- AE:PACKOFFER -->", "<!-- /AE:PACKOFFER -->"), ("<!-- AE:KKLOOKUP start -->", "<!-- AE:KKLOOKUP end -->"),
            ("<!-- AE:GEPTPRX -->", "<!-- /AE:GEPTPRX -->"),
            ("<!--AE:PRE-->", "<!--/AE:PRE-->"), ("<!-- AE:AUDIO start -->", "<!-- AE:AUDIO end -->")]
AL_RE = re.compile(r'<a href="[^"]*" data-al="1">(.*?)</a>', re.S)

def cfg():
    global _cfg
    if _cfg is None:
        _cfg = json.load(open(CFG, encoding="utf-8")) if os.path.exists(CFG) else {"rules": []}
        for r in _cfg["rules"]:
            r["kw"] = sorted(r["kw"], key=lambda k: len(k[3:]) if k.startswith("re:") else len(k), reverse=True)
    return _cfg

def strip(html):
    """Remove every link this tool made (idempotence; also what content_signature ignores)."""
    return AL_RE.sub(lambda m: m.group(1), html)

def page_slug(rel):
    d = os.path.dirname(rel)
    return d.replace(os.sep, "/")

def source_allowed(slug, today=None):
    c = cfg()
    if slug in c.get("skip_sources", []):
        return False
    pat = c.get("skip_source_pattern")
    if pat and re.search(pat, slug):
        return False
    today = today or datetime.date.today().isoformat()
    for until, pages in c.get("hold_sources_until", {}).items():
        if today < until and slug in pages:
            return False
    return True

_RX = {}
def _kw_regex(k):
    if k in _RX:
        return _RX[k]
    _RX[k] = _make_regex(k)
    return _RX[k]

def _make_regex(k):
    if k.startswith("re:"):                     # a raw pattern, e.g. 格線 but not 及格線
        return re.compile(k[3:])
    if re.search(r"[A-Za-z]", k):
        return re.compile(r"(?<![A-Za-z0-9])" + re.escape(k) + r"(?![A-Za-z0-9])")
    return re.compile(re.escape(k))

def _attrs_classes(tag):
    m = re.search(r'\bclass="([^"]*)"', tag)
    return set(m.group(1).split()) if m else set()

def apply(html, rel, today=None):
    html = strip(html)
    slug = page_slug(rel)
    c = cfg()
    if not c["rules"] or not source_allowed(slug, today):
        return html
    mm = re.search(r"<main\b.*?</main>", html, re.S)
    if not mm:
        return html
    main = mm.group(0)
    # protect tool blocks: swap them for placeholders that contain no text
    saved = []
    def hide(m):
        saved.append(m.group(0)); return f"\x00{len(saved) - 1}\x00"
    main = re.sub(r"<!-- AE:CHART (\S+) start -->.*?<!-- AE:CHART \1 end -->", hide, main, flags=re.S)
    for a, b in INJECTED:
        main = re.sub(re.escape(a) + r".*?" + re.escape(b), hide, main, flags=re.S)
    own = set(re.findall(r'href="/([^"#?]*?)/?(?:[#?][^"]*)?"', main))      # targets already linked in the text
    toks = re.split(r"(<[^>]+>)", main)
    # walk: find the first eligible match of every rule
    stack, block_id, nblock = [], None, 0
    first = {}                                  # rule index -> (token index, start, end, block id)
    for ti, t in enumerate(toks):
        if t.startswith("<"):
            if t.startswith("<!--") or t.startswith("<!"):
                continue
            m = re.match(r"<\s*(/)?\s*([a-zA-Z0-9]+)", t)
            if not m:
                continue
            closing, name = m.group(1), m.group(2).lower()
            if closing:
                for k in range(len(stack) - 1, -1, -1):
                    if stack[k][0] == name:
                        del stack[k:]; break
            elif name not in VOID and not t.endswith("/>"):
                stack.append((name, _attrs_classes(t), t))
                if name in BLOCKS:
                    nblock += 1
            continue
        if not t.strip() or "\x00" in t:
            continue
        names = [s[0] for s in stack]
        if not any(n in BLOCKS for n in names) or any(n in BANNED_TAGS for n in names):
            continue
        if any(s[1] & BANNED_CLASSES for s in stack):
            continue
        blk = max(i for i, s in enumerate(stack) if s[0] in BLOCKS)
        bid = id(stack[blk]) if False else (blk, stack[blk][2], nblock)
        for ri, r in enumerate(c["rules"]):
            if ri in first or r["target"] == slug or r["target"] in own:
                continue
            best = None
            for k in r["kw"]:
                for mt in _kw_regex(k).finditer(t):
                    if best is None or mt.start() < best[0]:
                        best = (mt.start(), mt.end())
                    break
            if best:
                first[ri] = (ti, best[0], best[1], bid)
    # choose by priority: one per paragraph, at most max_per_page, no overlapping spans
    chosen, used_blocks, spans = [], set(), {}
    for ri in sorted(first):
        if len(chosen) >= c.get("max_per_page", 8):
            break
        ti, a, b, bid = first[ri]
        if bid in used_blocks:
            continue
        if any(not (b <= x or a >= y) for x, y in spans.get(ti, [])):
            continue
        chosen.append((ti, a, b, c["rules"][ri]["target"]))
        used_blocks.add(bid); spans.setdefault(ti, []).append((a, b))
    if not chosen:
        return html
    for ti in sorted({x[0] for x in chosen}):
        t = toks[ti]
        for _, a, b, target in sorted([x for x in chosen if x[0] == ti], key=lambda x: -x[1]):
            t = t[:a] + f'<a href="/{target}/" data-al="1">' + t[a:b] + "</a>" + t[b:]
        toks[ti] = t
    main2 = "".join(toks)
    while "\x00" in main2:                     # blocks can sit inside blocks: restore until none are left
        main2 = re.sub(r"\x00(\d+)\x00", lambda m: saved[int(m.group(1))], main2)
    return html[:mm.start()] + main2 + html[mm.end():]

if __name__ == "__main__":                      # dry run: what would be linked, per page
    import glob, sys
    total, pages = 0, 0
    for f in sorted(glob.glob(os.path.join(SITE, "*/index.html")) + glob.glob(os.path.join(SITE, "*/*/index.html"))):
        rel = os.path.relpath(f, SITE)
        s = open(f, encoding="utf-8").read()
        if "noindex" in s[:6000]:
            continue
        out = apply(s, rel)
        n = len(AL_RE.findall(out))
        if n:
            total += n; pages += 1
            if "-v" in sys.argv:
                print(f"{n:2d}  {rel}: " + ", ".join(f"{m.group(1)}→{m.group(0).split(chr(34))[1]}" for m in AL_RE.finditer(out)))
    print(f"{total} links on {pages} pages")

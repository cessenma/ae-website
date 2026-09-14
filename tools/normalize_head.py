#!/usr/bin/env python3
"""
Restore the head-tag attribute order that BeautifulSoup round-trips destroy.

Why this is not cosmetic: seo_build.py finds a page's own URL with
    re.search(r'<link rel="canonical" href="([^"]+)"', html)
so a page written back through BeautifulSoup — which re-emits the tag as
<link href="..." rel="canonical"/> — stops matching, and that page silently loses
its BreadcrumbList. It cost /colors-english-vocabulary/ and
/english-abbreviations-guide/ their breadcrumbs, both pages that rank.

Any tool here that parses a page with BeautifulSoup must call normalize() on the
string it writes back.

Usage:  python3 tools/normalize_head.py          # fix every page
"""
import re, sys, glob, os

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def normalize(html: str) -> str:
    html = re.sub(r'<link\s+href="([^"]+)"\s+rel="canonical"\s*/?>',
                  r'<link rel="canonical" href="\1">', html)
    html = re.sub(r'<meta\s+content="([^"]*)"\s+property="(og:[^"]+)"\s*/?>',
                  r'<meta property="\2" content="\1">', html)
    html = re.sub(r'<meta\s+content="([^"]*)"\s+name="([^"]+)"\s*/?>',
                  r'<meta name="\2" content="\1">', html)
    html = re.sub(r'<meta\s+charset="([^"]+)"\s*/>', r'<meta charset="\1">', html)
    return html

if __name__ == "__main__":
    files = sys.argv[1:] or sorted(glob.glob(os.path.join(SITE, "*/index.html"))) + \
            [os.path.join(SITE, "index.html")]
    n = 0
    for f in files:
        if not os.path.exists(f): continue
        s = open(f, encoding="utf-8").read()
        t = normalize(s)
        if t != s:
            open(f, "w", encoding="utf-8").write(t); n += 1
            print("  normalized", os.path.relpath(f, SITE))
    print(f"{n} pages normalized")

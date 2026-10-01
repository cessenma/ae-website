#!/usr/bin/env python3
"""Re-hash every ledger entry and KEEP its date.

Run this once, right after an edit that is not a content update — removing a duplicated
byline, renaming a class, swapping a tag — so the edit does not stamp today's date on the
sitemap and on the page's "last updated" line. Do not run it after a real content change.

    python3 tools/rebaseline_lastmod.py            # every page
    python3 tools/rebaseline_lastmod.py kk-phonetic-chart months-english
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import seo_build as S

only = set(sys.argv[1:])
led = S.load_ledger()
n = 0
for key, ent in led.items():
    if only and key not in only:
        continue
    if os.path.splitext(key)[1] == ".pdf":
        continue
    f = os.path.join(S.SITE, "index.html" if key == "index" else ("404.html" if key == "404" else key + "/index.html"))
    if not os.path.exists(f):
        continue
    h = S.authored_hash(open(f, encoding="utf-8").read())
    if h != ent.get("hash"):
        ent["hash"] = h
        n += 1
S.save_ledger(led)
print(f"re-hashed {n} entries, dates kept")

#!/usr/bin/env python3
"""Bake the score calculators' input rows into the served HTML.

calc.js draws the rows of the KET / PET / FCE calculators and the shields page after the page
has appeared. The widget sits in the first screen, so everything under it jumped down by its
height: layout shift 0.15-0.18 at tablet width and 0.03 on desktop (2026-10 audit).

This runs each page once in headless Chromium, lets calc.js draw the rows, and writes that
markup into the empty container between the AE:PRE markers (the same markers
prerender_practice.py uses, so the page's content signature ignores it). In the browser
calc.js empties the container and draws the same rows again, so nothing moves.

Idempotent. Run after editing calc.js or one of the four pages, before seo_build.py:

    ~/.claude/skills/seo/.venv/bin/python3 tools/prerender_widgets.py
"""
import functools, http.server, os, re, sys, threading

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRE_A, PRE_B = "<!--AE:PRE-->", "<!--/AE:PRE-->"
PAGES = {"ket-score-calculator": "calc-rows", "pet-score-calculator": "calc-rows",
         "fce-score-calculator": "calc-rows", "cambridge-yle-shields": "sh-rows"}


def main():
    from playwright.sync_api import sync_playwright
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a, **k):
            pass
    handler = functools.partial(Quiet, directory=SITE)
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{srv.server_address[1]}"
    changed = 0
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page()
        pg.route("**/*", lambda r: r.continue_() if r.request.url.startswith(base) else r.abort())
        for slug, cls in PAGES.items():
            path = os.path.join(SITE, slug, "index.html")
            src = open(path, encoding="utf-8").read()
            box = re.compile(r'(<div class="%s">)(.*?)(</div>\s*<div class="[a-z -]*calc-result)' % cls, re.S)
            m = box.search(src)
            if not m:
                print(f"  {slug}: container .{cls} not found"); continue
            pg.goto(f"{base}/{slug}/", wait_until="load")
            pg.wait_for_selector(f".{cls} > *")
            rows = pg.evaluate(f"document.querySelector('.{cls}').innerHTML")
            new = src[:m.start(2)] + PRE_A + rows + PRE_B + src[m.end(2):]
            if new != src:
                open(path, "w", encoding="utf-8").write(new); changed += 1
            print(f"  {slug}: {len(rows)} characters of rows baked in")
        b.close()
    srv.shutdown()
    print(f"prerender_widgets: {changed} page(s) changed")
    return 0


if __name__ == "__main__":
    sys.exit(main())

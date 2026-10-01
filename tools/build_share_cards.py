#!/usr/bin/env python3
"""A share picture (1200x630 JPEG) for every page that has no picture of its own.

Why: 98 pages (the practice pages, the calculators, most local guides) showed the same brand
card when a link was pasted into LINE or Facebook, and their Article markup named that card as
the article's image. A card that carries the page's own headline says what the link is.

Each card is rendered by a real browser from the page's <h1> (and the small label above it),
so the text can never drift from the page. Run it after headlines change:

    python3 tools/build_share_cards.py            # every page that needs one
    python3 tools/build_share_cards.py slug ...   # only these folders
    python3 tools/seo_build.py --strict           # points og:image / JSON-LD at the cards

Output: assets/img/share/<folder>.jpg. Needs Playwright (the seo venv has it).
"""
import html as _html, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import seo_build as sb
from bs4 import BeautifulSoup

OUT = os.path.join(sb.SITE, "assets", "img", "share")
import base64
LOGO = "data:image/webp;base64," + base64.b64encode(
    open(os.path.join(sb.SITE, "assets", "img", "american-english-banqiao-logo-96.webp"), "rb").read()).decode()
GENERIC = (sb.OG_DEFAULT, sb.LOGO)

CARD = """<!doctype html><html lang="zh-Hant-TW"><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@700;800&family=DM+Serif+Display:ital@0;1&display=block" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{width:1200px;height:630px;overflow:hidden}
.card{position:relative;width:1200px;height:630px;padding:54px 72px 0;background:linear-gradient(155deg,#fff 0%,#F0F9FF 55%,#DDF4FF 100%);
  font-family:'Baloo 2','PingFang TC','Noto Sans TC',sans-serif;color:#1A2752;overflow:hidden}
.dot{position:absolute;border-radius:50%}
.brand{display:flex;align-items:center;gap:14px;font-weight:800;font-size:30px}
.brand img{width:54px;height:54px;border-radius:50%}
.brand b{color:#0889c6}
.mid{position:absolute;left:72px;right:72px;top:150px;bottom:112px;display:flex;flex-direction:column;justify-content:center}
.eye{align-self:flex-start;font-weight:700;font-size:25px;letter-spacing:2px;color:#066d9e;background:rgba(28,176,246,.14);padding:8px 22px;border-radius:100px;margin-bottom:22px}
h1{font-family:'DM Serif Display','Songti TC','Noto Serif TC','PMingLiU',serif;font-weight:400;font-size:@SIZE@px;line-height:1.16;letter-spacing:-.5px;line-break:strict;text-wrap:balance}
h1 em{font-style:italic;color:#0889c6}
h1 .l{display:inline-block;text-wrap:balance;max-width:100%}
.foot{position:absolute;left:0;right:0;bottom:0;height:86px;background:#1A2752;color:#fff;display:flex;align-items:center;justify-content:space-between;padding:0 72px;font-size:24px;font-weight:700}
.foot span:last-child{color:#FFC828}
</style></head><body><div class="card">
<span class="dot" style="width:210px;height:210px;right:-60px;top:-70px;background:rgba(28,176,246,.16)"></span>
<span class="dot" style="width:26px;height:26px;right:210px;top:92px;background:#FFC828"></span>
<span class="dot" style="width:18px;height:18px;right:120px;top:210px;background:#CE82FF"></span>
<span class="dot" style="width:14px;height:14px;right:300px;top:54px;background:#06C755"></span>
<div class="brand"><img src="@LOGO@" alt="">埃森<b>美語</b>&nbsp;American English</div>
<div class="mid">@EYE@<h1>@TITLE@</h1></div>
<div class="foot"><span>板橋中正路・美籍持證教師・每班 12 人以內</span><span>americanenglish.com.tw</span></div>
</div></body></html>"""

def needs_card(rel, page):
    """True when the page's share picture is, or would be, the brand card or the bare logo."""
    own = re.search(r'<meta[^>]*property="og:image"[^>]*content="([^"]+)"', page)
    if own:
        return own.group(1).endswith(GENERIC) or "/assets/img/share/" in own.group(1)
    return sb.share_image(rel, BeautifulSoup(page, "lxml"), cards=False) == sb.OG_DEFAULT

def card_html(page):
    page = re.sub(r"<wbr\s*/?>", "", page)              # (a parser treats <wbr> as a wrapper and loses the text after it)
    soup = BeautifulSoup(page, "lxml")
    h1 = soup.select_one("h1")
    if not h1:
        return None
    for s in h1.select("span.h1s"):
        s.unwrap()
    title = h1.decode_contents().strip()
    title = re.sub(r"<(?!/?(?:em|br)\b)[^>]+>", "", title)            # keep only <em> and <br>
    eye = soup.select_one(".page-hero .eyebrow, .hero .eyebrow, main .eyebrow")
    eye = f'<span class="eye">{_html.escape(eye.get_text(" ", strip=True))}</span>' if eye and len(eye.get_text(strip=True)) <= 26 else ""
    # the largest type that fits: 1040 px wide, about 300 px tall under the label (360 without one).
    # First choice: every line of the headline on one line; only a long headline is allowed to wrap.
    raw = re.split(r"<br\s*/?>", title)
    parts = [sb.snippet_width(_html.unescape(re.sub(r"<[^>]+>", "", x)).strip()) for x in raw]
    room = 300 if eye else 360
    def fits(px, wrap):
        lines = sum(max(1, -(-(u * px // 2) // 1040)) for u in parts)
        return (wrap or lines == len(parts)) and lines * px * 1.16 <= room
    size = next((px for px in (100, 92, 84, 76, 68, 60) if fits(px, False)),
                next((px for px in (68, 60, 54, 48) if fits(px, True)), 44))
    title = "<br>".join(f'<span class="l">{x.strip()}</span>' for x in raw)      # each line balances on its own
    return CARD.replace("@SIZE@", str(size)).replace("@LOGO@", LOGO).replace("@EYE@", eye).replace("@TITLE@", title)

def main():
    listing = "--list" in sys.argv
    want = set(a for a in sys.argv[1:] if not a.startswith("--"))
    pages = sorted(os.path.join(d, f) for d, _, fs in os.walk(sb.SITE) for f in fs if f == "index.html")
    jobs = []
    for path in pages:
        rel = os.path.relpath(path, sb.SITE)
        slug = os.path.dirname(rel) or "home"
        if rel in sb.SELF_CONTAINED or rel.startswith(("tools/", "pack-")) or (want and slug not in want):
            continue
        page = open(path, encoding="utf-8").read()
        if 'content="noindex' in page or not needs_card(rel, page):
            continue
        doc = card_html(page)
        if doc:
            jobs.append((slug.replace("/", "--"), doc))
    if listing:
        print(len(jobs), "pages need a card:", " ".join(n for n, _ in jobs)); return
    if not jobs:
        print("no page needs a share card"); return
    os.makedirs(OUT, exist_ok=True)
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport={"width": 1200, "height": 630}, device_scale_factor=1)
        for name, doc in jobs:
            pg.set_content(doc, wait_until="networkidle")
            pg.evaluate("document.fonts.ready")
            pg.screenshot(path=os.path.join(OUT, name + ".jpg"), type="jpeg", quality=84)
        b.close()
    kb = sum(os.path.getsize(os.path.join(OUT, n + ".jpg")) for n, _ in jobs) / 1024
    print(f"{len(jobs)} share cards written to assets/img/share/ ({kb:.0f} KB)")

if __name__ == "__main__":
    main()

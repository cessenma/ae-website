#!/usr/bin/env python3
"""
American English 埃森美語 — SEO build step.

Bakes into each static page (so non-JS / AI crawlers see them):
  - FAQPage JSON-LD  (from .faq-item)
  - BreadcrumbList JSON-LD  (from .breadcrumb)
  - hreflang alternates (zh-Hant-TW + x-default)
  - the header nav + drawer + progress bar (the chrome app.js used to inject)
Also regenerates sitemap.xml — <lastmod> comes from data/lastmod.json, a ledger keyed on a
hash of each page's AUTHORED html (injected blocks stripped), never from mtime or git date —
and bumps app.js?v=.

Idempotent: re-running replaces the marked blocks instead of duplicating.
app.js is guarded to skip anything already present (see assets/app.js).

Run:  ~/.claude/skills/seo/.venv/bin/python3 seo_build.py
(Lives OUTSIDE site/ so it is never deployed.)
"""
import os, re, json, datetime, hashlib
from urllib.parse import urljoin
from bs4 import BeautifulSoup

SITE   = os.path.expanduser("~/Documents/GitHub/ae-website")
ORIGIN = "https://americanenglish.com.tw"
APPJS_VER = 14
LINE = "https://lin.ee/W9J8TuQ"
LOGO = "/assets/img/american-english-banqiao-logo.jpg"
NAV  = [("首頁","/"),("課程","/courses/"),("劍橋英檢","/exams/"),("師資","/certified-american-teacher-banqiao/"),
        ("家長見證","/banqiao-parent-testimonials/"),("部落格","/blog/")]

SEO_START, SEO_END       = "<!-- AE:SEO-LD start -->", "<!-- AE:SEO-LD end -->"
CHROME_START, CHROME_END = "<!-- AE:CHROME start -->", "<!-- AE:CHROME end -->"
CRIT_START, CRIT_END     = "<!-- AE:CRIT start -->", "<!-- AE:CRIT end -->"
GTM_START, GTM_END       = "<!-- AE:GTM start -->", "<!-- AE:GTM end -->"

GA_ID = "G-CH7TGR171G"
# Everything above this stylesheet section is above-the-fold and gets inlined.
CRIT_CUT_MARKER = "Marquee"
# Self-contained landing pages: they ship their own complete <style> AND their own
# header/progress bar, and never link styles.css. Injecting the site CSS overrides their
# design (the site's `.split .stack` rule right-aligns /line/'s mobile hero copy), and
# injecting the chrome gives them a second <header> with duplicate id="siteHeader" /
# id="progress" — invalid HTML and a visibly doubled header on a paid-ad landing page.
# They still get hreflang + breadcrumb + FAQ JSON-LD via the SEO block.
SELF_CONTAINED = {"line/index.html",
                  # private pack delivery: standalone styling, no site nav,
                  # and it must stay out of the crawl surface entirely
                  "pack-9rvvw6p3nnmls4/index.html"}

def css_fingerprint():
    """Content hash of styles.css — cache-busts automatically whenever the CSS changes,
    which also guarantees the inlined critical block below can never go stale."""
    raw = open(os.path.join(SITE, "assets", "styles.css"), "rb").read()
    return hashlib.md5(raw).hexdigest()[:8]

def critical_css():
    """The above-the-fold slice of styles.css, comment-stripped and whitespace-collapsed.
    Inlining this removes the render-blocking stylesheet request: measured on the homepage
    (Lighthouse 12, simulated mobile) this took LCP 5.14s -> 1.90s and TBT 226ms -> 44ms."""
    css = open(os.path.join(SITE, "assets", "styles.css"), encoding="utf-8").read()
    lines = css.split("\n")
    cut = next((i for i, l in enumerate(lines)
                if CRIT_CUT_MARKER in l and l.strip().startswith("/*")), len(lines))
    crit = "\n".join(lines[:cut]).strip()
    crit = re.sub(r"/\*.*?\*/", "", crit, flags=re.S)
    crit = re.sub(r"\s*\n\s*", "", crit)
    return re.sub(r"\s{2,}", " ", crit)

def crit_block(ver, crit):
    href = f"/assets/styles.css?v={ver}"
    return (f"{CRIT_START}\n<style id=\"crit\">{crit}</style>\n"
            f'<link rel="preload" as="style" href="{href}" '
            "onload=\"this.onload=null;this.rel='stylesheet'\">"
            f'<noscript><link rel="stylesheet" href="{href}"></noscript>\n{CRIT_END}\n')

META_PIXEL_ID = "1023907773471013"

def gtm_block():
    """GA4 loaded on first interaction, or 2.5s after load — whichever comes first.
    Config is queued into dataLayer immediately, so no events are lost, but GTM's
    ~190ms of script evaluation and its long tasks leave the critical path."""
    return (
        f"{GTM_START}\n<script>(function(){{window.dataLayer=window.dataLayer||[];"
        "function gtag(){dataLayer.push(arguments);}window.gtag=gtag;"
        f"gtag('js',new Date());gtag('config','{GA_ID}');"
        # Meta Pixel on every page, same deferred loader. The stub queues init and
        # PageView now and fbevents.js drains the queue when it loads, so the
        # landing-page view still registers -- Meta needs it on the destination page
        # to optimise for landing page views at all. This is the ONE place the pixel
        # is initialised; pages that fire their own events (Lead on /line/, 購買 taps
        # on the pack page) call fbq but must not init or track PageView again.
        "if(!window.fbq){var n=window.fbq=function(){n.callMethod?"
        "n.callMethod.apply(n,arguments):n.queue.push(arguments)};"
        "window._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];}"
        f"fbq('init','{META_PIXEL_ID}');fbq('track','PageView');"
        "var loaded=0,load=function(){if(loaded)return;loaded=1;"
        "var s=document.createElement('script');s.async=1;"
        f"s.src='https://www.googletagmanager.com/gtag/js?id={GA_ID}';"
        "document.head.appendChild(s);"
        "var f=document.createElement('script');f.async=1;"
        "f.src='https://connect.facebook.net/en_US/fbevents.js';"
        "document.head.appendChild(f);};"
        "['pointerdown','keydown','touchstart','scroll'].forEach(function(e){"
        "addEventListener(e,load,{once:true,passive:true});});"
        f"addEventListener('load',function(){{setTimeout(load,2500);}});}})();</script>\n{GTM_END}\n"
    )

# the original eager GA4 pair, replaced by the deferred loader above
OLD_GTM_RE = re.compile(
    r'<script async src="https://www\.googletagmanager\.com/gtag/js\?id=' + GA_ID + r'"></script>\s*'
    r'<script>window\.dataLayer=window\.dataLayer\|\|\[\];function gtag\(\)\{dataLayer\.push\(arguments\);\}'
    r"gtag\('js',new Date\(\)\);gtag\('config','" + GA_ID + r"'\);</script>\s*")
# any bare stylesheet link (superseded by the inlined critical block + preload)
PLAIN_CSS_RE = re.compile(r'<link rel="stylesheet" href="/assets/styles\.css(?:\?v=[^"]*)?">\s*')

def jd(obj):  # compact, unicode-preserving (matches existing static JSON-LD)
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))

def page_key(path):  # mirror app.js pageKey()
    p = path.split("?")[0].split("#")[0].rstrip("/")
    p = p.split("/")[-1].replace(".html", "")
    return p or "index"

def nav_links(active_key, is_drawer):
    out = []
    for t, h in NAV:
        active = ' class="active"' if page_key(h) == active_key else ""
        out.append(f'<a href="{h}"{active}>{t}</a>')
    cls = "btn btn-primary" + ("" if is_drawer else " nav-cta")
    out.append(f'<a href="{LINE}" target="_blank" rel="noopener" class="{cls}">LINE 預約試聽</a>')
    return "".join(out)

def chrome_block(active_key):
    return (
        f"{CHROME_START}\n"
        '<div class="progress" id="progress"></div>\n'
        '<header class="site-header" id="siteHeader"><div class="wrap nav">'
        f'<a href="/" class="brand"><img class="brand-logo" src="{LOGO}" '
        'alt="American English 埃森美語 logo" width="38" height="38" fetchpriority="high">埃森<b>美語</b></a>'
        f'<nav class="nav-links" aria-label="主選單">{nav_links(active_key, False)}</nav>'
        '<button class="hamburger" id="hamburger" aria-label="開啟選單" aria-expanded="false" '
        'aria-controls="drawer"><span></span><span></span><span></span></button>'
        "</div></header>\n"
        f'<div class="drawer" id="drawer">{nav_links(active_key, True)}</div>\n'
        f"{CHROME_END}\n"
    )

def faq_ld(soup):
    faqs = []
    for item in soup.select(".faq-item"):
        q, a = item.select_one(".faq-q"), item.select_one(".faq-a")
        if not (q and a):
            continue
        for pm in q.select(".pm"):
            pm.extract()
        qt = q.get_text(strip=True)
        at = a.get_text(" ", strip=True)
        if qt and at:
            faqs.append({"@type": "Question", "name": qt,
                         "acceptedAnswer": {"@type": "Answer", "text": at}})
    if faqs:
        return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": faqs}
    return None

def breadcrumb_ld(soup, page_url):
    crumb = soup.select_one(".breadcrumb")
    if not crumb:
        return None
    parts, i = [], 1
    for a in crumb.select("a"):
        parts.append({"@type": "ListItem", "position": i,
                      "name": a.get_text(strip=True),
                      "item": urljoin(page_url, a.get("href", ""))})
        i += 1
    h1 = soup.select_one("h1")
    name = re.sub(r"\s+", " ", h1.get_text(strip=True)) if h1 else (soup.title.get_text(strip=True) if soup.title else "")
    parts.append({"@type": "ListItem", "position": i, "name": name})
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": parts}

def strip_block(html, start, end):
    return re.sub(re.escape(start) + r".*?" + re.escape(end) + r"\n?", "", html, flags=re.S)

# Publisher node for generated pages (practice/grammar/vocab): the question-bank builders
# emit no JSON-LD, so those pages carried only the injected BreadcrumbList and lost the
# entity/E-E-A-T association every hand-written page has. Injected only when the page does
# not already define the canonical #organization node itself. Deliberately compact — and
# deliberately WITHOUT aggregateRating, which stays on the hand-written pages only.
ORG_LD = {"@context": "https://schema.org",
          "@type": ["EducationalOrganization", "LocalBusiness"],
          "@id": ORIGIN + "/#organization",
          "name": "American English 埃森美語",
          "alternateName": "埃森美語",
          "url": ORIGIN,
          "logo": ORIGIN + LOGO,
          "telephone": "+886-928-067-772",
          "address": {"@type": "PostalAddress", "streetAddress": "中正路89巷4號1樓",
                      "addressLocality": "板橋區", "addressRegion": "新北市",
                      "postalCode": "220", "addressCountry": "TW"}}

def process_page(path, css_ver="", crit=""):
    rel = os.path.relpath(path, SITE)
    html = open(path, encoding="utf-8").read()
    original = html          # kept so we can skip writing files this build did not change
    soup = BeautifulSoup(html, "lxml")

    m = re.search(r'<link rel="canonical" href="([^"]+)"', html)
    canon = m.group(1) if m else urljoin(ORIGIN, "/" + os.path.dirname(rel) + "/" if os.path.dirname(rel) else ORIGIN + "/")
    key = page_key(canon)

    # --- build SEO-LD head block ---
    seo = [SEO_START,
           f'<link rel="alternate" hreflang="zh-Hant-TW" href="{canon}">',
           f'<link rel="alternate" hreflang="x-default" href="{canon}">']
    bc = breadcrumb_ld(soup, canon)
    fq = faq_ld(BeautifulSoup(html, "lxml"))  # fresh soup (faq_ld mutates)
    if bc: seo.append(f'<script type="application/ld+json">{jd(bc)}</script>')
    if fq: seo.append(f'<script type="application/ld+json">{jd(fq)}</script>')
    # org node for pages that define none of their own (checked against the page with the
    # old SEO block stripped, so a previous injection never suppresses the re-injection)
    if '"@id":"' + ORIGIN + '/#organization"' not in strip_block(html, SEO_START, SEO_END):
        seo.append(f'<script type="application/ld+json">{jd(ORG_LD)}</script>')
    seo.append(SEO_END)
    seo_block = "\n".join(seo) + "\n"

    # The page's declared language must match the hreflang code we emit below. The site
    # shipped lang="zh-Hant" against hreflang="zh-Hant-TW" — valid separately, inconsistent
    # together, and auditors flag the pair as a language mismatch.
    html = re.sub(r'<html lang="zh-Hant">', '<html lang="zh-Hant-TW">', html, count=1)

    # --- rewrite (literal str.replace only — no regex replacement-string escaping) ---
    html = strip_block(html, SEO_START, SEO_END)
    html = strip_block(html, CHROME_START, CHROME_END)
    html = strip_block(html, CRIT_START, CRIT_END)
    html = strip_block(html, GTM_START, GTM_END)
    if "</head>" not in html or not re.search(r"<body[^>]*>", html):
        return rel, "SKIP (no head/body)"

    # perf: inline critical CSS + async-load the rest; defer GA4 off the critical path
    html = OLD_GTM_RE.sub("", html)
    html = html.replace("</head>", seo_block + gtm_block() + "</head>", 1)

    # The critical block must land EARLY in <head> — ahead of any page-specific <style> —
    # so per-page overrides keep winning the cascade (certified-american-teacher-banqiao
    # tunes .compare there). Anchor it after the viewport meta, else right after <head>.
    if crit and rel not in SELF_CONTAINED:
        html = PLAIN_CSS_RE.sub("", html)
        block = crit_block(css_ver, crit)
        m = re.search(r'<meta[^>]+name=["\']viewport["\'][^>]*>\s*', html)
        if m:
            html = html[:m.end()] + block + html[m.end():]
        else:
            html = re.sub(r"(<head[^>]*>)\s*", lambda mm: mm.group(1) + "\n" + block, html, count=1)
    # insert chrome right after the <body> tag; consume following whitespace so re-runs stay idempotent
    if rel not in SELF_CONTAINED:
        html = re.sub(r"(<body[^>]*>)\s*", lambda m: m.group(1) + "\n" + chrome_block(key) + "\n", html, count=1)
    html = re.sub(r"app\.js\?v=\d+", f"app.js?v={APPJS_VER}", html)

    # app.js is not optional: styles.css ships .reveal{opacity:0} and app.js is what adds
    # .in to make it visible. A page authored without the tag renders BLANK — that is
    # exactly what happened to /exams/ and its three children, which shipped invisible.
    # The bump above only rewrites a tag that already exists, so add one when it does not.
    # Anchor on the LAST </body>, not the first: index.html mentions "</body>" inside an
    # HTML comment, and count=1 from the front would inject the tag into that comment.
    if rel not in SELF_CONTAINED and "app.js" not in html:
        cut = html.rfind("</body>")
        if cut != -1:
            html = (html[:cut].rstrip() +
                    f'\n<script src="/assets/app.js?v={APPJS_VER}"></script>\n' + html[cut:])

    # Only write when this build actually changed the file. Writing unconditionally
    # touched every page's mtime, so rebuild_sitemap() stamped the SAME <lastmod> on
    # all 103 URLs — and Google discounts lastmod that is uniformly the build date.
    # Skipping no-op writes keeps mtime meaning "content last changed".
    if html == original:
        return rel, "unchanged (mtime preserved)"

    open(path, "w", encoding="utf-8").write(html)
    return rel, f"chrome+hreflang{' +breadcrumb' if bc else ''}{' +faq('+str(len(fq['mainEntity']))+')' if fq else ''}"


# ---- per-page lastmod that means "authored content changed" -------------------------------
# File mtime and git commit date both lie on this site: a version bump (app.js?v=) or a
# site-wide chrome change rewrites every page in one commit, and rebuild_sitemap() then
# stamps the build date on all 200 URLs — exactly what happened on 2026-09-06 (commits
# 3ac62cc and 272d15a) and what a third-party audit flagged two days later. Google discounts
# blanket lastmod. So lastmod is now driven by a hash of the page with every injected block
# removed (CRIT, CHROME, GTM, SEO-LD, the app.js tag, the styles.css cache key): the date
# moves only when the AUTHORED html changes. The ledger lives in the repo so every session
# shares one history; CI never runs this script, so it cannot re-stamp.
LASTMOD_LEDGER = os.path.join(SITE, "data", "lastmod.json")
_INJECTED = [(CRIT_START, CRIT_END), (CHROME_START, CHROME_END), (GTM_START, GTM_END), (SEO_START, SEO_END)]

def authored_hash(html):
    for a, b in _INJECTED:
        html = re.sub(re.escape(a) + r".*?" + re.escape(b), "", html, flags=re.S)
    html = re.sub(r'<script src="/assets/app\.js\?v=\d+"></script>\s*', "", html)
    html = re.sub(r'/assets/styles\.css\?v=[0-9a-f]+', "/assets/styles.css", html)
    html = re.sub(r'<html lang="[^"]*">', "<html>", html)
    return hashlib.md5(re.sub(r"\s+", " ", html).strip().encode("utf-8")).hexdigest()

def load_ledger():
    try:
        return json.load(open(LASTMOD_LEDGER, encoding="utf-8"))
    except FileNotFoundError:
        return {}

def ledger_lastmod(ledger, rel, fpath, today):
    """lastmod for rel; the ledger entry moves only when the authored content hash changes."""
    if fpath.endswith(".pdf"):   # binary asset: mtime is the only signal, and it is honest there
        return datetime.date.fromtimestamp(os.path.getmtime(fpath)).isoformat()
    h = authored_hash(open(fpath, encoding="utf-8").read())
    ent = ledger.get(rel)
    if not ent or ent.get("hash") != h:
        ledger[rel] = {"hash": h, "date": today}
    return ledger[rel]["date"]

def rebuild_sitemap():
    sm = os.path.join(SITE, "sitemap.xml")
    xml = open(sm, encoding="utf-8").read()
    def add_lastmod(mobj):
        block = mobj.group(0)
        loc = re.search(r"<loc>([^<]+)</loc>", block).group(1)
        relpath = loc.replace(ORIGIN, "").strip("/")
        # A directory URL maps to its index.html; a file URL (the A4 PDFs) IS the file.
        # Without this the PDF entries lose their <lastmod> on every build, because
        # ".../x.pdf/index.html" never exists.
        if not relpath:
            fpath = os.path.join(SITE, "index.html")
        elif os.path.splitext(relpath)[1]:
            fpath = os.path.join(SITE, relpath)
        else:
            fpath = os.path.join(SITE, relpath + "/index.html")
        block = re.sub(r"<lastmod>[^<]*</lastmod>", "", block)  # drop any existing
        if os.path.exists(fpath):
            d = ledger_lastmod(ledger, relpath or "index", fpath, today)
            block = block.replace("</loc>", f"</loc><lastmod>{d}</lastmod>", 1)
        return block
    ledger = load_ledger(); today = datetime.date.today().isoformat()
    xml = re.sub(r"<url>.*?</url>", add_lastmod, xml, flags=re.S)
    open(sm, "w", encoding="utf-8").write(xml)
    os.makedirs(os.path.dirname(LASTMOD_LEDGER), exist_ok=True)
    json.dump(ledger, open(LASTMOD_LEDGER, "w", encoding="utf-8"), ensure_ascii=False, indent=0, sort_keys=True)
    return sum(1 for _ in re.finditer(r"<lastmod>", xml))

if __name__ == "__main__":
    pages = sorted([os.path.join(d, f) for d, _, fs in os.walk(SITE) for f in fs if f.endswith(".html")])
    css_ver = css_fingerprint()
    crit = critical_css()
    print(f"Processing {len(pages)} pages...  (styles.css v={css_ver}, critical inline {len(crit)}B)")
    for p in pages:
        rel, msg = process_page(p, css_ver, crit)
        print(f"  {rel:<52} {msg}")
    n = rebuild_sitemap()
    print(f"sitemap.xml: {n} <lastmod> dates written")
    print("Done. (app.js bumped to v=%d — make sure app.js guards are in place.)" % APPJS_VER)
    print(f"      critical CSS + deferred GA4 re-baked; styles.css cache key = {css_ver}")

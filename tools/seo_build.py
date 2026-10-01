#!/usr/bin/env python3
"""
American English 埃森美語 — SEO build step.

Bakes into each static page (so non-JS / AI crawlers see them):
  - FAQPage JSON-LD  (from .faq-item)
  - BreadcrumbList JSON-LD  (from .breadcrumb)
  - hreflang alternates (zh-Hant-TW + x-default)
  - the header nav + drawer + progress bar (the chrome app.js used to inject)
  - the site footer (address, phone, map link) on every page that has none of its own
  - a "last updated" line, a share image where the page declares none, and one
    consistent Organization / author / Article graph
Also regenerates sitemap.xml — <lastmod> comes from data/lastmod.json, a ledger keyed on a
hash of each page's AUTHORED html (injected blocks stripped), never from mtime or git date —
and bumps app.js?v=.

Idempotent: re-running replaces the marked blocks instead of duplicating.
app.js is guarded to skip anything already present (see assets/app.js).

Run:  ~/.claude/skills/seo/.venv/bin/python3 seo_build.py
(Lives OUTSIDE site/ so it is never deployed.)
"""
import os, re, json, datetime, hashlib, subprocess, unicodedata
from urllib.parse import urljoin
from bs4 import BeautifulSoup

SITE   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # repo root, wherever the checkout lives
ORIGIN = "https://americanenglish.com.tw"
def _appjs_ver():
    """Content hash of app.js, like styles.css: the cache key changes exactly when the file does."""
    return hashlib.md5(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                         "assets", "app.js"), "rb").read()).hexdigest()[:8]
_APPJS = _appjs_ver()
LINE = "https://lin.ee/W9J8TuQ"
LOGO = "/assets/img/american-english-banqiao-logo.jpg"
# the header/footer show the logo at 38px: a 3 KB WebP there, the 24 KB JPEG stays for schema and sharing
LOGO_SMALL = "/assets/img/american-english-banqiao-logo-96.webp"
NAV  = [("首頁","/"),("課程","/courses/"),("劍橋英檢","/exams/"),("全民英檢","/gept/"),("師資","/certified-american-teacher-banqiao/"),
        ("家長見證","/banqiao-parent-testimonials/"),("部落格","/blog/")]

SEO_START, SEO_END       = "<!-- AE:SEO-LD start -->", "<!-- AE:SEO-LD end -->"
CHROME_START, CHROME_END = "<!-- AE:CHROME start -->", "<!-- AE:CHROME end -->"
CRIT_START, CRIT_END     = "<!-- AE:CRIT start -->", "<!-- AE:CRIT end -->"
GTM_START, GTM_END       = "<!-- AE:GTM start -->", "<!-- AE:GTM end -->"
FOOT_START, FOOT_END     = "<!-- AE:FOOT start -->", "<!-- AE:FOOT end -->"
PMETA_START, PMETA_END   = "<!-- AE:PAGEMETA start -->", "<!-- AE:PAGEMETA end -->"
POP_START, POP_END       = "<!-- AE:POPULAR start -->", "<!-- AE:POPULAR end -->"
NEXT_START, NEXT_END     = "<!-- AE:NEXT start -->", "<!-- AE:NEXT end -->"
# One quiet line under a page's free-PDF box: the reader has just taken something useful, which
# is the moment to say what the school can do next. Tagged cta_position=mid_page in GA4.
NEXT_LINE = (f'{NEXT_START}<p class="ae-cta">下載之後：想知道孩子現在的英文程度？'
             f'<a href="{LINE}" target="_blank" rel="noopener">加 LINE 預約程度評估</a>'
             f'　·　<a href="/free-trial/">試聽怎麼進行</a></p>{NEXT_END}')

# The pages people actually arrive on, one click from the homepage, the blog index and the
# 404 page. The top search page sat four clicks deep and six pages could not be reached from
# the homepage at all (2026-10 audit). Order: reference charts, phrases, exams, practice.
POPULAR = [("KK 音標表", "/kk-phonetic-chart/"), ("自然發音規則總表", "/phonics-rules-chart/"),
           ("教育部 1200 單字表", "/moe-1200-words-guide/"), ("不規則動詞三態表", "/irregular-verbs-list/"),
           ("英文 12 時態總表", "/english-tenses-chart/"), ("英文字母表", "/english-alphabet-guide/"),
           ("月份英文", "/months-english/"), ("星期英文", "/days-of-week-english/"), ("序數英文", "/ordinal-numbers-english/"),
           ("英文名字怎麼取", "/english-names/"), ("生日快樂英文", "/happy-birthday-english/"),
           ("中秋節英文", "/mid-autumn-festival-english/"), ("謝謝英文", "/thank-you-english/"), ("加油英文", "/cheer-up-english/"),
           ("劍橋英檢等級對照", "/cambridge-english-levels/"), ("全民英檢初級攻略", "/gept-elementary-guide/"),
           ("會考英文級距", "/cap-english-guide/"), ("Cool English 怎麼用", "/cool-english-guide/"),
           ("學習扶助是什麼", "/learning-support-guide/"), ("領思 Linguaskill", "/linguaskill-guide/"),
           ("英文聽力怎麼練", "/english-listening-practice/"), ("英文口說怎麼練", "/english-speaking-practice/"),
           ("英文閱讀怎麼練", "/english-reading-practice/"), ("英文寫作怎麼練", "/english-writing-practice/"),
           ("免費 A4 學習單下載", "/download/")]
POPULAR_ON = {"index.html", "blog/index.html", "404.html"}

MAPS      = "https://maps.app.goo.gl/hLChkEqAMKCsMWpm6"
TEACHER   = "/certified-american-teacher-banqiao/"
ORG_ID    = ORIGIN + "/#organization"
PERSON_ID = ORIGIN + "/#christopher"
OG_DEFAULT = "/assets/img/og-default.jpg"
BYLINE_LINK = f'<a class="byl" href="{TEACHER}">Christopher</a>'
ARIA_H2 = ' role="heading" aria-level="2"'
ICON_OLD = '<link rel="icon" href="/assets/img/american-english-banqiao-logo.jpg">'
ICON_NEW = ('<link rel="icon" href="/favicon.ico" sizes="48x48">'
            '<link rel="icon" type="image/png" sizes="192x192" href="/icon-192.png">')
# The Google rating is on screen on these pages only. Google ignores a rating a business
# marks up about itself, and marking it up where the reader cannot see it is against the
# review-snippet guidelines — so the markup stays where the number is visible.
RATING_PAGES = {"index.html", "banqiao-parent-testimonials/index.html"}
# Pages that are not articles: no "last updated" line and no injected Article node.
NOT_ARTICLE = {"index.html", "404.html", "courses/index.html", "free-trial/index.html", "blog/index.html",
               "download/index.html", "chart-license/index.html", "contact/index.html",
               "banqiao-parent-testimonials/index.html", "cambridge-practice-exam-pack/index.html"}

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

def html_escape(t):
    return (t.replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;").replace('"', "&quot;"))

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
        f'<a href="/" class="brand"><img class="brand-logo" src="{LOGO_SMALL}" '
        'alt="American English 埃森美語 logo" width="38" height="38" fetchpriority="high">埃森<b>美語</b></a>'
        f'<nav class="nav-links" aria-label="主選單">{nav_links(active_key, False)}</nav>'
        '<button class="hamburger" id="hamburger" aria-label="開啟選單" aria-expanded="false" '
        'aria-controls="drawer"><span></span><span></span><span></span></button>'
        "</div></header>\n"
        f'<div class="drawer" id="drawer">{nav_links(active_key, True)}</div>\n'
        f"{CHROME_END}\n"
    )

def footer_block():
    """The same footer the homepage carries, baked into the page so a crawler that does
    not run scripts still finds the address, phone and map on every URL."""
    tel = "+886928067772"
    return (
        f"{FOOT_START}\n"
        '<footer class="site-footer"><div class="wrap"><div class="foot-grid"><div>'
        f'<div class="foot-logo"><img class="foot-logo-img" src="{LOGO_SMALL}" alt="American English 埃森美語 logo" '
        'width="34" height="34" loading="lazy" decoding="async">American English 埃森美語</div>'
        '<p class="foot-tag">板橋中正路在地深耕的美籍外師英文補習班。100% 美籍持證教師、每班 12 人小班制。</p>'
        f'<p class="foot-nap">220 新北市板橋區中正路89巷4號1樓　｜　<a href="tel:{tel}">☎ 0928-067-772</a></p></div>'
        '<nav class="foot-links" aria-label="頁尾導覽">'
        '<div class="foot-col"><p class="foot-h">課程</p><a href="/banqiao-english-cram-school/">板橋英文補習班</a>'
        '<a href="/courses/">課程總覽</a><a href="/kids-english-banqiao/">兒童美語</a>'
        '<a href="/junior-high-english-banqiao/">國中英文</a><a href="/free-trial/">預約試聽</a></div>'
        '<div class="foot-col"><p class="foot-h">學習資源</p><a href="/exams/">劍橋英檢</a><a href="/gept/">全民英檢</a>'
        '<a href="/english-pronunciation/">英文發音</a><a href="/download/">免費下載</a>'
        '<a href="/chart-license/">圖表授權</a></div>'
        f'<div class="foot-col"><p class="foot-h">關於</p><a href="{TEACHER}">師資介紹</a>'
        '<a href="/banqiao-parent-testimonials/">家長見證</a><a href="/blog/">部落格</a>'
        '<a href="/contact/">聯絡與交通</a></div>'
        f'<div class="foot-col"><p class="foot-h">聯絡</p><a href="tel:{tel}">電話 0928-067-772</a>'
        f'<a href="{LINE}" target="_blank" rel="noopener">LINE 線上預約</a>'
        f'<a href="{MAPS}" target="_blank" rel="noopener">Google 地圖位置</a></div>'
        '</nav></div>'
        '<div class="foot-bottom"><span>© 2026 American English 埃森美語</span>'
        '<span>私立埃森美語文理短期補習班　｜　新北市政府立案 社補教社字第115026號　｜　統一編號 61476523</span>'
        '<span>220 新北市板橋區中正路89巷4號1樓</span></div>'
        '<div class="foot-pref"><div google-add-preferred-source-btn data-theme="dark" data-lang="zh-TW"></div></div>'
        f"</div></footer>\n{FOOT_END}\n")

def popular_block():
    links = "".join(f'<a href="{h}">{t}</a>' for t, h in POPULAR
                    if os.path.exists(os.path.join(SITE, h.strip("/"), "index.html")))
    return (f"{POP_START}\n"
            '<section class="section bg-soft pop-sec"><div class="wrap">'
            '<div class="center stack"><span class="eyebrow eyebrow-yellow">熱門學習資源</span>'
            '<h2>家長最常查的<em>英文對照表與指南</em></h2></div>'
            f'<nav class="pop-links" aria-label="熱門學習資源">{links}</nav>'
            f"</div></section>\n{POP_END}\n")

def pmeta_block(date):
    y, m, d = date.split("-")
    return (f"{PMETA_START}\n"
            f'<div class="page-meta"><div class="wrap"><span>最後更新：<time datetime="{date}">{y} 年 {int(m)} 月 {int(d)} 日</time></span>'
            f'<span>內容製作：<a href="{TEACHER}">埃森美語 American English</a></span></div></div>\n'
            f"{PMETA_END}\n")

def snippet_width(t):
    """Display width the way a search result measures it: a CJK or full-width character
    takes two units, a Latin one takes one. Counting characters hid every overflow on
    this site — 37 Chinese characters "fit" a 60-character limit and still get cut."""
    return sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in t)

TITLE_MAX, DESC_MIN, DESC_MAX = 60, 100, 160     # width units; title is measured without the brand suffix
BRAND_SUFFIX = "｜埃森美語"
BRAND_RE = re.compile(r"(｜| — )埃森美語$")

# Search-result titles and descriptions live in ONE file, data/snippets.json, keyed by the
# page's folder. Whatever a page or its generator wrote, the build puts these in the head —
# so a snippet is edited in one place and a regenerated page cannot bring the old one back.
SNIPPETS_FILE = os.path.join(SITE, "data", "snippets.json")
_SNIPPETS = None
def apply_snippet(html, rel):
    global _SNIPPETS
    if _SNIPPETS is None:
        try:
            _SNIPPETS = json.load(open(SNIPPETS_FILE, encoding="utf-8"))
        except FileNotFoundError:
            _SNIPPETS = {}
    e = _SNIPPETS.get(os.path.dirname(rel) or os.path.splitext(rel)[0])
    if not e:
        return html
    def meta(html, attr, name, value):
        v = html_escape(value)
        pat = re.compile(r'<meta\s+(?:%s="%s"\s+content="[^"]*"|content="[^"]*"\s+%s="%s")\s*/?>' % (attr, re.escape(name), attr, re.escape(name)))
        return pat.sub(lambda m: f'<meta {attr}="{name}" content="{v}">', html, count=1)
    if e.get("title"):
        t = e["title"]
        html = re.sub(r"<title>.*?</title>", lambda m: "<title>" + t.replace("&", "&amp;").replace("<", "&lt;") + "</title>", html, count=1, flags=re.S)
        short = BRAND_RE.sub("", t)
        html = meta(html, "property", "og:title", short)
        html = meta(html, "name", "twitter:title", short)
    if e.get("description"):
        d = e["description"]
        html = meta(html, "name", "description", d)
        html = meta(html, "property", "og:description", d)
        html = meta(html, "name", "twitter:description", d)
    return html

PUBLISHED_LEDGER = os.path.join(SITE, "data", "published.json")
_PUBLISHED = None
_GIT_ADDS = None
def _git_first_add(rel):
    """Day the file first entered the repo, or None when git cannot say (a shallow CI clone
    reports every file as added in its single commit, so it is not trusted)."""
    global _GIT_ADDS
    if _GIT_ADDS is None:
        _GIT_ADDS = {}
        try:
            shallow = subprocess.run(["git", "-C", SITE, "rev-parse", "--is-shallow-repository"],
                                     capture_output=True, text=True).stdout.strip()
            if shallow == "false":
                out = subprocess.run(["git", "-C", SITE, "log", "--diff-filter=A", "--name-only", "--format=@%as"],
                                     capture_output=True, text=True).stdout
                day = None
                for line in out.splitlines():
                    if line.startswith("@"):
                        day = line[1:]
                    elif line.strip():
                        _GIT_ADDS[line.strip()] = day     # log runs newest first: the last write wins = first add
        except Exception:
            pass
    return _GIT_ADDS.get(rel)

def published_date(rel, today):
    """Publication date of a page. Kept in data/published.json so the weekly CI job and a
    local build always agree; a page seen for the first time is dated from git, else today."""
    global _PUBLISHED
    if _PUBLISHED is None:
        try:
            _PUBLISHED = json.load(open(PUBLISHED_LEDGER, encoding="utf-8"))
        except FileNotFoundError:
            _PUBLISHED = {}
    if rel not in _PUBLISHED:
        _PUBLISHED[rel] = _git_first_add(rel) or today
        os.makedirs(os.path.dirname(PUBLISHED_LEDGER), exist_ok=True)
        json.dump(_PUBLISHED, open(PUBLISHED_LEDGER, "w", encoding="utf-8"), ensure_ascii=False, indent=0, sort_keys=True)
    return _PUBLISHED[rel]

PERSON_REF = {"@type": "Person", "@id": PERSON_ID, "name": "Christopher", "url": ORIGIN + TEACHER}

_FULL_ORG = None
def full_org():
    """The homepage's Organization node is the single source; every other page gets a copy
    without the rating. Before this, four different Organization blocks were in circulation."""
    global _FULL_ORG
    if _FULL_ORG is None:
        src = open(os.path.join(SITE, "index.html"), encoding="utf-8").read()
        for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', strip_block(src, SEO_START, SEO_END), re.S):
            try:
                d = json.loads(m.group(1))
            except ValueError:
                continue
            if isinstance(d, dict) and d.get("@id") == ORG_ID and "geo" in d:
                _FULL_ORG = d
                break
        if _FULL_ORG is None:
            _FULL_ORG = dict(ORG_LD)
    return _FULL_ORG

def org_node(rel, own=None):
    d = json.loads(json.dumps(full_org()))
    d["url"] = ORIGIN + "/"
    if isinstance(d.get("founder"), dict):
        d["founder"] = dict(PERSON_REF)
    if rel not in RATING_PAGES:
        d.pop("aggregateRating", None); d.pop("review", None)
    elif own:                                   # a rating page keeps the reviews it shows
        for k in ("aggregateRating", "review"):
            if k in own: d[k] = own[k]
    return d

ARTICLE_TYPES = {"Article", "BlogPosting", "NewsArticle"}
OWN_TYPES = ARTICLE_TYPES | {"CollectionPage", "Quiz", "WebApplication", "Product", "ItemList", "WebPage", "Course", "LearningResource"}

def _types(node):
    t = node.get("@type")
    return set(t) if isinstance(t, list) else {t}

def normalize_ld(html, rel, canon, headline, desc, image, published, modified):
    """One consistent graph out of the hand-written JSON-LD: the same Organization node on
    every page, one author entity with an @id, Article dates that follow the page, and no
    Article block describing a different URL (nine pages were shipping the BlogPosting of
    the article they had been copied from). Returns (html, types found)."""
    found = set()
    def refs(v):
        """Swap an inline copy of the school ({"@type":"Organization","name":…}) for a reference."""
        ch = False
        if isinstance(v, dict):
            for k, x in list(v.items()):
                if isinstance(x, dict) and "@id" not in x and (_types(x) & {"Organization", "EducationalOrganization"}) \
                   and re.search("埃森|American English", str(x.get("name", ""))):
                    v[k] = {"@id": ORG_ID}; ch = True
                else:
                    ch = refs(x) or ch
        elif isinstance(v, list):
            for x in v:
                ch = refs(x) or ch
        return ch
    def fix(node):
        changed = False
        if not isinstance(node, dict):
            return changed
        ts = _types(node)
        found.update(t for t in ts if t)
        if node.get("@id") == ORG_ID and ts & {"EducationalOrganization", "LocalBusiness", "Organization"}:
            new = org_node(rel, node)
            if new != node:
                node.clear(); node.update(new); changed = True
        elif "Person" in ts and node.get("name") == "Christopher" and "jobTitle" in node:
            for k, v in (("@id", PERSON_ID), ("url", ORIGIN + TEACHER)):
                if node.get(k) != v:
                    node[k] = v; changed = True
            if isinstance(node.get("hasCredential"), str):
                node["hasCredential"] = {"@type": "EducationalOccupationalCredential",
                                         "credentialCategory": node["hasCredential"]}
                changed = True
        elif ts & ARTICLE_TYPES:
            me = node.get("mainEntityOfPage")
            me = me.get("@id") if isinstance(me, dict) else me
            if me != canon:                    # block copied from another page: rewrite it for this one
                node["headline"], node["description"], node["mainEntityOfPage"] = headline[:110], desc, canon
                node["datePublished"] = published
                if image: node["image"] = image
                changed = True
            pub = node.get("datePublished") or published
            mod = max(modified, pub[:10])
            if node.get("dateModified") != mod:
                node["dateModified"] = mod; changed = True
        if node.get("@id") != ORG_ID:
            changed = refs(node) or changed
        # any page-level node written by this school's founder points at the one author entity
        au = node.get("author")
        if isinstance(au, dict) and au.get("name") == "Christopher" and au != PERSON_REF:
            node["author"] = dict(PERSON_REF); changed = True
        # the exam pack is a download: tiers told apart by sku, no shipping block
        if "Product" in ts:
            offers = node.get("offers")
            for of in (offers if isinstance(offers, list) else [offers] if isinstance(offers, dict) else []):
                if "shippingDetails" in of:
                    del of["shippingDetails"]; changed = True
                if "sku" not in of and of.get("price"):
                    of["sku"] = "ae-exam-pack-" + str(of["price"]); changed = True
        return changed
    def sub(m):
        try:
            d = json.loads(m.group(1))
        except ValueError:
            return m.group(0)
        nodes = d.get("@graph", [d]) if isinstance(d, dict) else d
        ch = [fix(n) for n in (nodes if isinstance(nodes, list) else [nodes])]
        return f'<script type="application/ld+json">{jd(d)}</script>' if any(ch) else m.group(0)
    html = re.sub(r'<script type="application/ld\+json">(.*?)</script>', sub, html, flags=re.S)
    return html, found

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
    name = re.sub(r"\s+", " ", h1.get_text(" ", strip=True)) if h1 else (soup.title.get_text(strip=True) if soup.title else "")
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
    html = apply_snippet(html, rel)
    soup = BeautifulSoup(html, "lxml")

    # Attribute order is not guaranteed: anything round-tripped through BeautifulSoup
    # comes back as <link href="..." rel="canonical"/>. Match either order.
    m = (re.search(r'<link[^>]*\brel="canonical"[^>]*\bhref="([^"]+)"', html) or
         re.search(r'<link[^>]*\bhref="([^"]+)"[^>]*\brel="canonical"', html))
    canon = m.group(1) if m else urljoin(ORIGIN, "/" + os.path.dirname(rel) + "/" if os.path.dirname(rel) else ORIGIN + "/")
    key = page_key(canon)

    bc = breadcrumb_ld(soup, canon)
    fq = faq_ld(BeautifulSoup(html, "lxml"))  # fresh soup (faq_ld mutates)

    # The page's declared language must match the hreflang code we emit below. The site
    # shipped lang="zh-Hant" against hreflang="zh-Hant-TW" — valid separately, inconsistent
    # together, and auditors flag the pair as a language mismatch.
    html = re.sub(r'<html lang="zh-Hant">', '<html lang="zh-Hant-TW">', html, count=1)

    # --- rewrite (literal str.replace only — no regex replacement-string escaping) ---
    html = strip_block(html, SEO_START, SEO_END)
    html = strip_block(html, CHROME_START, CHROME_END)
    html = strip_block(html, CRIT_START, CRIT_END)
    html = strip_block(html, GTM_START, GTM_END)
    html = strip_block(html, FOOT_START, FOOT_END)
    html = strip_block(html, PMETA_START, PMETA_END)
    html = strip_block(html, POP_START, POP_END)
    html = re.sub(re.escape(NEXT_START) + r".*?" + re.escape(NEXT_END), "", html, flags=re.S)
    if "</head>" not in html or not re.search(r"<body[^>]*>", html):
        return rel, "SKIP (no head/body)"

    # --- page facts, taken from the authored page (every injected block is stripped now) ---
    today = datetime.date.today().isoformat()
    modified = page_date(rel, html, today)
    published = min(published_date(rel, today), modified)
    title = soup.title.get_text(strip=True) if soup.title else ""
    h1 = soup.select_one("h1")
    headline = re.sub(r"\s+", " ", h1.get_text(" ", strip=True)) if h1 else title.replace(BRAND_SUFFIX, "")
    md = soup.find("meta", attrs={"name": "description"})
    desc = (md.get("content") or "").strip() if md else ""
    own_og = re.search(r'<meta[^>]*property="og:image"[^>]*>', html)
    if own_og:
        mm = re.search(r'content="([^"]+)"', own_og.group(0))
        image = mm.group(1) if mm else ORIGIN + OG_DEFAULT
    else:
        image = urljoin(ORIGIN, share_image(rel, soup))
    article_page = bool(bc) and rel not in NOT_ARTICLE and rel not in SELF_CONTAINED

    html, found = normalize_ld(html, rel, canon, headline, desc, image, published, modified)

    # --- build SEO-LD head block ---
    seo = [SEO_START]
    if rel != "404.html":                      # an error page has no language alternates
        seo += [f'<link rel="alternate" hreflang="zh-Hant-TW" href="{canon}">',
                f'<link rel="alternate" hreflang="x-default" href="{canon}">']
    seo.append('<link rel="apple-touch-icon" href="/apple-touch-icon.png">')
    if not own_og:
        seo.append(f'<meta property="og:image" content="{image}">')
    if 'name="twitter:card"' not in html:
        seo.append('<meta name="twitter:card" content="summary_large_image">')
    if 'name="twitter:image"' not in html:
        seo.append(f'<meta name="twitter:image" content="{image}">')
    if bc: seo.append(f'<script type="application/ld+json">{jd(bc)}</script>')
    if fq: seo.append(f'<script type="application/ld+json">{jd(fq)}</script>')
    # org node for pages that define none of their own
    if '"@id":"' + ORG_ID + '"' not in html.replace('{"@id":"' + ORG_ID + '"}', ""):
        seo.append(f'<script type="application/ld+json">{jd(dict({"@context": "https://schema.org"}, **org_node(rel)))}</script>')
    # an Article node for content pages that carry no page-level type of their own
    if article_page and not (found & OWN_TYPES):
        seo.append('<script type="application/ld+json">' + jd({
            "@context": "https://schema.org", "@type": "Article", "headline": headline[:110],
            "description": desc, "inLanguage": "zh-Hant-TW", "mainEntityOfPage": canon, "image": image,
            "datePublished": published, "dateModified": modified,
            "author": {"@id": ORG_ID}, "publisher": {"@id": ORG_ID}}) + "</script>")
    if rel == TEACHER.strip("/") + "/index.html":
        seo.append('<script type="application/ld+json">' + jd({
            "@context": "https://schema.org", "@type": "ProfilePage", "url": canon,
            "dateModified": modified, "mainEntity": {"@id": PERSON_ID}}) + "</script>")
    if rel == "contact/index.html":
        seo.append('<script type="application/ld+json">' + jd({
            "@context": "https://schema.org", "@type": "ContactPage", "url": canon,
            "name": "聯絡與交通", "mainEntity": {"@id": ORG_ID}}) + "</script>")
    seo.append(SEO_END)
    seo_block = "\n".join(seo) + "\n"

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
    html = re.sub(r"app\.js\?v=[0-9a-f]+", f"app.js?v={_APPJS}", html)

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
                    f'\n<script src="/assets/app.js?v={_APPJS}"></script>\n' + html[cut:])

    mb = html.find('<div class="magnet-box')
    if mb != -1 and rel not in SELF_CONTAINED:
        end = html.find("</div>", mb)
        if end != -1:
            end += len("</div>")
            html = html[:end] + NEXT_LINE + html[end:]
    if rel in POPULAR_ON:
        at = html.rfind('<section class="section bg-blue">') if rel != "404.html" else html.rfind("</main>")
        if at != -1:
            html = html[:at] + popular_block() + html[at:]
    html = html.replace(ICON_OLD, ICON_NEW)
    # byline: the author's name links to the teacher page (it was plain text on ~150 pages)
    if rel != TEACHER.strip("/") + "/index.html":
        html = html.replace("作者：Christopher｜", "作者：" + BYLINE_LINK + "｜")
        html = html.replace("本文由埃森美語創辦人 Christopher 撰寫", "本文由埃森美語創辦人 " + BYLINE_LINK + " 撰寫")
    # heading order: when the first heading after the H1 is an h3/h4 (a signpost card, the
    # task-format box), tell assistive tech it sits at level 2 — the tag and its styling stay
    m1 = re.search(r"</h1>", html)
    if m1:
        mh = re.search(r"<h([2-4])(\s[^>]*)?>", html[m1.end():])
        if mh and mh.group(1) != "2" and "aria-level" not in (mh.group(2) or ""):
            at = m1.end() + mh.start() + len("<h" + mh.group(1))
            html = html[:at] + ARIA_H2 + html[at:]

    # footer and "last updated" line: after </main>, else ahead of the closing scripts
    if rel not in SELF_CONTAINED:
        tail = (pmeta_block(modified) if article_page else "") + \
               ("" if '<footer class="site-footer"' in html else footer_block())
        if tail:
            at = html.find('<footer class="site-footer"')
            if at == -1:
                at = html.rfind("</main>")
                if at != -1:                       # exactly one newline between </main> and the block
                    at += len("</main>")
                    html = html[:at] + "\n" + html[at:].lstrip("\n")
                    at += 1
            if at == -1:
                m2 = re.search(r'<script src="/assets/app\.js', html)
                at = m2.start() if m2 else html.rfind("</body>")
                if at != -1 and "<main" in html:        # <main> opened and never closed
                    html = html[:at] + "</main>\n" + html[at:]
                    at += len("</main>\n")
            if at != -1:
                html = html[:at] + tail + html[at:]

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
_INJECTED = [(CRIT_START, CRIT_END), (CHROME_START, CHROME_END), (GTM_START, GTM_END), (SEO_START, SEO_END),
             (FOOT_START, FOOT_END), (PMETA_START, PMETA_END), (POP_START, POP_END), (NEXT_START, NEXT_END),
             # the pack offer is a sales block repeated on ~100 pages: a price or button
             # change is not a change to the page (it stamped 95 URLs with one date on 09-25)
             ("<!-- AE:PACKOFFER -->", "<!-- /AE:PACKOFFER -->"),
             # "what next" link blocks are navigation the tools add (route_blocks.py, gept_links.py)
             ("<!-- AE:ROUTE -->", "<!-- /AE:ROUTE -->"), ("<!-- AE:GEPTPRX -->", "<!-- /AE:GEPTPRX -->")]

def authored_hash(html):
    """Hash of what the reader gets: the <body>, minus every injected block and minus
    JSON-LD. Head-only edits (a title or description trim) and schema clean-ups no longer
    move <lastmod> or the visible "last updated" date."""
    for a, b in _INJECTED:
        html = re.sub(re.escape(a) + r".*?" + re.escape(b), "", html, flags=re.S)
    m = re.search(r"<body[^>]*>(.*)</body>", html, flags=re.S)
    if m:
        html = m.group(1)
    html = re.sub(r'<script type="application/ld\+json">.*?</script>\s*', "", html, flags=re.S)
    html = re.sub(r'<script src="/assets/app\.js\?v=[0-9a-f]+"></script>\s*', "", html)
    # the byline link and the heading-level hint are added by this build, not by the author
    html = html.replace(BYLINE_LINK, "Christopher").replace(ARIA_H2, "")
    # Tools that round-trip a page through BeautifulSoup (build_word_audio) re-emit every tag
    # with its attributes sorted onto one line. The reader sees nothing new, so hash the
    # parsed form: the hand-formatted and the round-tripped page then agree, and <lastmod>
    # stops moving on serialiser noise (it moved on 15 untouched pages on 2026-09-22).
    html = str(BeautifulSoup(html, "html.parser"))
    return hashlib.md5(re.sub(r"\s+", " ", html).strip().encode("utf-8")).hexdigest()

def load_ledger():
    try:
        return json.load(open(LASTMOD_LEDGER, encoding="utf-8"))
    except FileNotFoundError:
        return {}

def save_ledger(ledger):
    os.makedirs(os.path.dirname(LASTMOD_LEDGER), exist_ok=True)
    json.dump(ledger, open(LASTMOD_LEDGER, "w", encoding="utf-8"), ensure_ascii=False, indent=0, sort_keys=True)

_LEDGER = None
def page_date(rel, html, today):
    """Ledger date for a page given its html (used while the page is being built)."""
    global _LEDGER
    if _LEDGER is None:
        _LEDGER = load_ledger()
    key = os.path.dirname(rel) or os.path.splitext(rel)[0]
    h = authored_hash(html)
    ent = _LEDGER.get(key)
    if not ent or ent.get("hash") != h:
        _LEDGER[key] = {"hash": h, "date": today}
        save_ledger(_LEDGER)
    return _LEDGER[key]["date"]

def share_image(rel, soup):
    """Share image for a page that declares none: its chart, else its first content
    picture, else the brand card."""
    rec = [r for r in chart_manifest().values() if r.get("page") == os.path.dirname(rel)]
    if rec:
        return rec[0]["png"]
    main = soup.find("main") or soup
    for im in main.find_all("img"):
        src = im.get("src") or ""
        if src.startswith(("/assets/img/blog/", "/assets/img/charts/")) or \
           (src.startswith("/assets/img/") and str(im.get("width") or "0").isdigit() and int(im.get("width") or 0) >= 600):
            return src
    return OG_DEFAULT

def ledger_lastmod(ledger, rel, fpath, today, prior=None):
    """lastmod for rel; the ledger entry moves only when the authored content hash changes."""
    if fpath.endswith(".pdf"):   # binary asset: dated by its bytes, so a re-deploy does not move it
        h = hashlib.md5(open(fpath, "rb").read()).hexdigest()
        ent = ledger.get(rel)
        if not ent:
            ledger[rel] = {"hash": h, "date": prior or datetime.date.fromtimestamp(os.path.getmtime(fpath)).isoformat()}
        elif ent.get("hash") != h:
            ledger[rel] = {"hash": h, "date": today}
        return ledger[rel]["date"]
    h = authored_hash(open(fpath, encoding="utf-8").read())
    ent = ledger.get(rel)
    if not ent or ent.get("hash") != h:
        ledger[rel] = {"hash": h, "date": today}
    return ledger[rel]["date"]

def chart_manifest():
    """slug -> chart record, written by tools/build_chart_images.py."""
    mf = os.path.join(SITE, "assets/img/charts/manifest.json")
    if not os.path.exists(mf):
        return {}
    try:
        return json.load(open(mf, encoding="utf-8"))
    except Exception:
        return {}

def rebuild_sitemap():
    sm = os.path.join(SITE, "sitemap.xml")
    xml = open(sm, encoding="utf-8").read()
    # Image entries: Google will not reliably discover a chart that is only an <img>
    # on the page. Keyed by page so a page can carry more than one chart.
    charts = {}
    for rec in chart_manifest().values():
        charts.setdefault(rec["page"], []).append(rec)
    if charts and "xmlns:image" not in xml:
        xml = xml.replace(
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
            '        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">')
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
        block = re.sub(r"<image:image>.*?</image:image>", "", block, flags=re.S)
        # Google reads only <image:loc> (title/caption were dropped in 2022) and ignores
        # <priority>/<changefreq> altogether
        block = re.sub(r"<(priority|changefreq)>[^<]*</\1>", "", block)
        for rec in charts.get(relpath.strip("/"), []):
            block = block.replace("</url>",
                "<image:image><image:loc>%s%s</image:loc></image:image></url>" % (ORIGIN, rec["png"]), 1)
        pm = re.search(r"<lastmod>([^<]*)</lastmod>", block)
        block = re.sub(r"<lastmod>[^<]*</lastmod>", "", block)  # drop any existing
        if os.path.exists(fpath):
            d = ledger_lastmod(ledger, relpath or "index", fpath, today, pm.group(1) if pm else None)
            block = block.replace("</loc>", f"</loc><lastmod>{d}</lastmod>", 1)
        return block
    global _LEDGER
    ledger = _LEDGER if _LEDGER is not None else load_ledger(); today = datetime.date.today().isoformat()
    # every A4 download a page links to belongs in the sitemap (10 of 23 were missing)
    linked = set()
    for d, _, fs in os.walk(SITE):
        if "index.html" in fs and ".git" not in d:
            linked.update(re.findall(r'href="(/assets/downloads/[^"#?]+\.pdf)"', open(os.path.join(d, "index.html"), encoding="utf-8").read()))
    for href in sorted(linked):
        if os.path.exists(os.path.join(SITE, href.lstrip("/"))) and f"<loc>{ORIGIN}{href}</loc>" not in xml:
            xml = xml.replace("</urlset>", f"  <url><loc>{ORIGIN}{href}</loc></url>\n</urlset>")
    xml = re.sub(r"<url>.*?</url>", add_lastmod, xml, flags=re.S)
    open(sm, "w", encoding="utf-8").write(xml)
    save_ledger(ledger); _LEDGER = ledger
    return sum(1 for _ in re.finditer(r"<lastmod>", xml))

def lint_snippets(pages):
    """Titles and descriptions that a search result will cut off, measured by width."""
    long_t, long_d, short_d = [], [], []
    for p in pages:
        rel = os.path.relpath(p, SITE)
        if rel in SELF_CONTAINED or rel == "404.html":
            continue
        sp = BeautifulSoup(open(p, encoding="utf-8").read(), "html.parser")
        t = sp.title.get_text(strip=True) if sp.title else ""
        md = sp.find("meta", attrs={"name": "description"})
        d = (md.get("content") or "").strip() if md else ""
        tw, dw = snippet_width(BRAND_RE.sub("", t)), snippet_width(d)
        if tw > TITLE_MAX: long_t.append((tw, rel))
        if dw > DESC_MAX: long_d.append((dw, rel))
        elif dw < DESC_MIN: short_d.append((dw, rel))
    print(f"snippet lint: {len(long_t)} titles > {TITLE_MAX} units · {len(long_d)} descriptions > {DESC_MAX} · "
          f"{len(short_d)} descriptions < {DESC_MIN}")
    for label, rows in (("title too wide", long_t), ("description too wide", long_d), ("description too short", short_d)):
        for w, rel in sorted(rows, reverse=True)[:12]:
            print(f"  {label:<22} {w:>4}  {rel}")

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
    lint_snippets(pages)
    print("Done. (app.js cache key = %s)" % _APPJS)
    print(f"      critical CSS + deferred GA4 re-baked; styles.css cache key = {css_ver}")

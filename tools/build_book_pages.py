#!/usr/bin/env python3
"""The school's two book pages, generated from data (2026-11-08, Chris: "a new tab at the top for the
story book collection … the books link present on the 1200 words pages … the grammar stuff can be part
of something else"). Run tools/seo_build.py afterwards (chrome, SEO blocks, sitemap date).

Writes
  chris-and-cora-readers/index.html          the 分級讀本 tab: 36 Chris and Cora readers
  chris-and-cora-readers/read/1a/            the free Level 1a flip book (self-contained, noindex)
  english-grammar-books/index.html           the grammar books + cheat sheets (linked from the grammar pages)
  assets/downloads/ae-grammar-*-page1-free.pdf   page 1 of every cheat sheet, free
  ~/Downloads/GLOSS-2026-11-08-BOOK-PAGES.md every Chinese line on both pages with its English (Chris reads English)

Data
  data/readers.json        titles, words per book, MOE words read by level, questions (from the ae-readers repo)
  data/grammar_books.json  units and points of the 16 grammar books (from the grammar series engine)
  data/books_store.json    Lemon Squeezy checkout link per VARIANT (each variant has its own checkout/buy/<uuid>;
                           a product's Share link opens on its FIRST variant). Empty = the button says 即將開放.

Facts on the pages come from those files; nothing here is typed from memory.
"""
import html, json, os, re, shutil

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIGIN = "https://americanenglish.com.tw"
LINE = "https://lin.ee/W9J8TuQ"
FLIP_SRC = os.path.expanduser("~/Downloads/AE-readers-out/flip")
FREE_PDF_SRC = os.path.expanduser("~/Downloads/AE-GRAMMAR-SERIES-2026-10-31/workbook/free")
GLOSS_OUT = os.path.expanduser("~/Downloads/GLOSS-2026-11-08-BOOK-PAGES.md")
READERS, GRAMMAR = "chris-and-cora-readers", "english-grammar-books"

R = json.load(open(os.path.join(SITE, "data", "readers.json"), encoding="utf-8"))
G = json.load(open(os.path.join(SITE, "data", "grammar_books.json"), encoding="utf-8"))
STORE_PATH = os.path.join(SITE, "data", "books_store.json")
STORE_DEFAULT = {
    "_note": "One Lemon Squeezy checkout link per variant (checkout/buy/<uuid> from the variant's own share link). Empty = 即將開放.",
    "readers_sets": {"1-4": "", "5-8": "", "9-12": "", "all": ""},
    "readers_levels": {str(n): "" for n in range(1, 13)},
    "grammar": {"elementary-books": "", "elementary-sheets": "", "junior-books": "", "junior-sheets": "",
                "senior-books": "", "senior-sheets": ""},
}
if not os.path.exists(STORE_PATH):
    json.dump(STORE_DEFAULT, open(STORE_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
STORE = json.load(open(STORE_PATH, encoding="utf-8"))

# prices: Chris 2026-11-05 (memory ae-readers-flashcards-plan); file sizes: ~/Downloads/AE-lemon-upload
P_LEVEL, P_SET, P_ALL = 390, 1390, 2690
P_GBOOKS, P_GSHEETS = 590, 190
MB_LEVEL = "23–36 MB"
MB_SET = {"1-4": 108, "5-8": 134, "9-12": 133, "all": 375}
MB_GRAMMAR = {"elementary": (28, 12), "junior": (36, 11), "senior": (35, 13)}

esc = html.escape
FP, LZ = 'fetchpriority="high"', 'loading="lazy"'   # the hero's middle cover loads first
GLOSS = {READERS: [], GRAMMAR: []}
_page = [READERS]

def Z(zh, en):
    """A Chinese string on the page, recorded with its English for Chris's gloss."""
    GLOSS[_page[0]].append((zh, en))
    return zh

def strip(t):
    return re.sub(r"<[^>]+>", "", t)

def n(x):
    return f"{x:,}"

# ---------------------------------------------------------------- shared pieces

LEMON = """<link rel="preconnect" href="https://americanenglish.lemonsqueezy.com">
<script src="https://app.lemonsqueezy.com/js/lemon.js" defer></script>
<script>(function(){
var L=null,T=null;
function hide(){if(L){L.remove();L=null;}if(T){clearTimeout(T);T=null;}}
function show(){hide();L=document.createElement("div");L.setAttribute("role","status");
  L.style.cssText="position:fixed;inset:0;z-index:2147483646;display:flex;align-items:center;justify-content:center;background:rgba(26,39,82,.35)";
  L.innerHTML='<div style="background:#fff;border-radius:999px;padding:14px 22px;font-weight:700;color:#1A2752;box-shadow:0 8px 30px rgba(0,0,0,.18);display:flex;align-items:center;gap:10px"><span style="width:18px;height:18px;border:3px solid #DDF4FF;border-top-color:#1CB0F6;border-radius:50%;display:inline-block;animation:aeSpin .8s linear infinite"></span>付款視窗開啟中，請稍候…</div><style>@keyframes aeSpin{to{transform:rotate(360deg)}}</style>';
  document.body.appendChild(L);T=setTimeout(hide,20000);}
document.addEventListener("click",function(e){var a=e.target&&e.target.closest&&e.target.closest("a.lemonsqueezy-button");if(a)show();},true);
function watch(){new MutationObserver(function(ms){ms.forEach(function(m){
  m.addedNodes.forEach(function(nd){if(nd.tagName==="IFRAME"&&/lemonsqueezy/.test(nd.src||"")){nd.addEventListener("load",function(){setTimeout(hide,600);});}});
  m.removedNodes.forEach(function(nd){if(nd.tagName==="IFRAME"&&/lemonsqueezy/.test(nd.src||""))hide();});
});}).observe(document.body,{childList:true});}
if(document.body)watch();else document.addEventListener("DOMContentLoaded",watch);
})();</script>
<script>(function(){var n=0,t=setInterval(function(){
  if(window.LemonSqueezy&&window.LemonSqueezy.Setup){clearInterval(t);window.LemonSqueezy.Setup({eventHandler:h});}
  else if(++n>100){clearInterval(t);}
},100);
function h(ev){
  if(!ev||ev.event!=="Checkout.Success")return;
  var d=(ev.data&&ev.data.attributes)||{},
      val=typeof d.total==="number"?d.total/100:0,
      cur=d.currency||"TWD",
      tid=String((ev.data&&ev.data.id)||d.identifier||""),
      nm=(d.first_order_item&&d.first_order_item.variant_name)||d.product_name||"books";
  try{if(window.fbq)fbq("track","Purchase",{value:val,currency:cur,content_category:"books",content_name:nm},tid?{eventID:"ls-"+tid}:undefined);}catch(e){}
}})();</script>"""

CSS = """
.bp-hero{display:grid;grid-template-columns:1.15fr .85fr;gap:28px;align-items:center}
@media (max-width:860px){.bp-hero{grid-template-columns:1fr}}
.bp-fan{position:relative;height:300px;max-width:420px;margin:0 auto;width:100%}
.bp-fan img{position:absolute;top:30px;width:150px;height:auto;border-radius:10px;border:3px solid #fff;box-shadow:0 14px 30px rgba(26,39,82,.22)}
.bp-fan img:nth-child(1){left:0;transform:rotate(-10deg)}
.bp-fan img:nth-child(2){left:22%;top:12px;transform:rotate(-4deg);z-index:1}
.bp-fan img:nth-child(3){left:44%;top:0;z-index:2}
.bp-fan img:nth-child(4){left:62%;top:14px;transform:rotate(5deg);z-index:1}
.bp-fan img:nth-child(5){right:0;top:34px;transform:rotate(10deg)}
@media (max-width:560px){.bp-fan{height:220px}.bp-fan img{width:108px}}
.bp-cta{display:flex;flex-wrap:wrap;gap:10px;margin-top:22px;justify-content:center}
@media (min-width:861px){.bp-hero>div:first-child{text-align:left}.bp-hero .divider{margin-left:0;margin-right:0}.bp-hero .bp-cta,.bp-hero .bp-facts{justify-content:flex-start}}
.bp-cta .btn{margin-top:0}
.bp-facts{display:flex;flex-wrap:wrap;gap:8px;margin-top:18px;justify-content:center}
.bp-facts span{background:#fff;border-radius:999px;padding:6px 13px;font-size:13px;font-weight:700;color:var(--navy);box-shadow:0 3px 10px rgba(26,39,82,.08)}
.bp-scroll{display:flex;gap:16px;overflow-x:auto;scroll-snap-type:x mandatory;padding:6px 2px 16px;margin-top:22px;-webkit-overflow-scrolling:touch}
.bp-scroll figure{flex:0 0 min(78vw,560px);scroll-snap-align:start;margin:0;background:#fff;border-radius:16px;box-shadow:0 6px 22px rgba(26,39,82,.10);overflow:hidden}
.bp-scroll.tall figure{flex-basis:min(62vw,300px)}
.bp-scroll img{display:block;width:100%;height:auto;border-bottom:1px solid rgba(26,39,82,.08)}
.bp-scroll figcaption{padding:12px 16px;font-size:14px;line-height:1.65;color:var(--text-body)}
.bp-scroll figcaption b{display:block;color:var(--navy);font-size:15px}
.bp-hint{font-size:13px;color:#64748b;text-align:center;margin-top:2px}
.bp-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:14px;margin-top:24px}
.bp-card{background:#fff;border:2px solid rgba(26,39,82,.08);border-radius:18px;padding:20px 22px;box-shadow:0 4px 0 rgba(26,39,82,.05)}
.bp-card b{display:block;font-family:'Baloo 2',sans-serif;font-size:17px;color:var(--navy);margin-bottom:6px}
.bp-card p{margin:0;font-size:14.5px;line-height:1.8;color:var(--text-body)}
.bp-card .bp-num{font-family:'Baloo 2',sans-serif;font-weight:800;font-size:30px;color:var(--blue);line-height:1;display:block;margin-bottom:8px}
.bp-stage{display:flex;flex-direction:column}
.bp-stage .bp-tag{align-self:flex-start;font-size:12.5px;font-weight:800;border-radius:999px;padding:3px 11px;margin-bottom:10px;background:#E8F7FF;color:#066d9e}
.bp-stage blockquote{margin:12px 0;padding:12px 14px;border-left:4px solid var(--yellow);background:#FFFBEF;border-radius:0 12px 12px 0;font-family:'Andika','Baloo 2',sans-serif;font-size:16px;line-height:1.6;color:var(--navy)}
.bp-stage .bp-small{font-size:13px;color:#64748b;margin-top:auto;padding-top:10px}
.bp-lv{background:#fff;border:2px solid rgba(26,39,82,.08);border-radius:16px;margin-top:10px;overflow:hidden}
.bp-lv summary{list-style:none;cursor:pointer;display:grid;grid-template-columns:70px 132px 1fr auto;gap:14px;align-items:center;padding:12px 16px}
.bp-lv summary::-webkit-details-marker{display:none}
.bp-lv .bp-l{font-family:'Baloo 2',sans-serif;font-weight:800;font-size:15px;color:var(--navy);line-height:1.2}
.bp-lv .bp-l small{display:block;font-weight:700;font-size:12px;color:#64748b}
.bp-lv .bp-cov{display:flex}
.bp-lv .bp-cov img{width:42px;height:auto;border-radius:4px;border:2px solid #fff;box-shadow:0 3px 8px rgba(26,39,82,.16);margin-left:-8px}
.bp-lv .bp-cov img:first-child{margin-left:0}
.bp-lv .bp-t{font-size:14px;line-height:1.55;color:var(--text-body)}
.bp-lv .bp-t i{font-style:normal;color:var(--navy);font-weight:700}
.bp-lv .bp-w{font-size:13px;color:#64748b;text-align:right;white-space:nowrap}
.bp-lv .bp-w b{display:block;font-size:15px;color:var(--navy)}
.bp-lv[open] summary{border-bottom:1px solid rgba(26,39,82,.08)}
.bp-lv .bp-in{padding:16px;display:grid;grid-template-columns:1.2fr 1fr;gap:18px;align-items:start}
.bp-lv .bp-in img{width:100%;height:auto;border-radius:10px;box-shadow:0 4px 14px rgba(26,39,82,.12)}
.bp-lv .bp-in h4{margin:0 0 6px;font-size:14.5px;color:var(--navy)}
.bp-lv .bp-in ul{margin:0 0 12px;padding-left:18px;font-size:13.5px;line-height:1.7;color:var(--text-body)}
.bp-lv .bp-in .btn{margin-top:4px}
@media (max-width:720px){.bp-lv summary{grid-template-columns:56px 1fr auto;gap:10px}.bp-lv .bp-cov{display:none}.bp-lv .bp-in{grid-template-columns:1fr}}
.bp-tiers{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin:22px auto 0;max-width:1040px}
@media (max-width:820px){.bp-tiers{grid-template-columns:1fr}}
.bp-tier{background:linear-gradient(135deg,#FFFBEF,#FFF4D6);border:1.5px solid var(--yellow);border-radius:18px;padding:18px;display:flex;flex-direction:column;gap:8px}
.bp-tier.hl{border-width:3px;box-shadow:0 10px 30px rgba(255,200,40,.28)}
.bp-tier .bp-tn{font-family:'Baloo 2',sans-serif;font-weight:800;font-size:15px;color:var(--navy)}
.bp-tier .bp-tp{font-family:'Baloo 2',sans-serif;font-weight:800;font-size:30px;color:var(--navy);line-height:1}
.bp-tier .bp-tu{font-size:12.5px;font-weight:700;color:#8a5f00}
.bp-tier .bp-td{font-size:13.5px;line-height:1.7;color:var(--text-body)}
.bp-tier .bp-pick{display:grid;grid-template-columns:repeat(4,1fr);gap:6px;margin-top:4px}
.bp-tier .bp-pick.two{grid-template-columns:1fr}
.bp-tier .btn{margin-top:0;min-height:44px;padding:8px 6px;font-size:14px;width:100%;text-align:center;justify-content:center}
.bp-soon{opacity:.5;cursor:not-allowed;box-shadow:none!important}
.bp-soon-note{text-align:center;margin:16px auto 0;max-width:640px;background:#FFF1F0;border:1.5px solid #FFC9C4;color:#9B2C22;border-radius:12px;padding:10px 14px;font-size:14px;font-weight:700}
.bp-trust{display:flex;flex-wrap:wrap;justify-content:center;gap:7px;margin:18px auto 0;max-width:900px}
.bp-trust span{display:inline-flex;align-items:center;gap:5px;background:#fff;border-radius:100px;padding:6px 12px;font-size:12.5px;font-weight:700;color:var(--navy);box-shadow:0 3px 10px rgba(26,39,82,.10)}
.bp-trust span::before{content:'✓';color:#12873d;font-weight:900}
.bp-fine{max-width:760px;margin:16px auto 0;font-size:13px;line-height:1.8;color:#64748b;text-align:center}
.bp-steps{counter-reset:s;list-style:none;padding:0;margin:22px auto 0;max-width:720px}
.bp-steps li{counter-increment:s;position:relative;padding:0 0 16px 46px;font-size:15.5px;line-height:1.8;color:var(--text-body)}
.bp-steps li::before{content:counter(s);position:absolute;left:0;top:1px;width:30px;height:30px;border-radius:10px;background:var(--blue);color:#fff;font-family:'Baloo 2',sans-serif;font-weight:800;font-size:14px;display:grid;place-items:center}
.bp-steps b{color:var(--navy)}
.bp-free{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:8px;margin-top:12px}
.bp-free a{display:flex;align-items:center;gap:8px;background:#fff;border:2px solid rgba(26,39,82,.08);border-radius:12px;padding:9px 12px;font-size:14px;font-weight:700;color:var(--navy);text-decoration:none}
.bp-free a::before{content:'PDF';font-size:10.5px;font-weight:800;color:#fff;background:#E5484D;border-radius:5px;padding:2px 5px}
.bp-free a:hover{border-color:var(--light-blue)}
.bp-book{background:#fff;border:2px solid rgba(26,39,82,.08);border-radius:14px;margin-top:8px}
.bp-book summary{cursor:pointer;padding:11px 14px;font-weight:800;color:var(--navy);font-size:15px}
.bp-book summary small{font-weight:700;color:#64748b;font-size:12.5px;margin-left:6px}
.bp-book ol{margin:0;padding:0 16px 14px 36px;font-size:14px;line-height:1.75;color:var(--text-body)}
.bp-book ol li span{color:#64748b;font-size:12.5px}
.bp-gcovers{display:flex;gap:5px;margin:4px 0 12px}
.bp-gcovers img{width:calc((100% - 25px)/6);max-width:64px;min-width:0;height:auto;border-radius:4px;box-shadow:0 3px 8px rgba(26,39,82,.15)}
"""

def head(slug, title, desc, og_title, og_desc, og_img, og_w, og_h, og_alt, ld, lemon):
    ldtags = "".join('<script type="application/ld+json">' + json.dumps(x, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
                     + "</script>\n" for x in ld)
    return f"""<!DOCTYPE html>
<html lang="zh-Hant-TW">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="theme-color" content="#1A2752">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{ORIGIN}/{slug}/">
<meta property="og:type" content="website">
<meta property="og:locale" content="zh_TW">
<meta property="og:site_name" content="American English 埃森美語">
<meta property="og:title" content="{esc(og_title)}">
<meta property="og:description" content="{esc(og_desc)}">
<meta property="og:url" content="{ORIGIN}/{slug}/">
<meta property="og:image" content="{ORIGIN}{og_img}">
<meta property="og:image:width" content="{og_w}">
<meta property="og:image:height" content="{og_h}">
<meta property="og:image:alt" content="{esc(og_alt)}">
<meta name="twitter:card" content="summary_large_image">
{lemon}
{ldtags}<style>{CSS}</style>
</head>
<body>
<main id="top">
"""

FOOT = """
</main>
<script src="/assets/app.js"></script>
</body>
</html>
"""

def buy(url, label, kind, item, price, cls="btn btn-yellow"):
    """A checkout button, or a greyed 即將開放 when Chris has not sent that variant's link yet."""
    if not url:   # the label stays, greyed out; one 即將開放 note sits above the price cards (SOON)
        return f'<span class="btn btn-outline bp-soon" aria-disabled="true">{esc(label)}</span>'
    sep = "&" if "?" in url else "?"
    return (f'<a class="{cls} lemonsqueezy-button" href="{esc(url)}{sep}checkout[billing_address][country]=TW" '
            f'data-book="{kind}" data-book-item="{esc(item)}" data-book-price="{price}">{esc(label)}</a>')

def wrange(ws):
    return n(min(ws)) if min(ws) == max(ws) else f"{n(min(ws))}–{n(max(ws))}"

def soon(live):
    """While no checkout link is set, one line says buying online opens soon (the buttons are greyed)."""
    if live:
        return ""
    zh = Z("線上購買即將開放。現在可以先免費試讀，有問題直接 <a href='" + LINE + "' target='_blank' rel='noopener'>LINE 問我們</a>。",
           "Buying online opens soon. Meanwhile, try the free sample; questions go to LINE.")
    return '<p class="bp-soon-note reveal">' + zh + '</p>'

def faq(items):
    out = []
    for q, a in items:
        qid = re.sub(r"[^\w\u4e00-\u9fff]+", "", strip(q))
        out.append(f'<div class="faq-item"><h3 id="{qid}" class="faq-h"><button class="faq-q" aria-expanded="false">{q}'
                   f'<span class="pm"></span></button></h3><div class="faq-a"><p>{a}</p></div></div>')
    return '<div class="faq reveal" style="margin-top:22px;max-width:820px;margin-left:auto;margin-right:auto">' + "".join(out) + "</div>"

def h2(eyebrow, hid, text, color=""):
    return (f'<div class="center stack reveal"><span class="eyebrow{(" eyebrow-" + color) if color else ""}">{eyebrow}</span>'
            f'<h2 id="{hid}">{text}</h2></div>')

# ---------------------------------------------------------------- readers page

def readers_page():
    _page[0] = READERS
    books = {b["code"]: b for b in R["books"]}
    cum = R["moe_words_by_level"]
    lv_new = [cum[0]] + [cum[i] - cum[i - 1] for i in range(1, 12)]
    words = lambda L: [books[f"{L}{x}"]["words"] for x in "abc"]
    any_link = any(STORE["readers_sets"].values()) or any(STORE["readers_levels"].values())
    title = Z("Chris and Cora 英語分級讀本：12 級 36 本，第一本免費讀｜埃森美語",
              "Chris and Cora English graded readers: 12 levels, 36 books, the first book free | American English")
    desc = Z(f"埃森美語自己寫的英語分級讀本：12 級 36 本，每本 48 頁，左頁文字、右頁整頁插圖，故事在台灣。"
             f"用到教育部 1,200 字表的 {n(cum[-1])} 個字，第一本免費線上讀。",
             f"Graded readers written by American English: 12 levels, 36 books, 48 pages each, words on the left page and a full-page "
             f"picture on the right, stories set in Taiwan. They use {n(cum[-1])} of the words on the MOE 1,200 list; the first book is free to read online.")
    og_t = Z("Chris and Cora 英語分級讀本：12 級 36 本，第一本免費讀", "Chris and Cora graded readers: 12 levels, 36 books, the first one free")
    ld = [{"@context": "https://schema.org", "@type": "Product", "name": "Chris and Cora 英語分級讀本（12 級 36 冊）",
           "description": strip(desc), "brand": {"@type": "Brand", "name": "埃森美語 American English"},
           "image": [f"{ORIGIN}/assets/img/readers/covers/{c}.webp" for c in ("1a", "6a", "12a")],
           **({"offers": {"@type": "AggregateOffer", "priceCurrency": "TWD", "lowPrice": P_LEVEL, "highPrice": P_ALL,
                          "offerCount": 16, "availability": "https://schema.org/InStock"}} if any_link else {})}]
    out = [head(READERS, title, desc, og_t, desc, "/assets/img/readers/og-all-36.jpg", 1600, 1200,
                Z("Chris and Cora 英語分級讀本 36 本封面", "the 36 Chris and Cora covers"), ld, LEMON if any_link else "")]

    # hero
    fan = "".join(f'<img src="/assets/img/readers/covers/{c}.webp" alt="{esc(books[c]["title"])} 封面" width="320" height="454" '
                  f'{FP if i == 2 else LZ} decoding="async">'
                  for i, c in enumerate(("1a", "3a", "6a", "9b", "12a")))
    out.append(f"""<section class="page-hero">
  <div class="wrap">
    <div class="breadcrumb reveal"><a href="/">首頁</a> ／ {Z("分級讀本", "graded readers")}</div>
    <div class="bp-hero">
      <div>
        <span class="eyebrow eyebrow-yellow reveal">{Z("埃森美語原創 · 12 級 36 本", "our own series · 12 levels, 36 books")}</span>
        <h1 class="reveal d1"><span style="white-space:nowrap">Chris and Cora</span> {Z("<em>英語分級讀本</em>", "English graded readers")}</h1>
        <div class="divider reveal d1"></div>
        <p class="body reveal d2">{Z(f"這套書是我們自己寫、自己編的：12 級、每級 3 本，共 36 本，每本 48 頁。左頁是英文，右頁是整頁插圖，故事發生在台灣的家、學校、公園和夜市。"
            f"第 1 級的 3 本只用 {cum[0]} 個教育部單字；讀完第 12 級，孩子已經在故事裡讀過教育部 1,200 字表裡的 <b>{n(cum[-1])} 個字</b>。",
            f"We wrote and laid out this series ourselves: 12 levels, 3 books each, 36 books of 48 pages. English on the left page, a full-page "
            f"picture on the right; the stories happen at home, at school, in the park and at the night market in Taiwan. The 3 books of Level 1 use only "
            f"{cum[0]} MOE words; by the end of Level 12 a child has read {n(cum[-1])} of the words on the MOE 1,200 list in the stories.")}</p>
        <div class="bp-cta reveal d2"><a class="btn btn-primary" href="/{READERS}/read/1a/" data-book="readers" data-book-item="free">{Z("免費讀第一本", "read the first book free")}</a>
          <a class="btn btn-outline" href="#buy">{Z("看價格", "see prices")}</a></div>
        <div class="bp-facts reveal d2"><span>{Z("PDF＋翻頁電子書", "PDF + flip book")}</span><span>{Z("每本 48 頁", "48 pages a book")}</span><span>{Z("台灣場景", "set in Taiwan")}</span><span>{Z("教育部 1,200 字", "MOE 1,200 words")}</span></div>
      </div>
      <div class="bp-fan reveal d1" aria-hidden="true">{fan}</div>
    </div>
  </div>
</section>
""")

    # what a book looks like
    spreads = [("1a-p12", "1a", Z("第 1 級：一頁一句", "Level 1: one sentence a page")),
               ("4b-p16", "4b", Z("第 4 級：一頁兩三句", "Level 4: two or three sentences a page")),
               ("8a-p20", "8a", Z("第 8 級：一頁一小段，有對話", "Level 8: a short paragraph a page, with dialogue")),
               ("12c-p24", "12c", Z("第 12 級：整段故事", "Level 12: full paragraphs"))]
    figs = "".join(f'<figure><img src="/assets/img/readers/spreads/{f}.webp" alt="{esc(books[c]["title"])} 內頁：左頁文字、右頁插圖" '
                   f'width="1200" height="851" loading="lazy" decoding="async"><figcaption><b>{cap}</b>{esc(books[c]["title"])}'
                   f'{Z("，全書", ", whole book ")} {n(books[c]["words"])} {Z("字", "words")}</figcaption></figure>' for f, c, cap in spreads)
    inside = [(Z("新字頁", "new-words page"), Z("書前一頁列出這一級的新字和圖畫字，先看一遍再讀故事。", "a page at the front lists the level's new words and picture words; look at it before the story.")),
              (Z("每頁標出新字", "new words marked on each page"), Z("新字第一次出現的那一頁，頁底會標出來。", "the page where a new word first appears names it at the bottom.")),
              (Z("讀完問問看", "questions after reading"), Z("書後有幾個關於故事的問題，用來聊，不是考試。", "questions about the story at the back, for talking, not testing.")),
              (Z("字彙總覽＋學過的字", "word summary + words we know"), Z("每個字第一次出現在第幾頁，還有到這本為止學過的字。", "the page each word first appears on, and every word learned so far.")),
              (Z("閱讀紀錄", "reading log"), Z("讀一次寫一次日期，同一本讀到順。", "write a date each time it is read; read the same book until it is smooth."))]
    cards = "".join(f'<div class="bp-card"><b>{t}</b><p>{d}</p></div>' for t, d in inside)
    out.append(f"""<section class="section">
  <div class="wrap">
    {h2(Z("內頁", "inside"), "一本書長什麼樣", Z("一本書，<em>長什麼樣</em>", "what a book looks like"))}
    <p class="body center" style="max-width:62ch;margin:14px auto 0">{Z("下面是實際的內頁，直接從書裡截下來。左右滑動看第 1、4、8、12 級：字一級一級變多，版面不變。", "These are real pages taken straight from the books. Swipe to see Levels 1, 4, 8 and 12: more words each level, same layout.")}</p>
    <div class="bp-scroll reveal">{figs}</div>
    <p class="bp-hint">{Z("← 左右滑動 →", "← swipe →")}</p>
    <div class="bp-grid reveal">{cards}</div>
  </div>
</section>
""")

    # stages (= the three 4-level sets)
    st = [("1-4", Z("剛開始讀", "just starting to read"), 1, 4, Z("This is Bobo. Look at Bobo!", "(sample from Book 1a)"),
           Z("認得字母、學過一點自然發音就可以開始。一頁一兩句，大人陪著讀。", "Start once the child knows the letters and some phonics. One or two sentences a page, read with an adult.")),
          ("5-8", Z("讀得出短句", "can read short sentences"), 5, 8, Z('They all walk to the market together. "I know the market," says Amy.', "(sample from Book 5a)"),
           Z("一頁兩三句到一小段，有對話。孩子自己讀，大人在旁邊問問題。", "Two or three sentences to a short paragraph a page, with dialogue. The child reads; the adult asks questions.")),
          ("9-12", Z("讀整段故事", "reading whole paragraphs"), 9, 12, Z('Dad took Chris to his office. "What do you do all day?" asked Chris.', "(sample from Book 9a)"),
           Z("一頁一段，過去式敘事。讀完這一段，教育部 1,200 字幾乎都讀過一遍。", "A paragraph a page, told in the past tense. By the end of this stage, almost all of the MOE 1,200 words have been read."))]
    stc = "".join(f'<div class="bp-card bp-stage"><span class="bp-tag">{Z(f"第 {a}–{b} 級", f"Levels {a}–{b}")}</span><b>{name}</b><p>{what}</p>'
                  f'<blockquote lang="en">{sample}</blockquote>'
                  f'<p class="bp-small">{Z(f"每本約 {n(min(words(a)))}–{n(max(words(b)))} 字；讀完第 {b} 級，讀過的教育部字累積 {n(cum[b-1])} 個。", f"about {n(min(words(a)))}–{n(max(words(b)))} words a book; after Level {b}, {n(cum[b-1])} MOE words read in all.")}</p></div>'
                  for key, name, a, b, sample, what in st)
    out.append(f"""<section class="section bg-soft">
  <div class="wrap">
    {h2(Z("從哪裡開始", "where to start"), "孩子在哪個階段", Z("孩子在<em>哪個階段</em>？", "which stage is your child at?"), "green")}
    <p class="body center" style="max-width:64ch;margin:14px auto 0">{Z("看程度，不看年齡。最快的方法：讓孩子大聲讀下面的句子。一頁裡不會的字不超過兩個（<a href='/graded-readers-guide/'>五指法則</a>），就從那個階段開始；不確定就先免費讀第一本。",
        "Go by level, not age. The quickest way: have the child read the sentence below aloud. If a page has no more than two unknown words (the five-finger rule), start at that stage; if unsure, read the first book free first.")}</p>
    <div class="bp-grid reveal">{stc}</div>
  </div>
</section>
""")

    # the 12 levels
    rows = []
    for L in range(1, 13):
        bs = [books[f"{L}{x}"] for x in "abc"]
        cov = "".join(f'<img src="/assets/img/readers/covers/{b["code"]}.webp" alt="" width="320" height="454" loading="lazy" decoding="async">' for b in bs)
        titles = "・".join(f'<i lang="en">{esc(b["title"])}</i>' for b in bs)
        spread = f"level-{L:02d}-{L}{'bca'[L % 3]}"
        qs = "".join(f'<h4 lang="en">{esc(b["title"])}</h4><ul lang="en">' + "".join(f"<li>{esc(q)}</li>" for q in b["questions"][:3]) + "</ul>" for b in bs)
        rows.append(f"""<details class="bp-lv"><summary><span class="bp-l">{Z(f"第 {L} 級", f"Level {L}")}<small>{Z("3 本", "3 books")}</small></span><span class="bp-cov">{cov}</span>
<span class="bp-t">{titles}</span><span class="bp-w"><b>{wrange([b["words"] for b in bs])}</b>{Z("字／本", "words a book")}</span></summary>
<div class="bp-in"><div><img src="/assets/img/readers/spreads/{spread}.webp" alt="第 {L} 級內頁" width="960" height="681" loading="lazy" decoding="async"></div>
<div><p style="margin:0 0 10px;font-size:14px;line-height:1.7">{Z(f"這一級新讀到的教育部字：<b>{lv_new[L-1]}</b> 個；讀完累積 <b>{n(cum[L-1])}</b> 個。", f"MOE words first read in this level: {lv_new[L-1]}; {n(cum[L-1])} in all after it.")}</p>
<p style="margin:0 0 6px;font-size:13.5px;font-weight:800;color:var(--navy)">{Z("讀完問問看（書後的問題）", "talk about it (questions from the back of each book)")}</p>{qs}
{buy(STORE["readers_levels"].get(str(L), ""), Z(f"買第 {L} 級・NT${P_LEVEL}", f"buy Level {L} · NT${P_LEVEL}"), "readers", f"level-{L}", P_LEVEL)}</div></div></details>""")
    out.append(f"""<section class="section">
  <div class="wrap" style="max-width:980px">
    {h2(Z("12 級一覽", "all 12 levels"), "12-級36-本一覽", Z("12 級 36 本，<em>一覽</em>", "the 12 levels and 36 books"))}
    <p class="body center" style="max-width:64ch;margin:14px auto 0">{Z("點開每一級，看內頁、每本書後的問題，和這一級新讀到的字。每一級的 3 本用同一批字：第一本先教，後兩本換個故事再讀。", "Open a level to see a page, the questions at the back of each book and the words it adds. The 3 books of a level share the same words: the first teaches them, the other two use them in new stories.")}</p>
    <div class="reveal" style="margin-top:20px">{"".join(rows)}</div>
  </div>
</section>
""")

    # why it is built this way
    why = [(f"{n(cum[-1])}", Z("個教育部字讀得到", "MOE words you meet in the stories"),
            Z(f"教育部 1,200 字表共 {n(R['official_entries'])} 條，36 本故事用到其中 {n(cum[-1])} 條。另外 {R['excluded_on_purpose']} 個（例如 kill、die、hate）不適合放進童書，我們故意不用。",
              f"The MOE 1,200 list has {n(R['official_entries'])} entries; the 36 stories use {n(cum[-1])} of them. The other {R['excluded_on_purpose']} (kill, die, hate and the like) don't belong in children's books, so we left them out on purpose.")),
           ("3+", Z("新字一出現就重複", "each new word repeats at once"),
            Z("新字出現的那本書裡至少再出現三次，後面的書繼續用。孩子不是背字，是讀到記住。", "A new word appears at least three times in the book that brings it, and later books keep using it. Children don't drill words; they read them until they stick.")),
           ("TW", Z("故事在台灣", "the stories happen in Taiwan"),
            Z("家裡、陽台、巷口、學校、公園、菜市場、夜市、捷運、動物園、海邊、農場和山上露營：孩子認得的地方，讀起來就不陌生。", "home, the balcony, the lane, school, the park, the market, the night market, the MRT, the zoo, the beach, a farm and a mountain camp: places children know.")),
           ("36", Z("本都是原創", "all 36 are original"),
            Z("故事和插圖都是為這套書做的，不是翻譯書，也不是改寫別人的故事。", "stories and pictures were made for this series; not translations, not retellings."))]
    wc = "".join(f'<div class="bp-card"><span class="bp-num">{a}</span><b>{b}</b><p>{c}</p></div>' for a, b, c in why)
    out.append(f"""<section class="section bg-soft">
  <div class="wrap">
    {h2(Z("怎麼編的", "how it is built"), "為什麼這樣編", Z("為什麼<em>這樣編</em>", "why it is built this way"), "yellow")}
    <div class="bp-grid reveal">{wc}</div>
  </div>
</section>
""")

    # reading together
    steps = [Z("<b>先看圖，用中文聊也可以。</b>右頁整頁插圖就是故事，先問孩子「你看到什麼？」", "Look at the picture first; talking in Chinese is fine. The full-page picture is the story: ask 'what do you see?'"),
             Z("<b>大人指著字慢慢讀，孩子跟著讀。</b>第二遍換孩子讀，大人只在卡住的時候幫忙。", "The adult points and reads slowly, the child reads along. The second time the child reads; help only when stuck."),
             Z("<b>讀完用書後的問題聊一聊。</b>答案在故事裡找得到，用指的、用中文回答都算。", "Talk about the questions at the back. The answers are in the story; pointing or answering in Chinese counts."),
             Z("<b>同一本讀到順，再換下一本。</b>每一級 3 本用同一批字，讀到第三本會順很多。", "Read the same book until it is smooth, then move on. The 3 books of a level share the same words, so the third goes much more smoothly.")]
    out.append(f"""<section class="section">
  <div class="wrap">
    {h2(Z("親子共讀", "reading together"), "陪孩子讀不需要英文很好", Z("陪孩子讀，<em>不需要英文很好</em>", "you don't need good English to read with your child"))}
    <ol class="bp-steps reveal">{"".join(f"<li>{s}</li>" for s in steps)}</ol>
    <p class="body center" style="max-width:66ch;margin:6px auto 0;font-size:14.5px">{Z("建議印出來一起讀：<a href='https://oro.open.ac.uk/75652' target='_blank' rel='noopener'>2021 年一份整合 39 篇研究的分析</a>發現，大人陪讀紙本，孩子對故事的理解比自己看電子書好。翻頁電子書適合在路上、或孩子自己再讀一遍。",
        "We suggest printing and reading together: a 2021 analysis of 39 studies found children understand a story better when an adult reads a paper book with them than when they read an e-book alone. The flip book suits reading on the go, or a child's own re-read.")}</p>
  </div>
</section>
""")

    # prices
    lv_btns = "".join(buy(STORE["readers_levels"].get(str(L), ""), Z(f"第 {L} 級", f"Level {L}"), "readers", f"level-{L}", P_LEVEL,
                          "btn btn-outline") for L in range(1, 13))
    set_btns = "".join(buy(STORE["readers_sets"].get(k, ""), Z(f"第 {k.replace('-', '–')} 級", f"Levels {k}"), "readers", f"set-{k}", P_SET)
                       for k in ("1-4", "5-8", "9-12"))
    tiers = f"""<div class="bp-tiers reveal" id="buy-tiers">
<div class="bp-tier"><span class="bp-tn">{Z("單級 3 本", "one level, 3 books")}</span><span class="bp-tp">NT${P_LEVEL}</span><span class="bp-tu">{Z(f"約 NT${round(P_LEVEL/3)}／本", f"about NT${round(P_LEVEL/3)} a book")}</span>
<span class="bp-td">{Z("先買孩子現在這一級試試看。每級約 23–36 MB。", "Try the level your child is at now. About 23–36 MB a level.")}</span><div class="bp-pick">{lv_btns}</div></div>
<div class="bp-tier hl"><span class="bp-tn">{Z("一個階段 4 級 12 本", "one stage, 4 levels, 12 books")}</span><span class="bp-tp">NT${n(P_SET)}</span><span class="bp-tu">{Z(f"約 NT${round(P_SET/12)}／本・比單級分開買省 NT${4*P_LEVEL-P_SET}", f"about NT${round(P_SET/12)} a book · NT${4*P_LEVEL-P_SET} less than 4 single levels")}</span>
<span class="bp-td">{Z("從孩子現在的階段買起，夠讀好幾個月。", "Start from your child's stage; enough for several months.")}</span><div class="bp-pick two">{set_btns}</div></div>
<div class="bp-tier"><span class="bp-tn">{Z("全套 12 級 36 本", "all 12 levels, 36 books")}</span><span class="bp-tp">NT${n(P_ALL)}</span><span class="bp-tu">{Z(f"約 NT${round(P_ALL/36)}／本・比 12 級分開買省 NT${n(12*P_LEVEL-P_ALL)}", f"about NT${round(P_ALL/36)} a book · NT${n(12*P_LEVEL-P_ALL)} less than 12 single levels")}</span>
<span class="bp-td">{Z(f"從第一句英文讀到整段故事，一次買齊。檔案約 {MB_SET['all']} MB。", f"From the first sentence to full paragraphs, all at once. About {MB_SET['all']} MB.")}</span><div class="bp-pick two">{buy(STORE["readers_sets"].get("all", ""), Z(f"買全套・NT${n(P_ALL)}", f"buy all · NT${n(P_ALL)}"), "readers", "all", P_ALL)}</div></div>
</div>"""
    trust = "".join(f"<span>{Z(a, b)}</span>" for a, b in [("安全刷卡", "secure card payment"), ("付款後立刻寄下載連結到 email", "download link emailed right after payment"),
                                                            ("不用註冊帳號", "no account needed"), ("價格已含稅", "prices include tax")])
    out.append(f"""<section class="section bg-soft" id="buy">
  <div class="wrap">
    {h2(Z("價格", "prices"), "三種買法照需要挑", Z("三種買法，<em>照需要挑</em>", "three ways to buy"), "yellow")}
    {soon(any_link)}<div class="bp-trust reveal">{trust}</div>
    {tiers}
    <p class="bp-fine">{Z("每本書都有 PDF（A5，可以自己印）和翻頁電子書（解壓縮後點開 index.html，電腦、平板、手機都能離線讀）。書裡沒有音檔。家庭自用；學校或補習班要全班用，請先 <a href='" + LINE + "' target='_blank' rel='noopener'>LINE 問我們</a>。",
        "Every book comes as a PDF (A5, print it yourself) and a flip book (unzip, open index.html; works offline on a computer, tablet or phone). There is no audio. For family use; for a whole class at a school or cram school, ask us on LINE first.")}<br>
    {Z("這是數位內容，付款後立刻提供下載；依《通訊交易解除權合理例外情事適用準則》第 2 條第 5 款，按下購買即表示你同意不適用七天解除權。請先免費讀第一本再決定。",
       "This is digital content delivered right after payment; under Article 2(5) of the rules on exceptions to the 7-day cancellation right, clicking buy means you agree the 7-day cancellation does not apply. Please read the first book free before deciding.")}</p>
  </div>
</section>
""")

    # FAQ
    qa = [(Z("適合幾歲的孩子？", "What age is it for?"),
           Z("看程度，不看年齡。認得字母、學過一點自然發音就可以從第 1 級開始；已經讀得出短句的孩子，從第 5 級開始。最準的方法是讓孩子讀上面「孩子在哪個階段」的句子，或先免費讀第一本。",
             "Go by level, not age. A child who knows the letters and some phonics can start at Level 1; one who already reads short sentences, at Level 5. The surest way is the sentences under 'which stage', or the free first book.")),
          (Z("有音檔嗎？", "Is there audio?"),
           Z("目前沒有。這套書是設計給大人陪讀、孩子自己讀的；不確定怎麼唸的字，可以查網站上的<a href='/pronunciation/word/'>單字發音頁</a>。",
             "Not yet. The books are made for an adult to read along and for the child to read alone; for a word you're unsure how to say, use the site's word-pronunciation pages.")),
          (Z("和學校課本有什麼關係？", "How does it relate to the school textbook?"),
           Z("字彙依教育部 1,200 字表排序，所以學校會教的字在故事裡都讀得到；但這套書不照課本的課次走，是課外閱讀。", "The vocabulary follows the MOE 1,200 list, so the words school teaches all appear in the stories; it doesn't follow the textbook's lessons — it is reading outside class.")),
          (Z("可以印出來嗎？", "Can I print it?"),
           Z("可以，家裡自己用都沒問題。PDF 是 A5 大小（一般 A4 對折的大小），印在 A4 紙上選「符合頁面」就行。", "Yes, for your own family. The PDF is A5 (half of A4); print on A4 with 'fit to page'.")),
          (Z("可以在班上或補習班用嗎？", "Can I use it in a class or cram school?"),
           Z("購買是給家庭自用。想在課堂上使用或多人授權，先在 LINE 跟我們說一聲，我們另外談。", "A purchase is for family use. For classroom use or several users, message us on LINE first.")),
          (Z("怎麼付款、多久拿到？", "How do I pay, and when do I get it?"),
           Z("在這一頁按購買，用信用卡付款（不會跳到別的網站，也不用註冊）。付款完成，下載連結會立刻寄到你填的 email。", "Click buy on this page and pay by card (you stay on this page; no account). When payment goes through, the download link goes straight to the email you entered.")),
          (Z("翻頁電子書在手機上能看嗎？", "Does the flip book work on a phone?"),
           Z("可以。電腦和平板上是左右兩頁一起翻，手機直拿會一次顯示一頁。也可以直接用 PDF。", "Yes. On a computer or tablet it turns two pages at a time; on an upright phone it shows one page at a time. The PDF works too."))]
    out.append(f"""<section class="section">
  <div class="wrap">
    {h2(Z("常見問題", "FAQ"), "分級讀本常見問題", Z("購買前，<em>大概會想問的</em>", "what you might ask before buying"))}
    {faq(qa)}
  </div>
</section>
<section class="section bg-blue">
  <div class="wrap">
    <div class="cta-box reveal">
      <span class="eyebrow eyebrow-green">{Z("免費試讀", "free sample")}</span>
      <h2 id="先讀第一本" style="margin-top:14px">{Z("先讀第一本，<em>再決定</em>", "read the first book, then decide")}</h2>
      <p class="body" style="max-width:560px;margin:16px auto 0">{Z(f"第 1 級第一本 <i lang='en'>This Is Bobo!</i> 整本免費，在網站上直接翻頁讀，不用下載也不用留資料。", "Level 1, Book 1, This Is Bobo!, is free in full: turn the pages right on the site, no download, no sign-up.")}</p>
      <div class="cta-row"><a class="btn btn-primary" href="/{READERS}/read/1a/" data-book="readers" data-book-item="free">{Z("免費讀第一本", "read the first book free")}</a>
      <a class="btn btn-outline" href="{LINE}" target="_blank" rel="noopener">{Z("LINE 問我們", "ask us on LINE")}</a></div>
    </div>
  </div>
</section>
""")
    out.append(FOOT)
    return "".join(out)

# ---------------------------------------------------------------- the free 1a flip book

def free_reader():
    src = os.path.join(FLIP_SRC, "1a")
    dst = os.path.join(SITE, READERS, "read", "1a")
    if not os.path.exists(src):
        print("  flip book source missing, kept what is on the site:", src)
        return
    os.makedirs(dst, exist_ok=True)
    shutil.copytree(os.path.join(src, "pages"), os.path.join(dst, "pages"), dirs_exist_ok=True)
    os.makedirs(os.path.join(SITE, READERS, "read", "lib"), exist_ok=True)
    for f in os.listdir(os.path.join(FLIP_SRC, "lib")):
        shutil.copy2(os.path.join(FLIP_SRC, "lib", f), os.path.join(SITE, READERS, "read", "lib", f))
    t = open(os.path.join(src, "index.html"), encoding="utf-8").read()
    t = t.replace('<html lang="en">', '<html lang="zh-Hant-TW">')
    t = t.replace('href="../index.html" title="All books">&#8249; Books</a>',
                  f'href="/{READERS}/" title="全部 36 本" data-book="readers" data-book-item="from-free">&#8249; 全部 36 本</a>')
    ga = ("<meta name='robots' content='noindex,follow'>\n"
          f"<link rel='canonical' href='{ORIGIN}/{READERS}/read/1a/'>\n"
          # GA4 itself comes from seo_build's AE:GTM block (this page is SELF_CONTAINED, which still gets it)
          "<script>document.addEventListener('click',function(e){var a=e.target.closest&&e.target.closest('a[data-book]');"
          "if(a&&typeof window.gtag==='function')gtag('event','book_tap',{product:'readers',item:a.getAttribute('data-book-item'),page_path:location.pathname,link_text:'page'});});</script>\n")
    t = t.replace("<title>", ga + "<title>", 1)
    open(os.path.join(dst, "index.html"), "w", encoding="utf-8").write(t)
    print("  free reader:", os.path.relpath(dst, SITE), len(os.listdir(os.path.join(dst, "pages"))), "pages")

# ---------------------------------------------------------------- grammar page

STAGES = [("elementary", ["G3", "G4", "G5", "G6"]), ("junior", ["G7-1", "G7-2", "G8-1", "G8-2", "G9-1", "G9-2"]),
          ("senior", ["G10-1", "G10-2", "G11-1", "G11-2", "G12-1", "G12-R"])]

def free_pdfs():
    """Page 1 of every cheat sheet, copied to /assets/downloads/ under site-style names."""
    got = {}
    for _, codes in STAGES:
        for c in codes:
            stem = f"{c}-pattern-cards" if c in ("G3", "G4", "G5", "G6") else f"{c}-grammar-cheatsheet"
            src = os.path.join(FREE_PDF_SRC, f"{stem}-page1-free.pdf")
            name = f"ae-grammar-{c.lower()}-page1-free.pdf"
            dst = os.path.join(SITE, "assets", "downloads", name)
            if os.path.exists(src) and not os.path.exists(dst):   # copy once: check_pdfs.py --fix repairs the site copy
                shutil.copy2(src, dst)                             # in place (Apple font fault); delete it to take a new build
            if os.path.exists(dst):
                got[c] = f"/assets/downloads/{name}"
    return got

def grammar_page():
    _page[0] = GRAMMAR
    B = {b["code"]: b for b in G}
    free = free_pdfs()
    any_link = any(STORE["grammar"].values())
    title = Z("英文文法書＋速查表：國小到高中每學期一本，第 1 頁免費下載｜埃森美語",
              "English grammar books + cheat sheets: one book per semester for elementary, junior and senior high, page 1 free | American English")
    desc = Z("國小句型書 4 冊、國中文法書 6 冊（康軒、翰林、南一適用）、高中文法書 6 冊（含學測總複習）。"
             "每個重點一頁規則與圖解，附練習、測驗、解答和速查表，第 1 頁免費下載。",
             "4 elementary sentence-pattern books, 6 junior-high grammar books (for the 康軒, 翰林, 南一 textbooks), 6 senior-high books (incl. a 學測 review). "
             "One page of rules and pictures per point, with practice, tests, answers and a cheat sheet; page 1 is a free download.")
    og_t = Z("英文文法書＋速查表：國小到高中每學期一本", "grammar books + cheat sheets, one per semester")
    ld = [{"@context": "https://schema.org", "@type": "Product", "name": "英文文法書・文法速查表（國小・國中・高中）",
           "description": strip(desc), "brand": {"@type": "Brand", "name": "埃森美語 American English"},
           "image": [f"{ORIGIN}/assets/img/grammar-books/covers/{c}.webp" for c in ("G3", "G8-1", "G10-1")],
           **({"offers": {"@type": "AggregateOffer", "priceCurrency": "TWD", "lowPrice": P_GSHEETS, "highPrice": P_GBOOKS,
                          "offerCount": 6, "availability": "https://schema.org/InStock"}} if any_link else {})}]
    out = [head(GRAMMAR, title, desc, og_t, desc, "/assets/img/grammar-books/og-grammar-books.jpg", 1600, 1200,
                Z("英文文法書與文法速查表封面", "covers of the grammar books and cheat sheets"), ld, LEMON if any_link else "")]
    fan = "".join(f'<img src="/assets/img/grammar-books/covers/{c}.webp" alt="{esc(B[c]["title"])} 封面" width="300" height="424" '
                  f'{FP if i == 2 else LZ} decoding="async">'
                  for i, c in enumerate(("G4", "G7-2", "G8-1", "G10-1", "G12-R")))
    out.append(f"""<section class="page-hero">
  <div class="wrap">
    <div class="breadcrumb reveal"><a href="/">首頁</a> ／ <a href="/junior-high-english-grammar/">{Z("國中英文文法", "junior-high grammar")}</a> ／ {Z("文法書", "grammar books")}</div>
    <div class="bp-hero">
      <div>
        <span class="eyebrow eyebrow-yellow reveal">{Z("埃森美語原創 · 國小到高中 16 冊", "our own series · 16 books, elementary to senior high")}</span>
        <h1 class="reveal d1">{Z("英文文法書＋<em>文法速查表</em>", "grammar books + cheat sheets")}</h1>
        <div class="divider reveal d1"></div>
        <p class="body reveal d2">{Z("國中、高中每學期一本，國小每年級一本。每本 36–38 頁：一個文法重點一頁，規則表、圖解、例句和練習放在同一頁；每個單元再加一頁綜合練習和一頁寫作應用，最後有複習測驗、兩回綜合測驗和完整解答。每一本都附同一冊的文法速查表。",
            "One book per semester for junior and senior high, one per grade for elementary. 36–38 pages each: one page per grammar point with the rule table, pictures, examples and exercises together; each unit adds a practice page and a grammar-for-writing page; then review tests, two full tests and a complete answer key. Each book comes with that semester's cheat sheet.")}</p>
        <div class="bp-cta reveal d2"><a class="btn btn-primary" href="#free">{Z("免費下載第 1 頁", "free page 1")}</a>
          <a class="btn btn-outline" href="#buy">{Z("看價格", "see prices")}</a></div>
        <div class="bp-facts reveal d2"><span>{Z("每學期一本", "one per semester")}</span><span>{Z("附解答", "answers included")}</span><span>{Z("可以列印", "printable")}</span><span>{Z("每冊附速查表", "cheat sheet with every book")}</span></div>
      </div>
      <div class="bp-fan reveal d1" aria-hidden="true">{fan}</div>
    </div>
  </div>
</section>
""")
    # the three stages
    info = {"elementary": (Z("國小 句型書 4 冊", "elementary: 4 sentence-pattern books"), Z("三～六年級，每年級一冊", "Grades 3–6, one per grade"),
                           Z("國小課綱不教文法規則，所以這 4 冊是「句型」：一個句型一頁，有對話、換換看、四線格描寫和練習，不講文法術語。每冊 12 個句型，附句型速查卡。",
                             "The elementary curriculum does not teach grammar rules, so these are sentence-pattern books: one pattern a page with a dialogue, a swap box, four-line handwriting and exercises, no grammar terms. 12 patterns a book, with pattern cards.")),
            "junior": (Z("國中 文法書 6 冊", "junior high: 6 grammar books"), Z("國一上～國三下，每學期一冊", "Grade 7 to Grade 9, one per semester"),
                       Z("每冊 11–12 個重點，對照康軒、翰林、南一每一課教的文法（附課本對照表）。國三下的那一冊是會考總複習。", "11–12 points a book, mapped to the grammar each lesson of 康軒, 翰林 and 南一 teaches (lesson map included). The Grade 9 second-semester book is the 會考 review.")),
            "senior": (Z("高中 文法書 6 冊", "senior high: 6 grammar books"), Z("高一上～高三上＋學測總複習", "Grade 10 to Grade 12 first semester + a 學測 review"),
                       Z("依文法主題編排，適用龍騰、三民、遠東（各版每課的文法不同，所以不列課次）。題型有中譯英和學測綜合測驗。最後一冊是學測文法總複習。", "Arranged by grammar topic for 龍騰, 三民 and 遠東 (each edition puts grammar in different lessons, so there are no lesson numbers). Exercises include Chinese-to-English translation and 學測-style cloze. The last book is the 學測 grammar review."))}
    cards = []
    for key, codes in STAGES:
        name, who, what = info[key]
        cov = "".join(f'<img src="/assets/img/grammar-books/covers/{c}.webp" alt="{esc(B[c]["title"])}" width="300" height="424" loading="lazy" decoding="async">' for c in codes)
        cards.append(f'<div class="bp-card bp-stage"><span class="bp-tag">{who}</span><b>{name}</b><div class="bp-gcovers">{cov}</div><p>{what}</p></div>')
    out.append(f"""<section class="section">
  <div class="wrap">
    {h2(Z("三個學程", "three stages"), "國小國中高中各一套", Z("國小、國中、高中，<em>各一套</em>", "one set each for elementary, junior and senior high"))}
    <div class="bp-grid reveal">{"".join(cards)}</div>
  </div>
</section>
""")
    # inside
    pages = [("elementary-pattern-page", Z("國小句型頁", "elementary pattern page"), Z("對話、換換看、四線格描寫、看圖練習", "dialogue, swap box, handwriting, picture exercise")),
             ("junior-grammar-page", Z("國中文法頁", "junior-high grammar page"), Z("規則表、圖解、例句、小提醒、A／B 練習", "rule table, pictures, examples, tip, A/B exercises")),
             ("junior-practice-page", Z("單元綜合練習", "unit practice page"), Z("看圖、選擇、重組、改錯、改寫", "pictures, choice, word order, fix the mistake, rewrite")),
             ("junior-writing-page", Z("寫作應用", "grammar for writing"), Z("短文填空和自己寫，把文法用在句子裡", "passage gaps and own writing, using the grammar in sentences")),
             ("junior-midterm-page", Z("期中測驗", "midterm test"), Z("100 分的綜合測驗，題型照學校段考", "a 100-point test in the style of school exams")),
             ("senior-grammar-page", Z("高中文法頁", "senior-high grammar page"), Z("一樣的版面，題目加上中譯英和綜合測驗", "same layout, with translation and cloze")),
             ("cheatsheet-page1", Z("文法速查表第 1 頁", "cheat sheet page 1"), Z("整學期的重點一頁看完，這一頁免費", "the whole semester on one page; this page is free"))]
    figs = "".join(f'<figure><img src="/assets/img/grammar-books/pages/{f}.webp" alt="{esc(strip(t))}" width="778" height="1100" loading="lazy" decoding="async">'
                   f'<figcaption><b>{t}</b>{d}</figcaption></figure>' for f, t, d in pages)
    parts = [(Z("一個重點一頁", "one point a page"), Z("規則表、圖、例句、小提醒和兩組練習在同一頁，看完馬上做。", "rule table, pictures, examples, a tip and two exercises on one page: read it, then do it.")),
             (Z("每單元兩頁應用", "two pages per unit"), Z("一頁綜合練習、一頁寫作應用，把同一單元的文法混在一起用。", "a practice page and a grammar-for-writing page that mix the unit's grammar.")),
             (Z("複習與測驗", "reviews and tests"), Z("每兩個單元一回複習測驗，再加上期中、期末兩回 100 分測驗。", "a review test every two units, plus a midterm and a final of 100 points each.")),
             (Z("完整解答", "full answer key"), Z("所有題目都有答案；有兩種寫法都對的題目，兩種都列出來。", "every item is answered; where two answers are right, both are given."))]
    pc = "".join(f'<div class="bp-card"><b>{t}</b><p>{d}</p></div>' for t, d in parts)
    out.append(f"""<section class="section bg-soft">
  <div class="wrap">
    {h2(Z("內頁", "inside"), "一本裡面有什麼", Z("一本裡面，<em>有什麼</em>", "what is inside a book"), "green")}
    <p class="body center" style="max-width:62ch;margin:14px auto 0">{Z("下面是實際的內頁，直接從書裡截下來。左右滑動看。", "Real pages taken straight from the books. Swipe to see them.")}</p>
    <div class="bp-scroll tall reveal">{figs}</div>
    <p class="bp-hint">{Z("← 左右滑動 →", "← swipe →")}</p>
    <div class="bp-grid reveal">{pc}</div>
  </div>
</section>
""")
    # contents of every book
    sec = []
    for key, codes in STAGES:
        name = info[key][0]
        items = []
        for c in codes:
            b = B[c]
            pts = "".join(f'<li>{esc(p["zh"])} <span lang="en">{esc(p["en"])}</span></li>' for u in b["units"] for p in u["points"])
            np_ = b["points"]
            items.append(f'<details class="bp-book"><summary>{esc(b["title"])}<small>{Z(f"{np_} 個重點・6 個單元", f"{np_} points, 6 units")}</small></summary><ol>{pts}</ol></details>')
        sec.append(f'<h3 id="{strip(name)}目錄" style="margin:24px 0 6px;font-size:18px">{name}</h3>' + "".join(items))
    out.append(f"""<section class="section">
  <div class="wrap" style="max-width:860px">
    {h2(Z("目錄", "contents"), "每一冊教什麼", Z("每一冊，<em>教什麼</em>", "what each book teaches"))}
    <p class="body center" style="max-width:62ch;margin:14px auto 0">{Z("點開每一冊，看完整的文法重點。", "Open a book to see its full list of grammar points.")}</p>
    <div class="reveal">{"".join(sec)}</div>
  </div>
</section>
""")
    # free page 1
    fl = []
    for key, codes in STAGES:
        links = "".join(f'<a href="{free[c]}" download data-book="grammar" data-book-item="free-{c}">{esc(B[c]["title"].split(" ")[0])}</a>'
                        for c in codes if c in free)
        fl.append(f'<h3 id="{strip(info[key][0])}免費" style="margin:22px 0 4px;font-size:17px">{info[key][0]}</h3><div class="bp-free">{links}</div>')
    out.append(f"""<section class="section bg-soft" id="free">
  <div class="wrap" style="max-width:860px">
    {h2(Z("免費", "free"), "第-1-頁免費下載", Z("每一冊的第 1 頁，<em>免費下載</em>", "page 1 of every book, free"), "green")}
    <p class="body center" style="max-width:62ch;margin:14px auto 0">{Z("第 1 頁就是整學期的文法重點，一頁看完：每個重點的名稱、句型和一個例句。不用留資料，直接下載、歡迎分享。", "Page 1 is the whole semester's grammar on one page: each point's name, pattern and an example. No sign-up; download it and share it.")}</p>
    <div class="reveal">{"".join(fl)}</div>
  </div>
</section>
""")
    # prices
    tiers = []
    for key, codes in STAGES:
        nb = len(codes)
        bmb, smb = MB_GRAMMAR[key]
        tiers.append(f"""<div class="bp-tier{" hl" if key == "junior" else ""}"><span class="bp-tn">{info[key][0]}</span><span class="bp-tp">NT${P_GBOOKS}</span>
<span class="bp-tu">{Z(f"{nb} 冊文法書＋{nb} 份速查表・約 NT${round(P_GBOOKS/nb)}／冊", f"{nb} books + {nb} cheat sheets · about NT${round(P_GBOOKS/nb)} a book")}</span>
<span class="bp-td">{info[key][1]}{Z(f"。PDF，約 {bmb} MB。", f". PDF, about {bmb} MB.")}</span>
<div class="bp-pick two">{buy(STORE["grammar"].get(f"{key}-books", ""), Z(f"買文法書・NT${P_GBOOKS}", f"buy the books · NT${P_GBOOKS}"), "grammar", f"{key}-books", P_GBOOKS)}
{buy(STORE["grammar"].get(f"{key}-sheets", ""), Z(f"只要速查表 {nb} 份・NT${P_GSHEETS}", f"cheat sheets only · NT${P_GSHEETS}"), "grammar", f"{key}-sheets", P_GSHEETS, "btn btn-outline")}</div></div>""")
    trust = "".join(f"<span>{Z(a, b)}</span>" for a, b in [("安全刷卡", "secure card payment"), ("付款後立刻寄下載連結到 email", "download link emailed right after payment"),
                                                            ("不用註冊帳號", "no account needed"), ("價格已含稅", "prices include tax")])
    out.append(f"""<section class="section" id="buy">
  <div class="wrap">
    {h2(Z("價格", "prices"), "一個學程一次買齊", Z("一個學程，<em>一次買齊</em>", "a whole stage in one purchase"), "yellow")}
    <p class="body center" style="max-width:62ch;margin:14px auto 0">{Z("文法書以學程為單位賣：一次拿到整個學程的每一冊，每冊都附速查表。只需要考前複習的話，可以只買速查表。", "Grammar books are sold by stage: every book of the stage at once, each with its cheat sheet. For exam review only, buy just the cheat sheets.")}</p>
    {soon(any_link)}<div class="bp-trust reveal">{trust}</div>
    <div class="bp-tiers reveal">{"".join(tiers)}</div>
    <p class="bp-fine">{Z("家庭自用，可以自己印。學校或補習班要全班用，請先 <a href='" + LINE + "' target='_blank' rel='noopener'>LINE 問我們</a>。", "For family use; print it yourself. For a whole class, ask us on LINE first.")}<br>
    {Z("這是數位內容，付款後立刻提供下載；依《通訊交易解除權合理例外情事適用準則》第 2 條第 5 款，按下購買即表示你同意不適用七天解除權。請先下載免費的第 1 頁再決定。",
       "This is digital content delivered right after payment; under Article 2(5) of the rules on exceptions to the 7-day cancellation right, clicking buy means you agree the 7-day cancellation does not apply. Please download the free page 1 before deciding.")}</p>
  </div>
</section>
""")
    qa = [(Z("適用哪一個版本的課本？", "Which textbook edition does it fit?"),
           Z("國中三個版本都適用：每一冊的對照表列出康軒、翰林、南一哪一課教這個文法。高中適用龍騰、三民、遠東，但各版每課教的文法不同，所以依文法主題編排、不列課次。國小依教育部基本學習內容整理。",
             "Junior high fits all three editions: each book's map shows which lesson of 康軒, 翰林 and 南一 teaches each point. Senior high fits 龍騰, 三民 and 遠東, but each edition places grammar differently, so the books go by topic with no lesson numbers. Elementary follows the MOE basic learning content.")),
          (Z("國小為什麼不講文法？", "Why no grammar rules for elementary?"),
           Z("國小英語課綱要求避免講解、分析文法，所以國小這 4 冊用「句型」：孩子先會說、會寫整句，國中再學規則。", "The elementary curriculum asks teachers to avoid explaining and analysing grammar, so these 4 books teach sentence patterns: children say and write whole sentences first and learn the rules in junior high.")),
          (Z("有解答嗎？", "Is there an answer key?"),
           Z("每一冊和每一份速查表最後都有完整解答。", "Every book and every cheat sheet ends with a full answer key.")),
          (Z("可以只買一冊嗎？", "Can I buy a single book?"),
           Z("目前以學程為單位賣（國小 4 冊、國中 6 冊、高中 6 冊），一套 NT$590；每一冊的第 1 頁可以先免費下載看看。", "For now they are sold by stage (4 elementary, 6 junior-high, 6 senior-high), NT$590 a set; page 1 of every book is free to try first.")),
          (Z("速查表和文法書差在哪？", "How is the cheat sheet different from the book?"),
           Z("速查表 14–15 頁：每個重點一頁加一頁解答，適合考前複習。文法書 36–38 頁：同樣的重點頁，再加上每單元的綜合練習、寫作應用、複習測驗和兩回 100 分測驗。", "The cheat sheet is 14–15 pages: one page per point and an answer page, for review before an exam. The book is 36–38 pages: the same point pages plus each unit's practice and writing pages, review tests and two 100-point tests.")),
          (Z("可以印給班上或補習班用嗎？", "Can I print it for a class or cram school?"),
           Z("購買是給家庭自用，自己印沒問題。想在課堂上使用或多人授權，先在 LINE 跟我們說一聲。", "A purchase is for family use; printing it yourself is fine. For classroom use or several users, message us on LINE first."))]
    out.append(f"""<section class="section bg-soft">
  <div class="wrap">
    {h2(Z("常見問題", "FAQ"), "文法書常見問題", Z("購買前，<em>大概會想問的</em>", "what you might ask before buying"))}
    {faq(qa)}
  </div>
</section>
<section class="section bg-blue">
  <div class="wrap">
    <div class="cta-box reveal">
      <span class="eyebrow eyebrow-green">{Z("免費", "free")}</span>
      <h2 id="先下載第-1-頁" style="margin-top:14px">{Z("先下載第 1 頁，<em>看看合不合用</em>", "download page 1 first and see if it suits")}</h2>
      <p class="body" style="max-width:560px;margin:16px auto 0">{Z("找到孩子這學期的那一冊，第 1 頁免費。也可以先看免費的<a href='/junior-high-english-grammar/'>國中英文文法總整理</a>。", "Find this semester's book; its page 1 is free. Or start with the free junior-high grammar summary.")}</p>
      <div class="cta-row"><a class="btn btn-primary" href="#free">{Z("免費下載第 1 頁", "free page 1")}</a><a class="btn btn-outline" href="{LINE}" target="_blank" rel="noopener">{Z("LINE 問我們", "ask us on LINE")}</a></div>
    </div>
  </div>
</section>
""")
    out.append(FOOT)
    return "".join(out)

# ---------------------------------------------------------------- og images + gloss

def og_images():
    """Share images from the Lemon thumbnails (1600×1200, already in the brand style)."""
    pairs = [("readers-1-all-36.jpg", "assets/img/readers/og-all-36.jpg"), ("grammar-1-all-16.jpg", "assets/img/grammar-books/og-grammar-books.jpg")]
    for src, dst in pairs:
        s = os.path.expanduser(f"~/Downloads/AE-lemon-upload/thumbnails/{src}")
        d = os.path.join(SITE, dst)
        if os.path.exists(s) and not os.path.exists(d):
            shutil.copy2(s, d)

def write_gloss():
    L = ["# Gloss: the two book pages (2026-11-08)", "",
         "Every Chinese line on the new pages, in page order, with its English. Built by `tools/build_book_pages.py` from the same strings it prints.",
         "Book titles in English (This Is Bobo! …) and the books' own questions are printed in English and not listed.", ""]
    for slug, head_ in ((READERS, "/chris-and-cora-readers/ — the 分級讀本 tab"), (GRAMMAR, "/english-grammar-books/ — grammar books")):
        L += [f"## {head_}", ""]
        seen = set()
        for zh, en in GLOSS[slug]:
            k = strip(zh)
            if k in seen:
                continue
            seen.add(k)
            L += [f"- {k}", f"  = '{strip(en)}'"]
        L.append("")
    open(GLOSS_OUT, "w", encoding="utf-8").write("\n".join(L))
    print("  gloss:", GLOSS_OUT, sum(len(v) for v in GLOSS.values()), "strings")

if __name__ == "__main__":
    og_images()
    for slug, fn in ((READERS, readers_page), (GRAMMAR, grammar_page)):
        os.makedirs(os.path.join(SITE, slug), exist_ok=True)
        open(os.path.join(SITE, slug, "index.html"), "w", encoding="utf-8").write(fn())
        print("  wrote", f"{slug}/index.html")
    free_reader()
    write_gloss()
    links = sum(bool(v) for g in ("readers_sets", "readers_levels", "grammar") for v in STORE[g].values())
    print(f"  checkout links set: {links} of 22 (data/books_store.json); buttons without one say 即將開放")

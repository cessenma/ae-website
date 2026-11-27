#!/usr/bin/env python3
"""The school's two book pages, generated from data (2026-11-08, Chris: "a new tab at the top for the
story book collection … the books link present on the 1200 words pages … the grammar stuff can be part
of something else"). Run tools/seo_build.py afterwards (chrome, SEO blocks, sitemap date).

Writes
  chris-and-cora-readers/index.html          the 分級讀本 tab: 36 Chris and Cora readers
  chris-and-cora-readers/read/1a|1b|1c/      the free Level 1 flip books (self-contained, noindex)
  english-grammar-books/index.html           the grammar books + cheat sheets (linked from the grammar pages)
  assets/downloads/ae-grammar-*-sample.pdf     one free sample page per grade (page 3: the first point in full)
  ~/Downloads/GLOSS-2026-11-08-BOOK-PAGES.md every Chinese line on both pages with its English (Chris reads English)

Data
  data/readers.json        titles, words per book, MOE words read by level, questions (from the ae-readers repo)
  data/grammar_books.json  units and points of the 16 grammar books (from the grammar series engine)
  data/books_store.json    Lemon Squeezy checkout link per VARIANT (each variant has its own checkout/buy/<uuid>;
                           a product's Share link opens on its FIRST variant). Empty = the button says 即將開放.

Facts on the pages come from those files; nothing here is typed from memory.
"""
import html, json, os, re, shutil, urllib.parse

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIGIN = "https://americanenglish.com.tw"
LINE = "https://lin.ee/W9J8TuQ"
FLIP_SRC = os.path.expanduser("~/Downloads/AE-readers-out/flip")
BOOK_PDF_SRC = os.path.expanduser("~/Downloads/AE-GRAMMAR-SERIES-2026-10-31/workbook")
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
P_LEVEL, P_SET, P_ALL = 290, 990, 1990      # lowered 11-14 (Chris: "lower the cost … no traffic yet")
P_GBOOKS, P_GSHEETS = 590, 140      # 11-15 Chris: books stay 590, sheets 140
P_GALL, P_GSALL = 1190, 390        # 11-15: all 16 books (like the GEPT 全部四級 bundle) / all 16 sheets
MB_LEVEL = "40–183 MB"
MB_SET = {"1-4": 217, "5-8": 438, "9-12": 667, "all": 1322}   # 11-10 zips with read-aloud audio
MB_GRAMMAR = {"elementary": (30, 12), "junior": (38, 11), "senior": (36, 13)}   # junior rebuilt 11-10 (段考 tests)

# measured 2026-11-10 from the ae-readers repo (data/books/*.json, data/ladder.json); see memory ae-book-pages-2026-11-08
FRY_LIST, FRY_READ = 296, 281        # Fry, Kress & Fountoukidis (2000) first-300 list as published (296 entries); entries met in the 36 books
CORE, CORE_10PLUS, CORE_MEDIAN = 300, 287, 27   # core words; core words met 10+ times across the 36 books; median encounters


# hero fan entrance (Chris 11-10): every picture comes in from the left and travels along the fan's own arch,
# through the slots of the pictures before it, to its place; rightmost first, so they deal out like cards
FREE = ("1a", "1b", "1c")   # Level 1, free on the site (Chris 11-11)

# Click a free book: it flies to the middle, the hard cover swings open slowly onto the title page,
# then the real flip book fades in over it. No JS / reduced motion: the link opens the reader page.
OPEN_JS = """<script>(()=>{const box=document.getElementById("bookOpen");if(!box||!box.animate)return;
const bg=box.querySelector(".bo-bg"),fr=box.querySelector(".bo-frame"),ifr=fr.querySelector("iframe"),x=box.querySelector(".bo-x");
const still=matchMedia("(prefers-reduced-motion: reduce)").matches;let fly=null,busy=false;
const E1="cubic-bezier(.22,.75,.25,1)",E2="cubic-bezier(.5,.05,.25,1)";
function open(a,ev){const c=a.dataset.open;if(!c||busy)return;ev.preventDefault();busy=true;
 const href=a.getAttribute("href"),src=href+(href.indexOf("?")<0?"?":"&")+"in=1"+(still?"":"&o=1");ifr.src=src;ifr.title=a.dataset.title||"";
 box.classList.add("on");document.documentElement.style.overflow="hidden";
 bg.animate([{opacity:0},{opacity:1}],{duration:still?1:600,fill:"forwards"});
 if(still){fr.style.opacity=1;x.style.opacity=1;busy=false;x.focus();return}
 const im=a.querySelector("img"),o=(im||a).getBoundingClientRect(),vw=innerWidth,vh=innerHeight;
 let H=Math.min(vh*.74,640),W=H*320/454;if(W*2>vw*.92){W=vw*.46;H=W*454/320}
 const L=vw/2,T=(vh-H)/2,s=o.width/W;
 fly=document.createElement("div");fly.className="bo-fly";fly.style.cssText=`left:${L}px;top:${T}px;width:${W}px;height:${H}px`;
 fly.innerHTML=`<div class="pg" style="background-image:url('${href}pages/02.jpg')"></div><div class="cv"><img src="${a.dataset.cover}" alt=""><span class="hb-gl" style="transform:none"></span><div class="in"></div></div>`;
 box.appendChild(fly);const cv=fly.querySelector(".cv");
 if(im)im.style.visibility="hidden";
 const a1=fly.animate([{transform:`translate(${o.left-L}px,${o.top-T}px) scale(${s}) perspective(1400px) rotateY(-26deg)`},
   {transform:"translate(0,0) scale(1) perspective(1400px) rotateY(0deg)"}],{duration:1300,easing:E1,fill:"forwards"});
 a1.finished.then(()=>cv.animate([{transform:"perspective(2200px) rotateY(0deg)"},{transform:"perspective(2200px) rotateY(-12deg)",offset:.12},
   {transform:"perspective(2200px) rotateY(-178deg)"}],{duration:2000,easing:E2,fill:"forwards"}).finished)
 .then(()=>{fr.animate([{opacity:0,transform:"translate(-50%,-50%) scale(.97)"},{opacity:1,transform:"translate(-50%,-50%) scale(1)"}],{duration:700,easing:E1,fill:"forwards"});
   x.animate([{opacity:0},{opacity:1}],{duration:700,fill:"forwards"});
   return fly.animate([{opacity:1},{opacity:0}],{duration:700,fill:"forwards"}).finished})
 .then(()=>{fly.remove();fly=null;if(im)im.style.visibility="";busy=false;x.focus()});}
function close(){if(busy)return;busy=true;const d=still?1:350;
 fr.animate([{opacity:1},{opacity:0}],{duration:d,fill:"forwards"});x.animate([{opacity:1},{opacity:0}],{duration:d,fill:"forwards"});
 bg.animate([{opacity:1},{opacity:0}],{duration:d,fill:"forwards"}).finished.then(()=>{box.classList.remove("on");ifr.src="about:blank";
 fr.getAnimations().forEach(a=>a.cancel());x.getAnimations().forEach(a=>a.cancel());fr.style.opacity="";x.style.opacity="";
 document.documentElement.style.overflow="";busy=false})}
document.addEventListener("click",e=>{const a=e.target.closest&&e.target.closest("a[data-open]");if(a&&!e.metaKey&&!e.ctrlKey&&!e.shiftKey)open(a,e)});
x.addEventListener("click",close);bg.addEventListener("click",close);
document.addEventListener("keydown",e=>{if(e.key==="Escape"&&box.classList.contains("on"))close()});
addEventListener("message",e=>{if(e.origin!==location.origin)return;if(e.data==="ae-close-book")close();
 if(e.data==="ae-go-buy"){close();setTimeout(()=>{const b=document.getElementById("buy");if(b)b.scrollIntoView({behavior:"smooth"})},400)}});})()</script>"""

FAN_JS = """<script>(()=>{const f=document.currentScript.previousElementSibling;
if(!f||!f.animate||matchMedia("(prefers-reduced-motion: reduce)").matches)return;
const im=[...f.querySelectorAll("img")],R=[-10,-4,0,5,10],S=im.map((e,i)=>({x:e.offsetLeft,y:e.offsetTop,r:R[i]}));
const dx=S[1].x-S[0].x;S.unshift({x:S[0].x-dx*1.1,y:S[0].y+28,r:-17});S.unshift({x:S[0].x-dx*1.3,y:S[0].y+40,r:-25});
f.style.visibility="hidden";const go=()=>{if(go.done)return;go.done=1;f.style.visibility="";im.forEach((e,i)=>{const k=i+2,me=S[k],fr=[];for(let j=0;j<=k;j++){const s=S[j];
fr.push({transform:`translate(${s.x-me.x}px,${s.y-me.y}px) rotate(${s.r}deg)`,opacity:Math.min(1,j/Math.max(1,k-1)),offset:j/k})}
e.animate(fr,{duration:2000+300*k,delay:200+(im.length-1-i)*260,easing:"cubic-bezier(.3,1.18,.45,1)",fill:"backwards"})})};
Promise.all(im.map(e=>e.decode?e.decode().catch(()=>{}):0)).then(go);setTimeout(go,1200)})()</script>"""

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
.page-hero{overflow-x:clip}
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
.bp-stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:16px;margin-top:26px}
.bp-stat{background:#fff;border-radius:22px;padding:22px 22px 20px;border:2px solid rgba(26,39,82,.08);box-shadow:0 5px 0 rgba(26,39,82,.06);position:relative;overflow:hidden}
.bp-stat::before{content:"";position:absolute;inset:0 0 auto 0;height:6px;background:var(--c,var(--blue))}
.bp-stat .big{font-family:'Baloo 2',sans-serif;font-weight:800;font-size:46px;line-height:1;color:var(--c,var(--blue));display:block;margin:6px 0 10px}
.bp-stat b{display:block;font-family:'Baloo 2',sans-serif;font-size:17.5px;color:var(--navy);margin-bottom:6px;line-height:1.35}
.bp-stat p{margin:0;font-size:14.5px;line-height:1.8;color:var(--text-body)}
.bp-stat .big span{display:inline-block;font-variant-numeric:tabular-nums}
.bp-anim .bp-stat{opacity:0;transform:translateY(28px) scale(.97)}
.bp-anim .bp-stat.go{opacity:1;transform:none;transition:opacity .6s ease,transform .7s cubic-bezier(.2,.9,.25,1)}
.bp-anim .bp-stat::before{transform:scaleX(0);transform-origin:left}
.bp-anim .bp-stat.go::before{transform:scaleX(1);transition:transform 1s cubic-bezier(.3,.8,.3,1) .35s}
.bp-anim .pop{opacity:0;transform:scale(.3) rotate(-14deg)}
.bp-anim .go .pop{opacity:1;transform:none;transition:opacity .4s ease .45s,transform .8s cubic-bezier(.3,1.7,.5,1) .45s}
@media (min-width:761px){.bp-anim .bp-stat.go:nth-child(2){transition-delay:.15s}.bp-anim .bp-stat.go:nth-child(3){transition-delay:.3s}.bp-anim .bp-stat.go:nth-child(4){transition-delay:.45s}}
@media (prefers-reduced-motion:reduce){.bp-anim .bp-stat,.bp-anim .bp-stat::before,.bp-anim .pop{opacity:1!important;transform:none!important;transition:none!important}}
@media (max-width:760px){.bp-stat .big{font-size:40px}}
.bp-stage .bp-tag{align-self:flex-start;font-size:12.5px;font-weight:800;border-radius:999px;padding:3px 11px;margin-bottom:10px;background:#E8F7FF;color:#066d9e}
.bp-stage blockquote{margin:12px 0;padding:12px 14px;border-left:4px solid var(--yellow);background:#FFFBEF;border-radius:0 12px 12px 0;font-family:'Andika','Baloo 2',sans-serif;font-size:16px;line-height:1.6;color:var(--navy)}
.bp-stage .bp-small{font-size:14px;color:#64748b;margin-top:auto;padding-top:10px}
.bp-lv{background:#fff;border:2px solid rgba(26,39,82,.08);border-radius:16px;margin-top:10px;overflow:hidden}
.bp-lv summary{list-style:none;cursor:pointer;display:grid;grid-template-columns:70px 132px 1fr auto;gap:14px;align-items:center;padding:12px 16px}
.bp-lv summary::-webkit-details-marker{display:none}
.bp-lv .bp-l{font-family:'Baloo 2',sans-serif;font-weight:800;font-size:15px;color:var(--navy);line-height:1.2}
.bp-lv .bp-l small{display:block;font-weight:700;font-size:12px;color:#64748b}
.bp-lv .bp-cov{display:flex}
.bp-lv .bp-cov img{width:42px;height:auto;border-radius:4px;border:2px solid #fff;box-shadow:0 3px 8px rgba(26,39,82,.16);margin-left:-8px}
.bp-lv .bp-cov img:first-child{margin-left:0}
.bp-lv .bp-t{font-size:15px;line-height:1.55;color:var(--text-body)}
.bp-lv .bp-t i{font-style:normal;color:var(--navy);font-weight:700}
.bp-lv .bp-w{font-size:13px;color:#64748b;text-align:right;white-space:nowrap}
.bp-lv .bp-w b{display:block;font-size:15px;color:var(--navy)}
.bp-lv[open] summary{border-bottom:1px solid rgba(26,39,82,.08)}
.bp-lv .bp-in{padding:16px;display:grid;grid-template-columns:1.2fr 1fr;gap:18px;align-items:start}
.bp-lv .bp-in img{width:100%;height:auto;border-radius:10px;box-shadow:0 4px 14px rgba(26,39,82,.12)}
.bp-lv .bp-in h4{margin:0 0 6px;font-size:14.5px;color:var(--navy)}
.bp-lv .bp-in ul{margin:0 0 12px;padding-left:18px;font-size:15px;line-height:1.7;color:var(--text-body)}
.bp-lv .bp-in .btn{margin-top:4px}
@media (max-width:720px){.bp-lv summary{grid-template-columns:56px 1fr auto;gap:10px}.bp-lv .bp-cov{display:none}.bp-lv .bp-in{grid-template-columns:1fr}}
/* the 3 free Level 1 books as hardcovers (Chris 11-11: "resemble hard cover books … pop open slowly") */
.bp-shelf{--bw:clamp(86px,25vw,190px);display:flex;justify-content:center;align-items:flex-start;gap:clamp(14px,5vw,64px);flex-wrap:wrap;margin:40px auto 0;perspective:1400px}
.hb{display:flex;flex-direction:column;align-items:center;gap:14px;width:var(--bw);text-decoration:none;color:var(--navy);text-align:center}
.hb-3d{position:relative;width:var(--bw);aspect-ratio:320/454;transform-style:preserve-3d;transform:rotateY(-26deg);transition:transform .7s cubic-bezier(.2,.8,.2,1)}
.hb:hover .hb-3d,.hb:focus-visible .hb-3d{transform:rotateY(-10deg) translateY(-8px)}
.hb-3d img,.hb-gl{position:absolute;inset:0;width:100%;height:100%;border-radius:2px 7px 7px 2px;transform:translateZ(10px)}
.hb-3d img{object-fit:cover;display:block}
.hb-gl{transform:translateZ(10.5px);pointer-events:none;background:
 linear-gradient(90deg,rgba(0,0,0,.30) 0,rgba(255,255,255,.30) 2.4%,rgba(0,0,0,.24) 4.6%,rgba(255,255,255,.14) 6.2%,rgba(0,0,0,0) 9%),
 linear-gradient(118deg,rgba(255,255,255,0) 38%,rgba(255,255,255,.20) 50%,rgba(255,255,255,0) 62%);box-shadow:inset 0 0 0 1px rgba(0,0,0,.08)}
.hb-3d::before{content:"";position:absolute;top:4px;bottom:4px;left:0;width:18px;
 transform:translateX(calc(var(--bw) - 12px)) rotateY(90deg);background:repeating-linear-gradient(90deg,#fffdf8 0 2px,#e4ddcf 2px 3px)}
.hb-3d::after{content:"";position:absolute;inset:0;border-radius:2px 7px 7px 2px;background:#1A2752;transform:translateZ(-10px);
 box-shadow:-16px 18px 34px rgba(26,39,82,.38)}
.hb b{font-size:15px;line-height:1.3}.hb small{font-size:12.5px;color:#64748b;margin-top:-8px}
@media(max-width:560px){.hb{gap:10px}.hb b{font-size:13px}.hb small{font-size:11px;margin-top:-6px}.hb .hb-go{font-size:12px;padding:5px 10px}}
.hb .hb-go{display:inline-block;white-space:nowrap;background:var(--yellow);color:var(--navy);font-weight:800;font-size:13.5px;border-radius:99px;padding:6px 14px;margin-top:-4px}
.bo{position:fixed;inset:0;z-index:2000;display:none}.bo.on{display:block}
.bo-bg{position:absolute;inset:0;background:rgba(15,23,50,.74);opacity:0}
.bo-frame{position:absolute;left:50%;top:50%;width:min(1120px,96vw);height:min(780px,90vh);transform:translate(-50%,-50%);
 border-radius:16px;overflow:hidden;background:#fff;box-shadow:0 30px 80px rgba(0,0,0,.45);opacity:0}
.bo-frame iframe{display:block;width:100%;height:100%;border:0}
.bo-x{position:absolute;top:max(10px,env(safe-area-inset-top));right:12px;z-index:3;width:44px;height:44px;border-radius:50%;border:0;
 background:#fff;color:var(--navy);font-size:26px;line-height:44px;cursor:pointer;box-shadow:0 4px 14px rgba(0,0,0,.3);opacity:0}
.bo-fly{position:fixed;transform-origin:0 0;transform-style:preserve-3d;pointer-events:none}
.bo-fly .pg{position:absolute;inset:0;border-radius:0 6px 6px 0;background:#fffdf8 center/cover no-repeat;box-shadow:0 22px 50px rgba(0,0,0,.4)}
.bo-fly .cv{position:absolute;inset:0;transform-origin:0 50%;transform-style:preserve-3d}
.bo-fly .cv>*{position:absolute;inset:0;border-radius:2px 7px 7px 2px;backface-visibility:hidden;-webkit-backface-visibility:hidden}
.bo-fly .cv img{width:100%;height:100%;object-fit:cover}
.bo-fly .cv .in{transform:rotateY(180deg);background:linear-gradient(90deg,#efe8da,#fbf8f1 88%,#e6dfd0);border-radius:7px 2px 2px 7px}
.bp-tiers{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin:22px auto 0;max-width:1040px}
@media (max-width:820px){.bp-tiers{grid-template-columns:1fr}}
.bp-tier{background:linear-gradient(135deg,#FFFBEF,#FFF4D6);border:1.5px solid var(--yellow);border-radius:18px;padding:18px;display:flex;flex-direction:column;gap:8px}
.bp-tier.hl{box-shadow:0 0 0 2px var(--yellow),0 10px 30px rgba(255,200,40,.28)}
.bp-tier .bp-tn{font-family:'Baloo 2',sans-serif;font-weight:800;font-size:15px;color:var(--navy)}
.bp-tier .bp-tp{font-family:'Baloo 2',sans-serif;font-weight:800;font-size:30px;color:var(--navy);line-height:1}
.bp-tier .bp-tu{font-size:12.5px;font-weight:700;color:#8a5f00}
.bp-tier .bp-td{font-size:15px;line-height:1.7;color:var(--text-body)}
.bp-tier .bp-pick{display:grid;grid-template-columns:repeat(4,1fr);gap:6px;margin-top:auto;padding-top:4px}
.bp-tier .bp-pick.two{grid-template-columns:1fr}
.bp-tier .btn{margin-top:0;min-height:44px;padding:8px 6px;font-size:14px;width:100%;text-align:center;justify-content:center}
.bp-soon{opacity:.5;cursor:not-allowed;box-shadow:none!important}
.bp-soon-note{text-align:center;margin:16px auto 0;max-width:640px;background:#FFF1F0;border:1.5px solid #FFC9C4;color:#9B2C22;border-radius:12px;padding:10px 14px;font-size:14px;font-weight:700}
.bp-trust{display:flex;flex-wrap:wrap;justify-content:center;gap:7px;margin:18px auto 0;max-width:900px}
.bp-trust span{display:inline-flex;align-items:center;gap:5px;background:#fff;border-radius:100px;padding:6px 12px;font-size:12.5px;font-weight:700;color:var(--navy);box-shadow:0 3px 10px rgba(26,39,82,.10)}
.bp-trust span::before{content:'✓';color:#12873d;font-weight:900}
.bp-sheets{max-width:1000px;margin:10px auto 0;text-align:center;font-size:14px;color:#64748b;line-height:1.8}
.bp-sheets a{color:var(--navy);font-weight:700;white-space:nowrap}
.bp-prom{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px;margin-top:26px;text-align:left}
.bp-pc{background:#fff;border-radius:22px;padding:22px 22px 20px;border:2px solid rgba(26,39,82,.08);box-shadow:0 5px 0 rgba(26,39,82,.06);display:flex;flex-direction:column;gap:8px}
.bp-pc .bp-pk{align-self:flex-start;font-size:13px;font-weight:800;letter-spacing:.5px;border-radius:999px;padding:3px 12px;background:var(--light-blue);color:var(--blue-ink)}
.bp-pc b{font-family:'Baloo 2','Noto Sans TC',sans-serif;font-size:21px;line-height:1.35;color:var(--navy)}
.bp-pc p{margin:0;font-size:15.5px;line-height:1.75;color:var(--text-body)}
.bp-pc.gu{background:#F0FBF4;border-color:#bfe9cf}.bp-pc.gu .bp-pk{background:var(--green);color:var(--navy)}
.bp-pc .btn{margin-top:auto;align-self:flex-start;text-transform:none}
.bp-studies{max-width:860px;margin:22px auto 0;padding:0;list-style:none;display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:10px 16px;text-align:left}
.bp-studies li{background:#fff;border-radius:14px;border:1px solid #e2e8f0;padding:12px 14px;font-size:15px;line-height:1.65;color:var(--text-body)}
.bp-studies a{display:block;font-weight:800;color:var(--blue-ink);text-decoration:none;margin-bottom:2px}
.bp-studies a:hover{text-decoration:underline}
.bp-gline{max-width:760px;margin:12px auto 0;text-align:center;font-size:15px;font-weight:700;color:var(--green-ink)}
.bp-gline a{color:inherit}
.bp-fine{max-width:760px;margin:16px auto 0;font-size:14.5px;line-height:1.8;color:#64748b;text-align:center}
.bp-safe{max-width:1040px;margin:22px auto 0;background:#fff;border:1.5px solid rgba(26,39,82,.12);border-radius:20px;padding:20px 22px;box-shadow:0 6px 22px rgba(26,39,82,.07)}
.bp-line{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:12px 18px;background:#F1FBF4;border:1.5px solid rgba(6,199,85,.28);border-radius:14px;padding:14px 16px}
.bp-line p{margin:0;flex:1 1 300px;font-size:15px;line-height:1.75;color:#374151}
.bp-line p b{color:var(--navy)}
.bp-line .btn{flex:0 0 auto;min-height:44px}
.bp-safe-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px 28px;margin-top:18px}
@media (max-width:760px){.bp-safe{padding:16px 14px}.bp-safe-grid{grid-template-columns:1fr}}
.bp-safe h3{margin:0 0 8px;font-size:16.5px;color:var(--navy)}
.bp-safe ul{margin:0;padding:0;list-style:none;display:flex;flex-direction:column;gap:8px}
.bp-safe li{position:relative;padding-left:22px;font-size:15px;line-height:1.75;color:#374151}
.bp-safe li::before{content:'✓';position:absolute;left:0;top:0;color:#12873d;font-weight:900}
.bp-safe li a{color:var(--navy);font-weight:700}
.bp-fields{margin-top:16px;border-top:1px solid rgba(26,39,82,.10);padding-top:12px}
.bp-fields summary{cursor:pointer;font-weight:800;color:var(--navy);font-size:14.5px;min-height:44px;display:flex;align-items:center;gap:8px;list-style:none}
.bp-fields summary::-webkit-details-marker{display:none}
.bp-fields summary::before{content:'＋';display:inline-flex;align-items:center;justify-content:center;width:24px;height:24px;border-radius:50%;background:#EAF6FF;color:var(--navy);font-weight:900;font-size:14px}
.bp-fields[open] summary::before{content:'－'}
.bp-fields table{width:100%;border-collapse:collapse;margin-top:6px;font-size:14px}
.bp-fields th,.bp-fields td{text-align:left;padding:9px 10px;border-bottom:1px solid rgba(26,39,82,.08);vertical-align:top;line-height:1.6}
.bp-fields th{width:40%;font-family:Inter,system-ui,sans-serif;font-weight:700;color:var(--navy);white-space:normal}
.bp-steps{counter-reset:s;list-style:none;padding:0;margin:22px auto 0;max-width:720px}
.bp-steps li{counter-increment:s;position:relative;padding:0 0 16px 46px;font-size:15.5px;line-height:1.8;color:var(--text-body)}
.bp-steps li::before{content:counter(s);position:absolute;left:0;top:1px;width:30px;height:30px;border-radius:10px;background:var(--blue);color:#fff;font-family:'Baloo 2',sans-serif;font-weight:800;font-size:14px;display:grid;place-items:center}
.bp-steps b{color:var(--navy)}
.bp-h1s{display:block;font-family:'DM Sans','Noto Sans TC',sans-serif;font-style:normal;font-weight:700;font-size:.34em;letter-spacing:.02em;color:var(--blue);margin-top:12px;line-height:1.5}
.bp-loop{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-top:24px}
@media (max-width:760px){.bp-loop{grid-template-columns:1fr}}
.bp-loop>div{background:#fff;border:2px solid rgba(26,39,82,.08);border-radius:18px;padding:20px 22px;box-shadow:0 4px 0 rgba(26,39,82,.05)}
.bp-loop .k{display:inline-grid;place-items:center;width:38px;height:38px;border-radius:12px;background:var(--c);color:#fff;font:800 19px 'Baloo 2',sans-serif;margin-bottom:10px}
.bp-loop b{display:block;font-size:19px;color:var(--navy)}
.bp-loop b small{font:700 11.5px 'DM Sans',sans-serif;color:#64748b;margin-left:8px;letter-spacing:.08em}
.bp-loop p{margin:8px 0 0;font-size:14.5px;line-height:1.75;color:var(--text-body)}
.bp-stair{display:grid;grid-template-columns:repeat(12,1fr);gap:6px;align-items:end;height:230px;margin:44px auto 0;max-width:820px;padding-top:22px}
.bp-stair div{display:flex;flex-direction:column;justify-content:flex-end;align-items:center;height:var(--h);min-height:36px;border-radius:10px 10px 4px 4px;background:var(--c);color:#fff;font:800 16px 'Baloo 2',sans-serif;padding-bottom:6px;position:relative}
.bp-stair div small{position:absolute;top:-20px;left:50%;transform:translateX(-50%);font:700 11.5px 'DM Sans',sans-serif;color:var(--navy);white-space:nowrap}
.bp-stair div i{position:absolute;bottom:-24px;left:50%;transform:translateX(-50%);font:800 11.5px 'Noto Sans TC',sans-serif;font-style:normal;color:#06893f;white-space:nowrap}
@media (max-width:640px){.bp-stair{gap:4px;height:190px}.bp-stair div{font-size:13px;border-radius:7px 7px 3px 3px}.bp-stair div:not(.mk) small{display:none}}
.bp-stair-key{display:flex;flex-wrap:wrap;gap:6px 18px;justify-content:center;margin:40px auto 0;font-size:13px;font-weight:700;color:var(--navy)}
.bp-stair-key span::before{content:"";display:inline-block;width:11px;height:11px;border-radius:3px;background:var(--c);margin-right:6px;vertical-align:-1px}
.fp-stage{background:#fff;border-radius:24px;padding:20px 22px 24px;margin-top:22px;box-shadow:0 8px 28px rgba(26,39,82,.07);border-top:6px solid var(--sc)}
.fp-elementary{--sc:#12B76A}.fp-junior{--sc:#1CB0F6}.fp-senior{--sc:#7C5CFF}
.fp-stage h3{margin:0 0 16px;font-size:18px;color:var(--navy);display:flex;align-items:center;gap:10px}
.fp-stage h3::before{content:"";width:10px;height:10px;border-radius:50%;background:var(--sc)}
.fp-row{display:flex;flex-wrap:wrap;justify-content:center;gap:22px 18px}
.fp{width:calc((100% - 90px) / 6);display:flex;flex-direction:column;align-items:center;gap:10px;text-decoration:none;color:var(--navy)}
.fp-pg{position:relative;display:block;width:100%;aspect-ratio:400/566;transition:transform .35s cubic-bezier(.2,.8,.2,1)}
.fp-pg::before,.fp-pg::after{content:"";position:absolute;inset:0;background:#fff;border-radius:6px;box-shadow:0 2px 8px rgba(26,39,82,.12);transition:transform .35s cubic-bezier(.2,.8,.2,1)}
.fp-pg::before{transform:rotate(-3deg) translate(-3px,3px)}.fp-pg::after{transform:rotate(2deg) translate(3px,2px)}
.fp-pg img{position:relative;z-index:1;display:block;width:100%;height:100%;border-radius:6px;box-shadow:0 6px 16px rgba(26,39,82,.18);background:#fff}
.fp-dl{position:absolute;z-index:2;left:50%;bottom:-11px;transform:translateX(-50%);white-space:nowrap;background:var(--sc);color:#fff;font-size:12.5px;font-weight:800;border-radius:99px;padding:4px 11px;box-shadow:0 4px 10px rgba(26,39,82,.2)}
.fp b{margin-top:8px;font-size:15px;text-align:center;line-height:1.3}
.fp:hover .fp-pg,.fp:focus-visible .fp-pg{transform:translateY(-6px)}
.fp:hover .fp-pg::before{transform:rotate(-7deg) translate(-8px,4px)}.fp:hover .fp-pg::after{transform:rotate(6deg) translate(8px,3px)}
@media(max-width:860px){.fp{width:calc((100% - 36px) / 3)}}
@media(max-width:420px){.fp-stage{padding:16px 14px 20px}.fp-row{gap:18px 12px}.fp{width:calc((100% - 24px) / 3)}.fp-dl{font-size:11px;padding:3px 8px}.fp b{font-size:13.5px}}
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

USD_RATE = 32.9     # NT$ per US$, the rate Lemon Squeezy applied on 2026-11-11 (NT$590 → US$17.93); only for the "約 US$" example
BSB = "https://bsb.kh.edu.tw/"                                  # 直轄市及各縣市短期補習班資訊管理系統: the public 立案 lookup
MAPS = "https://maps.app.goo.gl/hLChkEqAMKCsMWpm6"

def pay_safe(kind, price, waiver=False):
    """Under the price cards (2026-11-11): the LINE-order route (bank transfer) and who the buyer is paying.
    GA4 30 days: 21 people opened a checkout, 5 paid; the Lemon Squeezy form is English, charges in US dollars
    and has no LINE Pay / ATM, so the page says so up front and gives facts a parent can check."""
    usd = round(price / USD_RATE)
    line = (f'<div class="bp-line"><p>{Z("<b>不方便線上刷卡？</b>按「用 LINE 訂購（可轉帳）」，我們在 LINE 上回你轉帳帳號，收到款項後直接把下載連結傳給你。", "<b>Not comfortable paying by card online?</b> Tap “Order on LINE (bank transfer)”. We reply on LINE with the account to transfer to, and send you the download link once the payment arrives.")}</p>'
            f'<a class="btn btn-outline" href="{LINE}" target="_blank" rel="noopener" data-book="{kind}" data-book-item="line-order">{Z("用 LINE 訂購（可轉帳）", "Order on LINE (bank transfer)")}</a></div>')
    who = [Z(f"私立埃森美語文理短期補習班，新北市政府立案：社補教社字第115026號。可以到政府的<a href='{BSB}' target='_blank' rel='noopener'>短期補習班資訊管理系統</a>查。", "私立埃森美語文理短期補習班 (the school's registered name), registered with the New Taipei City Government: 社補教社字第115026號. You can look it up on the government's cram-school information system (link)."),
           Z("統一編號 61476523。", "Tax ID (統一編號) 61476523."),
           Z(f"教室在新北市板橋區中正路89巷4號1樓，<a href='{MAPS}' target='_blank' rel='noopener'>Google 地圖</a>上看得到位置和家長評價。", "The classroom is at 1F, No. 4, Lane 89, Zhongzheng Rd., Banqiao, New Taipei; Google Maps (link) shows the location and parents' reviews."),
           Z(f"有問題找得到人：電話 0928-067-772，或 <a href='{LINE}' target='_blank' rel='noopener'>LINE</a>。", "You can reach a person: phone 0928-067-772, or LINE (link).")]
    pay = [Z("刷卡由 Lemon Squeezy 處理，它是美國金流公司 Stripe 旗下的服務。卡號直接交給它加密處理，我們看不到你的卡號。", "Card payments are handled by Lemon Squeezy, a service owned by the US payments company Stripe. Your card number goes straight to it, encrypted; we never see it."),
           Z("付款頁是英文的，下面有每一格的中文說明。", "The payment page is in English; a Chinese guide to each field is below."),
           Z(f"畫面上寫新台幣，實際以美元扣款（例如 NT${price} 約 US${usd}，依當天匯率）。信用卡帳單上會是美元金額和英文的商店名稱，多數銀行會另收約 1.5% 的國外交易手續費。", f"The page shows NT dollars, but the card is charged in US dollars (e.g. NT${price} is about US${usd}, at the day's rate). Your card statement will show a US-dollar amount and an English merchant name, and most banks add a foreign-transaction fee of about 1.5%."),
           Z("付款完成，下載連結立刻寄到你填的 email。沒收到先看垃圾信匣，再 LINE 我們。", "Once you pay, the download link is emailed right away to the address you entered. If it doesn't arrive, check your spam folder, then message us on LINE.")]
    if waiver:
        # The exam-pack pages had no word on the 7-day cancellation right (audit 11-17: 2 of 144 selling pages).
        # Same sentence as the readers and grammar pages, which carry it in their own fine print.
        pay.append(Z("這是數位內容，付款後立刻提供下載；依《通訊交易解除權合理例外情事適用準則》第 2 條第 5 款，按下購買即表示你同意不適用七天解除權。",
                     "This is digital content delivered right after payment; under Article 2(5) of the rules on exceptions to the 7-day cancellation right, clicking buy means you agree the 7-day cancellation right does not apply."))
    fields = [("Email", Z("收下載連結的信箱，請確認沒有打錯", "the mailbox that receives the download link; check for typos")),
              ("Card number", Z("信用卡卡號（Visa、Mastercard、JCB、美國運通）", "card number (Visa, Mastercard, JCB, American Express)")),
              ("Expiration date", Z("卡片有效期限：月／年", "card expiry: month / year")),
              ("Security code", Z("卡片背面的 3 碼（美國運通是正面 4 碼）", "the 3 digits on the back of the card (4 on the front for American Express)")),
              ("Cardholder name", Z("持卡人姓名，照卡片上的英文拼", "cardholder name, spelled as on the card")),
              ("Billing address", Z("國家已經幫你選好 Taiwan，下面一格填郵遞區號", "the country is already set to Taiwan; put your postal code in the box below it")),
              ("Tax ID number (optional)", Z("公司統編，個人購買不用填", "company tax ID; leave blank for a personal purchase")),
              ("Pay with PayPal", Z("有 PayPal 帳戶的話，也可以改用 PayPal 付款", "if you have a PayPal account you can pay with PayPal instead")),
              ("Pay NT$…", Z("確認金額後按下去，就完成付款", "check the amount, then press to pay"))]
    rows = "".join(f'<tr><th lang="en">{esc(a)}</th><td>{b}</td></tr>' for a, b in fields)
    return (f'<div class="bp-safe" id="pay-safe">{line}<div class="bp-safe-grid">'
            f'<div><h3 id="你是向誰買">{Z("你是向誰買", "who you are buying from")}</h3><ul>{"".join(f"<li>{x}</li>" for x in who)}</ul></div>'
            f'<div><h3 id="線上刷卡會看到什麼">{Z("線上刷卡會看到什麼", "what you will see when you pay by card")}</h3><ul>{"".join(f"<li>{x}</li>" for x in pay)}</ul></div></div>'
            f'<details class="bp-fields"><summary>{Z("英文付款頁每一格怎麼填", "how to fill in each box on the English payment page")}</summary>'
            f'<table><tbody>{rows}</tbody></table></details></div>')

PAY_QA = ("付款安全嗎？付款頁為什麼是英文的？", "Is paying safe? Why is the payment page in English?",
          "刷卡由美國金流公司 Stripe 旗下的 Lemon Squeezy 處理，卡號加密後直接交給它，我們看不到。這家公司的付款頁沒有繁體中文，所以是英文的，頁面最下面有每一格的中文說明；實際以美元扣款，帳單上會是美元金額。不想線上刷卡，可以按「用 LINE 訂購（可轉帳）」。我們是新北市政府立案的補習班（社補教社字第115026號），教室在板橋中正路。",
          "Card payments are handled by Lemon Squeezy, owned by the US payments company Stripe; your card number goes to it encrypted and we never see it. Its payment page has no Traditional Chinese, so it is in English, and there is a Chinese guide to each field at the bottom of the page; the charge is in US dollars, so your statement shows a US-dollar amount. If you would rather not pay by card online, tap “Order on LINE (bank transfer)”. We are a cram school registered with the New Taipei City Government (社補教社字第115026號), with a classroom on Zhongzheng Road in Banqiao.")

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

# The buy strip (11-15, Chris: book pages "should look like" the GEPT one, "towards the top like the GEPT. those get
# the most attention", "super simple"): one line, the options as radio rows, LINE 購買 / 線上刷卡. The detail (which
# level, which stage) is picked on the checkout page, which lists every variant. Uses the site-wide .pkm styles.
def ls_url(u):
    return u + ("&" if "?" in u else "?") + "checkout[billing_address][country]=TW" if u else ""

def buy_strip(kind, product_zh, text, opts, under=""):
    """opts: (item, label, price, checkout url); the first is pre-picked. Returns the whole <section id="buy">."""
    def line(label, price):
        return "https://line.me/R/oaMessage/%40americanenglish/?" + urllib.parse.quote(f"我想購買{product_zh}：{strip(label)}（NT${n(price)}）。")
    chips = "".join(f'<label class="pkm-tier"><input type="radio" name="bs-{kind}"{" checked" if i == 0 else ""} data-item="{k}" data-price="{pr}" '
                    f'data-line="{esc(line(lab, pr))}" data-ls="{esc(ls_url(u))}"><span>{lab}</span><b>NT${n(pr)}</b></label>' for i, (k, lab, pr, u) in enumerate(opts))
    k0, lab0, pr0, u0 = opts[0]
    return f"""<section class="pkm-sec" id="buy">
  <div class="wrap">
    <aside class="pkm" id="buy-box">
      <p class="pkm-t">{text}</p>
      <div class="pkm-tiers" role="radiogroup" aria-label="{Z("選方案", "choose")}">{chips}</div>
      <p class="pkm-a"><a href="{esc(line(lab0, pr0))}" target="_blank" rel="noopener" class="pkm-line" data-book="{kind}" data-book-item="line-{k0}" data-book-price="{pr0}">{Z("LINE 購買", "buy on LINE")}</a><a href="{esc(ls_url(u0))}" class="pkm-card" data-book="{kind}" data-book-item="{k0}" data-book-price="{pr0}">{Z("線上刷卡", "pay by card")}</a></p>
    </aside>{under}
  </div>
</section>
<script>(()=>{{const b=document.getElementById("buy-box");if(!b)return;const l=b.querySelector(".pkm-line"),c=b.querySelector(".pkm-card");
b.querySelectorAll(".pkm-tier input").forEach(r=>r.addEventListener("change",function(){{const d=this.dataset;l.href=d.line;c.href=d.ls;
l.dataset.bookItem="line-"+d.item;c.dataset.bookItem=d.item;l.dataset.bookPrice=c.dataset.bookPrice=d.price;
if(typeof window.gtag==="function")gtag("event","book_pick",{{product:"{kind}",item:d.item,page_path:location.pathname}})}}))}})()</script>
"""


def readers_page():
    _page[0] = READERS
    books = {b["code"]: b for b in R["books"]}
    cum = R["moe_words_by_level"]
    lv_new = [cum[0]] + [cum[i] - cum[i - 1] for i in range(1, 12)]
    words = lambda L: [books[f"{L}{x}"]["words"] for x in "abc"]
    any_link = any(STORE["readers_sets"].values()) or any(STORE["readers_levels"].values())
    # 11-27 (Chris: "market this like hooked on phonics. like this will teach your kid to read"): the page leads with
    # what the series is FOR (teaching a child to read English), sold as a 12-level program with one routine and a free
    # first level. It says what the program does and how; it promises no result or timetable. The 12-month refund is the back-stop.
    title = Z("教孩子讀英文：Chris and Cora 分級讀本，第 1 級免費｜埃森美語",
              "Teach your child to read English: Chris and Cora graded readers, Level 1 free | American English")
    desc = Z(f"教孩子自己讀英文的 12 級分級讀本：36 本，先聽、跟著讀、再自己讀，每天 10–15 分鐘。"
             f"故事在台灣，用到教育部 1,200 字表的 {n(cum[-1])} 個字，第 1 級 3 本免費線上讀。",
             f"A 12-level graded reader series that teaches a child to read English on their own: 36 books, each one listen, read along, "
             f"then read alone; 10–15 minutes a day suggested. Stories set in Taiwan, using {n(cum[-1])} of the words on the MOE 1,200 list; Level 1 (3 books) is free to read online.")
    og_t = Z("教孩子自己讀英文：Chris and Cora 分級讀本，12 級 36 本，第 1 級免費", "Teach your child to read English: Chris and Cora graded readers, 12 levels, 36 books, Level 1 free")
    ld = [{"@context": "https://schema.org", "@type": "Product", "@id": f"{ORIGIN}/chris-and-cora-readers/#product", "url": f"{ORIGIN}/chris-and-cora-readers/", "name": "Chris and Cora 英語分級讀本（12 級 36 冊）",
           "description": strip(desc), "brand": {"@type": "Brand", "name": "埃森美語 American English"},
           "image": [f"{ORIGIN}/assets/img/readers/covers/{c}.webp" for c in ("1a", "6a", "12a")],
           **({"offers": {"@type": "AggregateOffer", "priceCurrency": "TWD", "lowPrice": P_LEVEL, "highPrice": P_ALL,
                          "offerCount": 15, "availability": "https://schema.org/InStock", "url": f"{ORIGIN}/{READERS}/#buy", "seller": {"@id": ORIGIN + "/#organization"}}} if any_link else {})}]
    out = [head(READERS, title, desc, og_t, desc, "/assets/img/readers/og-all-36.jpg", 1600, 1200,
                Z("Chris and Cora 英語分級讀本 36 本封面", "the 36 Chris and Cora covers"), ld, LEMON if any_link else "")]

    # hero
    fan = "".join(f'<img src="/assets/img/readers/covers/{c}.webp" alt="{esc(books[c]["title"])} 封面" width="320" height="454" '
                  f'{FP if i == 2 else ""} decoding="async">'
                  for i, c in enumerate(("1a", "3a", "6a", "9b", "12a")))
    out.append(f"""<section class="page-hero">
  <div class="wrap">
    <div class="breadcrumb reveal"><a href="/">首頁</a> ／ {Z("分級讀本", "graded readers")}</div>
    <div class="bp-hero">
      <div>
        <span class="eyebrow eyebrow-yellow reveal">{Z("12 級英文閱讀課程", "a 12-level English reading program")}</span>
        <h1 class="reveal d1">{Z("教孩子<em style='white-space:nowrap'>自己讀英文</em>", "teach your child to read English on their own")}<span class="bp-h1s">Chris and Cora {Z("英語分級讀本・12 級 36 本", "English graded readers · 12 levels, 36 books")}</span></h1>
        <div class="divider reveal d1"></div>
        <p class="body reveal d2">{Z("<strong>從一頁一句開始，一級一級讀到整段故事。</strong>每一本都是同樣三步：先聽、跟著讀、再自己讀，建議每天 10–15 分鐘。36 個故事都發生在台灣；除了角色名字，每個字都是學校會教的（教育部 1,200 字表）。",
            "It starts at one sentence a page and builds, level by level, to full paragraphs. Every book is the same three steps: listen, read along, then read alone; we suggest 10–15 minutes a day. All 36 stories are set in Taiwan; apart from the characters' names, every word is one that school teaches (the Ministry of Education's 1,200-word list).")}</p>
        <div class="bp-cta reveal d2"><a class="btn btn-primary" href="#read-book" data-book="readers" data-book-item="free">{Z("免費開始第 1 級", "start Level 1 free")}</a>
          <a class="btn btn-outline" href="#buy">{Z("看價格", "see prices")}</a></div>
        <div class="bp-facts reveal d2"><span>{Z("每天 10–15 分鐘", "10–15 minutes a day")}</span><span>{Z("會唸給孩子聽", "reads aloud to your child")}</span><span>{Z("12 級 36 本", "12 levels, 36 books")}</span><span>{Z("3 歲起陪讀", "from age 3, read together")}</span></div>
      </div>
      <div class="bp-fan" aria-hidden="true">{fan}</div>{FAN_JS}
    </div>
  </div>
</section>
""")

    # buy strip, under the hero (11-15): single level / one stage / all 36; level and stage are picked at checkout
    out.append(buy_strip("readers", "Chris and Cora 分級讀本",
        Z("想教孩子自己讀英文？<b>Chris and Cora 英語分級讀本</b>，12 級 36 本，每本附 PDF 和會唸給孩子聽的翻頁電子書：",
          "Want to teach your child to read English on their own? <b>Chris and Cora graded readers</b>, 12 levels, 36 books, each with a PDF and a flip book that reads aloud:"),
        [("level", Z("單級 3 本", "one level, 3 books"), P_LEVEL, STORE["readers_levels"].get("2", "")),
         ("set", Z("一個階段 4 級 12 本", "one stage, 4 levels, 12 books"), P_SET, STORE["readers_sets"].get("1-4", "")),
         ("all", Z("全套 12 級 36 本", "all 12 levels, 36 books"), P_ALL, STORE["readers_sets"].get("all", ""))],
        under=f'<p class="bp-gline">{Z("買全套 36 本：讀完覺得孩子沒有進步，12 個月內全額退費。", "Buy all 36: if you finish them and feel your child has not improved, a full refund within 12 months.")}<a href="#our-promise">{Z("看我們的保證 →", "see our promise →")}</a></p>'))

    # how it teaches (11-27): the one routine every book uses, and the 12 levels as a staircase.
    # Listening times are measured: the 1x read-aloud of all 36 flip books (ffprobe, 11-27) runs 74–86 s a book at
    # Level 1, 207–224 s at Level 4 and 776–794 s at Level 12. Bar height rises with the MOE words read in all after that level (16% floor so Level 1 is still a step).
    loop = [("#06C755", "1", Z("先聽", "listen first"), "LISTEN",
             Z("按「▶ 聽故事」。唸到哪個字，哪個字就亮起來；孩子的眼睛跟著字走，聲音和字就對上了。", "Press 'listen to the story'. Each word lights up as it is read; the child's eyes follow the words, so the sound and the spelling meet.")),
            ("var(--blue)", "2", Z("跟著讀", "read along"), "READ ALONG",
             Z("把速度放慢到 0.5 或 0.75 倍，孩子跟著聲音一起唸出來。唸錯沒關係，再聽一次就好。", "Slow it to 0.5x or 0.75x and the child reads aloud with the voice. Mistakes are fine; just listen again.")),
            ("#e0a800", "3", Z("自己讀", "read alone"), "READ ALONE",
             Z("關掉聲音，換孩子讀給你聽。讀完用書後的問題聊一聊，讀順了再換下一本。", "Turn the sound off and the child reads to you. Talk about the questions at the back; once it is smooth, move to the next book."))]
    lc = "".join(f'<div style="--c:{c}"><span class="k">{k}</span><b>{t}<small lang="en">{e}</small></b><p>{p}</p></div>' for c, k, t, e, p in loop)
    stage_c = lambda L: "#06C755" if L <= 4 else ("var(--blue)" if L <= 8 else "var(--navy)")
    stair = "".join(f'<div class="{"mk" if L in (1, 4, 8, 12) else ""}" style="--h:{round(16 + 84 * cum[L-1] / cum[-1])}%;--c:{stage_c(L)}"><small>{n(cum[L-1])}</small>{L}'
                    + (f'<i>{Z("免費", "free")}</i>' if L == 1 else "") + "</div>" for L in range(1, 13))
    out.append(f"""<section class="section" id="how-it-works" style="padding-bottom:20px">
  <div class="wrap">
    {h2(Z("怎麼教", "how it teaches"), "每一本書都是同樣三步", Z("每一本書，<em>都是同樣三步</em>", "every book, the same three steps"), "green")}
    <div class="bp-loop reveal">{lc}</div>
    <p class="body center" style="max-width:66ch;margin:20px auto 0">{Z("第 1 級一本聽完大約 1 分半鐘，第 4 級大約 3 分半鐘，第 12 級大約 13 分鐘（1 倍速，36 本的錄音實際量過）。前 4 級三步加起來大約 5 到 12 分鐘；後面的故事比較長，可以今天聽、明天讀。",
        "Listening to one book takes about a minute and a half at Level 1, about three and a half minutes at Level 4 and about 13 minutes at Level 12 (1x speed, measured on the recordings of all 36 books). For the first 4 levels the three steps together take about 5 to 12 minutes; later stories are longer, so listen one day and read the next.")}</p>
    <div class="bp-stair reveal" role="img" aria-label="{Z(f"12 級階梯圖：讀完第 1 級累積讀過 {cum[0]} 個教育部單字，讀完第 12 級累積 {n(cum[-1])} 個", f"staircase of the 12 levels: {cum[0]} MOE words read after Level 1, {n(cum[-1])} after Level 12")}">{stair}</div>
    <div class="bp-stair-key"><span style="--c:#06C755">{Z("第 1–4 級：剛開始讀", "Levels 1–4: just starting")}</span><span style="--c:var(--blue)">{Z("第 5–8 級：讀得出短句", "Levels 5–8: short sentences")}</span><span style="--c:var(--navy)">{Z("第 9–12 級：讀整段故事", "Levels 9–12: whole paragraphs")}</span></div>
    <p class="body center" style="max-width:66ch;margin:14px auto 0">{Z(f"<b>12 級，每一級只高一點。</b>柱子上的數字，是讀完那一級累積讀過的教育部單字：第 1 級 {cum[0]} 個，第 12 級 {n(cum[-1])} 個。同一級的 3 本用同一批字，孩子不會一下子遇到太多生字。",
        f"<b>12 levels, each only a little higher.</b> The number on each bar is the MOE words read in all by the end of that level: {cum[0]} at Level 1, {n(cum[-1])} at Level 12. The 3 books of a level share the same words, so the child never meets too many new words at once.")}</p>
    <div class="cta-row" style="margin-top:22px"><a class="btn btn-primary" href="#read-book" data-book="readers" data-book-item="free-how">{Z("免費開始第 1 級", "start Level 1 free")}</a></div>
  </div>
</section>
""")

    # why this series (Chris 11-10: simple; every number measured or sourced)
    why4 = [("var(--blue)", f'<span data-to="{cum[-1]}">{n(cum[-1])}</span>', Z("跟學校同一份字表", "the school's word list"),
             Z("除了角色名字，每個字都來自教育部 1,200 字表，跟學校課本同一份。", "Apart from the characters' names, every word is from the MOE 1,200 list, the same list as school textbooks.")),
            ("#06C755", '<span class="pop">⅔</span>', Z("英文書裡三分之二的字", "two-thirds of the words in English books"),
             Z(f"英文書裡約三分之二是最常用的 300 個字，這套書讀過其中 {round(FRY_READ / FRY_LIST * 100)}%。", f"About two-thirds of English reading is the 300 most-used words; the series reads {round(FRY_READ / FRY_LIST * 100)}% of them.")),
            ("#e0a800", '<span data-to="10" data-suf="+">10+</span>', Z("核心字讀 10 次以上", "core words read 10+ times"),
             Z(f"研究說新字要碰到約 10 次才記得住；{CORE} 個核心字有 {CORE_10PLUS} 個讀到 10 次以上。", f"Research says a new word takes about 10 encounters to stick; {CORE_10PLUS} of the {CORE} core words are read 10+ times.")),
            ("#CE82FF", '<span class="pop">' + Z("3 歲", "age 3") + "</span>", Z("3 歲起親子共讀", "read together from age 3"),
             Z("研究發現 2、3 歲就開始陪讀，字彙進步最明顯。", "Research finds reading together from age 2–3 grows vocabulary the most."))]
    sc = "".join(f'<div class="bp-stat" style="--c:{c}"><span class="big">{big}</span><b>{t}</b><p>{p}</p></div>' for c, big, t, p in why4)
    src = " · ".join(['<a href="https://eric.ed.gov/?id=EJ236457" target="_blank" rel="noopener">Fry (1980)</a>',
                      '<a href="https://eric.ed.gov/?id=EJ757328" target="_blank" rel="noopener">Webb (2007)</a>',
                      '<a href="https://eric.ed.gov/?id=EJ787378" target="_blank" rel="noopener">Mol et al. (2008)</a>',
                      '<a href="https://www.naer.edu.tw/PageCourse/projectDetail/RP000000001141" target="_blank" rel="noopener">NAER</a>'])
    out.append(f"""<section class="section" style="padding-bottom:20px">
  <div class="wrap">
    {h2(Z("為什麼選這套", "why this series"), "為什麼選這套", Z("為什麼選<em>這一套</em>", "why this series"), "green")}
    <div class="bp-stats" id="why-stats">{sc}</div>
    <p class="body center" style="max-width:62ch;margin:22px auto 0;font-weight:700;color:var(--navy)">{Z("我們找不到第二套照教育部字表編、故事又在台灣的英文分級讀本。（2026 年 11 月查）", "We could not find a second English graded reader series written to the MOE list with stories set in Taiwan. (checked November 2026)")}</p>
    <p class="bp-fine center" style="margin-top:8px">{Z("來源：", "sources: ")}{src}</p>
  </div>
</section>
<script>(()=>{{const s=document.getElementById("why-stats");if(!s||!("IntersectionObserver" in window))return;
const still=matchMedia("(prefers-reduced-motion: reduce)").matches;s.classList.add("bp-anim");
const io=new IntersectionObserver(es=>es.forEach(e=>{{if(!e.isIntersecting)return;io.unobserve(e.target);e.target.classList.add("go");if(still)return;
e.target.querySelectorAll("[data-to]").forEach(el=>{{const to=+el.dataset.to,suf=el.dataset.suf||"",d=1500,t0=performance.now()+150;
const f=t=>{{const p=Math.max(0,Math.min(1,(t-t0)/d));el.textContent=Math.round(to*(1-Math.pow(1-p,3))).toLocaleString("en-US")+suf;if(p<1)requestAnimationFrame(f)}};
el.textContent="0"+suf;requestAnimationFrame(f)}})}}),{{threshold:.35}});s.querySelectorAll(".bp-stat").forEach(c=>io.observe(c))}})()</script>
""")

    # Said straight (Chris 11-16): the pictures are AI-drawn, the stories and format are written by a US-licensed
    # teacher (his answer when asked) on six published studies, and the full set carries a 12-month money-back promise.
    # Not "scientifically proven": the studies back the methods; nobody has run a trial on these books, and the page says so.
    studies = [("Fry (1980)", "https://eric.ed.gov/?id=EJ236457",
                Z("最常用的 300 個字，約占一般讀物的三分之二。", "The 300 most-used words make up about two-thirds of ordinary reading.")),
               ("Webb (2007)", "https://eric.ed.gov/?id=EJ757328",
                Z("一個新字大約要遇到 10 次，才記得住。", "A new word takes about 10 encounters to stick.")),
               ("Waring & Takaki (2003)", "https://nflrc.hawaii.edu/rfl/item/78",
                Z("只讀一本分級讀本，留得住的新字很少；要大量、重複地讀。", "Very few new words stay after one graded reader; it takes a lot of repeated reading.")),
               ("Mol et al. (2008)", "https://eric.ed.gov/?id=EJ787378",
                Z("爸媽陪讀、邊讀邊聊，幼兒的字彙進步最多，2、3 歲開始最明顯。", "Reading together and talking about the book grows young children's vocabulary the most, clearest from age 2–3.")),
               ("Teng (2018)", "https://research.mpu.edu.mo/en/publications/incidental-vocabulary-acquisition-from-reading-only-and-reading-w/",
                Z("邊聽邊讀，比只用眼睛讀學到更多新字。", "Reading while listening teaches more new words than reading alone.")),
               ("Wei & Hu (2025)", "https://doaj.org/article/8eaac19fcab345dba973e4e94b7c25f8",
                Z("78 位高中生讀了 10 週：邊聽邊讀的一組，字音和字義記得比較好。", "78 senior-high students over 10 weeks: the reading-while-listening group remembered word sounds and meanings better."))]
    st = "".join(f'<li><a href="{u}" target="_blank" rel="noopener" lang="en">{nm}</a>{t}</li>' for nm, u, t in studies)
    out.append(f"""<section class="section bg-soft" id="our-promise">
  <div class="wrap">
    {h2(Z("先說清楚", "said straight"), "圖是-AI-畫的故事是老師寫的", Z("圖是 AI 畫的，<em>故事是老師寫的</em>", "the pictures are AI-drawn; the stories are written by a teacher"), "green")}
    <div class="bp-prom reveal">
      <div class="bp-pc"><span class="bp-pk">{Z("插圖", "pictures")}</span><b>{Z("插圖是 AI 畫的", "The pictures are AI-drawn")}</b>
        <p>{Z("這套書的插圖是用 AI 繪圖工具畫的，這一點我們直接告訴你。", "The pictures in these books were drawn with AI image tools, and we tell you so plainly.")}</p></div>
      <div class="bp-pc"><span class="bp-pk">{Z("故事與編排", "stories and format")}</span><b>{Z("故事由美國合格教師編寫", "The stories are written by a US-licensed teacher")}</b>
        <p>{Z("每一本的故事、用字順序和版面編排，都由持有美國正式教師執照的老師編寫，方法依據下面 6 篇已發表的閱讀與字彙研究。", "The story, the order of the words and the page format of every book are written by a teacher who holds a US teaching licence, using methods from the 6 published reading and vocabulary studies below.")}</p></div>
      <div class="bp-pc gu"><span class="bp-pk">{Z("我們的保證", "our promise")}</span><b>{Z("買全套，讀完沒進步就退費", "Buy the full set: no progress after finishing it, your money back")}</b>
        <p>{Z("買全套 36 本，陪孩子讀完。如果你覺得孩子的英文閱讀沒有進步，購買後 12 個月內用 LINE 告訴我們，全額退費，不需要提出證明。", "Buy all 36 books and read them through with your child. If you feel your child's English reading has not improved, tell us on LINE within 12 months of buying and we refund you in full; no proof needed.")}</p>
        <a class="btn btn-primary" href="#buy" data-book="readers" data-book-item="promise-buy">{Z("看全套 36 本", "see the full set")}</a></div>
    </div>
    <ul class="bp-studies reveal">{st}</ul>
    <p class="bp-fine center" style="margin-top:14px">{Z("這 6 篇研究支持的是這套書用的方法：常用字、重複出現、親子共讀、邊聽邊讀。它們不是拿這套書做的實驗，所以我們用退費保證來負責。", "These 6 studies support the methods the books use: frequent words, repetition, reading together, reading while listening. They were not experiments on these books, which is why we stand behind them with the refund promise.")}</p>
  </div>
</section>
""")

    # Level 1 is free (Chris 11-11: "offer 1a 1b and 1c for free"): three hardcovers; a click swings the cover open into the flip book
    shelf = "".join(
        f'<a class="hb" href="/{READERS}/read/{c}/" data-open="{c}" data-cover="/assets/img/readers/covers/{c}.webp" data-title="{esc(books[c]["title"])}" data-book="readers" data-book-item="free-{c}">'
        f'<span class="hb-3d"><img src="/assets/img/readers/covers/{c}.webp" alt="{esc(books[c]["title"])} 封面" width="320" height="454" loading="lazy" decoding="async"><span class="hb-gl"></span></span>'
        f'<b lang="en">{esc(books[c]["title"])}</b><small>{Z(f"{c}・{books[c]['words']} 字", f"{c} · {books[c]['words']} words")}</small>'
        f'<span class="hb-go">{Z("▶ 打開來讀", "open and read")}</span></a>' for c in FREE)
    out.append(f"""<section class="section" id="read-book">
  <div class="wrap">
    {h2(Z("免費試讀", "free to read"), "第-1-級-3-本免費讀", Z("第 1 級 3 本，<em>整本免費讀</em>", "Level 1: three books, free in full"))}
    <p class="body center" style="max-width:62ch;margin:14px auto 0">{Z("點一本書打開來讀。按「▶ 聽故事」，唸到的字會亮起來、自動翻頁；速度可以選 0.5～1.25 倍。",
        "Click a book to open it. Press '▶ listen to the story': each word lights up as it is read and the page turns; the speed can be 0.5x to 1.25x.")}</p>
    <div class="bp-shelf reveal">{shelf}</div>
    <p class="body center" style="margin-top:22px">{Z("想知道孩子讀懂多少？<a href='/english-reading-comprehension/'>12 級免費閱讀測驗</a>：讀一段故事，回答幾題，立刻對答案。", "Want to know how much your child understands? 12 free reading tests (link): read a story, answer a few questions, check right away.")}</p>
  </div>
</section>
<div class="bo" id="bookOpen" role="dialog" aria-modal="true" aria-label="{Z("翻頁電子書", "flip book")}"><div class="bo-bg"></div>
<div class="bo-frame"><iframe title="{Z("翻頁電子書", "flip book")}" allow="autoplay; fullscreen"></iframe></div>
<button class="bo-x" type="button" aria-label="{Z("關閉", "close")}">×</button></div>
{OPEN_JS}
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
    <p class="body center" style="max-width:64ch;margin:14px auto 0">{Z("讓孩子讀讀看下面的句子，讀得出來就從那裡開始。", "Have your child read the sentence below; start where they can read it.")}</p>
    <div class="bp-grid reveal">{stc}</div>
  </div>
</section>
""")

    # the 12 levels
    free_links = lambda: ('<div class="cta-row" style="justify-content:flex-start;margin-top:12px">' + "".join(
        f'<a class="btn btn-yellow" href="/{READERS}/read/{c}/" data-open="{c}" data-cover="/assets/img/readers/covers/{c}.webp" data-title="{esc(books[c]["title"])}" data-book="readers" data-book-item="free-{c}">{Z(f"免費讀 {c}", f"read {c} free")}</a>'
        for c in FREE) + "</div>")
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
<div><p style="margin:0 0 10px;font-size:14px;line-height:1.7">{Z(f"這一級教孩子多讀 <b>{lv_new[L-1]}</b> 個學校單字；讀完累積 <b>{n(cum[L-1])}</b> 個。", f"This level teaches your child to read {lv_new[L-1]} more school words; {n(cum[L-1])} in all after it.")}</p>
<p style="margin:0 0 6px;font-size:13.5px;font-weight:800;color:var(--navy)">{Z("讀完問問看（書後的問題）", "talk about it (questions from the back of each book)")}</p>{qs}
{free_links() if L == 1 else buy(STORE["readers_levels"].get(str(L), ""), Z(f"買第 {L} 級・NT${P_LEVEL}", f"buy Level {L} · NT${P_LEVEL}"), "readers", f"level-{L}", P_LEVEL)}</div></div></details>""")
    out.append(f"""<section class="section">
  <div class="wrap" style="max-width:980px">
    {h2(Z("12 級一覽", "all 12 levels"), "12-級36-本一覽", Z("12 級 36 本，<em>每一本都在教孩子讀</em>", "12 levels, 36 books: every one teaches your child to read"))}
    <p class="body center" style="max-width:64ch;margin:14px auto 0">{Z("點開每一級，看內頁和書名。", "Open a level to see a page and the titles.")}</p>
    <div class="reveal" style="margin-top:20px">{"".join(rows)}</div>
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
    {h2(Z("3 歲起親子共讀", "reading together from age 3"), "陪孩子讀不需要英文很好", Z("陪孩子讀，<em>不需要英文很好</em>", "you don't need good English to read with your child"))}
    <ol class="bp-steps reveal">{"".join(f"<li>{s}</li>" for s in steps)}</ol>
    <div class="cta-row" style="margin-top:14px"><a class="btn btn-outline" href="/assets/downloads/{CHART}" data-book="readers" data-book-item="chart">{Z("下載 36 本閱讀進度表（免費 PDF）", "download the 36-book reading chart (free PDF)")}</a></div>
    <p class="bp-fine center" style="margin-top:10px">{Z("印出來貼在牆上：讀順一本，讓孩子自己塗一顆星。", "Print it and put it on the wall: each time a book reads smoothly, the child colours in a star.")}</p>
  </div>
</section>
""")

    # fine print (the buy strip itself sits under the hero)
    out.append(f"""<section class="section" style="padding:6px 0 0">
  <div class="wrap">
    <p class="bp-fine">{Z("每本書都有 PDF（A5，可以自己印）和翻頁電子書（在電腦上解壓縮後點開 index.html，不用網路也能讀；手機、平板看 PDF 最方便）。翻頁電子書可以邊聽邊讀，唸到的字會亮起來，也可以放慢速度。家庭自用；學校或補習班要全班用，請先 <a href='" + LINE + "' target='_blank' rel='noopener'>LINE 問我們</a>。",
        "Every book comes as a PDF (A5, print it yourself) and a flip book (unzip on a computer and open index.html, no internet needed; on a phone or tablet the PDF is easiest). The flip books read aloud, lighting up each word, and the reading can be slowed down. For family use; for a whole class at a school or cram school, ask us on LINE first.")}<br>
    {Z("這是數位內容，付款後立刻提供下載；依《通訊交易解除權合理例外情事適用準則》第 2 條第 5 款，按下購買即表示你同意不適用七天解除權。請先免費讀第 1 級再決定。",
       "This is digital content delivered right after payment; under Article 2(5) of the rules on exceptions to the 7-day cancellation right, clicking buy means you agree the 7-day cancellation does not apply. Please read Level 1 free before deciding.")}<br>
    {Z("全套 36 本另有我們自己的 12 個月退費保證，和上面的法定規定是兩回事，見<a href='#our-promise'>「我們的保證」</a>。", "The full set of 36 also carries our own 12-month refund promise, which is separate from the legal rule above; see 'our promise'.")}</p>
  </div>
</section>
""")

    # FAQ
    w1 = words(1)
    qa = [(Z("孩子還不會讀英文，可以開始嗎？", "My child cannot read English yet. Can we start?"),
           Z(f"可以，第 1 級就是寫給剛開始讀的孩子。一頁只有一兩句，每本 {min(w1)}–{max(w1)} 字，而且可以先聽再讀。認得字母、學過一點自然發音的孩子可以跟著讀；還不認得字母的孩子，先由大人陪著聽故事、看圖。第 1 級 3 本免費，試了就知道。",
             f"Yes: Level 1 is written for a child who is just starting. One or two sentences a page, {min(w1)}–{max(w1)} words a book, and you can listen before reading. A child who knows the letters and some phonics can read along; one who does not know the letters yet starts by listening and looking at the pictures with an adult. Level 1's 3 books are free, so try and see.")),
          (Z("36 本要讀多久？", "How long do the 36 books take?"),
           Z("照孩子的速度就好。一週讀順一本是 36 週，一週兩本是 18 週。重點是同一本讀到順再換下一本，不是趕進度。",
             "Go at your child's pace. One book a week until it reads smoothly is 36 weeks; two a week is 18 weeks. What matters is reading each book until it is smooth before moving on, not rushing.")),
          (Z("適合幾歲的孩子？", "What age is it for?"),
           Z("看程度，不看年齡。認得字母、學過一點自然發音就可以從第 1 級開始；已經讀得出短句的孩子，從第 5 級開始。最準的方法是讓孩子讀上面「孩子在哪個階段」的句子，或先免費讀第 1 級。",
             "Go by level, not age. A child who knows the letters and some phonics can start at Level 1; one who already reads short sentences, at Level 5. The surest way is the sentences under 'which stage', or the free Level 1.")),
          (Z("有音檔嗎？", "Is there audio?"),
           Z("有。36 本的翻頁電子書都可以按「聽故事」：唸到哪個字、哪個字就亮起來，唸完自動翻頁（目前是 AI 語音）。速度可以選 0.5、0.75、1 或 1.25 倍，每一種速度都是事先做好的錄音，放慢了聲音一樣清楚。在電腦上下載後，不用網路也能聽。PDF 檔本身沒有聲音。",
             "Yes. All 36 flip books have 'listen to the story': each word lights up as it is read and the page turns by itself (an AI voice for now). The speed can be 0.5x, 0.75x, 1x or 1.25x; each speed is a recording made ahead of time, so the voice stays just as clear when slowed down. On a computer it works offline after download. The PDF files themselves have no sound.")),
          (Z("讀完沒有進步，可以退費嗎？", "Can I get a refund if there is no progress?"),
           Z("買全套 36 本可以。陪孩子讀完後，如果你覺得孩子的英文閱讀沒有進步，購買後 12 個月內用 LINE 告訴我們訂購的 email，我們全額退費，不需要提出證明。單級和 4 級一組不在這個保證裡，所以第 1 級 3 本整本免費，請先讀讀看。",
             "Yes, for the full set of 36. After reading them through with your child, if you feel their English reading has not improved, send us your order email on LINE within 12 months of buying and we refund you in full; no proof needed. Single levels and 4-level sets are not covered, which is why Level 1's 3 books are free in full: please try them first.")),
          (Z("插圖和故事是誰做的？", "Who made the pictures and the stories?"),
           Z("插圖是用 AI 繪圖工具畫的。故事、用字順序和版面編排由持有美國正式教師執照的老師編寫，方法依據 6 篇已發表的閱讀與字彙研究，研究清單在這一頁的「先說清楚」。",
             "The pictures were drawn with AI image tools. The stories, the word order and the page format are written by a teacher who holds a US teaching licence, using methods from 6 published reading and vocabulary studies, listed under 'said straight' on this page.")),
          (Z("可以印出來嗎？", "Can I print it?"),
           Z("可以，家裡自己用都沒問題。PDF 是 A5 大小（一般 A4 對折的大小），印在 A4 紙上選「符合頁面」就行。", "Yes, for your own family. The PDF is A5 (half of A4); print on A4 with 'fit to page'.")),
          (Z("怎麼付款、多久拿到？", "How do I pay, and when do I get it?"),
           Z("在這一頁按購買，用信用卡付款（不會跳到別的網站，也不用註冊）。付款完成，下載連結會立刻寄到你填的 email。", "Click buy on this page and pay by card (you stay on this page; no account). When payment goes through, the download link goes straight to the email you entered.")),
          (Z(PAY_QA[0], PAY_QA[1]), Z(PAY_QA[2], PAY_QA[3])),
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
      <h2 id="先讀第-1-級" style="margin-top:14px">{Z("先讀第 1 級，<em>再決定</em>", "read Level 1, then decide")}</h2>
      <p class="body" style="max-width:560px;margin:16px auto 0">{Z("第 1 級的 3 本（<i lang='en'>This Is Bobo!</i>、<i lang='en'>Bobo Is in the Bed!</i>、<i lang='en'>The Little Red Shop</i>）整本免費，在網站上直接翻頁讀，還可以按「聽故事」邊聽邊讀，唸到的字會亮起來。不用下載也不用留資料。", "The 3 books of Level 1 (This Is Bobo!, Bobo Is in the Bed!, The Little Red Shop) are free in full: turn the pages on the site, or press 'listen to the story' and read along as each word lights up. No download, no sign-up.")}</p>
      <div class="cta-row"><a class="btn btn-primary" href="#read-book" data-book="readers" data-book-item="free">{Z("免費開始第 1 級", "start Level 1 free")}</a>
      <a class="btn btn-outline" href="{LINE}" target="_blank" rel="noopener">{Z("LINE 問我們", "ask us on LINE")}</a></div>
    </div>
  </div>
</section>
""")
    out.append(FOOT)
    return "".join(out)

# ---------------------------------------------------------------- the free 1a flip book

CHART = "ae-chris-and-cora-reading-chart-a4.pdf"

def reading_chart():
    """Free A4 progress chart (11-27): the 36 covers in 12 rows, a star to colour under each. No Chinese beyond labels a child sees."""
    try:
        from weasyprint import HTML
        from PIL import Image
    except Exception as e:
        print("  reading chart skipped:", str(e)[:80]); return
    import tempfile
    fonts = os.path.expanduser("~/Documents/GitHub/ae-readers/tools/fonts")
    tmp = tempfile.mkdtemp()
    def cov(c):
        j = os.path.join(tmp, c + ".jpg")
        im = Image.open(os.path.join(SITE, "assets", "img", "readers", "covers", c + ".webp")).convert("RGB"); im.thumbnail((240, 340)); im.save(j, quality=80)
        return "file://" + j
    col = lambda L: "#06C755" if L <= 4 else ("#0B6FB8" if L <= 8 else "#1A2752")
    star = '<svg viewBox="0 0 24 24" width="8mm" height="8mm"><path d="M12 2.6l2.9 5.9 6.5.9-4.7 4.6 1.1 6.5L12 17.4l-5.8 3.1 1.1-6.5L2.6 9.4l6.5-.9z" fill="none" stroke="#1A2752" stroke-width="1.3" stroke-linejoin="round"/></svg>'
    cell = lambda c: f'<div class="b"><img src="{cov(c)}">{star}</div>'
    block = lambda L: f'<div class="lv"><span class="n" style="background:{col(L)}">{L}</span>{"".join(cell(f"{L}{x}") for x in "abc")}</div>'
    doc = f"""<html><head><meta charset="utf-8"><style>
@font-face{{font-family:TC;src:url(file://{fonts}/NotoSansTC-Regular.ttf)}}@font-face{{font-family:TC;font-weight:700;src:url(file://{fonts}/NotoSansTC-Bold.ttf)}}
@font-face{{font-family:DM;src:url(file://{fonts}/DMSans-Regular.ttf)}}@font-face{{font-family:DM;font-weight:700;src:url(file://{fonts}/DMSans-Bold.ttf)}}
@page{{size:A4;margin:11mm 12mm 12mm;@bottom-center{{content:"埃森美語 American English ・ americanenglish.com.tw/chris-and-cora-readers/";font:8pt TC;color:#64748b}}}}
body{{font:10pt/1.4 DM,TC;color:#1A2752;margin:0}}h1{{font:700 22pt DM,TC;margin:0}}h1 small{{font:700 12pt TC;color:#0B6FB8;margin-left:3mm}}
.top{{display:flex;justify-content:space-between;align-items:flex-end;border-bottom:1.5pt solid #FFC828;padding-bottom:2mm}}.nm{{font:11pt TC}}.nm i{{display:inline-block;width:52mm;border-bottom:.8pt solid #1A2752;margin-left:2mm}}
.how{{font:9.5pt/1.5 TC;color:#475569;margin:2.5mm 0 3mm}}
.g{{display:grid;grid-template-columns:1fr 1fr;gap:2.2mm 6mm}}
.lv{{display:flex;align-items:center;gap:2mm;border:.8pt solid #dbe3ee;border-radius:3mm;padding:2mm 2.4mm}}
.n{{flex:none;width:10mm;height:10mm;border-radius:3mm;color:#fff;font:700 15pt DM;display:flex;align-items:center;justify-content:center}}
.b{{flex:1;text-align:center}}.b img{{height:22.5mm;border-radius:1.2mm;display:block;margin:0 auto 1mm}}
</style></head><body>
<div class="top"><h1>My Reading Chart<small>我的英文閱讀進度表</small></h1><span class="nm">Name 名字<i></i></span></div>
<p class="how">Chris and Cora 分級讀本，教孩子自己讀英文・12 級 36 本。每一本：先聽 Listen → 跟著讀 Read along → 自己讀 Read alone。讀順了，就把書下面的星星塗上顏色。</p>
<div class="g">{"".join(block(L) for L in range(1, 13))}</div>
</body></html>"""
    out = os.path.join(SITE, "assets", "downloads", CHART)
    HTML(string=doc).write_pdf(out)
    print(f"  wrote assets/downloads/{CHART} ({os.path.getsize(out) // 1024} KB)")

def free_reader():
    for i, c in enumerate(FREE):
        free_book(c, FREE[i + 1] if i + 1 < len(FREE) else None)

def free_book(code, nxt):
    src = os.path.join(FLIP_SRC, code)
    dst = os.path.join(SITE, READERS, "read", code)
    if not os.path.exists(src):
        print("  flip book source missing, kept what is on the site:", src)
        return
    os.makedirs(dst, exist_ok=True)
    shutil.copytree(os.path.join(src, "pages"), os.path.join(dst, "pages"), dirs_exist_ok=True)
    # read-along (ae-readers tools/readalong.py): the same audio and timings as the paid flip books
    if os.path.exists(os.path.join(src, "readalong.json")):
        shutil.copytree(os.path.join(src, "audio"), os.path.join(dst, "audio"), dirs_exist_ok=True)
        shutil.copy2(os.path.join(src, "readalong.json"), os.path.join(dst, "readalong.json"))
    os.makedirs(os.path.join(SITE, READERS, "read", "lib"), exist_ok=True)
    for f in os.listdir(os.path.join(FLIP_SRC, "lib")):
        shutil.copy2(os.path.join(FLIP_SRC, "lib", f), os.path.join(SITE, READERS, "read", "lib", f))
    t = open(os.path.join(src, "index.html"), encoding="utf-8").read()
    t = t.replace('<html lang="en">', '<html lang="zh-Hant-TW">')
    nx = (f'<a class="nx" href="/{READERS}/read/{nxt}/" data-book="readers" data-book-item="next-{nxt}">下一本 &#8250;</a>' if nxt else
          f'<a class="nx" href="/{READERS}/#buy" data-book="readers" data-book-item="after-free">第 2 級以後 &#8250;</a>')
    old = t[t.index('<span class="lvl">'):t.index("</header>")]
    t = t.replace(old, old + nx, 1)
    t = t.replace('href="../index.html" title="All books">&#8249; Books</a>',
                  f'href="/{READERS}/" title="全部 36 本" data-book="readers" data-book-item="from-free">&#8249; 全部 36 本</a>')
    ga = ("<meta name='robots' content='noindex,follow'>\n"
          f"<link rel='canonical' href='{ORIGIN}/{READERS}/read/{code}/'>\n"
          # GA4 itself comes from seo_build's AE:GTM block (this page is SELF_CONTAINED, which still gets it)
          "<script>document.addEventListener('click',function(e){var a=e.target.closest&&e.target.closest('a[data-book]');"
          "if(a&&typeof window.gtag==='function')gtag('event','book_tap',{product:'readers',item:a.getAttribute('data-book-item'),page_path:location.pathname,link_text:'page'});});</script>\n")
    # inside the readers page's pop-up (?in=1): 全部 36 本 closes the pop-up, 第 2 級以後 leaves it; 下一本 stays inside
    ga += ("<script>if(window.self!==window.top)document.addEventListener('DOMContentLoaded',function(){"
           "document.documentElement.classList.add('embed');"
           "document.querySelectorAll('header a').forEach(function(a){if(a.classList.contains('nx')){if(a.href.indexOf('#buy')<0){a.href+='?in=1';return}}"
           "a.addEventListener('click',function(e){e.preventDefault();window.top.postMessage(a.classList.contains('nx')?'ae-go-buy':'ae-close-book',location.origin)})});});</script>\n")
    # opened from the readers page's hardcover (?o=1): the cover has just swung open, so start on the first spread
    ga += ("<script>if(/[?&]o=1/.test(location.search))addEventListener('load',function(){setTimeout(function(){"
           "try{pf.turnToPage(1)}catch(e){}},60)});</script>\n")
    t = t.replace("<title>", ga + "<title>", 1)
    t = t.replace("</style>", "header .nx{background:#FFC828;color:#1A2752;opacity:1;font-weight:700;font-size:14px;border-radius:99px;padding:4px 12px;white-space:nowrap}"
                  "header .nx:hover{background:#ffd75e}@media(max-width:600px){.embed header{padding-right:58px}.embed header h1{font-size:0}}\n</style>", 1)
    # the page-flip wrapper grows past #book and covered the footer: its buttons took no mouse clicks
    if "z-index:10" not in t:   # fixed in ae-readers flipbook.py 11-09; kept for older viewers
        t = t.replace("</style>", "header,footer{position:relative;z-index:10}\n</style>", 1)
    t = readalong(t, dst)
    open(os.path.join(dst, "index.html"), "w", encoding="utf-8").write(t)
    print("  free reader:", os.path.relpath(dst, SITE), len(os.listdir(os.path.join(dst, "pages"))), "pages")

# The read-along player (2026-11-09, Chris: "AI voice for now"): tools/build_readalong.py makes
# readalong.json (audio per story page + a timed box per printed word); this adds a 聽故事 button that
# reads each page aloud, lights up each word as it is spoken and turns the page by itself.
RA_CSS = """
.page{position:relative}
.hlw{position:absolute;border-radius:5px;background:rgba(255,200,40,.55);mix-blend-mode:multiply;opacity:0;
  transition:opacity .08s;pointer-events:none;transform:scale(1.12,1.18)}
.hlw.on{opacity:1}
#ra{background:#FFC828;color:#1A2752;font-weight:700;font-size:15px;white-space:nowrap}#ra:hover{background:#ffd75e}
#ra.on{background:#fff}
"""
RA_JS = """<script>
(function(){
const RA=__RA__, P=RA.pages, pgs=document.querySelectorAll('#book .page'), btn=document.getElementById('ra');
const boxes={};
Object.keys(P).forEach(function(p){const host=pgs[p-1];if(!host)return;boxes[p]=P[p].words.map(function(w){
  const d=document.createElement('div');d.className='hlw';
  d.style.cssText='left:'+w[2]+'%;top:'+w[3]+'%;width:'+w[4]+'%;height:'+w[5]+'%';host.appendChild(d);return d;});});
const order=Object.keys(P).map(Number).sort(function(a,b){return a-b;});
const audio=new Audio();audio.preload='auto';
let on=false,cur=null,raf=0,timer=0,sent=false;
function clear(){document.querySelectorAll('.hlw.on').forEach(function(e){e.classList.remove('on');});}
function spread(){const i=pf.getCurrentPageIndex();return [i+1,i+2];}
function textHere(){const s=spread();for(const p of s)if(P[p])return p;return null;}
function later(){const s=spread();return order.find(function(p){return p>s[1];});}
function tick(){const d=P[cur];if(!d)return;const t=audio.currentTime,w=d.words,b=boxes[cur];
  for(let k=0;k<w.length;k++){const end=k<w.length-1?w[k+1][0]:w[k][1]+.35;b[k].classList.toggle('on',t>=w[k][0]-.02&&t<end);}
  if(!audio.paused)raf=requestAnimationFrame(tick);}
function play(){clearTimeout(timer);const p=textHere();
  if(!p){const nx=later();if(nx){pf.turnToPage(nx-1);timer=setTimeout(play,900);}else stop();return;}
  cur=p;audio.src=P[p].audio;audio.currentTime=0;
  audio.play().then(function(){cancelAnimationFrame(raf);tick();}).catch(stop);}
function stop(){on=false;audio.pause();clearTimeout(timer);clear();btn.classList.remove('on');btn.textContent='▶ 聽故事';}
audio.onended=function(){setTimeout(clear,350);if(!on)return;
  timer=setTimeout(function(){if(!on)return;if(later())pf.flipNext();else stop();},1100);};
pf.on('flip',function(){audio.pause();clear();clearTimeout(timer);if(on)timer=setTimeout(play,800);});
btn.onclick=function(){if(on){stop();return;}on=true;btn.classList.add('on');btn.textContent='❚❚ 暫停';play();
  if(!sent&&typeof window.gtag==='function'){sent=true;gtag('event','book_tap',{product:'readers',item:'readalong-play',page_path:location.pathname,link_text:'play'});}};
})();
</script>"""

def readalong(t, dst):
    f = os.path.join(dst, "readalong.json")
    if 'id="ra"' in t:        # the flip book already carries the player (ae-readers flipbook.py, 11-09)
        _page[0] = READERS
        Z("聽故事", "listen to the story"); Z("暫停", "pause")
        if 'id="spd"' in t:   # 4-speed picker (ae-readers flipbook.py + speeds.py, 11-10)
            lab = Z("播放速度", "reading speed")
            t = t.replace('title="Reading speed" aria-label="Reading speed"', f'title="{lab}" aria-label="{lab}"', 1)
        return t
    if not os.path.exists(f):
        return t
    ra = json.load(open(f, encoding="utf-8"))
    _page[0] = READERS
    t = t.replace("</style>", RA_CSS + "</style>", 1)
    t = t.replace('<footer><button id="prev"', f'<footer><button id="ra" title="{Z("播放朗讀：每個字唸到時會亮起來，唸完自動翻頁", "play: each word lights up as it is read, then the page turns")}">▶ {Z("聽故事", "listen to the story")}</button><button id="prev"', 1)
    js = RA_JS.replace("__RA__", json.dumps({"pages": ra["pages"]}, separators=(",", ":")))
    t = t.replace("</body>", js + "\n</body>", 1)
    return t

# ---------------------------------------------------------------- grammar page

STAGES = [("elementary", ["G3", "G4", "G5", "G6"]), ("junior", ["G7-1", "G7-2", "G8-1", "G8-2", "G9-1", "G9-2"]),
          ("senior", ["G10-1", "G10-2", "G11-1", "G11-2", "G12-1", "G12-R"])]

# Chris 11-12: page 1 (the one-page summary of the whole semester) was free for all 16 books, so the
# samples together summarised the whole series. Now: one sample per GRADE (the first-semester book), and
# the sample is page 3, the first grammar point in full, not the summary.
SAMPLES = ["G3", "G4", "G5", "G6", "G7-1", "G8-1", "G9-1", "G10-1", "G11-1", "G12-1"]
SAMPLE_PAGE = 3

def free_pdfs():
    """Page 3 of each sample book's cheat sheet -> /assets/downloads/, plus its 400 px picture."""
    import subprocess, tempfile
    from PIL import Image
    got = {}
    for c in SAMPLES:
        stem = f"{c}-pattern-cards" if c in ("G3", "G4", "G5", "G6") else f"{c}-grammar-cheatsheet"
        src = os.path.join(BOOK_PDF_SRC, f"{stem}.pdf")
        name = f"ae-grammar-{c.lower()}-sample.pdf"
        dst = os.path.join(SITE, "assets", "downloads", name)
        img = os.path.join(SITE, "assets", "img", "grammar-books", "free", f"{c}-sample.webp")
        if os.path.exists(src) and not os.path.exists(dst):   # once: check_pdfs.py --fix repairs the site copy in place
            subprocess.run(["pdfseparate", "-f", str(SAMPLE_PAGE), "-l", str(SAMPLE_PAGE), src, dst], check=True)
        if os.path.exists(src) and not os.path.exists(img):
            with tempfile.TemporaryDirectory() as t:
                subprocess.run(["pdftoppm", "-png", "-r", "110", "-f", str(SAMPLE_PAGE), "-l", str(SAMPLE_PAGE),
                                "-singlefile", src, os.path.join(t, "p")], check=True)
                Image.open(os.path.join(t, "p.png")).convert("RGB").resize((400, 566), Image.LANCZOS).save(img, "WEBP", quality=82)
        if os.path.exists(dst):
            got[c] = f"/assets/downloads/{name}"
    return got

def grammar_page():
    _page[0] = GRAMMAR
    B = {b["code"]: b for b in G}
    free = free_pdfs()
    any_link = any(STORE["grammar"].values())
    title = Z("英文文法書＋速查表：國小到高中每學期一本，每年級一頁免費試讀｜埃森美語",
              "English grammar books + cheat sheets: one book per semester for elementary, junior and senior high, a free sample page for every grade | American English")
    desc = Z("國小句型書 4 冊、國中文法書 6 冊（康軒、翰林、南一適用）、高中 6 冊（含學測總複習）。"
             "每個重點一頁規則圖解，附練習、測驗、解答、速查表，每年級一頁免費試讀。",
             "4 elementary sentence-pattern books, 6 junior-high grammar books (for the 康軒, 翰林, 南一 textbooks), 6 senior-high books (incl. a 學測 review). "
             "One page of rules and pictures per point, with practice, tests, answers and a cheat sheet; a free sample page for every grade.")
    og_t = Z("英文文法書＋速查表：國小到高中每學期一本", "grammar books + cheat sheets, one per semester")
    ld = [{"@context": "https://schema.org", "@type": "Product", "@id": f"{ORIGIN}/english-grammar-books/#product", "url": f"{ORIGIN}/english-grammar-books/", "name": "英文文法書・文法速查表（國小・國中・高中）",
           "description": strip(desc), "brand": {"@type": "Brand", "name": "埃森美語 American English"},
           "image": [f"{ORIGIN}/assets/img/grammar-books/covers/{c}.webp" for c in ("G3", "G8-1", "G10-1")],
           **({"offers": {"@type": "AggregateOffer", "priceCurrency": "TWD", "lowPrice": P_GSHEETS, "highPrice": P_GALL,
                          "offerCount": sum(1 for v in STORE["grammar"].values() if v), "availability": "https://schema.org/InStock", "url": f"{ORIGIN}/{GRAMMAR}/", "seller": {"@id": ORIGIN + "/#organization"}}} if any_link else {})}]
    out = [head(GRAMMAR, title, desc, og_t, desc, "/assets/img/grammar-books/og-grammar-books.jpg", 1600, 1200,
                Z("英文文法書與文法速查表封面", "covers of the grammar books and cheat sheets"), ld, LEMON if any_link else "")]
    # hero fan (Chris 11-10): one page-1 overview at the back, the rest illustrated inside pages
    fan_imgs = [("covers/G8-1", 300, 424), ("pages/elementary-pattern-page", 778, 1100), ("pages/junior-grammar-page", 778, 1100),
                ("pages/senior-grammar-page", 778, 1100), ("pages/junior-exam-page", 778, 1100)]
    fan = "".join(f'<img src="/assets/img/grammar-books/{src}.webp" alt="" width="{w}" height="{h}" '
                  f'{FP if i == 2 else ""} decoding="async">'
                  for i, (src, w, h) in enumerate(fan_imgs))
    out.append(f"""<section class="page-hero">
  <div class="wrap">
    <div class="breadcrumb reveal"><a href="/">首頁</a> ／ <a href="/junior-high-english-grammar/">{Z("國中英文文法", "junior-high grammar")}</a> ／ {Z("文法書", "grammar books")}</div>
    <div class="bp-hero">
      <div>
        <span class="eyebrow eyebrow-yellow reveal">{Z("埃森美語原創 · 國小到高中 16 冊", "our own series · 16 books, elementary to senior high")}</span>
        <h1 class="reveal d1">{Z("英文文法書＋<em>文法速查表</em>", "grammar books + cheat sheets")}</h1>
        <div class="divider reveal d1"></div>
        <p class="body reveal d2">{Z("孩子英文課到底在學什麼，常常搞不清楚嗎？這套書照孩子學校的課綱和課本整理成一本一本：國小每年級一本，國中、高中每學期一本，每本附速查表和解答。",
            "Ever struggled to work out what your child is actually learning in English class? These books turn your child's school curriculum and textbooks into one simple book per grade (elementary) or per semester (junior and senior high), each with a cheat sheet and answers.")}</p>
        <p class="reveal d2" style="margin:10px 0 0;font-size:15px;font-weight:700"><a href="/banqiao-school-english/">{Z("先看孩子學校用哪個版本、每次段考考哪幾課 →", "first see which edition your child's school uses and what each exam covers →")}</a></p>
        <div class="bp-cta reveal d2"><a class="btn btn-primary" href="#free">{Z("免費試讀頁", "free sample page")}</a>
          <a class="btn btn-outline" href="#buy">{Z("看價格", "see prices")}</a></div>
        <div class="bp-facts reveal d2"><span>{Z("每學期一本", "one per semester")}</span><span>{Z("附解答", "answers included")}</span><span>{Z("可以列印", "printable")}</span><span>{Z("每冊附速查表", "cheat sheet with every book")}</span></div>
      </div>
      <div class="bp-fan" aria-hidden="true">{fan}</div>{FAN_JS}
    </div>
  </div>
</section>
""")
    out.append(buy_strip("grammar", "英文文法書",
        Z("想把整學期的文法一次整理好？<b>埃森美語原創英文文法書</b>，每冊附速查表與完整解答：",
          "Want a whole term's grammar in one place? <b>Our own English grammar books</b>, each with its cheat sheet and full answers:"),
        [("books", Z("一個學程（國小、國中或高中）", "one stage (elementary, junior or senior high)"), P_GBOOKS, STORE["grammar"].get("junior-books", "")),
         ("all-books", Z("全套 16 冊", "all 16 books"), P_GALL, STORE["grammar"].get("all-books", ""))],
        under=f'<p class="bp-sheets">{Z("只要速查表、不要文法書？", "Cheat sheets only, no books?")}<a href="{esc(ls_url(STORE["grammar"].get("junior-sheets", "")))}" data-book="grammar" data-book-item="sheets" data-book-price="{P_GSHEETS}">{Z(f"速查表 NT${P_GSHEETS} 起 →", f"cheat sheets from NT${P_GSHEETS} →")}</a></p>'))
    # the three stages
    info = {"elementary": (Z("國小 句型書 4 冊", "elementary: 4 sentence-pattern books"), Z("三～六年級，每年級一冊", "Grades 3–6, one per grade"),
                           Z("不講文法規則，一頁一個句型，附句型速查卡。",
                             "No grammar rules: one sentence pattern a page, with pattern cards.")),
            "junior": (Z("國中 文法書 6 冊", "junior high: 6 grammar books"), Z("國一上～國三下，每學期一冊", "Grade 7 to Grade 9, one per semester"),
                       Z("對照康軒、翰林、南一，照學校三次段考出測驗。", "Mapped to 康軒, 翰林 and 南一, with tests for the school's three exams.")),
            "senior": (Z("高中 文法書 6 冊", "senior high: 6 grammar books"), Z("高一上～高三上＋學測總複習", "Grade 10 to Grade 12 first semester + a 學測 review"),
                       Z("適用龍騰、三民、遠東，最後一冊是學測總複習。", "Fits 龍騰, 三民 and 遠東; the last book is the 學測 review."))}
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
             ("junior-exam-range-page", Z("段考範圍表", "exam-range page"), Z("康軒、翰林、南一每次段考要讀哪幾頁，一張表看完", "which pages to study before each exam for 康軒, 翰林 or 南一, on one table")),
             ("junior-exam-page", Z("段考模擬測驗", "school-exam practice test"), Z("兩頁 100 分，照學校三次段考的範圍出題", "two pages, 100 points, following the school's three exams")),
             ("senior-grammar-page", Z("高中文法頁", "senior-high grammar page"), Z("一樣的版面，題目加上中譯英和綜合測驗", "same layout, with translation and cloze")),
             ("cheatsheet-page1", Z("文法速查表第 1 頁", "cheat sheet page 1"), Z("整學期的重點一頁看完", "the whole semester on one page"))]
    figs = "".join(f'<figure><img src="/assets/img/grammar-books/pages/{f}.webp" alt="{esc(strip(t))}" width="778" height="1100" loading="lazy" decoding="async">'
                   f'<figcaption><b>{t}</b>{d}</figcaption></figure>' for f, t, d in pages)
    out.append(f"""<section class="section bg-soft">
  <div class="wrap">
    {h2(Z("內頁", "inside"), "一本裡面有什麼", Z("一本裡面，<em>有什麼</em>", "what is inside a book"), "green")}
    <p class="body center" style="max-width:62ch;margin:14px auto 0">{Z("真正的內頁，左右滑動看。", "Real pages; swipe to see them.")}</p>
    <div class="bp-scroll tall reveal">{figs}</div>
    <p class="bp-hint">{Z("← 左右滑動 →", "← swipe →")}</p>
  </div>
</section>
""")
    # free samples: one per grade (Chris 11-12), each a picture of its real page 3
    def short(c):
        return esc(B[c]["title"].split(" ")[0].replace("國小", ""))
    fl = []
    for key, codes in STAGES:
        links = "".join(
            f'<a class="fp" href="{free[c]}" download data-book="grammar" data-book-item="sample-{c}">'
            f'<span class="fp-pg"><img src="/assets/img/grammar-books/free/{c}-sample.webp" alt="{esc(B[c]["title"])} 試讀頁" width="400" height="566" loading="lazy" decoding="async">'
            f'<span class="fp-dl">{Z("免費下載", "free")} ↓</span></span><b>{short(c)}</b></a>'
            for c in codes if c in free)
        fl.append(f'<div class="fp-stage fp-{key}"><h3 id="{strip(info[key][0])}免費">{info[key][0]}</h3><div class="fp-row">{links}</div></div>')
    out.append(f"""<section class="section bg-soft" id="free">
  <div class="wrap" style="max-width:1080px">
    {h2(Z("免費", "free"), "每個年級一頁免費試讀", Z("每個年級一頁，<em>免費試讀</em>", "one free sample page for every grade"), "green")}
    <p class="body center" style="max-width:62ch;margin:14px auto 0">{Z("每個年級第一個重點的完整一頁：規則、圖解、例句和練習，先看看版面和難度合不合用。不用留資料。", "The first grammar point of each grade, in full: rules, pictures, examples and practice, so you can see the layout and level first. No sign-up.")}</p>
    <div class="reveal">{"".join(fl)}</div>
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
            items.append(f'<details class="bp-book" id="{c}"><summary>{esc(b["title"])}<small>{Z(f"{np_} 個重點・6 個單元", f"{np_} points, 6 units")}</small></summary><ol>{pts}</ol></details>')
        sec.append(f'<h3 id="{strip(name)}目錄" style="margin:24px 0 6px;font-size:18px">{name}</h3>' + "".join(items))
    out.append(f"""<section class="section">
  <div class="wrap" style="max-width:860px">
    {h2(Z("目錄", "contents"), "每一冊教什麼", Z("每一冊，<em>教什麼</em>", "what each book teaches"))}
    <p class="body center" style="max-width:62ch;margin:14px auto 0">{Z("點開每一冊，看完整的文法重點。", "Open a book to see its full list of grammar points.")}</p>
    <div class="reveal">{"".join(sec)}</div>
  </div>
</section>
""")
    # fine print (the buy strip itself sits under the hero)
    out.append(f"""<section class="section" style="padding:6px 0 0">
  <div class="wrap">
    <p class="bp-fine">{Z("家庭自用，可以自己印。學校或補習班要全班用，請先 <a href='" + LINE + "' target='_blank' rel='noopener'>LINE 問我們</a>。", "For family use; print it yourself. For a whole class, ask us on LINE first.")}<br>
    {Z("這是數位內容，付款後立刻提供下載；依《通訊交易解除權合理例外情事適用準則》第 2 條第 5 款，按下購買即表示你同意不適用七天解除權。請先下載免費的第 1 頁再決定。",
       "This is digital content delivered right after payment; under Article 2(5) of the rules on exceptions to the 7-day cancellation right, clicking buy means you agree the 7-day cancellation does not apply. Please download the free page 1 before deciding.")}</p>
  </div>
</section>
""")
    qa = [(Z("適用哪一個版本的課本？", "Which textbook edition does it fit?"),
           Z("國中三個版本都適用：每一冊的對照表列出康軒、翰林、南一哪一課教這個文法，段考範圍表再告訴你每次段考要讀哪幾頁。高中適用龍騰、三民、遠東，但各版每課教的文法不同，所以依文法主題編排、不列課次。國小依教育部基本學習內容整理。不知道孩子學校用哪個版本？看<a href='/banqiao-school-english/'>板橋國中小英文課程地圖</a>。",
             "Junior high fits all three editions: each book's map shows which lesson of 康軒, 翰林 and 南一 teaches each point, and the exam-range page shows which pages to study before each exam. Senior high fits 龍騰, 三民 and 遠東, but each edition places grammar differently, so the books go by topic with no lesson numbers. Elementary follows the MOE basic learning content. Not sure which edition your child's school uses? See the Banqiao school English curriculum maps.")),
          (Z("國小為什麼不講文法？", "Why no grammar rules for elementary?"),
           Z("國小英語課綱要求避免講解、分析文法，所以國小這 4 冊用「句型」：孩子先會說、會寫整句，國中再學規則。", "The elementary curriculum asks teachers to avoid explaining and analysing grammar, so these 4 books teach sentence patterns: children say and write whole sentences first and learn the rules in junior high.")),
          (Z(PAY_QA[0], PAY_QA[1]), Z(PAY_QA[2], PAY_QA[3])),
          (Z("可以只買一冊嗎？", "Can I buy a single book?"),
           Z(f"目前以學程為單位賣（國小 4 冊、國中 6 冊、高中 6 冊），一套 NT${P_GBOOKS}，國小到高中全套 16 冊 NT${n(P_GALL)}；每個年級都有一頁免費試讀，可以先下載看看。", f"For now they are sold by stage (4 elementary, 6 junior-high, 6 senior-high), NT${P_GBOOKS} a set, or all 16 books for NT${n(P_GALL)}; every grade has a free sample page to try first.")),
          (Z("速查表和文法書差在哪？", "How is the cheat sheet different from the book?"),
           Z("速查表 14–15 頁：每個重點一頁加一頁解答，適合考前複習。文法書 36–38 頁：同樣的重點頁，再加上每單元的綜合練習、寫作應用、測驗（國中是三次段考模擬測驗）和完整解答。", "The cheat sheet is 14–15 pages: one page per point and an answer page, for review before an exam. The book is 36–38 pages: the same point pages plus each unit's practice and writing pages, tests (in junior high, three school-exam practice tests) and a full answer key.")),
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
      <h2 id="先下載試讀頁" style="margin-top:14px">{Z("先下載試讀頁，<em>看看合不合用</em>", "download a sample page first and see if it suits")}</h2>
      <p class="body" style="max-width:560px;margin:16px auto 0">{Z("找到孩子的年級，下載那一頁免費試讀。也可以先看免費的<a href='/junior-high-english-grammar/'>國中英文文法總整理</a>。", "Find your child's grade and download its free sample page. Or start with the free junior-high grammar summary.")}</p>
      <div class="cta-row"><a class="btn btn-primary" href="#free">{Z("免費試讀頁", "free sample page")}</a><a class="btn btn-outline" href="{LINE}" target="_blank" rel="noopener">{Z("LINE 問我們", "ask us on LINE")}</a></div>
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

PAY_SAFE_OUT = os.path.join(SITE, "data", "pay_safe.html")

def write_pay_safe():
    """The trust section for the bottom of every page that sells something (11-15, Chris: "this section should be at
    the bottom of every page we sell something"). tools/seo_build.py places it (AE:PAYSAFE) above </main> on any page
    with a Lemon Squeezy checkout link; __KIND__ becomes readers / grammar / exam-pack."""
    css = "".join(l + "\n" for l in CSS.split("\n") if re.match(r"\.bp-(safe|line|fields)", l) or l.startswith("@media (max-width:760px){.bp-safe"))
    open(PAY_SAFE_OUT, "w", encoding="utf-8").write(
        '<section class="section ps-sec" style="padding-top:28px"><div class="wrap"><style>' + css + "</style>\n"
        + pay_safe("__KIND__", 590, waiver=True) + "</div></section>\n")
    print("  pay-safe block:", os.path.relpath(PAY_SAFE_OUT, SITE))

if __name__ == "__main__":
    write_pay_safe()
    og_images()
    for slug, fn in ((READERS, readers_page), (GRAMMAR, grammar_page)):
        os.makedirs(os.path.join(SITE, slug), exist_ok=True)
        open(os.path.join(SITE, slug, "index.html"), "w", encoding="utf-8").write(fn())
        print("  wrote", f"{slug}/index.html")
    free_reader()
    reading_chart()
    write_gloss()
    links = sum(bool(v) for g in ("readers_sets", "readers_levels", "grammar") for v in STORE[g].values())
    print(f"  checkout links set: {links} of 22 (data/books_store.json); buttons without one say 即將開放")

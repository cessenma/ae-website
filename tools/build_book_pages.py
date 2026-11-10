#!/usr/bin/env python3
"""The school's two book pages, generated from data (2026-11-08, Chris: "a new tab at the top for the
story book collection … the books link present on the 1200 words pages … the grammar stuff can be part
of something else"). Run tools/seo_build.py afterwards (chrome, SEO blocks, sitemap date).

Writes
  chris-and-cora-readers/index.html          the 分級讀本 tab: 36 Chris and Cora readers
  chris-and-cora-readers/read/1a|1b|1c/      the free Level 1 flip books (self-contained, noindex)
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
.bp-tier .bp-td{font-size:13.5px;line-height:1.7;color:var(--text-body)}
.bp-tier .bp-pick{display:grid;grid-template-columns:repeat(4,1fr);gap:6px;margin-top:auto;padding-top:4px}
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
    title = Z("Chris and Cora 英語分級讀本：12 級 36 本，第 1 級 3 本免費讀｜埃森美語",
              "Chris and Cora English graded readers: 12 levels, 36 books, Level 1 (3 books) free | American English")
    desc = Z(f"埃森美語自己寫的英語分級讀本：12 級 36 本，每本 48 頁，左頁文字、右頁整頁插圖，故事在台灣。"
             f"用到教育部 1,200 字表的 {n(cum[-1])} 個字，第 1 級 3 本免費線上讀。",
             f"Graded readers written by American English: 12 levels, 36 books, 48 pages each, words on the left page and a full-page "
             f"picture on the right, stories set in Taiwan. They use {n(cum[-1])} of the words on the MOE 1,200 list; Level 1 (3 books) is free to read online.")
    og_t = Z("Chris and Cora 英語分級讀本：12 級 36 本，第 1 級 3 本免費讀", "Chris and Cora graded readers: 12 levels, 36 books, Level 1 free")
    ld = [{"@context": "https://schema.org", "@type": "Product", "@id": f"{ORIGIN}/chris-and-cora-readers/#product", "url": f"{ORIGIN}/chris-and-cora-readers/", "name": "Chris and Cora 英語分級讀本（12 級 36 冊）",
           "description": strip(desc), "brand": {"@type": "Brand", "name": "埃森美語 American English"},
           "image": [f"{ORIGIN}/assets/img/readers/covers/{c}.webp" for c in ("1a", "6a", "12a")],
           **({"offers": {"@type": "AggregateOffer", "priceCurrency": "TWD", "lowPrice": P_LEVEL, "highPrice": P_ALL,
                          "offerCount": 15, "availability": "https://schema.org/InStock"}} if any_link else {})}]
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
        <span class="eyebrow eyebrow-yellow reveal">{Z("埃森美語原創", "our own series")}</span>
        <h1 class="reveal d1"><span style="white-space:nowrap">Chris and Cora</span> {Z("<em>英語分級讀本</em>", "English graded readers")}</h1>
        <div class="divider reveal d1"></div>
        <p class="body reveal d2">{Z("我們自己寫的 36 本英文故事書，故事發生在台灣，用的是學校的教育部 1,200 字表。",
            "36 English storybooks we wrote ourselves, set in Taiwan, using the school's MOE 1,200-word list.")}</p>
        <div class="bp-cta reveal d2"><a class="btn btn-primary" href="#read-book" data-book="readers" data-book-item="free">{Z("免費讀第 1 級 3 本", "read Level 1 (3 books) free")}</a>
          <a class="btn btn-outline" href="#buy">{Z("看價格", "see prices")}</a></div>
        <div class="bp-facts reveal d2"><span>{Z("PDF＋翻頁電子書", "PDF + flip book")}</span><span>{Z("邊聽邊讀", "reads aloud")}</span><span>{Z("12 級 36 本", "12 levels, 36 books")}</span><span>{Z("3 歲起陪讀", "from age 3, read together")}</span></div>
      </div>
      <div class="bp-fan" aria-hidden="true">{fan}</div>{FAN_JS}
    </div>
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
    src = " · ".join(['<a href="https://eric.ed.gov/?id=ED169516" target="_blank" rel="noopener">Fry (1980)</a>',
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
<div><p style="margin:0 0 10px;font-size:14px;line-height:1.7">{Z(f"這一級新讀到的教育部字：<b>{lv_new[L-1]}</b> 個；讀完累積 <b>{n(cum[L-1])}</b> 個。", f"MOE words first read in this level: {lv_new[L-1]}; {n(cum[L-1])} in all after it.")}</p>
<p style="margin:0 0 6px;font-size:13.5px;font-weight:800;color:var(--navy)">{Z("讀完問問看（書後的問題）", "talk about it (questions from the back of each book)")}</p>{qs}
{free_links() if L == 1 else buy(STORE["readers_levels"].get(str(L), ""), Z(f"買第 {L} 級・NT${P_LEVEL}", f"buy Level {L} · NT${P_LEVEL}"), "readers", f"level-{L}", P_LEVEL)}</div></div></details>""")
    out.append(f"""<section class="section">
  <div class="wrap" style="max-width:980px">
    {h2(Z("12 級一覽", "all 12 levels"), "12-級36-本一覽", Z("12 級 36 本，<em>一覽</em>", "the 12 levels and 36 books"))}
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
  </div>
</section>
""")

    # prices
    lv_btns = "".join(buy(STORE["readers_levels"].get(str(L), ""), Z(f"第 {L} 級", f"Level {L}"), "readers", f"level-{L}", P_LEVEL,
                          "btn btn-outline") for L in range(2, 13))
    set_btns = "".join(buy(STORE["readers_sets"].get(k, ""), Z(f"第 {k.replace('-', '–')} 級", f"Levels {k}"), "readers", f"set-{k}", P_SET)
                       for k in ("1-4", "5-8", "9-12"))
    tiers = f"""<div class="bp-tiers reveal" id="buy-tiers">
<div class="bp-tier"><span class="bp-tn">{Z("單級 3 本", "one level, 3 books")}</span><span class="bp-tp">NT${P_LEVEL}</span><span class="bp-tu">{Z(f"約 NT${round(P_LEVEL/3)}／本", f"about NT${round(P_LEVEL/3)} a book")}</span>
<span class="bp-td">{Z(f"先買孩子現在這一級試試看。第 1 級免費線上讀。每級約 {MB_LEVEL}。", f"Try the level your child is at now. Level 1 is free online. About {MB_LEVEL} a level.")}</span><div class="bp-pick">{lv_btns}</div></div>
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
    <p class="bp-fine">{Z("每本書都有 PDF（A5，可以自己印）和翻頁電子書（在電腦上解壓縮後點開 index.html，不用網路也能讀；手機、平板看 PDF 最方便）。翻頁電子書可以邊聽邊讀，唸到的字會亮起來，也可以放慢速度。家庭自用；學校或補習班要全班用，請先 <a href='" + LINE + "' target='_blank' rel='noopener'>LINE 問我們</a>。",
        "Every book comes as a PDF (A5, print it yourself) and a flip book (unzip on a computer and open index.html, no internet needed; on a phone or tablet the PDF is easiest). The flip books read aloud, lighting up each word, and the reading can be slowed down. For family use; for a whole class at a school or cram school, ask us on LINE first.")}<br>
    {Z("這是數位內容，付款後立刻提供下載；依《通訊交易解除權合理例外情事適用準則》第 2 條第 5 款，按下購買即表示你同意不適用七天解除權。請先免費讀第 1 級再決定。",
       "This is digital content delivered right after payment; under Article 2(5) of the rules on exceptions to the 7-day cancellation right, clicking buy means you agree the 7-day cancellation does not apply. Please read Level 1 free before deciding.")}</p>
  </div>
</section>
""")

    # FAQ
    qa = [(Z("適合幾歲的孩子？", "What age is it for?"),
           Z("看程度，不看年齡。認得字母、學過一點自然發音就可以從第 1 級開始；已經讀得出短句的孩子，從第 5 級開始。最準的方法是讓孩子讀上面「孩子在哪個階段」的句子，或先免費讀第 1 級。",
             "Go by level, not age. A child who knows the letters and some phonics can start at Level 1; one who already reads short sentences, at Level 5. The surest way is the sentences under 'which stage', or the free Level 1.")),
          (Z("有音檔嗎？", "Is there audio?"),
           Z("有。36 本的翻頁電子書都可以按「聽故事」：唸到哪個字、哪個字就亮起來，唸完自動翻頁（目前是 AI 語音）。速度可以選 0.5、0.75、1 或 1.25 倍，每一種速度都是事先做好的錄音，放慢了聲音一樣清楚。在電腦上下載後，不用網路也能聽。PDF 檔本身沒有聲音。",
             "Yes. All 36 flip books have 'listen to the story': each word lights up as it is read and the page turns by itself (an AI voice for now). The speed can be 0.5x, 0.75x, 1x or 1.25x; each speed is a recording made ahead of time, so the voice stays just as clear when slowed down. On a computer it works offline after download. The PDF files themselves have no sound.")),
          (Z("可以印出來嗎？", "Can I print it?"),
           Z("可以，家裡自己用都沒問題。PDF 是 A5 大小（一般 A4 對折的大小），印在 A4 紙上選「符合頁面」就行。", "Yes, for your own family. The PDF is A5 (half of A4); print on A4 with 'fit to page'.")),
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
      <h2 id="先讀第-1-級" style="margin-top:14px">{Z("先讀第 1 級，<em>再決定</em>", "read Level 1, then decide")}</h2>
      <p class="body" style="max-width:560px;margin:16px auto 0">{Z("第 1 級的 3 本（<i lang='en'>This Is Bobo!</i>、<i lang='en'>Bobo Is in the Bed!</i>、<i lang='en'>The Little Red Shop</i>）整本免費，在網站上直接翻頁讀，還可以按「聽故事」邊聽邊讀，唸到的字會亮起來。不用下載也不用留資料。", "The 3 books of Level 1 (This Is Bobo!, Bobo Is in the Bed!, The Little Red Shop) are free in full: turn the pages on the site, or press 'listen to the story' and read along as each word lights up. No download, no sign-up.")}</p>
      <div class="cta-row"><a class="btn btn-primary" href="#read-book" data-book="readers" data-book-item="free">{Z("免費讀第 1 級 3 本", "read Level 1 free")}</a>
      <a class="btn btn-outline" href="{LINE}" target="_blank" rel="noopener">{Z("LINE 問我們", "ask us on LINE")}</a></div>
    </div>
  </div>
</section>
""")
    out.append(FOOT)
    return "".join(out)

# ---------------------------------------------------------------- the free 1a flip book

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
    ld = [{"@context": "https://schema.org", "@type": "Product", "@id": f"{ORIGIN}/english-grammar-books/#product", "url": f"{ORIGIN}/english-grammar-books/", "name": "英文文法書・文法速查表（國小・國中・高中）",
           "description": strip(desc), "brand": {"@type": "Brand", "name": "埃森美語 American English"},
           "image": [f"{ORIGIN}/assets/img/grammar-books/covers/{c}.webp" for c in ("G3", "G8-1", "G10-1")],
           **({"offers": {"@type": "AggregateOffer", "priceCurrency": "TWD", "lowPrice": P_GSHEETS, "highPrice": P_GBOOKS,
                          "offerCount": 6, "availability": "https://schema.org/InStock"}} if any_link else {})}]
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
        <div class="bp-cta reveal d2"><a class="btn btn-primary" href="#free">{Z("免費下載第 1 頁", "free page 1")}</a>
          <a class="btn btn-outline" href="#buy">{Z("看價格", "see prices")}</a></div>
        <div class="bp-facts reveal d2"><span>{Z("每學期一本", "one per semester")}</span><span>{Z("附解答", "answers included")}</span><span>{Z("可以列印", "printable")}</span><span>{Z("每冊附速查表", "cheat sheet with every book")}</span></div>
      </div>
      <div class="bp-fan" aria-hidden="true">{fan}</div>{FAN_JS}
    </div>
  </div>
</section>
""")
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
             ("cheatsheet-page1", Z("文法速查表第 1 頁", "cheat sheet page 1"), Z("整學期的重點一頁看完，這一頁免費", "the whole semester on one page; this page is free"))]
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
    # free page 1
    # Chris 11-11: "these should be more aesthetically pleasing" -> each download is a picture of its real page 1
    def short(c):
        return Z("學測總複習", "exam review") if c == "G12-R" else esc(B[c]["title"].split(" ")[0].replace("國小", ""))
    fl = []
    for key, codes in STAGES:
        links = "".join(
            f'<a class="fp" href="{free[c]}" download data-book="grammar" data-book-item="free-{c}">'
            f'<span class="fp-pg"><img src="/assets/img/grammar-books/free/{c}.webp" alt="{esc(B[c]["title"])} 第 1 頁" width="400" height="566" loading="lazy" decoding="async">'
            f'<span class="fp-dl">{Z("免費下載", "free")} ↓</span></span><b>{short(c)}</b></a>'
            for c in codes if c in free)
        fl.append(f'<div class="fp-stage fp-{key}"><h3 id="{strip(info[key][0])}免費">{info[key][0]}</h3><div class="fp-row">{links}</div></div>')
    out.append(f"""<section class="section bg-soft" id="free">
  <div class="wrap" style="max-width:1080px">
    {h2(Z("免費", "free"), "第-1-頁免費下載", Z("每一冊的第 1 頁，<em>免費下載</em>", "page 1 of every book, free"), "green")}
    <p class="body center" style="max-width:62ch;margin:14px auto 0">{Z("第 1 頁是整學期的重點，一頁看完。不用留資料。", "Page 1 is the whole semester on one page. No sign-up.")}</p>
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
    {soon(any_link)}<div class="bp-trust reveal">{trust}</div>
    <div class="bp-tiers reveal">{"".join(tiers)}</div>
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
          (Z("可以只買一冊嗎？", "Can I buy a single book?"),
           Z("目前以學程為單位賣（國小 4 冊、國中 6 冊、高中 6 冊），一套 NT$590；每一冊的第 1 頁可以先免費下載看看。", "For now they are sold by stage (4 elementary, 6 junior-high, 6 senior-high), NT$590 a set; page 1 of every book is free to try first.")),
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

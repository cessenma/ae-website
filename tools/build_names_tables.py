#!/usr/bin/env python3
"""Full A–Z name tables + picker on /english-names-boys/ and /english-names-girls/.

Why (GSC 2026-09-13): 男生英文名字 gets 1,600 impressions/week at position 4–5 but only
2% CTR — the SERP is a list-size contest (parenting.com.tw "400個＋產生器", sundaykiss
"600+", manmandays "500種以上＋產生器") and our title said "40+ 精選". GA4 adds that the
page is a dead end (the only "next page" after it is itself). The curated 43/45 stay as
the hero of each page; this adds the complete list underneath, a filter/picker, and
tap-to-hear, and retitles the page to say what it now is.

Data: data/english-names-boys.json / -girls.json (n, p=唸法, m=意思, o=來源, s=風格, sy=音節).
The "老師精選" star is read from the page's own curated tables, so the two never drift.

Re-runnable: replaces the <!-- AE:NAMES-TABLE --> block and rewrites title/desc/H1.
Run tools/seo_build.py afterwards.
"""
import datetime, html, json, os, re, sys

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TODAY = datetime.date.today().isoformat()
YEAR = TODAY[:4]

PAGES = {
 "boys": dict(page="english-names-boys", zh="男生", other=("/english-names-girls/", "女生英文名字"),
              anchor="三個<em>經典地雷</em>", picked_label="老師精選"),
 "girls": dict(page="english-names-girls", zh="女生", other=("/english-names-boys/", "男生英文名字"),
               anchor="水果與物品名", picked_label="老師精選"),
}

CSS = """<style>
.nm-tools{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin:18px 0 10px}
.nm-tools input[type=search]{flex:1 1 220px;font:inherit;font-size:16px;padding:10px 14px;border:2px solid rgba(26,39,82,.14);border-radius:12px;background:#fff}
.nm-tools select{font:inherit;font-size:15px;padding:9px 12px;border:2px solid rgba(26,39,82,.14);border-radius:12px;background:#fff}
.nm-tools label.tg{font-size:14.5px;color:#4a5a72;display:flex;gap:6px;align-items:center;cursor:pointer}
.nm-chips{display:flex;flex-wrap:wrap;gap:6px;margin:4px 0 10px}
.nm-chips button{font-family:'Baloo 2',sans-serif;font-weight:800;font-size:14px;color:var(--navy);background:#fff;border:2px solid rgba(26,39,82,.12);border-radius:100px;padding:4px 11px;cursor:pointer}
.nm-chips button.on{background:var(--navy);color:#fff;border-color:var(--navy)}
.nm-chips.styles button.on{background:var(--blue);border-color:var(--blue)}
.nm-bar{display:flex;flex-wrap:wrap;gap:12px;align-items:center;justify-content:space-between;background:#fff;border:2px solid rgba(26,39,82,.08);border-radius:16px;padding:12px 16px;margin:0 0 14px}
.nm-bar b{font-family:'Baloo 2',sans-serif;font-size:20px;color:var(--navy)}
.nm-bar button{font:inherit;font-family:'Baloo 2',sans-serif;font-weight:800;font-size:14px;color:#fff;background:var(--green);border:0;border-radius:99px;padding:8px 16px;cursor:pointer}
.nm-pick{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 14px}
.nm-pick span{font-family:'Baloo 2',sans-serif;font-weight:800;font-size:16px;color:var(--navy);background:var(--light-blue,#e8f6fe);border-radius:12px;padding:8px 14px}
.nm-pick span small{display:block;font-family:'DM Sans','Noto Sans TC',sans-serif;font-weight:500;font-size:12.5px;color:#4a5a72}
.nm-wrap{overflow-x:auto;background:#fff;border:2px solid rgba(26,39,82,.08);border-radius:18px}
table.nm{width:100%;border-collapse:collapse;font-size:15.5px}
table.nm th{position:sticky;top:0;background:var(--navy);color:#fff;font-family:'Baloo 2',sans-serif;font-weight:700;font-size:14px;text-align:left;padding:10px 12px;z-index:1}
table.nm td{padding:8px 12px;border-top:1px solid #eef2f7;vertical-align:top}
table.nm td.n{font-family:'Baloo 2',sans-serif;font-weight:800;font-size:16.5px;color:var(--navy);cursor:pointer;white-space:nowrap}
table.nm td.n:hover{color:var(--blue)}
table.nm td.n::after{content:"🔊";font-size:12px;opacity:.35;margin-left:6px}
table.nm td.n i{font-style:normal;color:var(--yellow-dk,#e0a800);margin-left:4px}
table.nm td.p{color:#4a5a72;white-space:nowrap}
table.nm td.m{color:#333c4d}
table.nm td.o{color:#8a94a3;font-size:13px;white-space:nowrap}
table.nm td.s{font-size:12.5px;color:#8a94a3;white-space:nowrap}
table.nm tr[hidden]{display:none}
.nm-empty{padding:26px;text-align:center;color:#8a94a3}
.nm-note{font-size:13.5px;color:#8a94a3;margin-top:12px;line-height:1.7}
@media print{.nm-tools,.nm-chips,.nm-bar{display:none}table.nm tr[hidden]{display:table-row}}
</style>"""

JS = r"""<script>(function(){
var tb=document.getElementById('nm-body');if(!tb)return;
var rows=[].slice.call(tb.querySelectorAll('tr'));
var q=document.getElementById('nm-q'),sy=document.getElementById('nm-sy'),only=document.getElementById('nm-only'),az=document.getElementById('nm-az'),stc=document.getElementById('nm-styles'),empty=document.getElementById('nm-empty'),shown=document.getElementById('nm-shown'),pick=document.getElementById('nm-pick');
var letter='',styles={};
function norm(s){return (s||'').toLowerCase()}
function visible(){return rows.filter(function(r){return !r.hidden})}
function filt(){var s=norm(q.value).trim(),n=0,want=Object.keys(styles).filter(function(k){return styles[k]});
rows.forEach(function(r){var ok=true;if(letter&&r.dataset.l!==letter)ok=false;
if(ok&&sy.value){var v=+r.dataset.sy;ok=(sy.value==='3')?v>=3:v===+sy.value}
if(ok&&only.checked&&!r.dataset.pick)ok=false;
if(ok&&want.length){var have=r.dataset.s.split('|');ok=want.every(function(w){return have.indexOf(w)>-1})}
if(ok&&s){ok=norm(r.dataset.n).indexOf(s)>-1||r.cells[1].textContent.indexOf(s)>-1||r.cells[2].textContent.indexOf(s)>-1}
r.hidden=!ok;if(ok)n++});empty.hidden=n>0;shown.textContent=n}
q.addEventListener('input',filt);sy.addEventListener('change',filt);only.addEventListener('change',filt);
az.addEventListener('click',function(e){var b=e.target.closest('button');if(!b)return;letter=(b.dataset.l===letter)?'':b.dataset.l;[].forEach.call(az.querySelectorAll('button'),function(x){x.classList.toggle('on',x.dataset.l===letter&&letter!=='')});filt()});
stc.addEventListener('click',function(e){var b=e.target.closest('button');if(!b)return;styles[b.dataset.s]=!styles[b.dataset.s];b.classList.toggle('on',!!styles[b.dataset.s]);filt()});
document.getElementById('nm-draw').addEventListener('click',function(){var v=visible().slice();if(!v.length){pick.innerHTML='<span>目前的條件下沒有名字，先放寬篩選</span>';return}
for(var i=v.length-1;i>0;i--){var j=Math.floor(Math.random()*(i+1));var t=v[i];v[i]=v[j];v[j]=t}
pick.innerHTML=v.slice(0,5).map(function(r){return '<span>'+r.dataset.n+'<small>'+r.cells[1].textContent+'・'+r.cells[2].textContent+'</small></span>'}).join('');pick.scrollIntoView({block:'nearest'})});
var synth=window.speechSynthesis,voice=null;function pv(){if(!synth)return;var vs=synth.getVoices();voice=vs.filter(function(v){return /^en[-_]US/i.test(v.lang)})[0]||vs.filter(function(v){return /^en/i.test(v.lang)})[0]||null}
if(synth){pv();synth.onvoiceschanged=pv}
tb.addEventListener('click',function(e){var td=e.target.closest('td.n');if(!td||!synth)return;synth.cancel();var u=new SpeechSynthesisUtterance(td.parentNode.dataset.n);u.lang='en-US';if(voice)u.voice=voice;u.rate=0.85;synth.speak(u)});
filt();
})();</script>"""


def curated(page_html):
    return set(re.findall(r"<tr><th>([A-Za-z]+)</th>", page_html))


def block(kind, cfg, names, picked):
    e = html.escape
    zh = cfg["zh"]
    letters = sorted({n["n"][0].upper() for n in names})
    styles = []
    for n in names:
        for s in n["s"]:
            if s not in styles:
                styles.append(s)
    trs = []
    for n in sorted(names, key=lambda x: x["n"].lower()):
        star = '<i title="老師精選">★</i>' if n["n"] in picked else ""
        trs.append(f'<tr data-n="{e(n["n"])}" data-l="{n["n"][0].upper()}" data-sy="{n["sy"]}" data-s="{e("|".join(n["s"]))}"{" data-pick=1" if n["n"] in picked else ""}>'
                   f'<td class="n">{e(n["n"])}{star}</td><td class="p">{e(n["p"])}</td><td class="m">{e(n["m"])}</td><td class="o">{e(n["o"])}</td><td class="s">{e("・".join(n["s"]))}</td></tr>')
    total = len(names)
    az = "".join(f'<button type="button" data-l="{l}">{l}</button>' for l in letters)
    st = "".join(f'<button type="button" data-s="{e(s)}">{e(s)}</button>' for s in styles)
    return f"""<!-- AE:NAMES-TABLE start -->
<section class="section" id="all-names">
  <div class="wrap">
    <div class="center stack reveal"><span class="eyebrow eyebrow-green">完整清單</span><h2>{zh}英文名字<em>完整清單</em>：{total} 個，附中文唸法與意思</h2></div>
    <div class="prose reveal" style="margin-top:14px">
      <p>上面是老師實際推薦的精選；下面是<strong>{total} 個常用{zh}英文名字的完整清單</strong>，每個都附中文唸法提示、意思與來源。可以用<strong>開頭字母</strong>（例如中文名有「凱」就看 K、有「安」就看 A）、<strong>音節數</strong>、<strong>風格</strong>來篩，點名字可以<strong>聽美式發音</strong>，也可以按「隨機抽 5 個」讓孩子自己選。標 ★ 的是上面老師精選過的名字。</p>
    </div>
    {CSS}
    <div class="nm-bar reveal"><div>符合條件 <b id="nm-shown">{total}</b> <span style="color:#8a94a3">/ {total} 個</span></div><button type="button" id="nm-draw">🎲 隨機抽 5 個</button></div>
    <div class="nm-pick" id="nm-pick"></div>
    <div class="nm-tools reveal">
      <input type="search" id="nm-q" placeholder="搜尋名字、唸法或意思，例如 Leo、獅子" aria-label="搜尋名字">
      <select id="nm-sy" aria-label="音節數"><option value="">全部音節</option><option value="1">1 音節（最短）</option><option value="2">2 音節</option><option value="3">3 音節以上</option></select>
      <label class="tg"><input type="checkbox" id="nm-only"> 只看 ★ 老師精選</label>
    </div>
    <div class="nm-chips reveal" id="nm-az">{az}</div>
    <div class="nm-chips styles reveal" id="nm-styles">{st}</div>
    <div class="nm-wrap reveal">
      <table class="nm"><thead><tr><th>名字</th><th>中文唸法</th><th>意思</th><th>來源</th><th>風格</th></tr></thead>
      <tbody id="nm-body">{"".join(trs)}</tbody></table>
      <div class="nm-empty" id="nm-empty" hidden>沒有符合的名字——放寬一個條件試試。</div>
    </div>
    <p class="nm-note">「中文唸法」是幫家長抓重音和音節的提示，不是標準音標；真正的發音請點名字聽。「意思」與「來源」取常見的語源說法，同一個名字常有不止一種解釋。清單更新：{TODAY}。另一頁：<a href="{cfg['other'][0]}">{cfg['other'][1]}完整清單</a>；取名原則見<a href="/kids-english-names-guide/">小孩的英文名字怎麼取</a>。</p>
    {JS}
  </div>
</section>
<!-- AE:NAMES-TABLE end -->
"""


def sub1(pat, rep, s, flags=0, what=""):
    s2, n = re.subn(pat, rep, s, count=1, flags=flags)
    if n != 1:
        sys.exit(f"pattern not found: {what or pat[:60]}")
    return s2


def patch(kind, cfg):
    p = os.path.join(SITE, cfg["page"], "index.html")
    s = open(p, encoding="utf-8").read()
    names = json.load(open(os.path.join(SITE, "data", f"english-names-{kind}.json"), encoding="utf-8"))["names"]
    picked = curated(s.split("<!-- AE:NAMES-TABLE start -->")[0])
    total, npick = len(names), len(picked)
    zh = cfg["zh"]
    blk = block(kind, cfg, names, picked)
    if "<!-- AE:NAMES-TABLE start -->" in s:
        s = sub1(r"<!-- AE:NAMES-TABLE start -->.*?<!-- AE:NAMES-TABLE end -->\n?", lambda m: blk, s, re.S, "NAMES-TABLE block")
    else:
        # first run: insert before the 地雷 section (the bg-soft section that contains the anchor text)
        idx = s.find(cfg["anchor"])
        if idx < 0:
            sys.exit(f"anchor not found on {cfg['page']}")
        sec = s.rfind('<section class="section bg-soft">', 0, idx)
        s = s[:sec] + blk + s[sec:]
    e = html.escape
    title = f"{zh}英文名字 {YEAR}：{total} 個完整清單（附中文唸法＋意思）＋老師精選 {npick} 個與地雷｜埃森美語"
    og = f"{zh}英文名字 {YEAR}：{total} 個完整清單＋老師精選 {npick} 個"
    if kind == "boys":
        desc = (f"男生英文名字怎麼取？{total} 個常用名字完整清單，每個附中文唸法、意思與來源，可依開頭字母、音節、風格篩選、點名字聽美式發音。"
                f"美國持照教師另精選 {npick} 個真正常用的名字（經典 Ethan、Daniel、William，短名 Max、Leo、Jack，學院風 Henry、Oliver、Theodore），並點出三個台灣常見地雷與從中文名取名的方法。")
        h1 = f"男生英文名字怎麼取？<br><em>{total} 個完整清單＋老師精選 {npick} 個</em>"
    else:
        desc = (f"女生英文名字怎麼取？{total} 個常用名字完整清單，每個附中文唸法、意思與來源，可依開頭字母、音節、風格篩選、點名字聽美式發音。"
                f"美國持照教師另精選 {npick} 個課堂驗證過的名字（經典 Emma、Olivia，自然系 Lily、Iris，短名 Mia、Zoe，氣質長名 Charlotte、Isabella），並提醒三個台灣常見地雷與從中文名取名的方法。")
        h1 = f"女生英文名字怎麼取？<br><em>{total} 個完整清單＋老師精選 {npick} 個</em>"
    s = sub1(r"<title>.*?</title>", f"<title>{e(title)}</title>", s, re.S, "title")
    s = sub1(r'(<meta name="description" content=")[^"]*(")', lambda m: m.group(1) + e(desc, quote=True) + m.group(2), s, 0, "description")
    s = sub1(r'(<meta property="og:title" content=")[^"]*(")', lambda m: m.group(1) + e(og, quote=True) + m.group(2), s, 0, "og:title")
    s = sub1(r'(<meta property="og:description" content=")[^"]*(")', lambda m: m.group(1) + e(desc, quote=True) + m.group(2), s, 0, "og:description")
    s = sub1(r'<h1 class="reveal d1">.*?</h1>', lambda m: f'<h1 class="reveal d1">{h1}</h1>', s, re.S, "h1")
    # authored breadcrumb leaf (girls page carries one) and any BlogPosting headline
    s = re.sub(r'("position":3,"name":")[^"]*(")', lambda m: m.group(1) + e(f"{zh}英文名字完整清單", quote=True) + m.group(2), s, count=1)
    s = re.sub(r'("@type":"BlogPosting","headline":")[^"]*(")', lambda m: m.group(1) + e(og, quote=True) + m.group(2), s, count=1)
    s = re.sub(r'"dateModified":"[^"]*"', f'"dateModified":"{TODAY}"', s, count=1)
    open(p, "w", encoding="utf-8").write(s)
    print(f"  /{cfg['page']}/  {total} names · {npick} starred · {len(s):,} chars")


if __name__ == "__main__":
    for kind, cfg in PAGES.items():
        patch(kind, cfg)

#!/usr/bin/env python3
"""Put the full MOE 1,200-word list ON /moe-1200-words-guide/ (not just links to it).

Why: GSC (2026-09-13) shows the page's own queries are 1200單字下載 / 1200單字excel /
1200單字表 / 國中1200單字pdf — people want the list itself — and prepedu.com out-ranked
us with an on-page list. GA4 says 38% of the page's organic sessions download a file.

What this writes
  · assets/downloads/ae-moe-1200-official.csv   (UTF-8 BOM so Excel shows the Chinese)
  · assets/downloads/ae-moe-1200-official.xlsx  (two sheets: 全表 A–Z, 主題精選 200)
  · the <!-- AE:WORDLIST --> block in moe-1200-words-guide/index.html — every word in
    plain HTML (indexable), with a JS toolbar: search, A–Z chips, theme filter, a
    "會了" checkbox per word saved in localStorage, tap-to-hear via speechSynthesis.
  · title / description / H1 / BlogPosting dateModified / breadcrumb name, and the
    "更新" line under the H1, all from the same run.

Source of truth: ~/Documents/GitHub/data/wordlists.json → moe_1200_official (108 課綱
附錄五・表一, verified 2026-08-13, 1,211 entries) + moe_1200_selection (the 200 themed
subset) — the same data make_printables.py renders into the PDFs, so page, PDF, CSV
and Excel can never disagree.

Re-runnable: the block is replaced between its markers; head fields are rewritten by
regex. Run tools/seo_build.py afterwards (sitemap lastmod moves via the ledger).
"""
import csv, datetime, html, json, os, re, sys

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.expanduser("~/Documents/GitHub/data/wordlists.json")
PAGE = os.path.join(SITE, "moe-1200-words-guide", "index.html")
DL = os.path.join(SITE, "assets", "downloads")
TODAY = datetime.date.today().isoformat()
YEAR = TODAY[:4]

TITLE = f"教育部 1200 單字表（{YEAR} 官方核對版）：完整字表線上查＋PDF／Excel 免費下載｜埃森美語"
OG_TITLE = f"教育部 1200 單字表（{YEAR} 官方核對版）：完整字表線上查＋PDF／Excel 免費下載"
DESC = ("教育部國中小基本 1200 字詞（108 課綱附錄五・表一，共 1,211 條）完整字表直接線上查："
        "搜尋、依字母／主題篩選、會了打勾記進度、點單字聽發音；PDF、Excel、CSV 免費下載，不用留資料。"
        "逐條對照官方課綱核對，坊間舊版差 ±60 字。附分年段用法、會考範圍與常見問題。板橋美國持照教師整理。")
OG_DESC = ("教育部 1200 字詞完整字表（1,211 條，逐條對照 108 課綱核對）直接線上查、打勾記進度、聽發音；"
           "PDF／Excel／CSV 免費下載不用留資料——美籍持證教師整理。")
H1 = f'教育部 <em>1200 單字表</em>：{YEAR} 官方核對版<br>完整字表線上查・PDF／Excel 免費下載'
CRUMB = f"教育部 1200 單字表（{YEAR} 官方核對版）"


def load():
    d = json.load(open(DATA, encoding="utf-8"))
    off = d["moe_1200_official"]
    sel = d["moe_1200_selection"]
    # theme tag per headword: the 200-selection is "word — 中文"; official heads are
    # "airplane (plane)" — match on the first token before " (" / "/" for both.
    def head(s):
        return re.split(r"\s*[\(/]", s.strip(), 1)[0].strip().lower()
    theme = {}
    for g in sel["groups"]:
        tname = g["group"].split(" ")[0]          # "數字 Numbers" → 數字
        for w in g["words"]:
            theme[head(w.split(" — ")[0])] = tname
    rows = []
    for g in off["groups"]:
        for w in g["words"]:
            rows.append(dict(letter=g["group"], en=w["en"], zh=w["zh"], theme=theme.get(head(w["en"]), "")))
    themes = [g["group"].split(" ")[0] for g in sel["groups"]]
    return rows, themes, off


def write_csv(rows):
    p = os.path.join(DL, "ae-moe-1200-official.csv")
    with open(p, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["#", "英文", "中文", "字母", "主題（精選 200）", "會了✓"])
        for i, r in enumerate(rows, 1):
            w.writerow([i, r["en"], r["zh"], r["letter"], r["theme"], ""])
    return p


def write_xlsx(rows, themes):
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    from openpyxl.utils import get_column_letter
    wb = Workbook()
    hdr_font = Font(bold=True, color="FFFFFF"); hdr_fill = PatternFill("solid", fgColor="1A2752")

    def sheet(ws, title, data, cols):
        ws.title = title
        ws.append(cols)
        for c in ws[1]:
            c.font = hdr_font; c.fill = hdr_fill; c.alignment = Alignment(vertical="center")
        for r in data:
            ws.append(r)
        ws.freeze_panes = "A2"
        for i, wdt in enumerate([6, 34, 26, 8, 16, 8][:len(cols)], 1):
            ws.column_dimensions[get_column_letter(i)].width = wdt
        ws.auto_filter.ref = ws.dimensions

    ws = wb.active
    sheet(ws, "全表 A-Z（1,211 條）",
          [[i, r["en"], r["zh"], r["letter"], r["theme"], ""] for i, r in enumerate(rows, 1)],
          ["#", "英文", "中文", "字母", "主題（精選 200）", "會了✓"])
    ws2 = wb.create_sheet()
    sel = [r for r in rows if r["theme"]]
    sel.sort(key=lambda r: (themes.index(r["theme"]), r["en"].lower()))
    sheet(ws2, "主題精選 200",
          [[i, r["en"], r["zh"], r["theme"], ""] for i, r in enumerate(sel, 1)],
          ["#", "英文", "中文", "主題", "會了✓"])
    ws3 = wb.create_sheet(); ws3.title = "來源"
    ws3["A1"] = "教育部《十二年國民基本教育課程綱要》語文領域－英語文 附錄五・表一「基本 1,200 字」"
    ws3["A2"] = "官方以括號歸併變化形（如 be (am, is, are…)），故條目共 1,211 條。中譯為埃森美語自撰。"
    ws3["A3"] = "舊 97 課綱流傳版與本表差異約 ±60 字。整理：埃森美語 americanenglish.com.tw/moe-1200-words-guide/"
    ws3["A4"] = f"核對日期：{TODAY}"
    ws3.column_dimensions["A"].width = 110
    p = os.path.join(DL, "ae-moe-1200-official.xlsx")
    wb.save(p)
    return p


CSS = """<style>
.wl-tools{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin:18px 0 10px}
.wl-tools input[type=search]{flex:1 1 220px;font:inherit;font-size:16px;padding:10px 14px;border:2px solid rgba(26,39,82,.14);border-radius:12px;background:#fff}
.wl-tools select{font:inherit;font-size:15px;padding:9px 12px;border:2px solid rgba(26,39,82,.14);border-radius:12px;background:#fff}
.wl-tools label.tg{font-size:14.5px;color:#4a5a72;display:flex;gap:6px;align-items:center;cursor:pointer}
.wl-az{display:flex;flex-wrap:wrap;gap:6px;margin:4px 0 14px}
.wl-az button{font-family:'Baloo 2',sans-serif;font-weight:800;font-size:14px;color:var(--navy);background:#fff;border:2px solid rgba(26,39,82,.12);border-radius:100px;padding:4px 11px;cursor:pointer}
.wl-az button.on{background:var(--navy);color:#fff;border-color:var(--navy)}
.wl-bar{display:flex;flex-wrap:wrap;gap:12px;align-items:center;justify-content:space-between;background:#fff;border:2px solid rgba(26,39,82,.08);border-radius:16px;padding:12px 16px;margin:0 0 14px}
.wl-bar b{font-family:'Baloo 2',sans-serif;font-size:22px;color:var(--navy)}
.wl-bar .wl-prog{flex:1 1 160px;height:10px;background:#eef2f7;border-radius:99px;overflow:hidden}
.wl-bar .wl-prog i{display:block;height:100%;width:0;background:var(--green);transition:width .3s}
.wl-bar button{font:inherit;font-size:13px;color:#8a94a3;background:none;border:1px solid #d9e0ea;border-radius:99px;padding:4px 12px;cursor:pointer}
.wl-wrap{overflow-x:auto;background:#fff;border:2px solid rgba(26,39,82,.08);border-radius:18px}
table.wl{width:100%;border-collapse:collapse;font-size:16px}
table.wl th{position:sticky;top:0;background:var(--navy);color:#fff;font-family:'Baloo 2',sans-serif;font-weight:700;font-size:14px;text-align:left;padding:10px 12px;z-index:1}
table.wl td{padding:8px 12px;border-top:1px solid #eef2f7;vertical-align:middle}
table.wl td.c{width:34px;text-align:center}
table.wl td.w{font-weight:700;color:var(--navy);cursor:pointer;white-space:nowrap}
table.wl td.w:hover{color:var(--blue)}
table.wl td.w::after{content:"🔊";font-size:12px;opacity:.35;margin-left:6px}
table.wl td.z{color:#4a5a72}
table.wl td.t{color:#8a94a3;font-size:13px;white-space:nowrap}
table.wl tr.ok td.w{color:#9aa6b8;text-decoration:line-through}
table.wl tr[hidden]{display:none}
table.wl input{width:18px;height:18px;accent-color:var(--green);cursor:pointer}
.wl-empty{padding:26px;text-align:center;color:#8a94a3}
.wl-dl{display:flex;flex-wrap:wrap;gap:10px;margin-top:16px}
.wl-note{font-size:13.5px;color:#8a94a3;margin-top:12px;line-height:1.7}
@media print{.wl-tools,.wl-az,.wl-bar,.wl-dl{display:none}table.wl tr[hidden]{display:table-row}}
</style>"""

JS = r"""<script>(function(){
var KEY='ae1200';var tb=document.getElementById('wl-body');if(!tb)return;
var rows=[].slice.call(tb.querySelectorAll('tr'));var total=rows.length;rows.forEach(function(r){r.dataset.w=r.cells[1].textContent;r.cells[0].firstChild.setAttribute('aria-label','會了 '+r.dataset.w)});
var st={};try{st=JSON.parse(localStorage.getItem(KEY)||'{}')||{}}catch(e){}
function save(){try{localStorage.setItem(KEY,JSON.stringify(st))}catch(e){}}
var cnt=document.getElementById('wl-cnt'),bar=document.getElementById('wl-prog');
function paint(){var n=0;rows.forEach(function(r){var w=r.dataset.w;var on=!!st[w];r.classList.toggle('ok',on);r.querySelector('input').checked=on;if(on)n++});cnt.textContent=n.toLocaleString();bar.style.width=(100*n/total)+'%'}
tb.addEventListener('change',function(e){if(e.target.type!=='checkbox')return;var r=e.target.closest('tr');if(e.target.checked)st[r.dataset.w]=1;else delete st[r.dataset.w];save();paint()});
document.getElementById('wl-reset').addEventListener('click',function(){if(confirm('把打勾的進度全部清掉？'))
{st={};save();paint()}});
var q=document.getElementById('wl-q'),th=document.getElementById('wl-theme'),only=document.getElementById('wl-only'),az=document.getElementById('wl-az'),letter='',empty=document.getElementById('wl-empty');
function norm(s){return (s||'').toLowerCase()}
function filt(){var s=norm(q.value).trim(),t=th.value,o=only.checked,shown=0;
rows.forEach(function(r){var ok=true;if(letter&&r.dataset.l!==letter)ok=false;if(ok&&t&&r.dataset.t!==t)ok=false;if(ok&&o&&st[r.dataset.w])ok=false;
if(ok&&s){var en=norm(r.dataset.w),zh=r.cells[2].textContent;ok=en.indexOf(s)>-1||zh.indexOf(s)>-1}r.hidden=!ok;if(ok)shown++});
empty.hidden=shown>0;document.getElementById('wl-shown').textContent=shown.toLocaleString()}
q.addEventListener('input',filt);th.addEventListener('change',filt);only.addEventListener('change',filt);
az.addEventListener('click',function(e){var b=e.target.closest('button');if(!b)return;letter=(b.dataset.l===letter)?'':b.dataset.l;[].forEach.call(az.querySelectorAll('button'),function(x){x.classList.toggle('on',x.dataset.l===letter&&letter!=='')});filt()});
var synth=window.speechSynthesis,voice=null;function pick(){if(!synth)return;var vs=synth.getVoices();voice=vs.filter(function(v){return /^en[-_]US/i.test(v.lang)})[0]||vs.filter(function(v){return /^en/i.test(v.lang)})[0]||null}
if(synth){pick();synth.onvoiceschanged=pick}
tb.addEventListener('click',function(e){var td=e.target.closest('td.w');if(!td||!synth)return;var t=td.textContent.replace(/\s*\(.*?\)\s*/g,' ').replace(/[\/–—].*$/,'').trim();synth.cancel();var u=new SpeechSynthesisUtterance(t);u.lang='en-US';if(voice)u.voice=voice;u.rate=0.9;synth.speak(u)});
paint();filt();
})();</script>"""


def block(rows, themes):
    e = html.escape
    letters = sorted({r["letter"] for r in rows})
    trs = []
    for r in rows:
        w = e(r["en"]); t = e(r["theme"])
        trs.append(f'<tr data-l="{e(r["letter"])}" data-t="{t}"><td class="c"><input type="checkbox"></td>'
                   f'<td class="w">{w}</td><td class="z">{e(r["zh"])}</td><td class="t">{t}</td></tr>')
    n = len(rows)
    opts = "".join(f'<option value="{e(t)}">{e(t)}</option>' for t in themes)
    az = "".join(f'<button type="button" data-l="{l}">{l}</button>' for l in letters)
    return f"""<!-- AE:WORDLIST start -->
<section class="section bg-soft" id="wordlist">
  <div class="wrap">
    <div class="center stack reveal"><span class="eyebrow eyebrow-yellow">完整字表</span><h2>教育部 1200 字<em>完整字表</em>：{n:,} 條線上查（官方核對版）</h2></div>
    <div class="prose reveal" style="margin-top:14px">
      <p>下面就是整份表——108 課綱英語文領綱附錄五・表一「基本 1,200 字」逐條核對後的完整版（官方把變化形用括號歸併，例如 be (am, is, are…)，所以共 {n:,} 條）。可以直接<strong>搜尋</strong>、按<strong>字母</strong>或<strong>主題</strong>篩選、<strong>會了打勾</strong>（進度存在你的瀏覽器裡，下次打開還在）、<strong>點單字聽發音</strong>。想要檔案，PDF、Excel、CSV 都在表格下方，不用留資料。</p>
    </div>
    {CSS}
    <div class="wl-bar reveal"><div>已會 <b id="wl-cnt">0</b> <span style="color:#8a94a3">/ {n:,}</span>　<span style="color:#8a94a3;font-size:13px">目前顯示 <span id="wl-shown">{n:,}</span> 條</span></div><div class="wl-prog"><i id="wl-prog"></i></div><button type="button" id="wl-reset">清除進度</button></div>
    <div class="wl-tools reveal">
      <input type="search" id="wl-q" placeholder="搜尋英文或中文，例如 apple、蘋果" aria-label="搜尋單字">
      <select id="wl-theme" aria-label="依主題篩選"><option value="">全部主題</option>{opts}</select>
      <label class="tg"><input type="checkbox" id="wl-only"> 只看還沒會的</label>
    </div>
    <div class="wl-az reveal" id="wl-az">{az}</div>
    <div class="wl-wrap reveal">
      <table class="wl"><thead><tr><th>會了</th><th>英文</th><th>中文</th><th>主題</th></tr></thead>
      <tbody id="wl-body">{"".join(trs)}</tbody></table>
      <div class="wl-empty" id="wl-empty" hidden>沒有符合的字——換個字母或清掉搜尋試試。</div>
    </div>
    <div class="wl-dl reveal">
      <a class="btn btn-primary" href="/assets/downloads/ae-moe-1200-complete-a4.pdf" download>完整檢核表 PDF（A4 列印）</a>
      <a class="btn btn-blue" href="/assets/downloads/ae-moe-1200-official.xlsx" download>Excel 字表（.xlsx）</a>
      <a class="btn btn-outline" href="/assets/downloads/ae-moe-1200-official.csv" download>CSV（Google 試算表可開）</a>
      <a class="btn btn-outline" href="/assets/downloads/ae-moe-1200-themed-200-a4.pdf" download>主題精選 200 PDF</a>
    </div>
    <p class="wl-note">「主題」欄標的是我們〈主題精選 200〉裡的分組（數字、顏色、家庭、學校、食物、動物、身體、天氣、時間、動作、形容詞），官方原表本身只按字母排序、沒有分年級——課綱的年段目標是「國小畢業口語 300 字、拼寫 180 字，國中畢業 1,200 字」，分年段的用法見下文。中文釋義為埃森美語自撰，非官方翻譯。核對日期：{TODAY}。</p>
    {JS}
  </div>
</section>
<!-- AE:WORDLIST end -->"""


def sub1(pat, rep, s, flags=0, what=""):
    s2, n = re.subn(pat, rep, s, count=1, flags=flags)
    if n != 1:
        sys.exit(f"pattern not found: {what or pat[:60]}")
    return s2


def patch_page(rows, themes):
    s = open(PAGE, encoding="utf-8").read()
    blk = block(rows, themes)
    if "<!-- AE:WORDLIST start -->" in s:
        s = sub1(r"<!-- AE:WORDLIST start -->.*?<!-- AE:WORDLIST end -->", lambda m: blk, s, re.S, "WORDLIST block")
    else:
        # first run: the block replaces the old "字表長什麼樣？30 個範例" sample section
        s = sub1(r'<section class="section bg-soft">\s*<div class="wrap">\s*<div class="center stack reveal"><span class="eyebrow eyebrow-yellow">字表樣貌</span>.*?</section>',
                 lambda m: blk, s, re.S, "字表樣貌 section")
    e = html.escape
    s = sub1(r"<title>.*?</title>", f"<title>{e(TITLE)}</title>", s, re.S, "title")
    s = sub1(r'(<meta name="description" content=")[^"]*(")', lambda m: m.group(1) + e(DESC, quote=True) + m.group(2), s, 0, "description")
    s = sub1(r'(<meta property="og:title" content=")[^"]*(")', lambda m: m.group(1) + e(OG_TITLE, quote=True) + m.group(2), s, 0, "og:title")
    s = sub1(r'(<meta property="og:description" content=")[^"]*(")', lambda m: m.group(1) + e(OG_DESC, quote=True) + m.group(2), s, 0, "og:description")
    s = sub1(r'<h1 class="reveal d1">.*?</h1>', lambda m: f'<h1 class="reveal d1">{H1}</h1>', s, re.S, "h1")
    # visible update line under the author line (idempotent)
    upd = f'<p class="body reveal d2" id="wl-updated" style="font-size:14px;color:#8a94a3">最後更新：{TODAY}｜字表逐條對照 108 課綱附錄五・表一核對，共 {len(rows):,} 條</p>'
    if 'id="wl-updated"' in s:
        s = sub1(r'<p class="body reveal d2" id="wl-updated"[^>]*>.*?</p>', lambda m: upd, s, re.S, "updated line")
    else:
        s = sub1(r'(<p class="body reveal d2">作者：Christopher[^<]*</p>)', lambda m: m.group(1) + "\n    " + upd, s, 0, "author line")
    # BlogPosting headline/description/dateModified + breadcrumb leaf
    s = sub1(r'("@type":"BlogPosting","headline":")[^"]*(")', lambda m: m.group(1) + e(OG_TITLE, quote=True) + m.group(2), s, 0, "LD headline")
    s = sub1(r'("@type":"BlogPosting","headline":"[^"]*","description":")[^"]*(")', lambda m: m.group(1) + e(DESC, quote=True) + m.group(2), s, 0, "LD description")
    s = sub1(r'"dateModified":"[^"]*"', f'"dateModified":"{TODAY}"', s, 0, "dateModified")
    s = sub1(r'("position":3,"name":")[^"]*(")', lambda m: m.group(1) + e(CRUMB, quote=True) + m.group(2), s, 0, "breadcrumb leaf")
    # magnet box: add the Excel/CSV buttons once
    if "ae-moe-1200-official.xlsx" not in s.split("<!-- AE:WORDLIST start -->")[0]:
        s = sub1(r'(<a class="btn btn-blue" href="/assets/downloads/ae-moe-1200-complete-a4.pdf" download>完整檢核表</a>)',
                 lambda m: m.group(1) + '\n      <a class="btn btn-outline" href="/assets/downloads/ae-moe-1200-official.xlsx" download>Excel 字表</a>\n      <a class="btn btn-outline" href="#wordlist">直接線上查 ↓</a>',
                 s, 0, "magnet box")
    # FAQ answer (DOM + FAQPage LD carry the same sentence)
    old = "本頁提供兩份可直接下載的家庭版：主題分類精選 200，以及逐條對照官方課綱做成的完整檢核表——都不用註冊、不用留資料。"
    new = "本頁把整份 1,211 條字表直接放在網頁上可以查、可以打勾，另外提供四種可直接下載的檔案：完整檢核表 PDF、Excel（.xlsx）、CSV，以及主題分類精選 200 PDF——都不用註冊、不用留資料。"
    s = s.replace(old, new)
    open(PAGE, "w", encoding="utf-8").write(s)
    return len(s)


if __name__ == "__main__":
    rows, themes, off = load()
    assert 1150 <= len(rows) <= 1300, len(rows)
    c = write_csv(rows); x = write_xlsx(rows, themes)
    n = patch_page(rows, themes)
    tagged = sum(1 for r in rows if r["theme"])
    print(f"rows {len(rows)} (theme-tagged {tagged}) · csv {os.path.getsize(c):,} B · xlsx {os.path.getsize(x):,} B · page {n:,} chars")

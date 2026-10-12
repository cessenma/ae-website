#!/usr/bin/env python3
"""Put the full 108 課綱 2,000-word list ON /moe-2000-words-guide/ (not just talk about it).

Why: GSC (90 days to 2026-10-13) — 5,736 impressions, 3.3% CTR at positions 5–6, on
國中英文2000單字表 / 國中2000單字 / 2000單字表下載 / 國中2000單字excel / 國中2000單字分類 /
國中2000單字主題. People want the list itself, a download, and the list by topic; the page
had none of them (2,900 characters of advice, no table).

What this writes
  · assets/downloads/ae-moe-2000-official.csv   (UTF-8 BOM so Excel shows the Chinese)
  · assets/downloads/ae-moe-2000-official.xlsx  (全表 A–Z · 依主題 37 類 · 其他常用 800 · 來源)
  · the <!-- AE:WORDLIST --> block: all 2,005 entries in plain HTML (indexable) with a JS
    toolbar — search, 基本 1,200 / 其他常用 800 filter, the curriculum's own 37 topics
    (表三), A–Z chips, a "會了" checkbox saved in localStorage under the SAME key as the
    1,200 page (so a word ticked there is ticked here), tap-to-hear via speechSynthesis.
  · the H1, the BlogPosting headline/description, the "字表核對" line and the download FAQ.
    Title and meta description live in data/snippets.json (seo_build applies them).

Source of truth: ~/Documents/GitHub/data/wordlists.json
  moe_1200_official    表一 基本 1,200 字 (1,211 entries, verified 2026-08-13)
  moe_2000_additional  表二 其他常用 800 字 (794 entries, verified 2026-10-13)
  moe_2000_topics      表三 37 topics and each entry's topic numbers
Extracted from the NAER-published curriculum PDF (附錄五, pp. 54–67). The same data feeds
make_printables.py (ae-moe-2000-complete-a4.pdf), so page, PDF, CSV and Excel agree.

Re-runnable: the block is replaced between its markers. Run tools/seo_build.py afterwards.
"""
import csv, html, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_moe1200_list import CSS as CSS_1200   # one stylesheet for both word-list pages

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.expanduser("~/Documents/GitHub/data/wordlists.json")
PAGE = os.path.join(SITE, "moe-2000-words-guide", "index.html")
DL = os.path.join(SITE, "assets", "downloads")
# The day the list was checked against the curriculum PDF. Change it only after re-checking.
CHECKED_ON = "2026-10-13"

H1 = '國中英文 <em>2000 單字表</em><br>完整字表線上查・下載'   # line hints: seo_build H1_WBR
LD_HEADLINE = "國中英文 2000 單字表：完整字表線上查＋主題分類＋PDF／Excel 下載"
LD_DESC = ("108 課綱英語文參考字彙表完整版：表一基本 1,200 字＋表二其他常用 800 字，共 2,005 條，"
           "依課綱 37 個主題分類，可搜尋、打勾記進度、點單字聽發音；PDF、Excel、CSV 免費下載。"
           "另整理 2000 字和段考、會考、英檢的關係，以及 800 字擴充量怎麼背。")


def sort_key(en):
    return re.sub(r"[^a-z]", "", en.lower()) or en.lower()


def load():
    d = json.load(open(DATA, encoding="utf-8"))
    tp = d["moe_2000_topics"]
    names = {int(k): v for k, v in tp["names"].items()}       # n -> [English, 中文]
    rows = []
    for key, level in (("moe_1200_official", "基本"), ("moe_2000_additional", "其他常用")):
        for g in d[key]["groups"]:
            for w in g["words"]:
                rows.append(dict(letter=g["group"], en=w["en"], zh=w["zh"], level=level,
                                 topics=tp["of"].get(w["en"], [])))
    rows.sort(key=lambda r: (r["letter"], sort_key(r["en"])))
    return rows, names


def write_csv(rows, names):
    p = os.path.join(DL, "ae-moe-2000-official.csv")
    with open(p, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["#", "英文", "中文", "級別", "字母", "主題（課綱表三）", "會了✓"])
        for i, r in enumerate(rows, 1):
            w.writerow([i, r["en"], r["zh"], r["level"], r["letter"],
                        "、".join(names[t][1] for t in r["topics"]), ""])
    return p


def write_xlsx(rows, names):
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    from openpyxl.utils import get_column_letter
    wb = Workbook()
    hdr_font = Font(bold=True, color="FFFFFF"); hdr_fill = PatternFill("solid", fgColor="1A2752")

    def sheet(ws, title, data, cols, widths):
        ws.title = title
        ws.append(cols)
        for c in ws[1]:
            c.font = hdr_font; c.fill = hdr_fill; c.alignment = Alignment(vertical="center")
        for r in data:
            ws.append(r)
        ws.freeze_panes = "A2"
        for i, wdt in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(i)].width = wdt
        ws.auto_filter.ref = ws.dimensions

    tz = lambda r: "、".join(names[t][1] for t in r["topics"])
    sheet(wb.active, f"全表 A-Z（{len(rows):,} 條）",
          [[i, r["en"], r["zh"], r["level"], r["letter"], tz(r), ""] for i, r in enumerate(rows, 1)],
          ["#", "英文", "中文", "級別", "字母", "主題（課綱表三）", "會了✓"], [6, 30, 26, 10, 7, 26, 8])
    by = []
    for n in sorted(names):
        for r in rows:
            if n in r["topics"]:
                by.append([f"{n}. {names[n][1]}", r["en"], r["zh"], r["level"], ""])
    sheet(wb.create_sheet(), "依主題（37 類）", by, ["主題", "英文", "中文", "級別", "會了✓"], [22, 30, 26, 10, 8])
    extra = [r for r in rows if r["level"] == "其他常用"]
    sheet(wb.create_sheet(), f"其他常用 800（{len(extra)} 條）",
          [[i, r["en"], r["zh"], r["letter"], tz(r), ""] for i, r in enumerate(extra, 1)],
          ["#", "英文", "中文", "字母", "主題（課綱表三）", "會了✓"], [6, 30, 26, 7, 26, 8])
    ws = wb.create_sheet(); ws.title = "來源"
    ws["A1"] = "教育部《十二年國民基本教育課程綱要》語文領域－英語文 附錄五「參考字彙表（2,000 字）」"
    ws["A2"] = "表一「基本 1,200 字」（官方以括號歸併變化形，共 1,211 條）＋表二「其他常用 800 字」（794 條）＝ 2,005 條。"
    ws["A3"] = "主題為表三「依主題、詞性分類」的 37 類，一字可屬多類。中文釋義為埃森美語自撰，非官方翻譯。"
    ws["A4"] = f"核對日期：{CHECKED_ON}　整理：埃森美語 americanenglish.com.tw/moe-2000-words-guide/"
    ws.column_dimensions["A"].width = 110
    import datetime     # fixed document dates: a rerun with the same words gives the same file
    wb.properties.created = wb.properties.modified = datetime.datetime.fromisoformat(CHECKED_ON)
    p = os.path.join(DL, "ae-moe-2000-official.xlsx")
    wb.save(p)
    # an .xlsx is a zip, and every part carries the time it was written — pin those too
    import zipfile
    stamp = tuple(int(x) for x in CHECKED_ON.split("-")) + (0, 0, 0)
    with zipfile.ZipFile(p) as z:
        parts = [(i.filename, z.read(i.filename)) for i in z.infolist()]
    with zipfile.ZipFile(p, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in parts:
            if name == "docProps/core.xml":      # openpyxl re-stamps "modified" with now on save
                data = re.sub(rb"(<dcterms:modified[^>]*>)[^<]*", lambda m: m.group(1) + f"{CHECKED_ON}T00:00:00Z".encode(), data)
            z.writestr(zipfile.ZipInfo(name, date_time=stamp), data, compress_type=zipfile.ZIP_DEFLATED)
    return p


CSS = CSS_1200.replace("</style>", """table.wl td.v{font-size:12.5px;white-space:nowrap;color:#4a5a72}
table.wl td.v.x{color:#9a6b00}
table.wl th{white-space:nowrap}.wl-tools select{max-width:100%}
@media (max-width:600px){table.wl td.w{white-space:normal}table.wl th:nth-child(5),table.wl td.t{display:none}table.wl td,table.wl th{padding:7px 8px}table.wl td.v{font-size:11.5px}}
</style>""")

JS = r"""<script>(function(){
var KEY='ae1200';var tb=document.getElementById('wl-body');if(!tb)return;
var rows=[].slice.call(tb.querySelectorAll('tr'));var total=rows.length;rows.forEach(function(r){r.dataset.w=r.cells[1].textContent;r.cells[0].firstChild.setAttribute('aria-label','會了 '+r.dataset.w)});
var st={};try{st=JSON.parse(localStorage.getItem(KEY)||'{}')||{}}catch(e){}
function save(){try{localStorage.setItem(KEY,JSON.stringify(st))}catch(e){}}
var cnt=document.getElementById('wl-cnt'),bar=document.getElementById('wl-prog');
function paint(){var n=0;rows.forEach(function(r){var on=!!st[r.dataset.w];r.classList.toggle('ok',on);r.querySelector('input').checked=on;if(on)n++});cnt.textContent=n.toLocaleString();bar.style.width=(100*n/total)+'%'}
tb.addEventListener('change',function(e){if(e.target.type!=='checkbox')return;var r=e.target.closest('tr');if(e.target.checked)st[r.dataset.w]=1;else delete st[r.dataset.w];save();paint()});
document.getElementById('wl-reset').addEventListener('click',function(){if(confirm('把打勾的進度全部清掉？（1200 單字表頁的進度也會一起清掉）'))
{st={};save();paint()}});
var q=document.getElementById('wl-q'),th=document.getElementById('wl-theme'),lv=document.getElementById('wl-level'),only=document.getElementById('wl-only'),az=document.getElementById('wl-az'),letter='',empty=document.getElementById('wl-empty');
function norm(s){return (s||'').toLowerCase()}
function filt(){var s=norm(q.value).trim(),t=th.value,v=lv.value,o=only.checked,shown=0;
rows.forEach(function(r){var ok=true;if(letter&&r.dataset.l!==letter)ok=false;if(ok&&v&&r.dataset.v!==v)ok=false;if(ok&&t&&(' '+r.dataset.t+' ').indexOf(' '+t+' ')<0)ok=false;if(ok&&o&&st[r.dataset.w])ok=false;
if(ok&&s){var en=norm(r.dataset.w),zh=r.cells[2].textContent;ok=en.indexOf(s)>-1||zh.indexOf(s)>-1}r.hidden=!ok;if(ok)shown++});
empty.hidden=shown>0;document.getElementById('wl-shown').textContent=shown.toLocaleString()}
q.addEventListener('input',filt);th.addEventListener('change',filt);lv.addEventListener('change',filt);only.addEventListener('change',filt);
az.addEventListener('click',function(e){var b=e.target.closest('button');if(!b)return;letter=(b.dataset.l===letter)?'':b.dataset.l;[].forEach.call(az.querySelectorAll('button'),function(x){x.classList.toggle('on',x.dataset.l===letter&&letter!=='')});filt()});
var synth=window.speechSynthesis,voice=null;function pick(){if(!synth)return;var vs=synth.getVoices();voice=vs.filter(function(v){return /^en[-_]US/i.test(v.lang)})[0]||vs.filter(function(v){return /^en/i.test(v.lang)})[0]||null}
if(synth){pick();synth.onvoiceschanged=pick}
tb.addEventListener('click',function(e){var td=e.target.closest('td.w');if(!td||!synth)return;var t=td.textContent.replace(/\s*\(.*?\)\s*/g,' ').replace(/[\/–—].*$/,'').trim();synth.cancel();var u=new SpeechSynthesisUtterance(t);u.lang='en-US';if(voice)u.voice=voice;u.rate=0.9;synth.speak(u)});
paint();filt();
})();</script>"""


def block(rows, names):
    e = html.escape
    letters = sorted({r["letter"] for r in rows})
    n = len(rows)
    nb = sum(1 for r in rows if r["level"] == "基本")
    trs = []
    for r in rows:
        # kept lean: 2,005 rows — every byte here is paid 2,005 times
        t1 = names[r["topics"][0]][1] if r["topics"] else ""
        v = "b" if r["level"] == "基本" else "x"
        trs.append(f'<tr data-l="{e(r["letter"])}" data-v="{v}" data-t="{" ".join(map(str, r["topics"]))}">'
                   f'<td class="c"><input type="checkbox"></td><td class="w">{e(r["en"])}</td>'
                   f'<td class="z">{e(r["zh"])}</td><td class="v {v}">{e(r["level"])}</td>'
                   f'<td class="t">{e(t1)}</td></tr>')
    opts = "".join(f'<option value="{k}">{e(names[k][1])}（{e(names[k][0])}）</option>' for k in sorted(names))
    az = "".join(f'<button type="button" data-l="{l}">{l}</button>' for l in letters)
    return f"""<!-- AE:WORDLIST start -->
<section class="section bg-soft" id="wordlist">
  <div class="wrap">
    <div class="center stack reveal"><span class="eyebrow eyebrow-yellow">完整字表</span><h2>國中英文 2000 單字表<br><em>{n:,} 條</em>線上查</h2></div>
    <div class="prose reveal" style="margin-top:14px">
      <p>下面就是整份 108 課綱英語文參考字彙表：表一「基本 1,200 字」（官方把變化形用括號歸併，例如 be (am, is, are…)，共 {nb:,} 條）加上表二「其他常用 800 字」（{n - nb} 條），合計 {n:,} 條，逐條對照國家教育研究院發布的課綱原文。可以<strong>搜尋</strong>、只看<strong>基本 1,200</strong> 或<strong>其他常用 800</strong>、按課綱表三的 <strong>37 個主題</strong>篩選（例如「食物與飲料」「學校」「交通」）、<strong>會了打勾</strong>（進度存在你的瀏覽器裡；在 <a href="/moe-1200-words-guide/">1200 單字表</a>頁打過的勾，這裡也看得到）、<strong>點單字聽發音</strong>。PDF、Excel、CSV 都在表格下方，不用留資料。</p>
    </div>
    {CSS}
    <div class="wl-bar reveal"><div>已會 <b id="wl-cnt">0</b> <span style="color:#8a94a3">/ {n:,}</span>　<span style="color:#8a94a3;font-size:13px">目前顯示 <span id="wl-shown">{n:,}</span> 條</span></div><div class="wl-prog"><i id="wl-prog"></i></div><button type="button" id="wl-reset">清除進度</button></div>
    <div class="wl-tools reveal">
      <input type="search" id="wl-q" placeholder="搜尋英文或中文，例如 apple、蘋果" aria-label="搜尋單字">
      <select id="wl-level" aria-label="依級別篩選"><option value="">全部（{n:,} 條）</option><option value="b">基本 1,200 字（表一）</option><option value="x">其他常用 800 字（表二）</option></select>
      <select id="wl-theme" aria-label="依主題篩選"><option value="">全部主題（37 類）</option>{opts}</select>
      <label class="tg"><input type="checkbox" id="wl-only"> 只看還沒會的</label>
    </div>
    <div class="wl-az reveal" id="wl-az">{az}</div>
    <div class="wl-wrap reveal">
      <table class="wl"><thead><tr><th>會了</th><th>英文</th><th>中文</th><th>級別</th><th>主題</th></tr></thead>
      <tbody id="wl-body">{"".join(trs)}</tbody></table>
      <div class="wl-empty" id="wl-empty" hidden>沒有符合的字——換個字母、主題，或清掉搜尋試試。</div>
    </div>
    <div class="wl-dl reveal">
      <a class="btn btn-primary" href="/assets/downloads/ae-moe-2000-complete-a4.pdf" download>完整檢核表 PDF（A4 列印）</a>
      <a class="btn btn-blue" href="/assets/downloads/ae-moe-2000-official.xlsx" download>Excel 字表（.xlsx）</a>
      <a class="btn btn-outline" href="/assets/downloads/ae-moe-2000-official.csv" download>CSV（Google 試算表可開）</a>
      <a class="btn btn-outline" href="/moe-1200-words-guide/">只要基本 1200 字 →</a>
    </div>
    <p class="wl-note">「級別」：基本＝表一「基本 1,200 字」（國中小最基本字詞，會考命題字彙依據）；其他常用＝表二「其他常用 800 字」。「主題」是課綱表三「依主題、詞性分類」的 37 類——一個字可以同時屬於好幾類，篩選時每一類都找得到，表格只顯示第一類。中文釋義為埃森美語自撰，非官方翻譯。字表核對：{CHECKED_ON}。</p>
    {JS}
  </div>
</section>
<!-- AE:WORDLIST end -->"""


def sub1(pat, rep, s, flags=0, what=""):
    s2, k = re.subn(pat, rep, s, count=1, flags=flags)
    if k != 1:
        sys.exit(f"pattern not found: {what or pat[:60]}")
    return s2


FAQ_OLD = "課綱文件（含參考字彙表附錄）公布在教育部與國家教育研究院的課綱網站，免費公開；各版本課本與坊間字表整理都以它為源頭。不需要購買任何「獨家字表」。"
FAQ_NEW = ("課綱文件（含參考字彙表附錄）公布在教育部與國家教育研究院的課綱網站，免費公開。本頁已把整份字表"
           "（表一基本 1,200 字＋表二其他常用 800 字，共 2,005 條）逐條放在網頁上，另附 PDF、Excel、CSV "
           "免費下載，不用留資料，也不需要購買任何「獨家字表」。")


def patch_page(rows, names):
    s = open(PAGE, encoding="utf-8").read()
    blk = block(rows, names)
    if "<!-- AE:WORDLIST start -->" in s:
        s = sub1(r"<!-- AE:WORDLIST start -->.*?<!-- AE:WORDLIST end -->", lambda m: blk, s, re.S, "WORDLIST block")
    else:
        # first run: the list goes straight after the opening paragraph, before the advice
        s = sub1(r'(<section class="section">\s*<div class="wrap">\s*<div class="prose reveal">\s*<p>家長口中的「2000 單字」.*?</section>)',
                 lambda m: m.group(1) + "\n\n" + blk, s, re.S, "intro section")
    s = sub1(r'<h1 class="reveal d1">.*?</h1>', lambda m: f'<h1 class="reveal d1">{H1}</h1>', s, re.S, "h1")
    e = html.escape
    upd = (f'<p class="body reveal d2" id="wl-updated" style="font-size:14px;color:#8a94a3">字表核對：{CHECKED_ON}'
           f'｜逐條對照 108 課綱附錄五・表一＋表二，共 {len(rows):,} 條｜<a href="#wordlist">直接看字表 ↓</a></p>')
    if 'id="wl-updated"' in s:
        s = sub1(r'<p class="body reveal d2" id="wl-updated"[^>]*>.*?</p>', lambda m: upd, s, re.S, "updated line")
    else:
        s = sub1(r'(<p class="body reveal d2" style="font-size:14px">本文由埃森美語創辦人 Christopher 撰寫.*?</p>)',
                 lambda m: m.group(1) + "\n    " + upd, s, re.S, "author line")
    s = sub1(r'("@type":"BlogPosting","headline":")[^"]*(")', lambda m: m.group(1) + e(LD_HEADLINE, quote=True) + m.group(2), s, 0, "LD headline")
    s = sub1(r'("@type":"BlogPosting","headline":"[^"]*","description":")[^"]*(")', lambda m: m.group(1) + e(LD_DESC, quote=True) + m.group(2), s, 0, "LD description")
    if FAQ_OLD in s:
        s = s.replace(FAQ_OLD, FAQ_NEW)          # the FAQ answer appears in the page and in FAQPage LD
    open(PAGE, "w", encoding="utf-8").write(s)
    return len(s)


if __name__ == "__main__":
    rows, names = load()
    assert 1990 <= len(rows) <= 2020, len(rows)
    assert all(r["topics"] for r in rows), [r["en"] for r in rows if not r["topics"]][:5]
    c = write_csv(rows, names); x = write_xlsx(rows, names)
    n = patch_page(rows, names)
    print(f"rows {len(rows)} (基本 {sum(r['level'] == '基本' for r in rows)}, 其他常用 "
          f"{sum(r['level'] != '基本' for r in rows)}) · csv {os.path.getsize(c):,} B · "
          f"xlsx {os.path.getsize(x):,} B · page {n:,} chars")

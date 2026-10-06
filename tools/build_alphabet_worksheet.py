#!/usr/bin/env python3
"""Build the A4 英文字母練習表 — the A–Z upper/lower-case tracing worksheet on 四線三格 lines.

    ~/.claude/skills/seo/.venv/bin/python3 tools/build_alphabet_worksheet.py

Output: assets/downloads/ae-english-alphabet-worksheet-a4.pdf, linked from
/english-alphabet-worksheet/. This file is HAND-BUILT: it is not one of the table-to-PDF
twins that build_chart_pdfs.py produces, so keep that slug out of its PDFS map.

Design (what a Taiwan 四線三格 workbook does): four lines, three equal bands, the middle
band tinted and its top line dashed, the baseline heavier. Capitals live in the top two
bands; x-height letters in the middle band; b d f h k l t rise to the top line; g j p q y
drop their tails into the bottom band. Each letter gets one upper-case row and one
lower-case row: the letter printed solid once, then four light-grey copies to trace, then
four empty cells to write. Three letters per page, cover-less; the last page carries the
full A–Z and a–z strips plus empty rows for free writing. Footer on every page carries
americanenglish.com.tw.

Fonts: letters are set in Edu SA Beginner (SIL OFL, Google Fonts) — an upright school
print alphabet whose x-height is half the capital height, i.e. drawn for exactly these
thirds. Chinese and branding text use the TrueType files the exam packs ship with
(Noto Sans TC, DM Serif Display, Baloo 2, DM Sans). Everything is TrueType on purpose:
WeasyPrint's CFF subsets of the macOS system fonts draw wrongly in Apple's PDF viewers
(see tools/check_pdfs.py), and this file must open cleanly on an iPhone.

Letters are placed with inline SVG <text>, whose y is the baseline itself, so no font
line-box arithmetic is involved: font-size = band / x-height ratio, read from the font.
CSS keeps to single-layer backgrounds — WeasyPrint drops multi-layer and %-gradient ones.
"""
import os, re, sys, subprocess, urllib.request

from weasyprint import HTML
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(SITE, "assets", "downloads", "ae-english-alphabet-worksheet-a4.pdf")
SLUG = "english-alphabet-worksheet"
CACHE = os.path.expanduser("~/.cache/ae-fonts")
QBANK_FONTS = os.path.expanduser("~/Documents/GitHub/ae-question-bank/tools/fonts")
GFONTS_CSS = "https://fonts.googleapis.com/css2?family={family}"

# printable_style.py (the five workbooks' design system) supplies the brand tokens, the
# logo data-URI helper and the PDF metadata block; fall back to local copies if absent.
sys.path.insert(0, os.path.expanduser("~/Documents/GitHub"))
try:
    import printable_style as ps
    BLUE, BLUE_DK, GREEN, YELLOW, NAVY = ps.BLUE, ps.BLUE_DK, ps.GREEN, ps.YELLOW, ps.NAVY
    LBLUE, TINT, MUTED, TEXTB = ps.LBLUE, ps.TINT, ps.MUTED, ps.TEXTB
    img_uri, pdf_meta = ps.img_uri, ps.pdf_meta
except Exception:                                   # stand-alone: same values as printable_style
    import base64
    BLUE, BLUE_DK, GREEN, YELLOW, NAVY = "#1CB0F6", "#1391cc", "#06C755", "#FFC828", "#1A2752"
    LBLUE, TINT, MUTED, TEXTB = "#DDF4FF", "#F4FAFF", "#5b6b8a", "#4b5563"

    def img_uri(rel):
        p = os.path.join(SITE, rel.lstrip("/"))
        if not os.path.exists(p):
            return None
        mime = {"webp": "image/webp", "png": "image/png"}.get(p.rsplit(".", 1)[-1].lower(), "image/jpeg")
        return f"data:{mime};base64," + base64.b64encode(open(p, "rb").read()).decode()

    def pdf_meta(title, sub, source_page, keywords=""):
        return (f"<title>{title}｜埃森美語 American English</title>"
                f'<meta name="author" content="埃森美語 American English（板橋）">'
                f'<meta name="description" content="{sub}　·　埃森美語整理，可自由列印使用。'
                f'完整說明：americanenglish.com.tw/{source_page}/">'
                f'<meta name="keywords" content="{keywords}">'
                f'<meta name="generator" content="americanenglish.com.tw">')

GREY = "#C3CBDA"        # the trace copies: light enough to write over, dark enough to see
LINE = "#9AA7BD"        # guide lines 1, 2 (dashed) and 4
BAND_TINT = "#EAF6FF"   # the middle band (single flat fill)

# ── fonts ─────────────────────────────────────────────────────────────────
def google_ttf(family, dest):
    """Download a family's regular TTF from Google Fonts (a non-browser UA is served TTF)."""
    if os.path.exists(dest):
        return dest
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    req = urllib.request.Request(GFONTS_CSS.format(family=family.replace(" ", "+")),
                                 headers={"User-Agent": "Mozilla/5.0"})
    css = urllib.request.urlopen(req, timeout=60).read().decode()
    m = re.search(r"url\((https://fonts\.gstatic\.com/[^)]+\.ttf)\)", css)
    if not m:
        sys.exit(f"{family}: no TTF url in Google Fonts CSS")
    data = urllib.request.urlopen(urllib.request.Request(m.group(1), headers={"User-Agent": "Mozilla/5.0"}),
                                  timeout=120).read()
    if data[:4] not in (b"\x00\x01\x00\x00", b"true"):
        sys.exit(f"{family}: not a TrueType file")
    open(dest, "wb").write(data)
    print(f"  fetched {os.path.basename(dest)} ({len(data) // 1024} KB)")
    return dest

def text_font(name, family):
    """A branding/Chinese TTF: the exam-pack copy if present, else Google's."""
    p = os.path.join(QBANK_FONTS, name)
    return p if os.path.exists(p) else google_ttf(family, os.path.join(CACHE, name))

HAND = google_ttf("Edu SA Beginner", os.path.join(CACHE, "EduSABeginner-Regular.ttf"))
FACES = {
    "Edu SA Beginner": [(HAND, 400)],
    "Noto Sans TC": [(text_font("NotoSansTC-Regular.ttf", "Noto Sans TC"), 400)],
    "DM Serif Display": [(text_font("DMSerifDisplay-Regular.ttf", "DM Serif Display"), 400)],
    "DM Sans": [(text_font("DMSans-Regular.ttf", "DM Sans"), 400)],
}
bold_tc = os.path.join(QBANK_FONTS, "NotoSansTC-Bold.ttf")
if os.path.exists(bold_tc):
    FACES["Noto Sans TC"].append((bold_tc, 700))
baloo = os.path.join(QBANK_FONTS, "Baloo2-ExtraBold.ttf")
if os.path.exists(baloo):
    FACES["Baloo 2"] = [(baloo, 800)]

FONT_CSS = "".join(
    f"@font-face{{font-family:'{fam}';font-weight:{w};src:url('file://{p}') format('truetype')}}"
    for fam, lst in FACES.items() for p, w in lst)
ROUND = "'Baloo 2','Noto Sans TC',sans-serif" if "Baloo 2" in FACES else "'Noto Sans TC',sans-serif"
SERIF = "'DM Serif Display','Noto Sans TC',serif"
SANS = "'DM Sans','Noto Sans TC',sans-serif"

# The hand font's own proportions decide the font size: x-height must equal one band.
_f = TTFont(HAND)
_upm = _f["head"].unitsPerEm
_cmap = _f.getBestCmap()
_gs = _f.getGlyphSet()
def _top(ch):
    pen = BoundsPen(_gs); _gs[_cmap[ord(ch)]].draw(pen); return pen.bounds[3] / _upm
X_RATIO = _top("x")          # 0.416 em
CAP_RATIO = _top("H")        # 0.772 em  → capitals reach 1.86 bands, as the font is drawn

# ── content ───────────────────────────────────────────────────────────────
# letter, example word (same words as /english-alphabet-guide/), gloss, upper-case stroke
# hint, lower-case stroke hint. Hints describe the manuscript (ball-and-stick) forms the
# font prints — e.g. its q ends in a hook, its y and j in a curved tail.
LETTERS = [
    ("A", "apple", "蘋果", "左斜、右斜、中間一橫", "先寫圓，再一條直線"),
    ("B", "ball", "球", "直線、上半圓、下半圓", "先長直線，再往上繞圓"),
    ("C", "cat", "貓", "從右上往左繞，一筆", "從右上往左繞，一筆"),
    ("D", "dog", "狗", "直線、大半圓", "先寫圓，再一條長直線"),
    ("E", "egg", "蛋", "直線、上中下三橫", "中間一橫，再繞圓"),
    ("F", "fish", "魚", "直線、上橫、中橫", "從上面勾下來，再加一橫"),
    ("G", "girl", "女孩", "像 C，再往內一橫", "先寫圓，尾巴到第四線"),
    ("H", "hat", "帽子", "兩直線、中間一橫", "長直線，再一個拱門"),
    ("I", "ice cream", "冰淇淋", "一條直線", "短直線，上面一點"),
    ("J", "juice", "果汁", "直線下來往左勾", "到第四線往左勾，加一點"),
    ("K", "kite", "風箏", "直線、斜上、斜下", "長直線、斜上、斜下"),
    ("L", "lion", "獅子", "直線、底下一橫", "一條長直線"),
    ("M", "monkey", "猴子", "直、斜下、斜上、直", "短直線，兩個拱門"),
    ("N", "nose", "鼻子", "直、斜下、直", "短直線，一個拱門"),
    ("O", "orange", "柳橙", "從上面往左繞一圈", "從上面往左繞一圈"),
    ("P", "pig", "豬", "直線、上半圓", "直線到第四線，再繞圓"),
    ("Q", "queen", "皇后", "圓圈，右下加尾巴", "先寫圓，直線到第四線"),
    ("R", "rabbit", "兔子", "直線、上半圓、斜線", "短直線，再一個小彎"),
    ("S", "sun", "太陽", "從右上開始，像小蛇", "從右上開始，像小蛇"),
    ("T", "tiger", "老虎", "直線、上橫", "直線（比 l 矮），再一橫"),
    ("U", "umbrella", "雨傘", "下來彎上去，一筆", "下來彎上去，再短直線"),
    ("V", "violin", "小提琴", "斜下、斜上", "斜下、斜上"),
    ("W", "watermelon", "西瓜", "斜下、斜上、斜下、斜上", "斜下斜上寫兩次"),
    ("X", "box", "盒子", "兩條斜線交叉", "兩條短斜線交叉"),
    ("Y", "yellow", "黃色", "兩短斜到中間，再直線下", "短斜線，長斜線到第四線"),
    ("Z", "zebra", "斑馬", "上橫、斜線、下橫", "上橫、斜線、下橫"),
]

# ── geometry (mm) ─────────────────────────────────────────────────────────
W = 190.0          # printable width: A4 210 − 10 − 10
BAND = 8.0         # one of the three bands in the letter rows
CELLS = 9          # per row: 1 solid + 4 grey + 4 empty
N_GREY = 4
PER_PAGE = 3
PAD = 1.0          # keeps the outer lines' stroke inside the SVG box

def guide_row(letters, fills, band, cells, hint_x=None):
    """One 四線三格 row as inline SVG: letters sit with their baseline on line 3."""
    h = 3 * band + 2 * PAD
    cell = W / cells
    fs = band / X_RATIO
    base = PAD + 2 * band
    s = [f'<svg class="row" width="{W}mm" height="{h}mm" viewBox="0 0 {W} {h}" xmlns="http://www.w3.org/2000/svg">',
         f'<rect x="0" y="{PAD + band}" width="{W}" height="{band}" fill="{BAND_TINT}"/>']
    for i, y in enumerate((PAD, PAD + band, PAD + 2 * band, PAD + 3 * band)):
        if i == 1:
            s.append(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}" stroke="{LINE}" stroke-width="0.3" stroke-dasharray="1.6 1.2"/>')
        elif i == 2:
            s.append(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}" stroke="{NAVY}" stroke-width="0.45"/>')
        else:
            s.append(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}" stroke="{LINE}" stroke-width="0.3"/>')
    for i, (ch, fill) in enumerate(zip(letters, fills)):
        if not ch:
            continue
        s.append(f'<text x="{cell * i + cell / 2:.2f}" y="{base}" font-family="Edu SA Beginner" '
                 f'font-size="{fs:.3f}" fill="{fill}" text-anchor="middle">{ch}</text>')
    s.append("</svg>")
    return "".join(s)

def trace_row(ch):
    letters = [ch] * (1 + N_GREY) + [""] * (CELLS - 1 - N_GREY)
    fills = [NAVY] + [GREY] * N_GREY + [""] * (CELLS - 1 - N_GREY)
    return guide_row(letters, fills, BAND, CELLS)

def letter_block(up, word, gloss, hint_u, hint_l):
    lo = up.lower()
    pair = (f'<svg width="30mm" height="13mm" viewBox="0 0 30 13" xmlns="http://www.w3.org/2000/svg">'
            f'<text x="9" y="10.4" font-family="Edu SA Beginner" font-size="12.5" fill="{NAVY}" text-anchor="middle">{up}</text>'
            f'<text x="22" y="10.4" font-family="Edu SA Beginner" font-size="12.5" fill="{BLUE_DK}" text-anchor="middle">{lo}</text>'
            f'</svg>')
    return (f'<div class="blk">'
            f'<div class="bh">{pair}'
            f'<div class="bw"><span class="w">{word}</span><span class="g">{gloss}</span></div>'
            f'<div class="bt"><span class="k">筆順</span>'
            f'<span><b>{up}</b> {hint_u}</span><span><b>{lo}</b> {hint_l}</span></div>'
            f'</div>'
            f'{trace_row(up)}{trace_row(lo)}'
            f'</div>')

def header(right):
    lg = img_uri("assets/img/american-english-banqiao-logo.jpg")
    logo = f'<div class="hlogo" style="background-image:url(\'{lg}\')"></div>' if lg else ""
    return (f'<div class="hdr">{logo}'
            f'<span class="hbrand">埃森<b>美語</b><span class="hen">American English</span></span>'
            f'<span class="htitle">英文字母練習表　A–Z 大小寫描寫・四線三格</span>'
            f'<span class="hright">{right}</span></div>')

HOWTO = (
    '<div class="how">'
    '<div class="steps">'
    '<span><b>1</b>描：沿著灰色的字母描四次</span>'
    '<span><b>2</b>寫：在空格自己寫四次</span>'
    '<span><b>3</b>唸：每寫一個就唸字母名稱</span>'
    '<span><b>4</b>說：最後唸一次例字（apple 蘋果）</span>'
    '</div>'
    '<p class="legend">四線三格：大寫住上面兩格；a c e m n o r s u v w x z 住中間一格；'
    'b d f h k l t 往上到第一線；g j p q y 的尾巴往下到第四線。每天 10 分鐘，一次 2–3 個字母就好。</p>'
    '</div>')

def pages():
    out = []
    n_pages = -(-len(LETTERS) // PER_PAGE) + 1
    for pi in range(0, len(LETTERS), PER_PAGE):
        chunk = LETTERS[pi:pi + PER_PAGE]
        pno = pi // PER_PAGE + 1
        letters = " · ".join(f"{u}{u.lower()}" for u, *_ in chunk)
        body = "".join(letter_block(*c) for c in chunk)
        out.append(f'<section class="pg">{header(f"{letters}　｜　{pno} / {n_pages}")}'
                   f'{HOWTO if pno == 1 else ""}{body}</section>')
    # last page: full strips
    band = 6.5
    ups = [u for u, *_ in LETTERS]
    los = [u.lower() for u in ups]
    def strip(chars):
        return guide_row(chars, [GREY] * len(chars), band, 13)
    def empty():
        return guide_row([""] * 13, [""] * 13, band, 13)
    body = (f'<p class="st">大寫 A–Z：先描一次，再在下面兩行自己寫</p>'
            f'{strip(ups[:13])}{strip(ups[13:])}{empty()}{empty()}'
            f'<p class="st">小寫 a–z：先描一次，再在下面兩行自己寫</p>'
            f'{strip(los[:13])}{strip(los[13:])}{empty()}{empty()}'
            f'<p class="st">自由練習：寫自己的英文名字、今天學到的單字</p>'
            f'{empty()}{empty()}')
    out.append(f'<section class="pg last">{header(f"A–Z 自由練習　｜　{n_pages} / {n_pages}")}{body}</section>')
    return "".join(out)

CSS = f"""
{FONT_CSS}
@page {{
  size: A4; margin: 10mm 10mm 14mm 10mm;
  @bottom-left  {{ content: "埃森美語 American English · 板橋中正路89巷4號1樓 · 美籍持證教師 · 12 人小班";
                   font-family: {SANS}; font-size: 7.2pt; color: {MUTED}; }}
  @bottom-right {{ content: "americanenglish.com.tw · 第 " counter(page) " 頁";
                   font-family: {SANS}; font-size: 7.2pt; color: {MUTED}; }}
}}
* {{ box-sizing: border-box; }}
body {{ font-family: {SANS}; font-size: 9pt; line-height: 1.45; color: {TEXTB}; margin: 0; }}
svg.row {{ display: block; }}
.pg {{ break-after: page; }}
.pg.last {{ break-after: auto; }}

.hdr {{ display: flex; align-items: center; gap: 2.6mm; padding: 0 .5mm 2.2mm; margin: 0 0 3mm;
        border-bottom: .4pt solid rgba(26,39,82,.12); }}
.hdr .hlogo {{ width: 8.6mm; height: 8.6mm; border-radius: 50%; background-size: cover;
               background-position: center; background-color: {LBLUE}; }}
.hdr .hbrand {{ font-family: {ROUND}; font-weight: 800; font-size: 12pt; color: {NAVY}; white-space: nowrap; }}
.hdr .hbrand b {{ color: {BLUE}; }}
.hdr .hen {{ font-family: {ROUND}; font-weight: 800; font-size: 7.4pt; color: #475569; margin-left: 1.6mm; }}
.hdr .htitle {{ font-family: {SERIF}; font-size: 11pt; color: {NAVY}; margin-left: 3mm; white-space: nowrap; }}
.hdr .hright {{ margin-left: auto; font-family: {ROUND}; font-weight: 800; font-size: 8pt;
                color: {BLUE_DK}; white-space: nowrap; }}

.how {{ background: {TINT}; border: .4pt solid rgba(26,39,82,.08); border-radius: 3mm;
        padding: 2.4mm 3.5mm 2.2mm; margin: 0 0 3.5mm; }}
.how .steps {{ display: flex; gap: 2mm 4mm; flex-wrap: wrap; font-size: 8.4pt; color: {NAVY}; }}
.how .steps span {{ white-space: nowrap; }}
.how .steps b {{ display: inline-block; width: 4.6mm; height: 4.6mm; line-height: 4.6mm; text-align: center;
                 border-radius: 50%; background: {BLUE}; color: #fff; font-family: {ROUND}; font-weight: 800;
                 font-size: 7.6pt; margin-right: 1.4mm; }}
.how .legend {{ margin: 1.6mm 0 0; font-size: 7.8pt; color: {TEXTB}; line-height: 1.5; }}

.blk {{ margin: 0 0 5mm; break-inside: avoid; }}
.blk .bh {{ display: flex; align-items: center; gap: 3mm; margin: 0 0 .8mm; }}
.blk .bh svg {{ flex: 0 0 30mm; display: block; }}
.blk .bw {{ flex: 0 0 34mm; }}
.blk .bw .w {{ display: block; font-family: {ROUND}; font-weight: 800; font-size: 12pt; color: {NAVY};
               line-height: 1.15; }}
.blk .bw .g {{ display: block; font-size: 9pt; color: {TEXTB}; }}
.blk .bt {{ flex: 1; font-size: 8pt; color: {TEXTB}; line-height: 1.5; }}
.blk .bt span {{ display: block; }}
.blk .bt .k {{ display: inline-block; font-family: {ROUND}; font-weight: 800; font-size: 7pt; color: #067033;
               background: rgba(6,199,85,.12); border-radius: 100px; padding: .2mm 2.2mm; margin: 0 0 .6mm; }}
.blk .bt b {{ font-family: 'Edu SA Beginner'; font-size: 10pt; color: {NAVY}; margin-right: 1.4mm; }}
.blk svg.row + svg.row {{ margin-top: 2mm; }}

.st {{ font-family: {ROUND}; font-weight: 800; font-size: 9.4pt; color: {NAVY}; margin: 1.8mm 0 1.2mm; }}
.st:first-of-type {{ margin-top: 0; }}
.last svg.row + svg.row {{ margin-top: 1mm; }}
"""

KEYWORDS = ("英文字母練習表,英文字母練習,英文字母練習簿,英文字母練習本,英文字母練習pdf,字母描寫,"
            "四線三格,英文字母練習格線,ABC練習,大小寫練習,列印版,學習單,A4,埃森美語,板橋美語")

def build():
    meta = pdf_meta("英文字母練習表 A–Z 大小寫描寫（四線三格）",
                    "26 個字母・每個字母先描 4 次再寫 4 次・最後一頁 A–Z 自由練習・適合 4–7 歲",
                    SLUG, KEYWORDS)
    doc = (f'<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8">{meta}'
           f'<style>{CSS}</style></head><body>{pages()}</body></html>')
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    html = HTML(string=doc, base_url=SITE)
    html.write_pdf(OUT)
    n = len(html.render().pages)
    print(f"  ✓ {os.path.relpath(OUT, SITE)}  {os.path.getsize(OUT) / 1024:.0f} KB  {n} 頁")
    try:                                     # the Apple-viewer trap: every font must be TrueType
        fonts = subprocess.run(["pdffonts", OUT], capture_output=True, text=True).stdout
        bad = [l for l in fonts.splitlines() if "Type 0C" in l or "Type 1C" in l]
        print("  fonts: " + ("all TrueType ✓" if not bad else "CFF fonts present ✗\n" + "\n".join(bad)))
    except FileNotFoundError:
        print("  (poppler not installed: font check skipped)")
    return OUT

if __name__ == "__main__":
    build()

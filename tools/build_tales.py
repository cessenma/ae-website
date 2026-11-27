#!/usr/bin/env python3
"""英文故事 — classic tales retold in reader-level English, each a page (2026-11-27, Chris: "Yes, build 5 tales").

Why: Keyword Planner 11-24 — each famous tale gets 1K–10K searches a month in Chinese and its 「X 英文」 form
100–1K (三隻小豬英文, 龜兔賽跑英文, 灰姑娘英文 …), 英文小短文 1K–10K; the pages that rank are videos and blog lists
with no text + audio + Chinese + printable in one place. Each tale ends on the Chris and Cora readers.

  english-stories/                 hub
  english-stories/<slug>/          one tale: key lines, 6 scenes (picture, English, Chinese, read-aloud), story
                                   words, 5 questions, free A4 PDF, moral, FAQ
  assets/downloads/ae-<slug>-story-a4.pdf

Inputs: tools/tales_data.py (text), assets/img/tales/ (tools/draw_tales.py), assets/audio/tales/ (tools/tales_audio.py).
Run seo_build.py afterwards. Gloss for Chris: ~/Downloads/GLOSS-2026-11-27-ENGLISH-STORIES.md
"""
import html, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_reading_tests as RT
from tales_data import TALES

SITE, ORIGIN, Z, esc = RT.SITE, RT.ORIGIN, RT.Z, html.escape
HUB, READERS, TESTS = "english-stories", "chris-and-cora-readers", "english-reading-comprehension"
FONTS = os.path.expanduser("~/Documents/GitHub/ae-readers/tools/fonts")
GLOSS_OUT = os.path.expanduser("~/Downloads/GLOSS-2026-11-27-ENGLISH-STORIES.md")

CSS = """
.tl-lines{max-width:760px;margin:20px auto 0;display:flex;flex-direction:column;gap:10px}
.tl-line{background:#fff;border-radius:14px;padding:12px 16px;box-shadow:0 4px 14px rgba(26,39,82,.07);border-left:5px solid var(--yellow)}
.tl-line b{display:block;font-size:18px;color:var(--navy);font-family:'DM Sans',system-ui,sans-serif}
.tl-line span{font-size:14.5px;color:#475569}
.tl-bar{display:flex;flex-wrap:wrap;gap:10px;justify-content:center;margin:18px 0 0}
.tl-bar button{border:2px solid rgba(26,39,82,.14);background:#fff;color:var(--navy);font-weight:800;font-size:14.5px;border-radius:99px;padding:8px 16px;cursor:pointer}
.tl-bar button.main{background:var(--yellow);border-color:var(--yellow)}
.tl-story{display:flex;flex-direction:column;gap:18px;max-width:980px;margin:22px auto 0}
.tl-page{display:grid;grid-template-columns:1fr 1fr;gap:22px;align-items:center;background:#fff;border-radius:20px;padding:16px;box-shadow:0 6px 22px rgba(26,39,82,.08);border:2px solid transparent}
.tl-page.now{border-color:var(--yellow)}
.tl-page img{width:100%;height:auto;border-radius:12px;display:block}
.tl-page .en{margin:0;font-size:20px;line-height:1.75;color:var(--navy);font-family:'DM Sans',system-ui,sans-serif}
.tl-page .zh{margin:10px 0 0;font-size:15.5px;line-height:1.8;color:#475569}
.tl-story.nozh .zh{display:none}
.tl-page .n{font-family:'Baloo 2',sans-serif;font-weight:800;font-size:13px;color:#94a3b8}
@media(max-width:760px){.tl-page{grid-template-columns:1fr;gap:12px;padding:12px}.tl-page .en{font-size:18px}}
.tl-words{max-width:760px;margin:18px auto 0;display:flex;flex-wrap:wrap;gap:8px;justify-content:center}
.tl-words span{background:#fff;border-radius:12px;padding:7px 12px;font-size:15px;box-shadow:0 3px 10px rgba(26,39,82,.07)}
.tl-words b{color:var(--navy);font-family:'DM Sans',system-ui,sans-serif;margin-right:6px}
.tl-cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:18px;margin-top:24px}
.tl-card{background:#fff;border-radius:18px;overflow:hidden;text-decoration:none;color:var(--navy);box-shadow:0 6px 20px rgba(26,39,82,.09);display:flex;flex-direction:column}
.tl-card img{width:100%;height:auto;display:block}
.tl-card span{padding:12px 16px 16px;display:block}
.tl-card b{display:block;font-size:18px}.tl-card small{display:block;color:#64748b;font-size:13.5px;line-height:1.6;margin-top:2px}
.tl-moral{max-width:720px;margin:20px auto 0;text-align:center;background:#FFFBEF;border:1.5px solid var(--yellow);border-radius:18px;padding:18px 20px}
.tl-moral b{display:block;font-size:21px;color:var(--navy);font-family:'DM Sans',system-ui,sans-serif}
"""

JS = """<script>(()=>{const S=document.getElementById("tlStory");if(!S)return;const pages=[...S.querySelectorAll(".tl-page")];let cur=null,all=false;
const stop=()=>{if(cur){cur.pause();cur.currentTime=0}pages.forEach(p=>p.classList.remove("now"));document.querySelectorAll(".rt-play.on").forEach(x=>x.classList.remove("on"));cur=null};
function play(i,chain){stop();const p=pages[i];if(!p){all=false;return}const a=p.querySelector("audio"),b=p.querySelector(".rt-play");cur=a;p.classList.add("now");b.classList.add("on");
if(chain)p.scrollIntoView({behavior:"smooth",block:"center"});a.play();a.onended=()=>{b.classList.remove("on");p.classList.remove("now");if(chain&&all)play(i+1,true)}}
pages.forEach((p,i)=>p.querySelector(".rt-play").addEventListener("click",()=>{const on=p.classList.contains("now");all=false;if(on)stop();else play(i,false);
if(typeof gtag==="function")gtag("event","story_play",{mode:"page",page_path:location.pathname})}));
const pa=document.getElementById("tlAll");pa&&pa.addEventListener("click",()=>{if(all){all=false;stop();return}all=true;play(0,true);
if(typeof gtag==="function")gtag("event","story_play",{mode:"all",page_path:location.pathname})});
const tz=document.getElementById("tlZh");tz&&tz.addEventListener("click",()=>{const off=S.classList.toggle("nozh");tz.textContent=off?tz.dataset.show:tz.dataset.hide});
})()</script>"""


def faq(items):
    out = []
    for q, a in items:
        qid = re.sub(r"[^\w一-鿿-]+", "", q.replace(" ", "-"))
        out.append(f'<div class="faq-item"><h3 id="{qid}" class="faq-h"><button class="faq-q" aria-expanded="false">{q}<span class="pm"></span></button></h3>'
                   f'<div class="faq-a"><p>{a}</p></div></div>')
    return '<div class="faq" style="max-width:760px;margin:20px auto 0">' + "".join(out) + "</div>"


def pdf(t):
    """Free A4 printable: page 1 the story with its pictures, page 2 Chinese, story words, questions, answers."""
    from weasyprint import HTML
    out = os.path.join(SITE, "assets", "downloads", f"ae-{t['slug']}-story-a4.pdf")
    import tempfile
    from PIL import Image
    tmp = tempfile.mkdtemp()
    def img(i):  # JPEG copies: WeasyPrint stores WebP losslessly, which made each PDF ~3.5 MB
        j = os.path.join(tmp, f"{i}.jpg")
        Image.open(os.path.join(SITE, "assets", "img", "tales", f"{t['slug']}-{i}.webp")).convert("RGB").save(j, quality=82)
        return "file://" + j
    scenes = "".join(f'<div class="s"><img src="{img(i)}"><p><b>{i}</b> {esc(s["en"])}</p></div>' for i, s in enumerate(t["scenes"], 1))
    zh = "".join(f"<p><b>{i}</b> {esc(s['zh'])}</p>" for i, s in enumerate(t["scenes"], 1))
    words = " ・ ".join(f"<b>{esc(k)}</b> {esc(v)}" for k, v in t["words"].items())
    qs = "".join(f"<li>{esc(q['q'])}<br>" + "　".join(f"({'ABCD'[j]}) {esc(o)}" for j, o in enumerate(q["options"])) + "</li>" for q in t["questions"])
    ans = "　".join(f"{i}. {'ABCD'[q['answer']]}" for i, q in enumerate(t["questions"], 1))
    doc = f"""<html><head><meta charset="utf-8"><style>
@font-face{{font-family:TC;src:url(file://{FONTS}/NotoSansTC-Regular.ttf)}}@font-face{{font-family:TC;font-weight:700;src:url(file://{FONTS}/NotoSansTC-Bold.ttf)}}
@font-face{{font-family:DM;src:url(file://{FONTS}/DMSans-Regular.ttf)}}@font-face{{font-family:DM;font-weight:700;src:url(file://{FONTS}/DMSans-Bold.ttf)}}
@page{{size:A4;margin:13mm 13mm 15mm;@bottom-center{{content:"埃森美語 American English ・ americanenglish.com.tw/english-stories/";font:8pt TC;color:#64748b}}}}
body{{font:10.5pt/1.5 DM,TC;color:#1A2752}}h1{{font:700 20pt DM,TC;margin:0 0 1mm}}h1 small{{font:400 11pt TC;color:#475569;margin-left:3mm}}
h2{{font:700 12pt TC;margin:5mm 0 2mm;border-bottom:1.5pt solid #FFC828;padding-bottom:1mm}}
.g{{display:grid;grid-template-columns:1fr 1fr;gap:4mm 6mm;margin-top:3mm}}.s img{{width:100%;border-radius:2mm}}.s p{{margin:1.5mm 0 0;font-size:11pt;line-height:1.5}}
.s b,.z b{{color:#0B6FB8}}.z p{{margin:0 0 1.6mm;font:10pt/1.6 TC}}.w{{font:10pt/1.9 DM,TC}}ol{{margin:0;padding-left:5mm}}li{{margin-bottom:2.2mm}}
.a{{margin-top:6mm;font-size:8.5pt;color:#64748b;transform:rotate(180deg);text-align:left}}.m{{margin-top:3mm;font:700 11pt DM,TC}}
</style></head><body>
<h1>{esc(t['en'])}<small>{esc(t['zh'])}・英文故事</small></h1>
<div class="g">{scenes}</div>
<div style="page-break-before:always"></div>
<h1>{esc(t['en'])}<small>中文、單字與題目</small></h1>
<h2>中文對照</h2><div class="z">{zh}</div>
<h2>故事單字</h2><div class="w">{words}</div>
<h2>讀完回答（Questions）</h2><ol>{qs}</ol>
<p class="m">{esc(t['moral_en'])}　{esc(t['moral_zh'])}</p>
<p class="a">答案：{ans}</p>
</body></html>"""
    HTML(string=doc).write_pdf(out)
    return f"/assets/downloads/ae-{t['slug']}-story-a4.pdf", os.path.getsize(out) // 1024


def tale_page(t, idx):
    RT._cur[0] = t["slug"]
    slug = f"{HUB}/{t['slug']}"
    n_words = len(re.findall(r"[A-Za-z']+", " ".join(s["en"] for s in t["scenes"])))
    full = " ".join(s["en"] for s in t["scenes"])
    for q in t["questions"]:
        if q["evidence"] not in full:
            sys.exit(f"{t['slug']}: evidence not in text: {q['evidence']!r}")
    pdf_url, kb = pdf(t)
    lines = "".join(f'<div class="tl-line"><b lang="en">{esc(a)}</b><span>{Z(b, "(the Chinese meaning of: " + a + ")")}</span></div>' for a, b in t["lines"])
    story = []
    for i, s in enumerate(t["scenes"], 1):
        RT.GLOSS[RT._cur[0]].append((s["zh"], s["en"]))
        story.append(f'<div class="tl-page reveal"><img src="/assets/img/tales/{t["slug"]}-{i}.webp" alt="{esc(t["zh"])}英文故事 第 {i} 段插圖" width="1000" height="667" {"" if i == 1 else "loading=\"lazy\" "}decoding="async">'
                     f'<div><span class="n">{i} / {len(t["scenes"])}</span><p class="en" lang="en">{esc(s["en"])}</p><p class="zh">{esc(s["zh"])}</p>'
                     f'<button type="button" class="rt-play">▶ {Z("聽這一段", "listen to this part")}</button><audio preload="none" src="/assets/audio/tales/{t["slug"]}-{i}.mp3"></audio></div></div>')
    words = "".join(f'<span><b lang="en">{esc(k)}</b>{esc(v)}</span>' for k, v in t["words"].items())
    qs = []
    for i, q in enumerate(t["questions"]):
        RT.GLOSS[RT._cur[0]].append((q["why_zh"], q["why_en"]))
        opts = "".join(f'<label><input type="radio" name="q{i}" value="{j}"><span lang="en">{esc(o)}</span></label>' for j, o in enumerate(q["options"]))
        qs.append(f'<div class="rt-q" data-a="{q["answer"]}"><b lang="en">{esc(q["q"])}</b>{opts}<p class="rt-why">{esc(q["why_zh"])}</p></div>')
    nxt = TALES[(idx + 1) % len(TALES)]
    fq = faq([
        (Z(f"{t['zh'].split('（')[0]}的英文怎麼說？", f"How do you say {t['zh']} in English?"),
         Z(f"{t['zh'].split('（')[0]}的英文是 <b lang='en'>{esc(t['en'])}</b>。這個故事是{t['source_zh']}。", f"It is {t['en']}; the story is {t['source_en']}.")),
        (Z("這個故事的寓意，英文怎麼說？", "How do you say the moral in English?"),
         Z(f"<b lang='en'>{esc(t['moral_en'])}</b>（{t['moral_zh']}）", f"{t['moral_en']}")),
        (Z("這個英文版本適合誰讀？", "Who is this English version for?"),
         Z(f"全文約 {n_words} 個英文字，句子短、用現在式。除了上面列出的故事單字和專有名稱，其他的字都在教育部國中小 1,200 字表裡，適合已經讀得出短句的孩子；還不會讀的孩子可以先聽朗讀、看圖和中文。",
           f"About {n_words} English words, short sentences in the present tense. Apart from the story words listed above and proper names, every word is on the MOE 1,200 list. It suits children who can read short sentences; younger ones can listen, look at the pictures and read the Chinese.")),
    ])
    main = f"""<section class="section">
  <div class="wrap">
    <div class="center stack reveal"><span class="eyebrow eyebrow-yellow">{Z("一句話回答", "the short answer")}</span><h2 id="英文怎麼說">{Z(f"{t['zh'].split('（')[0]}的英文是 <em lang=\"en\">{esc(t['en'])}</em>", f"{t['zh']} in English is {t['en']}")}</h2></div>
    <p class="body center" style="max-width:62ch;margin:14px auto 0">{Z(f"故事裡最有名的幾句，英文是這樣說的：", "The best-known lines of the story in English:")}</p>
    <div class="tl-lines reveal">{lines}</div>
  </div>
</section>
<section class="section bg-soft">
  <div class="wrap">
    <div class="center stack reveal"><span class="eyebrow eyebrow-green">{Z("故事全文", "the whole story")}</span><h2 id="英文故事全文">{Z(f"<em lang=\"en\">{esc(t['en'])}</em> 英文故事，中英對照", f"{t['en']}: the story in English with Chinese")}</h2></div>
    <div class="tl-bar"><button type="button" class="main" id="tlAll">▶ {Z("從頭聽到尾", "listen from start to end")}</button>
      <button type="button" id="tlZh" data-hide="{Z("隱藏中文（自己讀讀看）", "hide the Chinese (try reading it yourself)")}" data-show="{Z("顯示中文", "show the Chinese")}">{Z("隱藏中文（自己讀讀看）", "hide the Chinese (try reading it yourself)")}</button>
      <a class="btn btn-outline" style="min-height:0;padding:8px 16px;font-size:14.5px" href="{pdf_url}" download>{Z("免費下載 A4 列印版", "free A4 printable")}</a></div>
    <div class="tl-story" id="tlStory">{"".join(story)}</div>
    <div class="tl-moral reveal"><b lang="en">{esc(t['moral_en'])}</b>{Z(t['moral_zh'], t['moral_en'])}</div>
  </div>
</section>
<section class="section">
  <div class="wrap">
    <div class="center stack reveal"><span class="eyebrow eyebrow-yellow">{Z("故事單字", "story words")}</span><h2 id="故事單字">{Z(f"{len(t['words'])} 個<em>故事單字</em>", f"{len(t['words'])} story words")}</h2></div>
    <div class="tl-words reveal">{words}</div>
  </div>
</section>
<section class="section bg-soft">
  <div class="wrap">
    <div class="center stack reveal"><span class="eyebrow eyebrow-green">{Z("讀完回答", "after reading")}</span><h2 id="閱讀測驗">{Z(f"讀懂了嗎？<em>{len(t['questions'])} 題</em>", f"did you understand? {len(t['questions'])} questions")}</h2></div>
    <div class="rt-qs">{"".join(qs)}</div>
    <div class="rt-check"><button type="button" class="btn btn-primary" id="rtCheck">{Z("對答案", "check answers")}</button><span class="rt-score" id="rtScore"></span></div>
    <div class="cta-box reveal" id="rtNext" style="margin-top:26px">
      <span class="eyebrow eyebrow-yellow">{Z("讀得懂這一篇？", "could read this one?")}</span>
      <h2 id="下一步" style="margin-top:14px">{Z("下一步：<em>每天讀一本</em>，教孩子自己讀英文", "next: a book a day, to teach your child to read English on their own")}</h2>
      <p class="body" style="max-width:580px;margin:16px auto 0">{Z("Chris and Cora 分級讀本是寫來教孩子自己讀英文的：36 本這樣的故事，分 12 級，一級一級加新字，每本都可以邊聽邊讀。第 1 級 3 本整本免費。", "The Chris and Cora readers are written to teach a child to read English on their own: 36 stories like this in 12 levels, adding new words level by level, all with read-aloud. Level 1 (3 books) is free in full.")}</p>
      <div class="cta-row"><a class="btn btn-primary" href="/{READERS}/" data-book="readers" data-book-item="tale-{t['slug']}">{Z("免費開始第 1 級", "start Level 1 free")}</a>
      <a class="btn btn-outline" href="/{HUB}/{nxt['slug']}/">{Z(f"下一篇：{nxt['zh'].split('（')[0]}", f"next story: {nxt['en']}")}</a></div>
    </div>
  </div>
</section>
<section class="section">
  <div class="wrap">
    <div class="center stack reveal"><span class="eyebrow eyebrow-green">{Z("常見問題", "FAQ")}</span><h2 id="常見問題">{Z("關於<em>這個故事</em>", "about this story")}</h2></div>
    {fq}
    <p class="body center" style="margin-top:18px;font-size:14px"><a href="/{HUB}/">{Z("全部英文故事", "all English stories")}</a> ・ <a href="/{TESTS}/">{Z("12 級免費閱讀測驗", "12 free reading tests")}</a></p>
  </div>
</section>
{RT.JS}
{JS}
"""
    kwz = t["zh"].split("（")[0]
    tail = "版" if kwz.endswith("故事") else "故事"  # 「年獸的故事英文故事」 reads double
    wide = lambda x: sum(2 if ord(c) > 0x2E7F else 1 for c in x)  # the snippet lint's unit: 60 with the brand suffix
    title = next(c for c in (f"{kwz}英文{tail}：{t['en']} 中英對照、朗讀、PDF", f"{kwz}英文：{t['en']} 中英對照、朗讀、PDF",
                              f"{kwz}英文：{t['en']} 中英對照＋朗讀", f"{kwz}英文：{t['en']}")
                 if wide(c + "｜埃森美語") <= 60)
    title = Z(title, f"{t['zh']} in English: {t['en']}, with Chinese, read-aloud and a PDF")
    desc = Z(f"{kwz}的英文是 {t['en']}。完整英文故事 {n_words} 字、6 張插圖、逐段中文對照與美式朗讀，附故事單字、{len(t['questions'])} 題閱讀測驗和免費 A4 列印版 PDF。",
             f"{t['zh']} in English is {t['en']}. The full story in {n_words} words with 6 pictures, Chinese, American read-aloud, story words, {len(t['questions'])} questions and a free A4 PDF.")
    crumb = f'<a href="/">首頁</a> ／ <a href="/{HUB}/">{Z("英文故事", "English stories")}</a> ／ {kwz}'
    h1 = Z(f'<span class="h1s"><em>{kwz}英文</em>{tail}</span><br><span class="h1s" lang="en">{esc(t["en"])}</span>', f"{t['zh']} in English: {t['en']}")
    lead = Z(f"{t['source_zh']}，用孩子讀得懂的簡單英文重新寫過：6 段故事、每段有插圖、中文對照和朗讀，讀完還有 {len(t['questions'])} 題小測驗。",
             f"{t['source_en'].capitalize()}, retold in simple English a child can read: 6 parts, each with a picture, Chinese and read-aloud, then {len(t['questions'])} questions.")
    RT.shell(slug, title + "｜埃森美語", desc, crumb, h1, lead, f"/assets/img/tales/{t['slug']}-1.webp", f"{kwz}英文{tail}插圖", main,
             extra_head=f"<style>{CSS}</style>\n", eyebrow=Z("中英對照・附朗讀", "English with Chinese, read aloud"))
    return slug, title + "｜埃森美語", desc, n_words, kb


def hub_page(rows):
    RT._cur[0] = "stories-hub"
    cards = "".join(f'<a class="tl-card" href="/{HUB}/{t["slug"]}/"><img src="/assets/img/tales/{t["slug"]}-1.webp" alt="{esc(t["zh"])}英文故事" width="1000" height="667" loading="lazy" decoding="async">'
                    f'<span><b>{t["zh"].split("（")[0]}</b><small lang="en">{esc(t["en"])}</small><small>{Z(f"{nw} 字・6 段・朗讀・PDF", f"{nw} words, 6 parts, read-aloud, PDF")}</small></span></a>'
                    for t, nw in rows)
    main = f"""<section class="section">
  <div class="wrap">
    <div class="center stack reveal"><span class="eyebrow eyebrow-yellow">{Z("經典故事", "classic stories")}</span><h2 id="英文故事列表">{Z("選一個<em>孩子聽過的故事</em>", "pick a story your child already knows")}</h2></div>
    <p class="body center" style="max-width:62ch;margin:14px auto 0">{Z("孩子已經知道故事在說什麼，讀英文的時候就猜得出生字的意思。這是最容易開始讀英文的方法。", "When a child already knows the story, they can guess the new words while reading the English. It is the easiest way to start reading English.")}</p>
    <div class="tl-cards reveal">{cards}</div>
  </div>
</section>
<section class="section bg-soft">
  <div class="wrap" style="max-width:760px">
    <div class="cta-box reveal">
      <span class="eyebrow eyebrow-green">{Z("讀完這幾篇", "after these stories")}</span>
      <h2 id="讀完之後" style="margin-top:14px">{Z("想讓孩子<em>自己讀英文</em>？", "want your child to read English alone?")}</h2>
      <p class="body" style="max-width:580px;margin:16px auto 0">{Z("Chris and Cora 分級讀本教孩子自己讀英文：從一頁一句開始，12 級 36 本，一級一級往上讀。故事在台灣，用的是學校的教育部字表。第 1 級 3 本整本免費。", "The Chris and Cora readers start at one sentence a page: 12 levels, 36 books, level by level. Set in Taiwan, using the school's MOE word list. Level 1 (3 books) is free in full.")}</p>
      <div class="cta-row"><a class="btn btn-primary" href="/{READERS}/" data-book="readers" data-book-item="tales-hub">{Z("免費開始第 1 級", "start Level 1 free")}</a>
      <a class="btn btn-outline" href="/{TESTS}/">{Z("12 級免費閱讀測驗", "12 free reading tests")}</a></div>
    </div>
  </div>
</section>
"""
    title = Z("英文故事：經典童話中英對照，附朗讀、閱讀測驗與免費 PDF", "English stories: classic tales with Chinese, read-aloud, questions and free PDFs")
    desc = Z(f"免費英文故事 {len(rows)} 篇：三隻小豬、龜兔賽跑、狼來了、灰姑娘、年獸的故事。用簡單英文重寫，每段有插圖、中文對照和美式朗讀，附閱讀測驗與 A4 列印版 PDF。",
             f"{len(rows)} free English stories: Three Little Pigs, Tortoise and the Hare, The Boy Who Cried Wolf, Cinderella, Nian. Simple English with pictures, Chinese, American read-aloud, questions and A4 PDFs.")
    h1 = Z('<span class="h1s"><em>英文故事</em></span><br><span class="h1s">經典童話，中英對照</span>', "English stories: classic tales with Chinese")
    lead = Z("孩子聽過的經典故事，用簡單英文重新寫過。每一篇都有插圖、中文對照、美式朗讀、閱讀測驗，還可以免費下載列印。",
             "Classic stories your child already knows, retold in simple English. Each has pictures, Chinese, American read-aloud, questions and a free printable.")
    RT.shell(HUB, title + "｜埃森美語", desc, f'<a href="/">首頁</a> ／ {Z("英文故事", "English stories")}', h1, lead,
             f"/assets/img/tales/{TALES[0]['slug']}-1.webp", "英文故事插圖", main, extra_head=f"<style>{CSS}</style>\n",
             eyebrow=Z("免費・中英對照・附朗讀", "free, with Chinese and read-aloud"))
    return HUB, title + "｜埃森美語", desc


def main():
    made, rows = [], []
    for i, t in enumerate(TALES):
        slug, ttl, desc, nw, kb = tale_page(t, i)
        made.append((slug, ttl, desc)); rows.append((t, nw))
        print(f"  wrote {slug} ({nw} words, PDF {kb} KB)")
    made.append(hub_page(rows))
    snip_p = os.path.join(SITE, "data", "snippets.json")
    snip = json.load(open(snip_p, encoding="utf-8"))
    for slug, ttl, desc in made:
        snip[slug] = {"description": desc, "title": ttl}
    json.dump(snip, open(snip_p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    open(snip_p, "a", encoding="utf-8").write("\n")
    sm = os.path.join(SITE, "sitemap.xml")
    xml = open(sm, encoding="utf-8").read()
    add = [f"{ORIGIN}/{s}/" for s, _, _ in made if f"<loc>{ORIGIN}/{s}/</loc>" not in xml]
    if add:
        open(sm, "w", encoding="utf-8").write(xml.replace("</urlset>", "".join(f"  <url><loc>{u}</loc></url>\n" for u in add) + "</urlset>"))
    print("  sitemap:", len(add), "added")
    L = ["# 英文故事 pages — Chinese with English (2026-11-27)", ""]
    for page, rr in RT.GLOSS.items():
        L += [f"## {page}", ""]
        for zh, en in rr:
            L += [f"- {re.sub(r'<[^>]+>', '', zh)}", f"  - *{re.sub(r'<[^>]+>', '', en)}*"]
        L.append("")
    open(GLOSS_OUT, "w", encoding="utf-8").write("\n".join(L))
    print("  gloss:", GLOSS_OUT)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""國小英文閱讀測驗 — 12 free online reading tests built from the Chris and Cora readers (2026-11-23,
Chris: "get more traffic to the readers page"). Keyword Planner: 國小英文閱讀測驗 (題庫/免費/下載/線上/推薦),
英文閱讀, 英文故事線上聽 — a cluster the site had no page for; each test is the opening of a real book
(text + picture + the book's own read-aloud audio) with questions, and ends on the readers page.

  english-reading-comprehension/            hub: 12 levels
  english-reading-comprehension/level-N/    one test per level (book Na)
  assets/img/readers/tests/<code>-<n>.webp  the excerpt pictures (from the flip book, 600 px)
  assets/audio/readers/<code>/p<nn>.mp3     the excerpt audio (the flip book's 1x read-along)

Inputs: ae-readers data/books/<code>.json (text), ~/Downloads/AE-readers-out/flip/<code>/ (pictures, audio),
questions JSON (every answer has an "evidence" quote checked against the text here). Run seo_build.py afterwards.
Gloss for Chris: ~/Downloads/GLOSS-2026-11-23-READING-TESTS.md
"""
import html, json, os, re, shutil, sys

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIGIN = "https://americanenglish.com.tw"
HUB = "english-reading-comprehension"
READERS = "chris-and-cora-readers"
BOOKS = os.path.expanduser("~/Documents/GitHub/ae-readers/data/books")
FLIP = os.path.expanduser("~/Downloads/AE-readers-out/flip")
QFILE = os.path.join(SITE, "data", "reading_tests.json")
TEMPLATE = os.path.join(SITE, "gept-elementary-speaking-writing", "index.html")
GLOSS_OUT = os.path.expanduser("~/Downloads/GLOSS-2026-11-23-READING-TESTS.md")
TODAY = "2026-11-23"
esc = html.escape
GLOSS, _cur = {}, ["hub"]
STAGE = {1: ("剛開始讀", "just starting to read"), 5: ("讀得出短句", "can read short sentences"), 9: ("讀整段故事", "reading whole paragraphs")}


def Z(zh, en):
    GLOSS.setdefault(_cur[0], []).append((zh, en))
    return zh


def stage(L):
    return STAGE[1 if L <= 4 else 5 if L <= 8 else 9]


def excerpt(L):
    b = json.load(open(os.path.join(BOOKS, f"{L}a.json"), encoding="utf-8"))
    pages, words = [], 0
    for p in b["pages"]:
        pages.append(p)
        words += len(p["text"].split())
        if (len(pages) >= 4 and words >= 110) or len(pages) >= 8:
            break
    return b, pages, words


def assets(code, pages):
    """Copy the picture (flip page 2n-1) and the 1x audio (flip page 2n-2) of each excerpt page."""
    from PIL import Image
    idir = os.path.join(SITE, "assets", "img", "readers", "tests")
    adir = os.path.join(SITE, "assets", "audio", "readers", code)
    os.makedirs(idir, exist_ok=True)
    os.makedirs(adir, exist_ok=True)
    for p in pages:
        n = p["n"]
        img = os.path.join(idir, f"{code}-{n}.webp")
        if not os.path.exists(img):
            im = Image.open(os.path.join(FLIP, code, "pages", f"{2 * n - 1:02d}.jpg")).convert("RGB")
            im.thumbnail((600, 900))
            im.save(img, "WEBP", quality=80, method=6)
        src = os.path.join(FLIP, code, "audio", f"p{2 * n - 2:02d}.mp3")
        dst = os.path.join(adir, f"p{2 * n - 2:02d}.mp3")
        if os.path.exists(src) and not os.path.exists(dst):
            shutil.copy2(src, dst)


CSS = """
.rt-story{display:flex;flex-direction:column;gap:16px;max-width:860px;margin:22px auto 0}
.rt-page{display:grid;grid-template-columns:200px 1fr;gap:18px;align-items:center;background:#fff;border-radius:18px;padding:14px;box-shadow:0 6px 20px rgba(26,39,82,.08)}
.rt-page img{width:100%;height:auto;border-radius:10px;display:block}
.rt-page p{margin:0;font-size:19px;line-height:1.75;color:var(--navy);font-family:'DM Sans',system-ui,sans-serif}
.rt-play{margin-top:10px;border:0;border-radius:99px;background:var(--yellow);color:var(--navy);font-weight:800;font-size:14px;padding:7px 14px;cursor:pointer}
.rt-play.on{background:var(--navy);color:#fff}
@media(max-width:600px){.rt-page{grid-template-columns:110px 1fr;gap:12px;padding:10px}.rt-page p{font-size:17px}}
.rt-qs{max-width:760px;margin:22px auto 0;display:flex;flex-direction:column;gap:14px;counter-reset:q}
.rt-q{background:#fff;border-radius:16px;padding:16px 18px;box-shadow:0 4px 16px rgba(26,39,82,.07);border:2px solid transparent}
.rt-q b{display:block;font-size:17px;color:var(--navy);margin-bottom:10px;font-family:'DM Sans',system-ui,sans-serif}
.rt-q b::before{counter-increment:q;content:counter(q) ". "}
.rt-q label{display:flex;gap:10px;align-items:center;padding:8px 10px;border-radius:10px;cursor:pointer;font-size:16px;font-family:'DM Sans',system-ui,sans-serif}
.rt-q label:hover{background:#F1F7FD}
.rt-q.ok{border-color:#12B76A}.rt-q.no{border-color:#E5484D}
.rt-q label.right{background:#E7F8EF;font-weight:700}.rt-q label.wrong{background:#FDECEC}
.rt-why{display:none;margin:10px 0 0;font-size:14.5px;line-height:1.7;color:#374151;background:#F8FAFC;border-radius:10px;padding:8px 12px}
.rt-q.done .rt-why{display:block}
.rt-check{display:flex;flex-wrap:wrap;gap:10px;justify-content:center;align-items:center;margin-top:18px}
.rt-score{font-weight:800;color:var(--navy);font-size:18px}
.rt-steps{margin:18px auto 0;padding-left:22px;font-size:16px;line-height:1.9;color:var(--text-body,#374151)}.rt-steps li{margin-bottom:8px}.rt-steps b{color:var(--navy)}
.rt-levels{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:14px;margin-top:22px}
.rt-level{display:flex;gap:12px;align-items:center;background:#fff;border-radius:16px;padding:12px;text-decoration:none;color:var(--navy);box-shadow:0 4px 16px rgba(26,39,82,.07)}
.rt-level img{width:64px;height:auto;border-radius:6px;box-shadow:0 3px 8px rgba(26,39,82,.18)}
.rt-level b{display:block;font-size:15px}.rt-level small{display:block;color:#64748b;font-size:12.5px;line-height:1.5}
.rt-level span.lv{font-family:'Baloo 2',sans-serif;font-weight:800;color:var(--blue-ink,#0B6FB8);font-size:13px}
"""

JS = """<script>(()=>{let cur=null;
document.querySelectorAll(".rt-play").forEach(b=>b.addEventListener("click",()=>{const a=document.getElementById(b.dataset.a);if(!a)return;
if(cur&&cur!==a){cur.pause();cur.currentTime=0;document.querySelectorAll(".rt-play.on").forEach(x=>x.classList.remove("on"))}
if(a.paused){a.play();b.classList.add("on");cur=a;a.onended=()=>b.classList.remove("on")}else{a.pause();b.classList.remove("on")}
if(typeof gtag==="function")gtag("event","reading_test_play",{page_path:location.pathname})}));
const go=document.getElementById("rtCheck");if(!go)return;go.addEventListener("click",()=>{let ok=0,n=0;
document.querySelectorAll(".rt-q").forEach(q=>{n++;const pick=q.querySelector("input:checked"),ans=+q.dataset.a;
q.classList.add("done");q.classList.remove("ok","no");q.querySelectorAll("label").forEach((l,i)=>{l.classList.toggle("right",i===ans);l.classList.toggle("wrong",!!pick&&+pick.value===i&&i!==ans)});
if(pick&&+pick.value===ans){ok++;q.classList.add("ok")}else q.classList.add("no")});
document.getElementById("rtScore").textContent=ok+" / "+n;document.getElementById("rtNext").hidden=false;
if(typeof gtag==="function")gtag("event","reading_test_check",{score:ok,total:n,page_path:location.pathname})})})()</script>"""


def shell(slug, title, desc, crumb, h1, lead, img, img_alt, main_html, extra_head="", eyebrow=None):
    t = open(TEMPLATE, encoding="utf-8").read()
    url = f"{ORIGIN}/{slug}/"
    t = re.sub(r"<title>.*?</title>", f"<title>{esc(title)}</title>", t, count=1, flags=re.S)
    t = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{esc(desc)}">', t, count=1)
    t = t.replace(f"{ORIGIN}/gept-elementary-speaking-writing/", url)
    t = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{esc(title.split("｜")[0])}">', t, count=1)
    t = re.sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{esc(desc)}">', t, count=1)
    t = re.sub(r'<meta property="og:image" content="[^"]*">', f'<meta property="og:image" content="{ORIGIN}{img}">', t, count=1)
    t = re.sub(r'<meta property="og:image:width" content="[^"]*">\s*<meta property="og:image:height" content="[^"]*">', "", t, count=1)
    t = re.sub(r'<meta property="og:image:alt" content="[^"]*">', f'<meta property="og:image:alt" content="{esc(img_alt)}">', t, count=1)
    t = t.replace("/assets/img/blog/gept-speaking-test-interview-practice.webp", img)
    ld = {"@context": "https://schema.org", "@type": "LearningResource", "name": title.split("｜")[0], "description": desc, "url": url,
          "inLanguage": ["zh-Hant-TW", "en"], "learningResourceType": "Reading comprehension practice", "isAccessibleForFree": True,
          "educationalLevel": "elementary school", "datePublished": TODAY, "dateModified": TODAY,
          "author": {"@type": "Person", "name": "Christopher", "url": f"{ORIGIN}/certified-american-teacher-banqiao/"},
          "publisher": {"@id": f"{ORIGIN}/#organization"}}
    t = re.sub(r'<script type="application/ld\+json">\{"@context":"https://schema.org","@type":"BlogPosting".*?</script>',
               lambda m: '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False, separators=(",", ":")) + "</script>", t, count=1, flags=re.S)
    t = t.replace('data-page="gept-elementary-speaking-writing"', f'data-page="{slug.replace("/", "-")}"')
    t = t.replace("</head>", f"<style>{CSS}</style>\n{extra_head}</head>", 1)
    hero = f"""<section class="page-hero">
  <div class="bg-deco"></div>
  <div class="wrap">
    <div class="breadcrumb reveal">{crumb}</div>
    <span class="eyebrow eyebrow-green reveal">{eyebrow or Z("免費線上閱讀測驗", "free online reading test")}</span>
    <h1 class="reveal d1">{h1}</h1>
    <div class="divider reveal d1"></div>
    <p class="body reveal d2">{lead}</p>
  </div>
</section>
"""
    a, b = t.index("\n<main id=\"top\">"), t.index("<!-- AE:BYL start -->")
    t = t[:a] + "\n<main id=\"top\">\n\n" + hero + main_html + "\n" + t[b:]
    d = os.path.join(SITE, slug)
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(t)
    return url


def test_page(L, Q, total):
    _cur[0] = f"level-{L}"
    b, pages, words = excerpt(L)
    code, title = b["book"], b["title"]
    assets(code, pages)
    full = " ".join(p["text"] for p in pages)
    for q in Q:
        if q["evidence"] not in full:
            sys.exit(f"level {L}: evidence not in text: {q['evidence']!r}")
    st_zh, st_en = stage(L)
    story = []
    for p in pages:
        n = p["n"]
        aud = f"/assets/audio/readers/{code}/p{2 * n - 2:02d}.mp3"
        story.append(f'<div class="rt-page reveal"><img src="/assets/img/readers/tests/{code}-{n}.webp" alt="{esc(title)} p.{n}" width="600" height="851" loading="lazy" decoding="async">'
                     f'<div><p lang="en">{esc(p["text"])}</p><button type="button" class="rt-play" data-a="a{n}">▶ {Z("聽這一頁", "listen to this page")}</button>'
                     f'<audio id="a{n}" preload="none" src="{aud}"></audio></div></div>')
    qs = []
    for i, q in enumerate(Q):
        opts = "".join(f'<label><input type="radio" name="q{i}" value="{j}"><span lang="en">{esc(o)}</span></label>' for j, o in enumerate(q["options"]))
        GLOSS[_cur[0]].append((q["why_zh"], q["why_en"]))
        qs.append(f'<div class="rt-q" data-a="{q["answer"]}"><b lang="en">{esc(q["q"])}</b>{opts}<p class="rt-why">{esc(q["why_zh"])}</p></div>')
    nxt = f'<a class="btn btn-outline" href="/{HUB}/level-{L + 1}/">{Z(f"下一級：第 {L + 1} 級", f"next: Level {L + 1}")}</a>' if L < total else ""
    prv = f'<a href="/{HUB}/level-{L - 1}/">{Z(f"← 第 {L - 1} 級", f"← Level {L - 1}")}</a>' if L > 1 else ""
    main = f"""<section class="section">
  <div class="wrap">
    <div class="center stack reveal"><span class="eyebrow eyebrow-yellow">{Z("先讀故事", "read the story first")}</span><h2 id="先讀故事">{Z(f"先讀 <em lang=\"en\">{esc(title)}</em>", f"first read {title}")}</h2></div>
    <p class="body center" style="max-width:62ch;margin:14px auto 0">{Z(f"這是 Chris and Cora 分級讀本第 {L} 級第一本的前 {len(pages)} 頁（{words} 個字）。每一頁都可以按「聽這一頁」，聽美式發音朗讀。", f"These are the first {len(pages)} pages ({words} words) of the first Level {L} Chris and Cora reader. Each page has a 'listen' button with American read-aloud audio.")}</p>
    <div class="rt-story">{"".join(story)}</div>
  </div>
</section>
<section class="section bg-soft">
  <div class="wrap">
    <div class="center stack reveal"><span class="eyebrow eyebrow-green">{Z("回答問題", "answer the questions")}</span><h2 id="回答問題">{Z(f"讀完了？回答 <em>{len(Q)} 題</em>", f"done? answer {len(Q)} questions")}</h2></div>
    <p class="body center" style="max-width:62ch;margin:14px auto 0">{Z("答案都在上面的故事裡。可以回去再看一次，答完按「對答案」，每題都有中文解說。", "All answers are in the story above; you may look back. Press 'check answers' for a Chinese explanation of each.")}</p>
    <div class="rt-qs">{"".join(qs)}</div>
    <div class="rt-check"><button type="button" class="btn btn-primary" id="rtCheck">{Z("對答案", "check answers")}</button><span class="rt-score" id="rtScore"></span></div>
    <div class="cta-box reveal" id="rtNext" hidden style="margin-top:26px">
      <span class="eyebrow eyebrow-yellow">{Z("讀完整本", "read the whole book")}</span>
      <h2 id="讀完整本" style="margin-top:14px">{Z(f"故事還沒完：<em lang=\"en\">{esc(title)}</em> 一共 20 頁", f"the story goes on: {title} has 20 pages")}</h2>
      <p class="body" style="max-width:560px;margin:16px auto 0">{Z(f"Chris and Cora 分級讀本 12 級 36 本，故事在台灣、用學校的教育部字表，每本都可以邊聽邊讀。第 1 級 3 本整本免費讀。", "Chris and Cora graded readers: 12 levels, 36 books set in Taiwan, using the school's MOE word list, all with read-aloud. Level 1 (3 books) is free in full.")}</p>
      <div class="cta-row"><a class="btn btn-primary" href="/{READERS}/" data-book="readers" data-book-item="reading-test-{L}">{Z("看 36 本分級讀本", "see the 36 readers")}</a>{nxt}</div>
    </div>
    <p class="body center" style="margin-top:18px;font-size:14px">{prv}{" ・ " if prv else ""}<a href="/{HUB}/">{Z("全部 12 級閱讀測驗", "all 12 reading tests")}</a></p>
  </div>
</section>
{JS}
"""
    slug = f"{HUB}/level-{L}"
    ttl = Z(f"國小英文閱讀測驗第 {L} 級：{title}", f"Elementary English reading test, Level {L}: {title}")
    desc = Z(f"免費國小英文閱讀測驗第 {L} 級（{st_zh}）：先讀 Chris and Cora 分級讀本《{title}》前 {len(pages)} 頁、可以聽朗讀，再線上回答 {len(Q)} 題，每題附中文解說。",
             f"Free elementary English reading test, Level {L} ({st_en}): read the first pages of {title} with read-aloud audio, then answer {len(Q)} questions online, each with a Chinese explanation.")
    crumb = f'<a href="/">首頁</a> ／ <a href="/{HUB}/">{Z("國小英文閱讀測驗", "elementary reading tests")}</a> ／ {Z(f"第 {L} 級", f"Level {L}")}'
    h1 = Z(f'<span class="h1s"><em>國小英文閱讀測驗</em>第 {L} 級</span><br><span class="h1s" lang="en">{esc(title)}</span>', f"Elementary English reading test, Level {L}: {title}")
    lead = Z(f"{st_zh}的孩子適合這一級。先讀故事、聽朗讀，再回答 {len(Q)} 題；答完立刻看到分數和每一題的中文解說，不用註冊。",
             f"For children who are {st_en}. Read and listen, then answer {len(Q)} questions; the score and a Chinese explanation for each appear right away, no sign-up.")
    url = shell(slug, ttl + "｜埃森美語", desc, crumb, h1, lead, f"/assets/img/readers/tests/{code}-{pages[0]['n']}.webp", f"{title} 插圖", main)
    return slug, ttl + "｜埃森美語", desc, url, code, title, words, len(Q)


def hub_page(rows):
    _cur[0] = "hub"
    cards = "".join(f'<a class="rt-level" href="/{HUB}/level-{L}/"><img src="/assets/img/readers/covers/{code}.webp" alt="{esc(title)} 封面" width="320" height="454" loading="lazy" decoding="async">'
                    f'<span><span class="lv">{Z(f"第 {L} 級", f"Level {L}")}・{stage(L)[0]}</span><b lang="en">{esc(title)}</b><small>{Z(f"{w} 字・{nq} 題", f"{w} words, {nq} questions")}</small></span></a>'
                    for L, code, title, w, nq in rows)
    steps = [Z("<b>不知道從哪一級開始？</b>先試第 3 級：讀得很順就往上跳，卡住就往下。", "<b>Not sure where to start?</b> Try Level 3: if it is easy go up, if it is hard go down."),
             Z("<b>先聽一次，再自己讀一次。</b>每一頁都有朗讀，聽完再讀，生字比較記得住。", "<b>Listen once, then read it yourself.</b> Every page has read-aloud; listening first helps new words stick."),
             Z("<b>答案都在故事裡。</b>可以回去找，找答案本身就是閱讀練習。", "<b>The answers are in the story.</b> Looking back is part of the reading practice.")]
    main = f"""<section class="section">
  <div class="wrap">
    <div class="center stack reveal"><span class="eyebrow eyebrow-yellow">{Z("12 級", "12 levels")}</span><h2 id="12-級閱讀測驗">{Z("12 級，<em>由淺到深</em>", "12 levels, easy to hard")}</h2></div>
    <div class="rt-levels reveal">{cards}</div>
  </div>
</section>
<section class="section bg-soft">
  <div class="wrap" style="max-width:760px">
    <div class="center stack reveal"><span class="eyebrow eyebrow-green">{Z("怎麼用", "how to use")}</span><h2 id="怎麼用">{Z("三個<em>小建議</em>", "three tips")}</h2></div>
    <ol class="rt-steps reveal">{"".join(f"<li>{s}</li>" for s in steps)}</ol>
    <p class="body center" style="margin-top:8px">{Z(f"每一份測驗都是 <a href='/{READERS}/'>Chris and Cora 分級讀本</a>的真實內頁：12 級 36 本，故事在台灣，用學校的教育部 1,200 字表。", f"Every test is real pages from the Chris and Cora readers: 12 levels, 36 books set in Taiwan, using the school's MOE 1,200-word list.")}</p>
    <p class="body center" style="margin-top:8px">{Z("想先讀孩子聽過的故事？<a href='/english-stories/'>經典英文故事</a>：三隻小豬、龜兔賽跑、灰姑娘，每篇都有中文對照和朗讀。", "Rather start with a story your child already knows? Classic stories in English (link): Three Little Pigs, Tortoise and the Hare, Cinderella, each with Chinese and read-aloud.")}</p>
  </div>
</section>
"""
    title = Z("國小英文閱讀測驗：12 級免費線上作答，附故事朗讀與中文解說", "Elementary English reading tests: 12 free levels with read-aloud and Chinese explanations")
    desc = Z("免費國小英文閱讀測驗 12 級：每一級先讀一段真實的英文故事、可以聽美式朗讀，再線上回答問題、立刻對答案，每題都有中文解說，不用註冊、不用下載。",
             "12 free elementary English reading tests: read a real story with American read-aloud, answer online, check instantly with Chinese explanations, no sign-up.")
    h1 = Z('<span class="h1s"><em>國小英文閱讀測驗</em></span><br><span class="h1s">12 級，免費線上作答</span>', "Elementary English reading tests: 12 levels, free online")
    lead = Z("先讀一段英文故事、聽朗讀，再回答問題。答完立刻看到分數，每題都有中文解說。故事來自埃森美語自己寫的 Chris and Cora 分級讀本。",
             "Read an English story, listen, then answer. The score and a Chinese explanation appear right away. The stories are from our own Chris and Cora readers.")
    shell(HUB, title + "｜埃森美語", desc, f'<a href="/">首頁</a> ／ {Z("國小英文閱讀測驗", "elementary reading tests")}', h1, lead,
          "/assets/img/readers/covers/5a.webp", "Chris and Cora 分級讀本封面", main)
    return HUB, title + "｜埃森美語", desc


def main():
    Q = json.load(open(QFILE, encoding="utf-8"))
    rows, made = [], []
    for L in range(1, 13):
        slug, ttl, desc, url, code, title, w, nq = test_page(L, Q[str(L)], 12)
        rows.append((L, code, title, w, nq))
        made.append((slug, ttl, desc))
        print("  wrote", slug)
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
    L = ["# 國小英文閱讀測驗 pages — Chinese with English (2026-11-23)", ""]
    for page, rows_ in GLOSS.items():
        L += [f"## {page}", ""]
        for zh, en in rows_:
            L += [f"- {re.sub(r'<[^>]+>', '', zh)}", f"  - *{re.sub(r'<[^>]+>', '', en)}*"]
        L.append("")
    open(GLOSS_OUT, "w", encoding="utf-8").write("\n".join(L))
    print("  gloss:", GLOSS_OUT)


if __name__ == "__main__":
    main()

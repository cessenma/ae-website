#!/usr/bin/env python3
"""
Per-word pronunciation pages (pilot, 2026-10-21): /pronunciation/<word>/ and the hub /pronunciation/.

Why: searches like 「X 發音」「X 怎麼唸」「X kk」 click at ~3.5% where the site appears (translation
lookups: 0.6%), and the site already gets impressions for "television kk", "giraffe kk" … with no
page per word. Pilot = 300 words of the MOE 1200 list; readout ~2026-12-28: scale toward 2,000 if
≥0.1 clicks/page/day and rising, stop if <0.02 (plan: ~/Downloads/AE-3X-PLAN-2026-10-19.md).

Data: tools/data/words/pilot.json (computed from CMUdict with kk_lookup's KK rules: KK, syllables,
stress, rhymes, confusable pairs) + tools/data/words/content.json (written per word: the Taiwanese
learner's typical mistake and its fix, two examples, part of speech). A word without content is skipped.
Audio = the device's own speech engine (speechSynthesis), normal and slow; GA4 event word_play.

    python3 tools/build_word_pages.py      # all pages + hub + sitemap entries, then run seo_build.py
"""
import html, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from word_sounds import SOUNDS, split
import seo_build as S

SITE = S.SITE
ORIGIN = "https://americanenglish.com.tw"
DATA = json.load(open(os.path.join(HERE, "data/words/pilot.json"), encoding="utf-8"))
CONTENT = json.load(open(os.path.join(HERE, "data/words/content.json"), encoding="utf-8")) \
    if os.path.exists(os.path.join(HERE, "data/words/content.json")) else {}
SHELL = os.path.join(SITE, "kk-phonetic-chart/index.html")
PUBLISHED = "2026-10-21"
ORG = ORIGIN + "/#organization"
W = {d["slug"]: d for d in DATA if d["slug"] in CONTENT}
ORDER = sorted(W, key=str.lower)
esc = html.escape

def width(t):
    return S.snippet_width(t)

def title_for(d):
    w, k = d["word"], d["kk"]
    for t in (f"{w} 發音怎麼唸？KK 音標 [{k}]、慢速示範與常見錯誤", f"{w} 發音怎麼唸？KK 音標 [{k}]＋慢速示範",
              f"{w} 發音：KK 音標 [{k}]＋慢速示範", f"{w} 發音：KK 音標 [{k}]"):
        if width(t) <= 60:
            return t + "｜埃森美語"
    return f"{w} 發音｜埃森美語"

def syl_text(d):
    return "單音節字" if d["n_syll"] == 1 else f"{d['n_syll']} 個音節，重音在第 {d['stress']} 個音節"

def desc_for(d, c):
    base = (f"{d['word']}（{d['zh']}）怎麼唸？KK 音標 [{d['kk']}]，{syl_text(d)}。"
            f"點一下聽正常速度和慢速發音，再看台灣學生最常唸錯的地方和例句。")
    if width(base) > 160:
        base = f"{d['word']}（{d['zh']}）怎麼唸？KK 音標 [{d['kk']}]，{syl_text(d)}。可聽正常與慢速發音，附常見錯誤與例句。"
    return base

def say(text, label="🔊"):
    return f'<button type="button" class="say" data-say="{esc(text)}" aria-label="播放 {esc(text)} 的發音">{label}</button>'

def link_word(slug, text=None):
    text = text or (W[slug]["word"] if slug in W else slug)
    return f'<a href="/pronunciation/{slug}/">{esc(text)}</a>' if slug in W else esc(text)

def sound_examples(sym, own):
    """Up to three other pilot words that use this sound, as links."""
    out = []
    for s in ORDER:
        if s != own and sym in split(W[s]["kk"]):
            out.append(link_word(s))
            if len(out) == 3:
                break
    return "、".join(out) or "—"

def body(d, c):
    w, slug, kk = d["word"], d["slug"], d["kk"]
    sylls = c.get("sylls") or ""
    if sylls.replace("·", "") != re.sub("[ˈˌ]", "", kk) or sylls.count("·") + 1 != d["n_syll"]:
        sylls = "·".join(s for s, _ in d["sylls"])      # written against an older KK: use the computed split
    parts = sylls.split("·")
    stress_i = d["stress"] - 1 if d["n_syll"] > 1 else -1
    chips = "".join(f'<span class="{"st" if i == stress_i else ""}">{esc(p)}</span>' for i, p in enumerate(parts))
    card = (f'<section class="section"><div class="wrap"><div class="wd-card reveal">'
            f'<div class="wd-word" lang="en">{esc(w)}</div><div class="wd-kk">[{esc(kk)}]</div>'
            f'<div class="wd-btns"><button type="button" data-say="{esc(w)}" data-rate="1">🔊 正常速度</button>'
            f'<button type="button" class="slow" data-say="{esc(w)}" data-rate="0.55">🐢 慢速</button></div>'
            f'<div class="wd-syl" aria-label="音節">{chips}</div>'
            f'<p class="wd-meta">{esc(syl_text(d))}　·　{esc(c["pos_zh"])}：{esc(d["zh"])}</p>'
            f'<p class="wd-note" hidden>這台裝置沒有英文語音，無法播放；可以換一個瀏覽器，或用手機開啟。</p>'
            f'</div></div></section>')
    tip = f'<p>{esc(c["tip_zh"])}</p>'
    extra = "".join(f'<li>{esc(c[k])}</li>' for k in ("variant_zh", "spelling_zh") if c.get(k))
    s1 = (f'<section class="section bg-soft"><div class="wrap"><div class="center stack reveal">'
          f'<h2 id="怎麼唸">{esc(w)} 怎麼唸？台灣學生最常唸錯的地方</h2></div>'
          f'<div class="prose reveal">{tip}{"<ul>" + extra + "</ul>" if extra else ""}</div></div></section>')
    rows = "".join(f'<tr><th><a href="/kk-phonetic-chart/">[{esc(sym)}]</a></th><td>{esc(SOUNDS[sym][0])}</td>'
                   f'<td>{sound_examples(sym, slug)}</td></tr>'
                   for sym in dict.fromkeys(split(kk)) if sym in SOUNDS)
    rh = "".join(f'<li>{link_word(r)}</li>' for r in d["rhymes"][:8])
    pairs = "".join(f'<li>{esc(w)} [{esc(kk)}] {say(w)}　vs　{link_word(p["word"])} '
                    f'[{esc(W[p["word"]]["kk"]) if p["word"] in W else ""}] {say(p["word"])}</li>'
                    for p in d["pairs"][:4] if p["word"] in W)
    s2 = (f'<section class="section"><div class="wrap"><div class="center stack reveal">'
          f'<h2 id="用到的音">{esc(w)} 用到的音與相似字</h2></div>'
          f'<div class="compare reveal"><table><thead><tr><th>KK 音標</th><th>嘴巴怎麼做</th><th>也有這個音的字</th></tr></thead>'
          f'<tbody>{rows}</tbody></table></div>'
          + (f'<div class="prose reveal"><h3>跟 {esc(w)} 押韻的字</h3><ul class="wd-chips">{rh}</ul></div>' if rh else "")
          + (f'<div class="prose reveal"><h3>容易跟 {esc(w)} 唸混的字</h3><ul class="wd-pairs">{pairs}</ul></div>' if pairs else "")
          + '</div></section>')
    ex = "".join(f'<li><span lang="en">{esc(x["en"])}</span> {say(x["en"])}<br><span class="zh">{esc(x["zh"])}</span></li>'
                 for x in c["examples"])
    s3 = (f'<section class="section bg-soft"><div class="wrap"><div class="center stack reveal">'
          f'<h2 id="例句">{esc(w)} 例句</h2></div><div class="prose reveal"><ul class="wd-ex">{ex}</ul></div></div></section>')
    if d["n_syll"] > 1:
        q2 = (f"{w} 的重音在哪裡？", f"重音在第 {d['stress']} 個音節 {parts[stress_i]}，KK 音標裡的「ˈ」就標在這個音節前面；"
                                    f"其他音節唸得比較輕、比較短。")
    else:
        end = split(kk)[-1] if split(kk) else ""
        q2 = (f"{w} 有幾個音節？", f"{w} 只有 1 個音節，一口氣唸完。" + (
            f"字尾的 [{end}] 也要清楚唸出來，後面不要多加一個母音。" if end not in
            ("i", "ɪ", "e", "ɛ", "æ", "ɑ", "ɔ", "o", "ʊ", "u", "ʌ", "ə", "ɝ", "ɚ", "aɪ", "aʊ", "ɔɪ")
            else "母音要唸飽滿，不要太短。"))
    faq = [(f"{w} 的 KK 音標怎麼寫？", f"{w} 的 KK 音標是 [{kk}]（美式發音），分成 {d['n_syll']} 個音節：{' · '.join(parts)}。"), q2]
    fq = "".join(f'<div class="faq-item"><h3 class="faq-h"><button class="faq-q" aria-expanded="false">{esc(q)}'
                 f'<span class="pm"></span></button></h3><div class="faq-a"><p>{esc(a)}</p></div></div>' for q, a in faq)
    i = ORDER.index(slug)
    prv, nxt = ORDER[i - 1] if i else None, ORDER[i + 1] if i + 1 < len(ORDER) else None
    nav = (f'<nav class="wd-nav" aria-label="其他單字">'
           + (f'<a href="/pronunciation/{prv}/">← {esc(W[prv]["word"])}</a>' if prv else "<span></span>")
           + '<a href="/pronunciation/">全部 300 個單字發音</a>'
           + (f'<a href="/pronunciation/{nxt}/">{esc(W[nxt]["word"])} →</a>' if nxt else "<span></span>") + '</nav>')
    s4 = (f'<section class="section"><div class="wrap"><div class="center stack reveal">'
          f'<h2 id="常見問題">{esc(w)} 發音常見問題</h2></div><div class="faq">{fq}</div>'
          f'<p class="wd-more">其他單字的 KK 音標，可以用 <a href="/kk-phonetic-chart/">KK 音標表</a>上方的查詢框；'
          f'這個字在<a href="/moe-1200-words-guide/">教育部 1200 單字表</a>裡。</p>{nav}</div></section>')
    cta = ('<section class="section bg-blue"><div class="wrap"><div class="center stack reveal">'
           '<h2>發音要有人聽過，才知道對不對</h2><p class="body">在埃森美語，美籍老師每堂課都會聽孩子把字唸出來、當場修正。'
           '想知道孩子現在的發音程度，可以先用 LINE 問我們。</p>'
           '<a class="btn btn-primary" href="/line/">加 LINE 問我們</a></div></div></section>')
    return card + s1 + s2 + s3 + s4 + cta + SCRIPT

SCRIPT = """<script>(function(){var ss=window.speechSynthesis,v=null;function pick(){var a=ss?ss.getVoices():[];
v=a.filter(function(x){return/^en[-_]US/i.test(x.lang)})[0]||a.filter(function(x){return/^en/i.test(x.lang)})[0]||null;}
if(ss){pick();ss.onvoiceschanged=pick;}document.addEventListener('click',function(e){var b=e.target.closest('[data-say]');if(!b)return;
if(!ss){var n=document.querySelector('.wd-note');if(n)n.hidden=false;return;}ss.cancel();var u=new SpeechSynthesisUtterance(b.getAttribute('data-say'));
u.lang='en-US';if(v)u.voice=v;u.rate=parseFloat(b.getAttribute('data-rate')||'0.9');ss.speak(u);
if(window.gtag)gtag('event','word_play',{word:document.querySelector('.wd-word')?document.querySelector('.wd-word').textContent:'',rate:u.rate,page_path:location.pathname});});})();</script>"""

def page(slug, title, desc, h1, crumbs, hero, main_html, ld):
    shell = open(SHELL, encoding="utf-8").read()
    url = f"{ORIGIN}/{slug}/"
    head = shell.split("</head>")[0]
    for pat, rep in ((r"<title>.*?</title>", f"<title>{esc(title)}</title>"),
                     (r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{esc(desc)}">'),
                     (r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{url}">'),
                     (r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{esc(h1)}">'),
                     (r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{esc(desc)}">'),
                     (r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{url}">'),
                     (r'<meta property="og:image" content="[^"]*">', f'<meta property="og:image" content="{ORIGIN}/assets/img/og-default.jpg">')):
        head = re.sub(pat, lambda m: rep, head, flags=re.S)
    head = re.sub(r'<script type="application/ld\+json">.*?</script>\s*', "", head, flags=re.S)
    head = head.rstrip() + '\n<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False, separators=(",", ":")) + "</script>\n"
    bc = " › ".join(f'<a href="{h}">{esc(t)}</a>' for t, h in crumbs[:-1]) + f" › {esc(crumbs[-1][0])}"
    main = (f'<main id="top"><section class="page-hero"><div class="bg-deco"></div><div class="wrap">'
            f'<div class="breadcrumb reveal">{bc}</div><h1 class="reveal d1">{h1}</h1><div class="divider reveal d1"></div>'
            f'<p class="body reveal d2">{hero}</p></div></section>{main_html}</main>')
    tail = shell.split("</head>", 1)[1]
    tail = re.sub(r'<main id="top">.*?</main>', lambda m: main, tail, flags=re.S)
    d = os.path.join(SITE, slug)
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(head + "</head>" + tail)

def word_page(slug):
    d, c = W[slug], CONTENT[slug]
    url = f"{ORIGIN}/pronunciation/{slug}/"
    ld = {"@context": "https://schema.org", "@type": "LearningResource", "name": f"{d['word']} 發音與 KK 音標",
          "description": desc_for(d, c), "inLanguage": "zh-Hant-TW", "url": url, "isAccessibleForFree": True,
          "learningResourceType": "pronunciation guide", "educationalLevel": "國小、國中",
          "about": {"@type": "DefinedTerm", "name": d["word"], "description": d["zh"],
                    "inDefinedTermSet": "教育部國民中小學英語基本 1200 字"},
          "publisher": {"@id": ORG}, "author": {"@id": ORG}, "datePublished": PUBLISHED}
    hero = (f'<strong lang="en">{esc(d["word"])}</strong> 是「{esc(d["zh"])}」，教育部國中小基本 1200 字之一。'
            f'下面可以點按鈕聽正常速度和慢速發音，再看台灣學生最常唸錯的地方。')
    page(f"pronunciation/{slug}", title_for(d), desc_for(d, c), f'{esc(d["word"])} 發音：KK 音標 [{esc(d["kk"])}]',
         [("首頁", "/"), ("英文單字發音", "/pronunciation/"), (d["word"], "")], hero, body(d, c), ld)

def hub():
    groups = {}
    for s in ORDER:
        groups.setdefault(W[s]["word"][0].upper(), []).append(s)
    secs = []
    for i, (L, ss) in enumerate(sorted(groups.items())):
        rows = "".join(f'<tr><th>{link_word(s)}</th><td>[{esc(W[s]["kk"])}]</td><td>{esc(W[s]["zh"])}</td></tr>' for s in ss)
        secs.append(f'<section class="section{" bg-soft" if i % 2 else ""}"><div class="wrap"><div class="center stack reveal">'
                    f'<h2 id="{L}">{L} 開頭的單字</h2></div><div class="compare reveal"><table><thead><tr><th>單字</th>'
                    f'<th>KK 音標</th><th>中文</th></tr></thead><tbody>{rows}</tbody></table></div></div></section>')
    n = len(ORDER)
    title = f"英文單字發音：{n} 個常用字 KK 音標、怎麼唸＋慢速示範｜埃森美語"
    desc = (f"英文單字怎麼唸？教育部 1200 字裡 {n} 個常用單字，每個都有 KK 音標、音節與重音、"
            f"正常和慢速發音，以及台灣學生最常唸錯的地方。依字母查，點單字看完整發音頁。")
    intro = (f'<section class="section"><div class="wrap"><div class="prose reveal"><p>這裡收錄教育部國中小基本 1200 字裡 {n} 個'
             f'最值得練的單字：多音節、重音容易放錯，或含有 [θ]、[ð]、[v]、[æ]、[ɝ] 這些台灣學生常唸錯的音。'
             f'每個單字頁都有 KK 音標、音節拆解、正常和慢速發音，還有一段「最常唸錯的地方」。</p>'
             f'<p>想查清單以外的字，可以用 <a href="/kk-phonetic-chart/">KK 音標表</a>上方的查詢框；'
             f'想先認識 41 個音，從 <a href="/english-pronunciation/">英文發音完整指南</a>開始。</p></div></div></section>')
    ld = {"@context": "https://schema.org", "@type": "CollectionPage", "name": f"英文單字發音：{n} 個常用字",
          "url": ORIGIN + "/pronunciation/", "inLanguage": "zh-Hant-TW", "description": desc,
          "publisher": {"@id": ORG}, "datePublished": PUBLISHED}
    page("pronunciation", title, desc, f"英文單字發音：{n} 個常用字怎麼唸", [("首頁", "/"), ("英文單字發音", "")],
         "每個單字都有 KK 音標、音節與重音、正常和慢速發音，以及台灣學生最常唸錯的地方。", intro + "".join(secs), ld)

def add_to_sitemap(paths):
    sm = os.path.join(SITE, "sitemap.xml")
    xml = open(sm, encoding="utf-8").read()
    anchor = "</urlset>"
    added = 0
    for p in paths:
        if f"<loc>{ORIGIN}/{p}/</loc>" in xml:
            continue
        xml = xml.replace(anchor, f"  <url><loc>{ORIGIN}/{p}/</loc><changefreq>monthly</changefreq>"
                                  f"<priority>{'0.7' if p == 'pronunciation' else '0.5'}</priority></url>\n" + anchor, 1)
        added += 1
    open(sm, "w", encoding="utf-8").write(xml)
    return added

if __name__ == "__main__":
    for s in ORDER:
        word_page(s)
    hub()
    n = add_to_sitemap(["pronunciation"] + [f"pronunciation/{s}" for s in ORDER])
    print(f"{len(ORDER)} word pages + hub; {len(DATA) - len(ORDER)} words still without content; sitemap +{n}")

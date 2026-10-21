#!/usr/bin/env python3
"""
KK 音標查詢 / 英文發音查詢: type a word, see its KK transcription, hear it.

Why (2026-10-18): 英文發音 is the largest winnable search pool and Google gives it to tools
(Translate, Cambridge); /english-pronunciation/ had no lookup and ~0 impressions for it. The KK
chart already holds 「kk 音標 發音 查詢」 at position 1.9 (553 impr/28d, 19% CTR) without a
real lookup. So both pages get the same box.

Data: the CMU Pronouncing Dictionary (tools/data/cmudict/, BSD licence, 135k words, General
American) converted ARPAbet → KK here, sharded by the first two letters into
assets/kk/<xx>.json (each a few KB), fetched only for the word typed. Sound: the device's own
en-US speech voice (speechSynthesis) — no audio files, no API key.

Usage:  python3 tools/kk_lookup.py          # rebuild shards + re-inject both page blocks
"""
import os, re, json, hashlib, collections

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(SITE, "tools/data/cmudict/cmudict.dict")
OUT = os.path.join(SITE, "assets/kk")
PAGES = {"kk-phonetic-chart": "kk", "english-pronunciation": "pron"}
START, END = "<!-- AE:KKLOOKUP start -->", "<!-- AE:KKLOOKUP end -->"

VOW = {"AA": "ɑ", "AE": "æ", "AO": "ɔ", "AW": "aʊ", "AY": "aɪ", "EH": "ɛ", "EY": "e",
       "IH": "ɪ", "OW": "o", "OY": "ɔɪ", "UH": "ʊ", "UW": "u"}
CON = {"B": "b", "CH": "tʃ", "D": "d", "DH": "ð", "F": "f", "G": "g", "HH": "h", "JH": "dʒ",
       "K": "k", "L": "l", "M": "m", "N": "n", "NG": "ŋ", "P": "p", "R": "r", "S": "s",
       "SH": "ʃ", "T": "t", "TH": "θ", "V": "v", "W": "w", "Y": "j", "Z": "z", "ZH": "ʒ"}
ONSETS = {tuple(x.split()) for x in """P R|P L|B R|B L|T R|D R|K R|K L|G R|G L|F R|F L|TH R|SH R
|S P|S T|S K|S M|S N|S L|S W|T W|D W|K W|G W|TH W|P Y|B Y|F Y|V Y|M Y|K Y|HH Y|G Y
|S P R|S P L|S T R|S K R|S K W|S K Y|S P Y""".replace("\n", "").split("|")}

def is_vowel(p):
    return p[:2] in VOW or p[:2] in ("AH", "ER", "IY")

def normalize(phones):
    """CMU writes the r of around / arrive / every as an unstressed ER before a vowel (ER0 AW1 …),
    which gave [ɚˈaʊnd]; Taiwan KK writes [əˈraʊnd] — a schwa, then r starting the next syllable."""
    out = []
    for i, p in enumerate(phones):
        if p == "ER0" and i + 1 < len(phones) and is_vowel(phones[i + 1]):
            out += ["AH0", "R"]
        elif p in ("IY2", "IH2") and i == len(phones) - 1:
            out.append(p[:-1] + "0")       # nobody, everybody: CMU's final IY2 → an unstressed [ɪ], as KK writes it
        else:
            out.append(p)
    # two primary stresses (engineer EH1…IH1, thirteen ER1…IY1): the LAST is the main one, the
    # earlier ones become secondary — thirteen is θɝˈtin, which is how 13 differs from 30
    ones = [i for i, p in enumerate(out) if is_vowel(p) and p.endswith("1")]
    for i in ones[:-1]:
        out[i] = out[i][:-1] + "2"
    # a short [ɪ]/[ʊ] secondary right after the main stress is a CMU artefact (hospital IH2,
    # badminton IH2): KK writes [ˈhɑspɪtḷ], [ˈbædmɪntṇ]
    vs = [i for i, p in enumerate(out) if is_vowel(p)]
    for a_, b_ in zip(vs, vs[1:]):
        if out[a_].endswith("1") and out[b_] in ("IH2", "UH2"):     # not ʌ/u: grandmother, bathroom keep theirs
            out[b_] = out[b_][:-1] + "0"
    return out

# Single words where CMU's first entry is not the form Taiwan's KK dictionaries teach.
OVERRIDES = {"every": "EH1 V R IY0", "even": "IY1 V AH0 N", "sometimes": "S AH1 M T AY2 M Z",
             "actually": "AE1 K CH UH0 AH0 L IY0", "usually": "Y UW1 ZH UH0 AH0 L IY0", "unhappy": "AH2 N HH AE1 P IY0",
             "thirty": "TH ER1 T IY0"}      # CMU lists the flap [d] first; Taiwan dictionaries write [ˈθɝtɪ]

def kk(phones):
    """ARPAbet (with stress digits) → KK string, stress marks before the stressed syllable."""
    phones = normalize(phones)
    ph = phones[:]
    vidx = [i for i, p in enumerate(ph) if is_vowel(p)]
    out = []                                       # one symbol string per phone
    for i, p in enumerate(ph):
        base, st = (p[:-1], p[-1]) if p[-1].isdigit() else (p, None)
        nxt = ph[i + 1] if i + 1 < len(ph) else None
        prv = ph[i - 1] if i else None
        last_v = i == (vidx[-1] if vidx else -1)
        if base == "AH":
            if st == "0" and nxt in ("L", "N") and prv and not is_vowel(prv) and prv not in ("R", "W", "Y", "L", "N") \
               and (i + 2 >= len(ph) or not is_vowel(ph[i + 2])) and (nxt == "L" or prv in ("T", "D")):
                out.append("")                     # syllabic ḷ / ṇ: the vowel folds into the consonant
                ph[i + 1] = "L_SYL" if nxt == "L" else "N_SYL"
                continue
            out.append("ʌ" if st in ("1", "2") else "ə")
        elif base == "ER":
            if st == "0" and prv and prv[:2] in ("AY", "AW") and i == len(ph) - 1:
                out.append("r")                    # fire /faɪr/, hour /aʊr/
            else:
                out.append("ɝ" if st in ("1", "2") else "ɚ")
        elif base == "IY":
            out.append("ɪ" if (st == "0" or nxt == "R") else "i")   # happy /ˈhæpɪ/, here /hɪr/
        elif base in VOW:
            out.append(VOW[base])
        elif base == "L_SYL":
            out.append("ḷ")
        elif base == "N_SYL":
            out.append("ṇ")
        else:
            out.append(CON.get(base, ""))
    # stress: mark goes before the onset of the stressed syllable (maximal legal onset)
    marks = {}
    # syllable nuclei: every vowel except an ER that became plain r (fire /faɪr/ is one syllable)
    vowels = [i for i, p in enumerate(phones) if is_vowel(p) and out[i] != "r"]
    if len(vowels) > 1:
        for k, vi in enumerate(vowels):
            st = phones[vi][-1]
            if st not in ("1", "2"):
                continue
            lo = vowels[k - 1] + 1 if k else 0
            cluster = [ph[j] for j in range(lo, vi)]
            start = vi
            if k == 0:
                start = lo
            else:
                for n in range(len(cluster), 0, -1):
                    cand = tuple(cluster[-n:])
                    if (n == 1 and cand[0] not in ("NG",) and not cand[0].endswith("_SYL")) or cand in ONSETS:
                        start = vi - n
                        break
            marks[start] = "ˈ" if st == "1" else "ˌ"
    return "".join(marks.get(i, "") + s for i, s in enumerate(out))

WORD_RE = re.compile(r"^[a-z]+(?:'[a-z]+)?$")

def build():
    data = collections.defaultdict(dict)
    for line in open(SRC, encoding="utf-8"):
        line = line.split("#")[0].strip()
        if not line:
            continue
        w, *phones = line.split()
        w = re.sub(r"\(\d+\)$", "", w)
        if not WORD_RE.match(w):
            continue
        if w in OVERRIDES:
            phones = OVERRIDES[w].split()
        t = kk(phones)
        key = (w[:2] if len(w) > 1 and w[1].isalpha() else w[0] + "_")
        cur = data[key].get(w)
        if cur is None:
            data[key][w] = t
        elif t not in cur.split("|") and cur.count("|") < 1:
            data[key][w] = cur + "|" + t
    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):
        if f.endswith(".json"):
            os.remove(os.path.join(OUT, f))
    h = hashlib.md5()
    total = 0
    for key in sorted(data):
        s = json.dumps(data[key], ensure_ascii=False, separators=(",", ":"), sort_keys=True)
        open(os.path.join(OUT, key + ".json"), "w", encoding="utf-8").write(s)
        h.update(s.encode())
        total += len(data[key])
    return total, len(data), h.hexdigest()[:8]

TESTS = {"cat": "kæt", "happy": "ˈhæpɪ", "water": "ˈwɔtɚ", "little": "ˈlɪtḷ", "button": "ˈbʌtṇ",
         "music": "ˈmjuzɪk", "teacher": "ˈtitʃɚ", "computer": "kəmˈpjutɚ", "banana": "bəˈnænə",
         "apple": "ˈæpḷ", "people": "ˈpipḷ", "the": "ðə", "fire": "faɪr", "here": "hɪr", "bird": "bɝd",
         "student": "ˈstudṇt", "very": "ˈvɛrɪ", "garden": "ˈgɑrdṇ", "lemon": "ˈlɛmən", "sing": "sɪŋ",
         "thank": "θæŋk", "mother": "ˈmʌðɚ", "pleasure": "ˈplɛʒɚ", "about": "əˈbaʊt", "english": "ˈɪŋglɪʃ", "around": "əˈraʊnd", "camera": "ˈkæmərə", "different": "ˈdɪfərənt", "nobody": "ˈnoˌbɑdɪ", "engineer": "ˌɛndʒəˈnɪr", "thirteen": "ˌθɝˈtin", "hospital": "ˈhɑspɪtḷ"}

def selftest():
    d = {}
    for line in open(SRC, encoding="utf-8"):
        w, *p = line.split("#")[0].split()
        if w in TESTS and w not in d:
            d[w] = kk(p)
    bad = {w: (d.get(w), want) for w, want in TESTS.items() if d.get(w) != want}
    return bad

BLOCK = """<!-- AE:KKLOOKUP start -->
<section class="section kkl-sec" id="kk-lookup"><div class="wrap">
<div class="center stack reveal"><h2>{h2}</h2><p class="body">{lead}</p></div>
<div class="kkl reveal">
<form class="kkl-f" onsubmit="return false"><label class="sr" for="kkl-in">輸入英文單字或句子</label>
<input id="kkl-in" type="search" inputmode="latin" autocomplete="off" autocapitalize="off" spellcheck="false" maxlength="80" placeholder="輸入英文單字或句子，例如 water">
<button type="submit" class="btn btn-primary" id="kkl-go">查詢</button></form>
<div class="kkl-chips">{chips}</div>
<div id="kkl-out" aria-live="polite"></div>
<p class="kkl-note">音標由美式發音字典（CMU Pronouncing Dictionary，約 13 萬字）自動轉成 KK，少數字可能和課本寫法略有不同；聲音是你手機或電腦內建的美式語音。符號看不懂？對照 <a href="/kk-phonetic-chart/">KK 音標表</a>。</p>
</div></div></section>
<style>.kkl{{max-width:720px;margin:18px auto 0;background:#fff;border-radius:20px;box-shadow:var(--card-shadow);padding:18px}}
.kkl-f{{display:flex;gap:8px}}.kkl-f input{{flex:1;min-width:0;font-size:18px;padding:12px 14px;border:2px solid rgba(26,39,82,.15);border-radius:12px;font-family:inherit}}
.kkl-f .btn{{white-space:nowrap}}.kkl .sr{{position:absolute;left:-9999px}}
.kkl-chips{{display:flex;flex-wrap:wrap;gap:8px;margin-top:10px}}.kkl-chips button{{border:1px solid rgba(26,39,82,.15);background:#F4FAFF;color:var(--navy);border-radius:999px;padding:6px 12px;font-size:14px;font-family:inherit;cursor:pointer}}
#kkl-out{{margin-top:12px}}.kkl-r{{display:flex;flex-wrap:wrap;align-items:center;gap:6px 12px;padding:10px 0;border-top:1px solid rgba(26,39,82,.08)}}
.kkl-w{{font-weight:700;color:var(--navy);font-size:18px}}.kkl-k{{font-family:'Lucida Sans Unicode','Arial Unicode MS','DejaVu Sans',sans-serif;font-size:20px;color:#0b5cad}}
.kkl-r button{{border:none;background:var(--navy);color:#fff;border-radius:999px;padding:6px 12px;font-size:14px;font-family:inherit;cursor:pointer}}.kkl-r button.s{{background:#5b6b8c}}
.kkl-miss{{color:var(--muted);font-size:14.5px}}.kkl-p{{font-weight:700;font-size:14px;color:var(--blue-ink)}}.kkl-note{{font-size:13px;color:var(--muted);margin-top:12px;line-height:1.6}}</style>
<script>(function(){{var V="{ver}",cache={{}},inp=document.getElementById('kkl-in'),out=document.getElementById('kkl-out'),sent=0;
function key(w){{return w.length>1&&/[a-z]/.test(w[1])?w.slice(0,2):w[0]+'_';}}
function shard(k){{return cache[k]||(cache[k]=fetch('/assets/kk/'+k+'.json?v='+V).then(function(r){{return r.ok?r.json():{{}};}}).catch(function(){{return {{}};}}));}}
function words(s){{return (s.toLowerCase().match(/[a-z]+(?:'[a-z]+)?/g)||[]).slice(0,12);}}
function voice(){{var vs=speechSynthesis.getVoices();return vs.filter(function(v){{return v.lang==='en-US';}})[0]||vs.filter(function(v){{return /^en/.test(v.lang);}})[0];}}
function say(t,rate){{if(!('speechSynthesis' in window))return;speechSynthesis.cancel();var u=new SpeechSynthesisUtterance(t);u.lang='en-US';var v=voice();if(v)u.voice=v;u.rate=rate;speechSynthesis.speak(u);
 if(window.gtag)gtag('event','kk_play',{{page_path:location.pathname}});}}
var PG={pages};
function esc(s){{return s.replace(/[&<>"]/g,function(c){{return {{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}}[c];}});}}
async function look(w){{var d=await shard(key(w));return d[w]||null;}}
async function run(){{var s=inp.value.trim(),ws=words(s);if(!ws.length){{out.innerHTML='';return;}}
 var res=await Promise.all(ws.map(look)),html='',miss=0;
 if(ws.length>1)html+='<div class="kkl-r"><span class="kkl-w">'+esc(s)+'</span><button type="button" data-t="'+esc(s)+'" data-r="0.9">▶ 整句聽</button><button type="button" class="s" data-t="'+esc(s)+'" data-r="0.6">慢速</button></div>';
 ws.forEach(function(w,i){{var k=res[i];if(!k)miss++;
  html+='<div class="kkl-r"><span class="kkl-w">'+esc(w)+'</span>'+(k?'<span class="kkl-k">'+k.split('|').map(function(x){{return '/'+esc(x)+'/';}}).join(' 或 ')+'</span>':'<span class="kkl-miss">查不到這個字，請檢查拼字；仍可按播放聽電腦唸。</span>')+
  '<button type="button" data-t="'+esc(w)+'" data-r="0.9">▶ 聽發音</button><button type="button" class="s" data-t="'+esc(w)+'" data-r="0.6">慢速</button>'+
  (PG.indexOf(w.toLowerCase())>-1?'<a class="kkl-p" href="/pronunciation/'+esc(w.toLowerCase())+'/">完整發音頁 →</a>':'')+'</div>';}});
 out.innerHTML=html;
 if(window.gtag&&sent<20){{sent++;gtag('event','kk_lookup',{{page_path:location.pathname,words:ws.length,found:ws.length-miss}});}}}}
out.addEventListener('click',function(e){{var b=e.target.closest('button[data-t]');if(b)say(b.getAttribute('data-t'),+b.getAttribute('data-r'));}});
document.getElementById('kkl-go').addEventListener('click',run);inp.addEventListener('keydown',function(e){{if(e.key==='Enter'){{e.preventDefault();run();}}}});
document.querySelectorAll('.kkl-chips button').forEach(function(b){{b.addEventListener('click',function(){{inp.value=b.textContent;run();}});}});
if('speechSynthesis' in window)speechSynthesis.getVoices();
// WebMCP (experimental browser API for AI agents): offer the same lookup as a tool where supported
try{{var mc=document.modelContext||navigator.modelContext,tool={{name:'lookup_kk_pronunciation',
 description:'Look up the American English pronunciation of English words in KK phonetic symbols (the notation used in Taiwan). Input: one or more English words.',
 inputSchema:{{type:'object',properties:{{text:{{type:'string',description:'English word or short sentence'}}}},required:['text']}},
 execute:async function(a){{var ws=words(a&&a.text||''),r=await Promise.all(ws.map(look));return {{content:[{{type:'text',text:ws.map(function(w,i){{return w+': '+(r[i]?r[i].split('|').map(function(x){{return '/'+x+'/';}}).join(' or '):'not found');}}).join('\\n')}}]}};}}}};
 if(mc&&mc.registerTool)mc.registerTool(tool);else if(mc&&mc.provideContext)mc.provideContext({{tools:[tool]}});}}catch(e){{}}
}})();</script>
<!-- AE:KKLOOKUP end -->
"""
COPY = {
 "kk": ("KK 音標查詢：輸入單字，馬上看音標、聽發音",
        "不用翻字典：打一個英文字（或一整句），立刻看到 KK 音標，按一下就聽美式發音，還能放慢速度跟著唸。"),
 "pron": ("英文發音查詢：輸入單字或句子，聽發音、看 KK 音標",
          "下面整套發音規則讀起來太長？先查你要的那個字：輸入英文，馬上看到 KK 音標，按一下就聽美式發音，也可以放慢速度。"),
}
CHIPS = ["water", "banana", "comfortable", "vegetable", "thank you", "How are you?"]

def word_pages():
    """Words that have their own page under /pronunciation/ (tools/build_word_pages.py)."""
    d = os.path.join(SITE, "pronunciation")
    return sorted(x for x in os.listdir(d) if os.path.isdir(os.path.join(d, x))) if os.path.isdir(d) else []

def inject(ver):
    for page, kind in PAGES.items():
        fp = os.path.join(SITE, page, "index.html")
        s = open(fp, encoding="utf-8").read()
        h2, lead = COPY[kind]
        chips = "".join(f'<button type="button">{c}</button>' for c in CHIPS)
        blk = BLOCK.format(h2=h2, lead=lead, chips=chips, ver=ver, pages=json.dumps(word_pages()))
        if START in s:
            s = re.sub(re.escape(START) + r".*?" + re.escape(END) + r"\n?", lambda m: blk, s, flags=re.S)
        else:                                     # right after the page hero
            i = s.index('<section class="page-hero">')
            j = s.index("</section>", i) + len("</section>")
            s = s[:j] + "\n" + blk + s[j:].lstrip("\n")
        open(fp, "w", encoding="utf-8").write(s)
        print(f"  /{page}/ lookup block in place")

if __name__ == "__main__":
    bad = selftest()
    for w, (got, want) in bad.items():
        print(f"  selftest {w}: got /{got}/ want /{want}/")
    n, shards, ver = build()
    print(f"{n} words in {shards} shards (assets/kk/), version {ver}; selftest {len(TESTS) - len(bad)}/{len(TESTS)}")
    inject(ver)

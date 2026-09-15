#!/usr/bin/env python3
"""
Per-word pronunciation audio for the reference tables.

Why: the page holding #1 for this cluster ships 376 audio elements — per-symbol
playback is the single measured thing competitors have and this site does not.
A phonetic table you cannot hear is a table you have to already understand.

Scale note: the exam pipeline batches SSML because Azure's free tier throttles to
roughly 20 requests a minute and that bank holds 4,604 lines. Here the vocabulary is
~120 unique example words, so one request per word is fine (≈6 min) and gives clean
per-word files instead of a sprite that needs offset bookkeeping.

Usage:  python3 tools/build_word_audio.py [page ...]
        AZURE_SPEECH_KEY / AZURE_SPEECH_REGION override the credentials file.
"""
import os, re, sys, json, time, html, urllib.request, urllib.error
from bs4 import BeautifulSoup
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from normalize_head import normalize   # BeautifulSoup reorders head attributes; see that file

SITE   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIO  = os.path.join(SITE, "assets/audio/words")
KEYFILE = os.path.expanduser("~/.claude/credentials/azure_speech.txt")
VOICE  = "en-US-AvaMultilingualNeural"      # the site teaches American English
REGION = os.environ.get("AZURE_SPEECH_REGION", "eastasia")
PAGES  = ["english-pronunciation", "kk-phonetic-chart", "phonics-rules-chart",
          "english-numbers-guide", "months-english", "days-of-week-english",
          "colors-english-vocabulary", "fruits-english-vocabulary", "body-parts-english",
          "countries-english", "jobs-english", "animals-english-vocabulary",
          "english-abbreviations-guide", "thank-you-english", "cheer-up-english"]
EXAMPLE_HEADS = ("例字", "例詞", "單字", "字例", "英文", "English", "Country", "國家")

def key():
    k = os.environ.get("AZURE_SPEECH_KEY")
    if k:
        return k.strip()
    try:
        return open(KEYFILE, encoding="utf-8").read().strip()
    except OSError:
        raise SystemExit(f"No Azure key: export AZURE_SPEECH_KEY or write {KEYFILE}")

def slug(w):
    """Words and whole phrases both become safe filenames."""
    return re.sub(r"[^a-z0-9]+", "-", w.lower()).strip("-")[:60]

def synth(word, path, k):
    ssml = (f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" '
            f'xml:lang="en-US"><voice name="{VOICE}">'
            f'<prosody rate="-12%">{html.escape(word)}</prosody></voice></speak>')
    req = urllib.request.Request(
        f"https://{REGION}.tts.speech.microsoft.com/cognitiveservices/v1",
        data=ssml.encode("utf-8"),
        headers={"Ocp-Apim-Subscription-Key": k,
                 "Content-Type": "application/ssml+xml",
                 "X-Microsoft-OutputFormat": "audio-24khz-48kbitrate-mono-mp3",
                 "User-Agent": "ae-word-audio"})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                data = r.read()
            if len(data) < 500:
                raise RuntimeError("suspiciously small audio")
            open(path, "wb").write(data)
            return True
        except urllib.error.HTTPError as e:
            if e.code == 429:                      # free tier throttle
                time.sleep(12 * (attempt + 1)); continue
            print(f"    !! {word}: HTTP {e.code} {e.reason}"); return False
        except Exception as e:
            time.sleep(4 * (attempt + 1))
    print(f"    !! {word}: gave up"); return False

def words_on(page):
    """Example words live in the 例字 column of each reference table."""
    fp = os.path.join(SITE, page, "index.html")
    if not os.path.exists(fp):
        return []
    soup = BeautifulSoup(open(fp, encoding="utf-8").read(), "html.parser")
    out = []
    for tb in soup.find_all("table"):
        first = tb.find("tr")
        heads = [c.get_text(strip=True) for c in first.find_all(["th", "td"])] if first else []
        cols = [i for i, h in enumerate(heads) if any(e in h for e in EXAMPLE_HEADS)]
        if not cols:
            continue
        rows = tb.find_all("tr")
        for ri, tr in enumerate(rows):
            cells = [] if ri == 0 else tr.find_all(["td", "th"])
            for i in cols:
                if i < len(cells):
                    txt = cells[i].get_text(" ", strip=True)
                    for w in re.split(r"[,、，/／・·･;；]", txt):
                        w = w.strip()
                        if re.fullmatch(r"[A-Za-z][A-Za-z' \-]{0,24}", w):
                            out.append(w)
                        elif (len(w) <= 44 and w[:1].isupper() and w[-1:] in ".!?"
                              and re.fullmatch(r"[A-Za-z][A-Za-z ',!.?\-]+", w)):
                            out.append(w)
    return out

SAY = ('<button type="button" class="say" data-w="{src}" aria-label="播放 {w} 的發音">'
       '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">'
       '<path d="M4 9v6h4l5 4V5L8 9H4z"/><path d="M16.5 8.5a5 5 0 0 1 0 7"/>'
       '</svg></button>')

def mark_up(page, have):
    """Put a play button after each example word, inside an AE:AUDIO-marked page."""
    fp = os.path.join(SITE, page, "index.html")
    if not os.path.exists(fp):
        print(f"  /{page}/  skipped (no such page)")
        return 0
    src = open(fp, encoding="utf-8").read()
    # Strip any existing buttons before re-adding. Attribute order is NOT stable —
    # BeautifulSoup re-emits this as <button aria-label=... class="say" ... type="button">,
    # so a pattern that assumes the original order silently appends a second copy on
    # every run. Match on the class alone.
    src = re.sub(r'<button[^>]*class="say"[^>]*>.*?</button>', "", src, flags=re.S)
    soup = BeautifulSoup(src, "html.parser")
    n = 0
    for tb in soup.find_all("table"):
        first = tb.find("tr")
        heads = [c.get_text(strip=True) for c in first.find_all(["th", "td"])] if first else []
        cols = [i for i, h in enumerate(heads) if any(e in h for e in EXAMPLE_HEADS)]
        if not cols:
            continue
        rows = tb.find_all("tr")
        for ri, tr in enumerate(rows):
            cells = [] if ri == 0 else tr.find_all(["td", "th"])
            for i in cols:
                if i >= len(cells):
                    continue
                cell = cells[i]
                whole = cell.get_text(" ", strip=True)
                cands = [whole] + re.split(r"[,、，/／・·･;；]", whole)
                first = next((w.strip() for w in cands if slug(w.strip()) in have), None)
                if not first:
                    continue
                btn = BeautifulSoup(SAY.format(src=f"/assets/audio/words/{slug(first)}.mp3",
                                               w=html.escape(first, quote=True)), "html.parser")
                cell.append(btn)
                n += 1
    out = normalize(str(soup))
    if "AE:AUDIO" not in out:
        out = out.replace("</main>", "</main>\n<!-- AE:AUDIO start -->\n"
            '<script>(function(){var a=null;document.addEventListener("click",function(e){'
            'var b=e.target.closest(".say");if(!b)return;e.preventDefault();'
            'if(a){a.pause();}a=new Audio(b.dataset.w);a.play().catch(function(){});'
            'b.classList.add("playing");a.onended=function(){b.classList.remove("playing")};'
            '});})();</script>\n<!-- AE:AUDIO end -->', 1)
    open(fp, "w", encoding="utf-8").write(out)
    return n

if __name__ == "__main__":
    pages = sys.argv[1:] or PAGES
    os.makedirs(AUDIO, exist_ok=True)
    wanted = []
    for p in pages:
        wanted += words_on(p)
    uniq = sorted({w for w in wanted}, key=str.lower)
    print(f"{len(uniq)} unique example words across {len(pages)} pages")
    k = key(); made = skipped = 0
    have = set()
    for i, w in enumerate(uniq, 1):
        path = os.path.join(AUDIO, slug(w) + ".mp3")
        if os.path.exists(path) and os.path.getsize(path) > 500:
            have.add(slug(w)); skipped += 1; continue
        if synth(w, path, k):
            have.add(slug(w)); made += 1
            print(f"  [{i}/{len(uniq)}] {w}", flush=True)
            time.sleep(2.2)                     # stay under the free-tier throttle
    print(f"audio: {made} new, {skipped} cached, {len(have)} usable")
    for p in pages:
        n = mark_up(p, have)
        print(f"  /{p}/  {n} play buttons")

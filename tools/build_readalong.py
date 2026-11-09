#!/usr/bin/env python3
"""Read-along for a Chris and Cora flip book: audio per story page + a timed box for every word.

    ~/.claude/skills/seo/.venv/bin/python3 tools/build_readalong.py 1a

Chris 2026-11-09: "AI voice for now" (his own recording can replace the audio later: drop the new
pNN.mp3 files in, delete readalong.json, rerun; the timing step works on any recording).

For each story-text page of the book (the even pages that carry story text in the screen PDF):
  1. the words and their boxes come from the PDF itself (pdftotext -bbox-layout), so the highlight
     sits exactly on the printed word; the footer (page number, NEW WORDS line) is left out;
  2. audio: OpenAI text-to-speech (gpt-4o-mini-tts, a slow, clear teacher voice) → audio/pNN.mp3,
     made once and kept (delete a file to remake it);
  3. timing: OpenAI speech-to-text with word timestamps (whisper-1) on that audio, matched to the
     page's words in order; a word the transcript missed gets a time between its neighbours.
Writes chris-and-cora-readers/read/<code>/readalong.json:
  {"voice": ..., "pages": {"4": {"audio": "audio/p04.mp3", "words": [[t0, t1, x, y, w, h], ...]}}}
with x/y/w/h in percent of the page, so the boxes scale with the page image.
tools/build_book_pages.py adds the player to the viewer when this file exists.
Cost: about US$0.02 per minute of audio (speech + timing); 1a is under two minutes.
"""
import difflib, html, json, os, re, subprocess, sys, urllib.request, uuid

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF_DIR = os.path.expanduser("~/Downloads/AE-readers-out/screen")
KEY = open(os.path.expanduser("~/.claude/credentials/openai.txt")).read().strip()
VOICE, MODEL = "coral", "gpt-4o-mini-tts"
INSTRUCTIONS = ("You are a warm American English teacher reading a picture book aloud to a young child in Taiwan who is "
                "learning to read. Read slowly and very clearly, word by word, with a short pause after each sentence. "
                "Friendly and calm, never rushed. Pronounce names as written: Chris, Cora, Bobo.")

def norm(w):
    return re.sub(r"[^a-z0-9']", "", w.lower().replace("’", "'"))

def page_words(pdf):
    """{page number: [(word, xMin, yMin, xMax, yMax)]} for the story text, in percent of the page."""
    out = subprocess.run(["pdftotext", "-bbox-layout", pdf, "-"], capture_output=True, text=True, check=True).stdout
    res = {}
    for i, (w, h, body) in enumerate(re.findall(r'<page width="([\d.]+)" height="([\d.]+)">(.*?)</page>', out, re.S), 1):
        W, H = float(w), float(h)
        words = [(html.unescape(t), float(a), float(b), float(c), float(d)) for a, b, c, d, t in
                 re.findall(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</word>', body)]
        story = []
        for t, a, b, c, d in words:               # the story text ends where the page number starts the footer
            if t == str(i) or t == "NEW":
                break
            story.append((t, a / W * 100, b / H * 100, (c - a) / W * 100, (d - b) / H * 100))
        if words and words[0][0] == "Questions":   # the story is over: questions, word lists, log, back cover follow
            break
        if story and i % 2 == 0 and i >= 4:
            res[i] = story
    return res

def post(url, body, headers, raw=False):
    req = urllib.request.Request(url, data=body, headers={"Authorization": f"Bearer {KEY}", **headers})
    with urllib.request.urlopen(req, timeout=180) as r:
        data = r.read()
    return data if raw else json.loads(data)

def tts(text, path):
    body = json.dumps({"model": MODEL, "voice": VOICE, "input": text, "instructions": INSTRUCTIONS,
                       "response_format": "mp3"}).encode()
    open(path, "wb").write(post("https://api.openai.com/v1/audio/speech", body, {"Content-Type": "application/json"}, raw=True))

def transcribe(path):
    b = uuid.uuid4().hex
    parts = []
    for k, v in (("model", "whisper-1"), ("response_format", "verbose_json"), ("timestamp_granularities[]", "word"), ("language", "en")):
        parts.append(f'--{b}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode())
    parts.append(f'--{b}\r\nContent-Disposition: form-data; name="file"; filename="a.mp3"\r\nContent-Type: audio/mpeg\r\n\r\n'.encode()
                 + open(path, "rb").read() + b"\r\n")
    parts.append(f"--{b}--\r\n".encode())
    r = post("https://api.openai.com/v1/audio/transcriptions", b"".join(parts), {"Content-Type": f"multipart/form-data; boundary={b}"})
    return r.get("words", []), r.get("duration", 0)

def align(tokens, heard, duration):
    """A (t0, t1) for every printed word, from the transcript's words matched in order."""
    a, b = [norm(t) for t in tokens], [norm(w["word"]) for w in heard]
    times = [None] * len(tokens)
    for blk in difflib.SequenceMatcher(None, a, b, autojunk=False).get_matching_blocks():
        for k in range(blk.size):
            w = heard[blk.b + k]
            times[blk.a + k] = (float(w["start"]), float(w["end"]))
    for i in range(len(times)):                   # fill gaps between known neighbours
        if times[i] is None:
            prev = next((times[j][1] for j in range(i - 1, -1, -1) if times[j]), 0.0)
            nxt = next((times[j][0] for j in range(i + 1, len(times)) if times[j]), duration or prev + 0.5)
            times[i] = (prev, max(prev + 0.15, nxt))
    return times, sum(t is not None for t in times)

def main(code):
    out_dir = os.path.join(SITE, "chris-and-cora-readers", "read", code)
    os.makedirs(os.path.join(out_dir, "audio"), exist_ok=True)
    pages = page_words(os.path.join(PDF_DIR, f"{code}.pdf"))
    result = {}
    for p, words in sorted(pages.items()):
        text = " ".join(t for t, *_ in words)
        mp3 = os.path.join(out_dir, "audio", f"p{p:02d}.mp3")
        if not os.path.exists(mp3):
            tts(text, mp3)
        heard, dur = transcribe(mp3)
        times, matched = align([t for t, *_ in words], heard, dur)
        exact =sum(1 for i, t in enumerate(words) if any(norm(h["word"]) == norm(t[0]) for h in heard))
        result[str(p)] = {"audio": f"audio/p{p:02d}.mp3",
                          "words": [[round(t0, 3), round(t1, 3), round(x, 2), round(y, 2), round(w, 2), round(h, 2)]
                                    for (t0, t1), (_, x, y, w, h) in zip(times, words)]}
        print(f"  p{p:02d} {dur:5.1f}s  {len(words):2d} words, {exact} heard as written  | {text[:60]}")
    json.dump({"voice": f"AI ({MODEL}, {VOICE})", "pages": result}, open(os.path.join(out_dir, "readalong.json"), "w"),
              separators=(",", ":"))
    print(f"{code}: {len(result)} pages → {os.path.relpath(out_dir, SITE)}/readalong.json")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "1a")

#!/usr/bin/env python3
"""Find (and repair) downloadable PDFs that Apple's viewer draws wrongly.

WeasyPrint embeds the macOS system fonts PingFang TC / Hiragino Sans as CFF, CID-keyed subsets
whose glyph numbering Apple's PDF engine (Preview, Quick Look, Safari and Mail on iPhone and
Mac) reads differently from everyone else: Latin text comes out two letters off ("cat" shows
as "ec") and Chinese body text goes missing. Chrome and Android draw the same file correctly,
so the fault is invisible unless the PDF is opened on an Apple device. Thirteen free downloads
(six flashcard sets and seven workbooks) had it from August to October 2026.

    python3 tools/check_pdfs.py            # list the PDFs that have the problem
    python3 tools/check_pdfs.py --fix      # repair them in place

The repair re-writes the file with poppler's pdftocairo (same pages, same vector artwork,
selectable text; cairo writes the font subsets correctly) and puts the title, author, subject
and keywords back with pypdf. It refuses a result whose page count or characters differ.
Needs poppler (pdffonts, pdftocairo, pdftotext, pdfinfo) and pypdf.
New PDFs: build them with TrueType fonts (Noto Sans TC, as the exam packs do), or run this.
"""
import glob, os, re, shutil, subprocess, sys, tempfile

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR = os.path.join(SITE, "assets", "downloads")

def run(*a):
    try:
        return subprocess.run(a, capture_output=True, text=True, errors="replace").stdout
    except FileNotFoundError:          # poppler not installed: nothing can be said
        return ""

def broken(path):
    """A WeasyPrint file carrying CFF CID fonts."""
    if "WeasyPrint" not in run("pdfinfo", path):
        return False
    return "CID Type 0C" in run("pdffonts", path)

def words(path):
    """Every character of the text, order ignored: the rewrite may emit the same text boxes in
    a different sequence, which is not a change a reader can see."""
    return sorted(re.sub(r"\s+", "", run("pdftotext", path, "-")))

def pages(path):
    m = re.search(r"Pages:\s+(\d+)", run("pdfinfo", path))
    return int(m.group(1)) if m else -1

def repair(path):
    from pypdf import PdfReader, PdfWriter
    tmp = tempfile.mkdtemp()
    try:
        a, b = os.path.join(tmp, "a.pdf"), os.path.join(tmp, "b.pdf")
        subprocess.run(["pdftocairo", "-pdf", path, a], check=True)
        info = PdfReader(path).metadata or {}
        w = PdfWriter(clone_from=a)
        w.add_metadata({k: str(v) for k, v in info.items() if k in ("/Title", "/Author", "/Subject", "/Keywords", "/Creator")})
        with open(b, "wb") as fh:
            w.write(fh)
        if pages(b) != pages(path):
            return f"page count changed ({pages(path)} -> {pages(b)}), left alone"
        if words(b) != words(path):
            return "text changed, left alone"
        shutil.copyfile(b, path)
        return "repaired"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

def check(fix=False, quiet=False):
    if not shutil.which("pdffonts"):
        if not quiet:
            print("check_pdfs: poppler not installed, skipped")
        return 0
    bad = [p for p in sorted(glob.glob(os.path.join(DIR, "*.pdf"))) if broken(p)]
    for p in bad:
        print(f"  {os.path.basename(p):<44} " + (repair(p) if fix else "draws wrongly on Apple devices (run tools/check_pdfs.py --fix)"))
    left = [p for p in bad if broken(p)] if fix else bad
    if not quiet or bad:
        print(f"pdf check: {len(left)} of {len(glob.glob(os.path.join(DIR, '*.pdf')))} downloadable PDFs have the Apple-viewer font problem")
    return len(left)

if __name__ == "__main__":
    sys.exit(1 if check(fix="--fix" in sys.argv) else 0)

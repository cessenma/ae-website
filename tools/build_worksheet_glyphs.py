#!/usr/bin/env python3
"""
Letter paths for the 四線三格 worksheet maker (/english-worksheet-maker/).

Why: Taiwanese 4-line paper has three equal spaces — lowercase bodies fill the middle space,
tall letters and capitals touch the top line, descenders touch the bottom line. No upright
print web font has those proportions (x-height / ascender is 0.64–0.81 in every candidate;
the paper needs 0.50), so printed text never sits on the lines. This takes Andika (SIL OFL,
a literacy font with single-storey a and g) and remaps each outline vertically, piecewise:
  lowercase:  0..x-height → 0..1 gap,  x-height..ascender → 1..2,  descender..0 → −1..0
  capitals, digits, ! ? ' ":  0..cap height → 0..2 (linear)
Coordinates are in gap units ×100, y up. The cursive option uses Playwrite US Trad directly
(its proportions already fit: 0.51 and 1.00).

Usage:  python3 tools/build_worksheet_glyphs.py
"""
import os, json
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen
from fontTools.pens.boundsPen import BoundsPen

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(SITE, "tools/data/fonts/Andika-Regular.ttf")
OUT = os.path.join(SITE, "assets/worksheet-glyphs.json")
CHARS = ("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
         ".,!?'\"-:;()&/ ")
CAPLIKE = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!?'\"&/()")

class WarpPen(BasePen):
    def __init__(self, gs, fy, sx):
        super().__init__(gs); self.fy, self.sx, self.d = fy, sx, []
    def p(self, pt):
        return f"{round(pt[0] * self.sx * 100)} {round(self.fy(pt[1]) * 100)}"
    def _moveTo(self, pt): self.d.append("M" + self.p(pt))
    def _lineTo(self, pt): self.d.append("L" + self.p(pt))
    def _curveToOne(self, a, b, c): self.d.append("C" + " ".join(self.p(x) for x in (a, b, c)))
    def _qCurveToOne(self, a, b): self.d.append("Q" + self.p(a) + " " + self.p(b))
    def _closePath(self): self.d.append("Z")

def build():
    f = TTFont(SRC)
    gs, cmap = f.getGlyphSet(), f.getBestCmap()
    def bbox(ch):
        bp = BoundsPen(gs); gs[cmap[ord(ch)]].draw(bp); return bp.bounds
    xh = bbox("x")[3]
    asc = max(bbox(c)[3] for c in "bdhkl")
    cap = bbox("H")[3]
    desc = min(bbox(c)[1] for c in "gpqy")
    lower = lambda y: y / xh if 0 <= y <= xh else (1 + (y - xh) / (asc - xh) if y > xh else y / -desc)
    upper = lambda y: 2 * y / cap if y >= 0 else y / -desc
    sx_low, sx_cap = 1 / xh, (1 / xh * 2 / cap) ** 0.5     # caps: between the two vertical scales
    out = {}
    for ch in CHARS:
        gn = cmap.get(ord(ch))
        if not gn:
            continue
        capl = ch in CAPLIKE
        sx = sx_cap if capl else sx_low
        pen = WarpPen(gs, upper if capl else lower, sx)
        gs[gn].draw(pen)
        out[ch] = [round(gs[gn].width * sx * 100), "".join(pen.d)]
    meta = {"src": "Andika (SIL OFL 1.1), outlines remapped to 4-line paper", "unit": "gap*100, y up"}
    json.dump({"meta": meta, "g": out}, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    return len(out), os.path.getsize(OUT), dict(xh=xh, asc=asc, cap=cap, desc=desc)

if __name__ == "__main__":
    n, size, m = build()
    print(f"{n} glyphs → assets/worksheet-glyphs.json ({size // 1024} KB); font zones {m}")

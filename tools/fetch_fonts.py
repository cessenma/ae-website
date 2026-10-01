#!/usr/bin/env python3
"""Copy the site's three typefaces from Google Fonts into assets/fonts/ so the site serves
them itself.

Why: the pages load ten small font files from fonts.gstatic.com. A second server means a
second connection before any font can arrive; in Lighthouse's slow-phone model that is the
difference between a first paint at about 1.3 s and one at about 2.2 s (performance score 98
against 92, measured locally on 2026-10-01 with stand-in files of the same size). Once the
files are in assets/fonts/, tools/seo_build.py notices and points every page at them.

    python3 tools/fetch_fonts.py          # downloads 10 files, about 250 KB in total
    python3 tools/seo_build.py --strict   # pages now use /assets/fonts/

The fonts are Baloo 2, DM Serif Display and DM Sans, all under the SIL Open Font License,
which allows hosting them yourself. To go back to Google's copies, delete assets/fonts/ and
run seo_build.py again.
"""
import os, sys, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import seo_build as sb

DEST = os.path.join(sb.SITE, "assets", "fonts")

def main():
    os.makedirs(DEST, exist_ok=True)
    total = 0
    for fam, style, weight, latin, ext, pre in sb.FONT_FACES:
        for remote in (latin, ext):
            name = sb.font_local_name(remote)
            out = os.path.join(DEST, name)
            req = urllib.request.Request(sb.GSTATIC + remote, headers={"User-Agent": "Mozilla/5.0"})
            data = urllib.request.urlopen(req, timeout=60).read()
            if data[:4] != b"wOF2":
                sys.exit(f"{remote}: not a WOFF2 file, stopped")
            open(out, "wb").write(data)
            total += len(data)
            print(f"  {name:<44} {len(data) / 1024:6.1f} KB   {fam} {style} {weight}")
    open(os.path.join(DEST, "LICENSE.txt"), "w", encoding="utf-8").write(
        "Baloo 2, DM Serif Display and DM Sans are licensed under the SIL Open Font License 1.1\n"
        "(https://openfontlicense.org). Files copied from fonts.gstatic.com by tools/fetch_fonts.py.\n")
    print(f"{total / 1024:.0f} KB in {DEST}. Now run: python3 tools/seo_build.py --strict")

if __name__ == "__main__":
    main()

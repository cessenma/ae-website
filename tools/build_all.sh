#!/bin/sh
# One command for the whole generated-content pipeline, in the only order that works.
# Regenerating a page rewrites <main>, which wipes its AE:CHART block, its PDF offer and
# its audio buttons — so every later stage must run again after the generator.
set -e
cd "$(dirname "$0")/.."
python3 tools/build_vocab_topic_pages.py "$@"
python3 tools/route_blocks.py
python3 tools/build_chart_images.py
python3 tools/build_chart_pdfs.py
python3 tools/build_word_audio.py
python3 tools/normalize_head.py
python3 tools/seo_build.py

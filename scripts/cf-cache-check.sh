#!/usr/bin/env bash
# Edge-vs-origin staleness check for americanenglish.com.tw.
#
# Run this after any deploy, and before trusting any live crawl of this site.
# A ?cb= query is a distinct Cloudflare cache key, so it always reaches the origin;
# the plain URL is what Googlebot and real users get. If they differ, the edge is
# serving stale HTML — which is what stranded ~26 pages out of Google's index.
#
#   ./scripts/cf-cache-check.sh            # check the usual suspects
#   ./scripts/cf-cache-check.sh /blog/ /   # check specific paths

set -uo pipefail

ORIGIN="https://americanenglish.com.tw"
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"

PATHS=("$@")
if [ ${#PATHS[@]} -eq 0 ]; then
  PATHS=(/ /blog/ /courses/ /banqiao-english-cram-school/ /phonics-rules-chart/)
fi

printf '%-42s %10s %10s %9s %s\n' PATH EDGE ORIGIN DELTA STATUS
stale=0

for p in "${PATHS[@]}"; do
  edge_body=$(curl -sS -A "$UA" --max-time 30 "${ORIGIN}${p}")
  edge_hdr=$(curl -sSI -A "$UA" --max-time 30 "${ORIGIN}${p}" | tr -d '\r')
  sleep 1
  orig_body=$(curl -sS -A "$UA" --max-time 30 "${ORIGIN}${p}?cb=${RANDOM}${RANDOM}")

  e=${#edge_body}
  o=${#orig_body}
  d=$((o - e))
  age=$(printf '%s' "$edge_hdr" | grep -i '^age:' | awk '{print $2}')
  cf=$(printf '%s' "$edge_hdr" | grep -i '^cf-cache-status:' | awk '{print $2}')

  if [ "$edge_body" = "$orig_body" ]; then
    status="ok (${cf:-?} age=${age:-0})"
  else
    status="STALE  (${cf:-?} age=${age:-?})"
    stale=$((stale + 1))
  fi
  printf '%-42s %10s %10s %9s %s\n' "$p" "$e" "$o" "$d" "$status"
  sleep 1
done

echo
if [ "$stale" -gt 0 ]; then
  echo "FAIL: ${stale} of ${#PATHS[@]} path(s) stale at the edge."
  echo "Purge Cloudflare, then see docs/CACHING.md — a nonzero result after a purge means"
  echo "the zone's Cache Rule Edge TTL is overriding the origin's s-maxage=300."
  exit 1
fi
echo "PASS: edge matches origin on all ${#PATHS[@]} path(s)."

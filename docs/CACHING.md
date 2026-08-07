# Caching — why the edge goes stale, and how it is fixed

## The failure mode

Twice on 2026-08-07 the Cloudflare edge served HTML that was hours out of date while
the origin was correct. The consequence is not cosmetic: Googlebot fetched a stale
`/blog/` that was missing internal links, and **~26 pages were left "unknown to
Google" for weeks** because nothing linked to them from a page Google could see.

## Diagnosis (measured 2026-08-07)

Origin, fetched directly from Hostinger, bypassing Cloudflare:

```
$ curl -sSI --resolve americanenglish.com.tw:443:37.44.245.80 \
    https://americanenglish.com.tw/graded-readers-guide/
cache-control: public, max-age=0, s-maxage=300, must-revalidate, no-transform
server: LiteSpeed
```

**The origin is correct.** `.htaccess` sets this for `\.html$`, and it survives.

The edge, same URL, normal request:

```
cache-control: public, max-age=0, s-maxage=300, must-revalidate, no-transform
age: 1229
cf-cache-status: HIT
```

`s-maxage=300` means a shared cache must treat the object as stale after 300 s.
Cloudflare served it as a `HIT` at **age 1229** — four times past its own stated TTL.
So Cloudflare is not honouring the origin's TTL.

**Why:** Cloudflare does not cache HTML at all by default. Getting
`cf-cache-status: HIT` on an HTML document means a **Cache Rule** (or a legacy Page
Rule) has made HTML eligible for cache — and those rules carry their own **Edge TTL**
setting, which *overrides* `s-maxage` unless it is explicitly set to respect origin
headers. A fixed Edge TTL of hours or a day matches both observations: 20 minutes of
age here, 15 hours of staleness this morning.

Note this is **not** fixed by the response-header transform rule that was added to
stop the JSD script injection. That rule rewrites the header sent downstream; it does
not change how long Cloudflare stores the object.

## Fix 1 — root cause (dashboard, one time)

Cloudflare → **Caching → Cache Rules** → open the rule that makes HTML cacheable
(the one whose filter matches directory paths, e.g. `*/`).

Set **Edge TTL** to:

> **Use cache-control header if present, bypass cache if not**

Do **not** leave it on a fixed "Edge TTL: 1 day"-style value. With the setting above,
the origin's `s-maxage=300` becomes authoritative and the edge self-heals within 5
minutes of any deploy.

Leave the `Cache-Control` transform rule alone — `no-transform` is what keeps the
`/cdn-cgi/challenge-platform/` script out of the HTML, and `s-maxage=300` is
deliberate. Keep the full directive; never replace it with `no-transform` alone.

## Fix 2 — belt and braces (automated)

`.github/workflows/cloudflare-purge.yml` runs on every push to `main`:

1. Fingerprints the committed `index.html`.
2. Polls the origin through a `?cb=` cache-buster until it serves that exact build —
   i.e. waits for Hostinger's Git deploy to actually finish. Fails after 15 minutes.
3. Purges the Cloudflare cache.
4. Re-fetches the **normal** URL (no cache-buster) and fails the run if the edge is
   still serving old bytes.

Step 4 is the point. A purge that silently does not take is exactly how this problem
survived two rounds of "I already purged it".

### Required secrets

GitHub → repo → Settings → Secrets and variables → Actions:

| Secret | Where to get it |
|---|---|
| `CLOUDFLARE_ZONE_ID` | Cloudflare dashboard → the domain → Overview → right sidebar → Zone ID |
| `CLOUDFLARE_API_TOKEN` | My Profile → API Tokens → Create Token → **Custom token** |

Scope the token to the minimum: **Zone → Cache Purge → Purge**, and restrict
*Zone Resources* to `americanenglish.com.tw` only. Do not use the Global API Key.

## Checking it by hand

```bash
./scripts/cf-cache-check.sh
```

Any nonzero byte delta means the edge is stale and the automation did not fire.

## Do not "fix" these

- `no-transform` in the `Cache-Control` header is load-bearing — it suppresses
  Cloudflare's JS-detection script injection, which cost ~573 ms of JS execution.
  Verified: `content-encoding: br` still applies, so it did not break compression.
- `SELF_CONTAINED = {"line/index.html"}` in `seo_build.py` — `/line/` is the paid-ad
  LINE bridge page and ships its own CSS and header.

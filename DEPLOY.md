# Deploying to Hostinger via Git

This is a **static site** (HTML/CSS/JS — no Node.js, no build step). The contents of
this folder go directly into Hostinger's `public_html`.

## A. One-time: put this folder on GitHub
Run these from inside this `site/` folder (it must be the repo root so `index.html`
sits at the top level):

```bash
cd /Users/christopher/Downloads/american-english-website/site
git init
git add -A
git commit -m "American English 埃森美語 — static site"
git branch -M main
# create an EMPTY repo on github.com first (e.g. ae-website), then:
git remote add origin https://github.com/<your-username>/ae-website.git
git push -u origin main
```

## B. One-time: connect Hostinger to the repo
hPanel → **Websites** → select `americanenglish.com.tw` → **Advanced → Git**
1. **Continue with GitHub** → authorize → install the Hostinger extension on the repo
2. Repository: `ae-website` · Branch: `main`
3. Install path / root directory: **`public_html`**
4. **Deploy**

After this, every `git push` auto-deploys. You can also click **Redeploy** to pull manually.

## C. Before going live (important)
- **Back up the current WordPress site first** (hPanel → Files → backup, or download `public_html`).
  Deploying here will replace what's in `public_html`.
- **No redirects needed.** Every page is a real folder (`courses/index.html`), so the live URL
  is `/courses/` — trailing slash and all — which **exactly matches the old WordPress permalinks**.
  Nothing to migrate, no 301s. The included **`.htaccess`** only does HTTPS + caching + the 404 page.
- Because URLs are plain folders, this deploys identically on any static host
  (Hostinger, Netlify, Cloudflare Pages, GitHub Pages) with zero config.

## D. After going live (SEO)
1. Visit the site, click through nav + a few pages, test a LINE button.
2. Google **Search Console** → make sure `americanenglish.com.tw` is verified →
   **Sitemaps** → submit `https://americanenglish.com.tw/sitemap.xml`.
3. Optionally "Request indexing" for the homepage to speed up re-crawl.

## Files in this deploy
- `index.html` (home) + 17 page folders, each `<slug>/index.html` · `assets/styles.css` · `assets/app.js`
- `sitemap.xml` · `robots.txt` · `.htaccess`
- External runtime deps (loaded via CDN, nothing to install): Google Fonts, Leaflet (home map), brand images.

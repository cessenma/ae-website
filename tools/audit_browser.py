"""Every page in headless Chromium at 375px: console errors, JS exceptions, local 4xx, sideways scroll.
External requests (GA4, Meta, Lemon) are blocked so a run never counts as a visit.
Serves the repo itself on 127.0.0.1:4655. Run: ~/.claude/skills/seo/.venv/bin/python3 tools/audit_browser.py"""
import glob,os,collections,json,threading,functools,http.server
from playwright.sync_api import sync_playwright
SITE=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(SITE)
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*a): pass
srv=http.server.ThreadingHTTPServer(('127.0.0.1',4655), functools.partial(Q, directory=SITE))
threading.Thread(target=srv.serve_forever,daemon=True).start()
pages=sorted(p[:-len('index.html')] for p in glob.glob('*/index.html'))+['']
issues=collections.defaultdict(list)
with sync_playwright() as pw:
    b=pw.chromium.launch()
    for width in (375,):
        ctx=b.new_context(viewport={'width':width,'height':800})
        ctx.route('**/*', lambda r: r.continue_() if r.request.url.startswith('http://127.0.0.1:4655') else r.abort())
        pg=ctx.new_page()
        cur={'p':''}
        pg.on('console', lambda m: issues['console '+m.type+': '+m.text[:120]].append(cur['p']) if m.type=='error' and 'net::ERR_FAILED' not in m.text and 'ERR_BLOCKED' not in m.text else None)
        pg.on('pageerror', lambda e: issues['JS exception: '+str(e)[:140]].append(cur['p']))
        pg.on('response', lambda r: issues[f'HTTP {r.status} '+r.url.replace("http://127.0.0.1:4655","")[:100]].append(cur['p']) if r.status>=400 and r.url.startswith('http://127.0.0.1:4655') else None)
        for p in pages:
            cur['p']=p or '/'
            try:
                pg.goto('http://127.0.0.1:4655/'+p, wait_until='load', timeout=30000)
                pg.wait_for_timeout(300)
                ov=pg.evaluate("""() => { const w=document.documentElement.clientWidth; let worst=null;
                   for (const el of document.querySelectorAll('body *')) { const r=el.getBoundingClientRect();
                     if (r.width>0 && r.right>w+2 && getComputedStyle(el).position!=='fixed') { if(!worst||r.right>worst.r) worst={r:Math.round(r.right),t:el.tagName+'.'+(el.className||'').toString().split(' ')[0]}; } }
                   return {sw: document.documentElement.scrollWidth, w, worst}; }""")
                if ov['sw']>ov['w']+1: issues[f'page scrolls sideways at {width}px ({ov["worst"]})'].append(p or '/')
            except Exception as e:
                issues['load failed: '+str(e)[:80]].append(p or '/')
        ctx.close()
    b.close()
for k,v in sorted(issues.items(), key=lambda x:-len(set(x[1])))[:40]:
    u=sorted(set(v)); print(f'{len(u):4d} pages  {k[:160]}   e.g. {u[:3]}')
print(len(issues),'distinct issues')
print('checked',len(pages),'pages')

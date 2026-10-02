"""Site-wide static HTML check: titles/descriptions, canonical vs sitemap, one <h1>/<main>, duplicate ids,
img alt+size, broken internal links/anchors/assets, og:image. Run: python3 tools/audit_html.py"""
import os,re,glob,collections,urllib.parse,json
from bs4 import BeautifulSoup
os.chdir(os.path.expanduser('~/Documents/GitHub/ae-website'))
ORIGIN='https://americanenglish.com.tw'
issues=collections.defaultdict(list)
def bad(p,m): issues[m].append(p)
pages=sorted(glob.glob('*/index.html'))+['index.html']
exists=lambda path: os.path.isfile(path) or os.path.isfile(os.path.join(path,'index.html'))
titles=collections.defaultdict(list); descs=collections.defaultdict(list)
sm=open('sitemap.xml').read(); smurls=set(re.findall(r'<loc>([^<]+)</loc>',sm))
robots=open('robots.txt').read() if os.path.exists('robots.txt') else ''
for p in pages:
    raw=open(p,encoding='utf-8').read(); soup=BeautifulSoup(raw,'html.parser')
    url=ORIGIN+'/'+(p[:-len('index.html')])
    t=(soup.title.string or '').strip() if soup.title else ''
    if not t: bad(p,'no <title>')
    titles[t].append(p)
    md=soup.find('meta',attrs={'name':'description'}); d=(md.get('content') or '').strip() if md else ''
    if not d: bad(p,'no meta description')
    descs[d].append(p)
    can=soup.find('link',rel='canonical'); c=can.get('href') if can else None
    rob=soup.find('meta',attrs={'name':'robots'}); noindex = rob and 'noindex' in (rob.get('content') or '')
    if not c: bad(p,'no canonical')
    elif c!=url and not noindex: bad(p,f'canonical points elsewhere ({c})')
    if not noindex and url not in smurls and p!='404.html': bad(p,'indexable page missing from sitemap')
    if noindex and url in smurls: bad(p,'noindex page IS in sitemap')
    h1=soup.find_all('h1')
    if len(h1)!=1: bad(p,f'{len(h1)} <h1>')
    mains=raw.count('<main'); 
    if mains!=1 or raw.count('</main>')!=mains: bad(p,f'<main> open/close {mains}/{raw.count("</main>")}')
    ids=[x.get('id') for x in soup.find_all(id=True)]
    d_ids=[k for k,v in collections.Counter(ids).items() if v>1]
    if d_ids: bad(p,f'duplicate id(s)')
    for img in soup.find_all('img'):
        if img.get('alt') is None: bad(p,'img without alt')
        if not (img.get('width') and img.get('height')): bad(p,'img without width/height')
        src=img.get('src','')
        if src.startswith('/') and not exists(src.lstrip('/').split('?')[0]): bad(p,f'img src missing {src}')
    for a in soup.find_all('a',href=True):
        h=a['href']
        if h.startswith(ORIGIN): h=h[len(ORIGIN):]
        if h.startswith('/') and not h.startswith('//'):
            path=urllib.parse.unquote(h.split('#')[0].split('?')[0]).lstrip('/')
            if path and not exists(path): bad(p,f'broken internal link {h.split("#")[0]}')
            if '#' in h and (h.split('#')[0] in ('', '/'+p[:-10])):
                frag=h.split('#',1)[1]
                if frag and not soup.find(id=frag) and not soup.find(attrs={'name':frag}): bad(p,f'in-page anchor #{frag} missing')
        if a.get('target')=='_blank' and 'noopener' not in (a.get('rel') or []): bad(p,'target=_blank without rel=noopener')
    for s in soup.find_all(['script','link']):
        u=s.get('src') or (s.get('href') if s.name=='link' and s.get('rel') and 'stylesheet' in s.get('rel') else None)
        if u and u.startswith('/') and not u.startswith('//') and not exists(u.lstrip('/').split('?')[0]): bad(p,f'asset missing {u}')
    if 'http://' in raw.replace('http://www.w3.org','').replace('xmlns','') :
        for m in re.finditer(r'(?:src|href)="http://[^"]+"',raw): bad(p,'insecure http:// link/asset'); break
    lang=soup.html.get('lang') if soup.html else None
    if not lang: bad(p,'no <html lang>')
    if not soup.find('meta',attrs={'name':'viewport'}): bad(p,'no viewport meta')
    og=soup.find('meta',attrs={'property':'og:image'})
    if not og: bad(p,'no og:image')
    elif og.get('content','').startswith(ORIGIN):
        if not exists(og['content'][len(ORIGIN)+1:].split('?')[0]): bad(p,'og:image file missing')
for t,v in titles.items():
    if len(v)>1: issues['duplicate <title>'].extend(v)
for d,v in descs.items():
    if d and len(v)>1: issues['duplicate meta description'].extend(v)
for u in smurls:
    path=u[len(ORIGIN):].lstrip('/')
    if not exists(path or 'index.html'): issues['sitemap URL with no file'].append(u)
for k,v in sorted(issues.items(), key=lambda x:-len(x[1])):
    u=sorted(set(v)); print(f'{len(u):4d} pages {len(v):5d}x  {k}   e.g. {u[:3]}')
print('robots.txt:', robots[:300].replace('\n',' | '))

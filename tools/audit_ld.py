"""Site-wide JSON-LD check against Google's required/recommended fields (Quiz, FAQ, Breadcrumb, Article,
App, Course, Product, ImageObject, LocalBusiness). Run: python3 tools/audit_ld.py"""
import json,re,glob,collections,sys,os
os.chdir(os.path.expanduser('~/Documents/GitHub/ae-website'))
def walk(o,path=''):
    if isinstance(o,dict):
        yield o,path
        for k,v in o.items(): yield from walk(v,path+'.'+k)
    elif isinstance(o,list):
        for v in o: yield from walk(v,path)
def T(o):
    t=o.get('@type'); return set(t if isinstance(t,list) else [t])
issues=collections.defaultdict(list)
def bad(p,msg): issues[msg].append(p)
for p in sorted(glob.glob('*/index.html'))+['index.html']:
    s=open(p).read()
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>',s,re.S):
        try: d=json.loads(m.group(1))
        except Exception as e: bad(p,'JSON parse error'); continue
        for o,path in walk(d):
            t=T(o)
            if 'FAQPage' in t:
                for q in o.get('mainEntity',[]):
                    if not q.get('name'): bad(p,'FAQ: question without name')
                    if not (q.get('acceptedAnswer') or {}).get('text'): bad(p,'FAQ: no acceptedAnswer.text')
            if 'BreadcrumbList' in t:
                items=o.get('itemListElement',[])
                for i,li in enumerate(items,1):
                    if li.get('position')!=i: bad(p,'Breadcrumb: position out of order')
                    if not li.get('name'): bad(p,'Breadcrumb: item without name')
                    if i<len(items) and not li.get('item'): bad(p,'Breadcrumb: non-last item without item URL')
            if t & {'Article','BlogPosting'}:
                for f in ('headline','datePublished','author','image'):
                    if not o.get(f): bad(p,f'Article: missing {f}')
                a=o.get('author'); 
                for au in (a if isinstance(a,list) else [a]):
                    if isinstance(au,dict) and not au.get('name') and '@id' in au: bad(p,'Article: author is bare @id (no name)')
                if len(str(o.get('headline','')))>110: bad(p,'Article: headline > 110 chars')
            if t & {'SoftwareApplication','WebApplication','MobileApplication'}:
                if not (o.get('offers') or o.get('aggregateRating') or o.get('review')): bad(p,'App: needs offers or aggregateRating/review')
                if o.get('offers'):
                    of=o['offers']; of=of if isinstance(of,list) else [of]
                    for x in of:
                        if 'price' not in x: bad(p,'App: offers without price')
                if not o.get('applicationCategory'): bad(p,'App: no applicationCategory (recommended)')
                if not o.get('operatingSystem'): bad(p,'App: no operatingSystem (recommended)')
            if 'Course' in t:
                for f in ('name','description','provider'):
                    if not o.get(f): bad(p,f'Course: missing {f}')
                if not o.get('hasCourseInstance'): bad(p,'Course info: no hasCourseInstance')
                if not o.get('offers'): bad(p,'Course info: no offers')
                for ci in (o.get('hasCourseInstance') or []) if isinstance(o.get('hasCourseInstance'),list) else [o.get('hasCourseInstance') or {}]:
                    if ci and not ci.get('courseMode'): bad(p,'CourseInstance: no courseMode')
                    if ci and not (ci.get('courseSchedule') or ci.get('courseWorkload')): bad(p,'CourseInstance: no courseSchedule/courseWorkload')
            if 'Product' in t:
                if not o.get('image'): bad(p,'Product: no image')
                of=o.get('offers'); 
                if not of and not o.get('review') and not o.get('aggregateRating'): bad(p,'Product: needs offers/review/aggregateRating')
                for x in (of if isinstance(of,list) else [of] if of else []):
                    for f in ('price','priceCurrency'):
                        if f not in x and 'lowPrice' not in x: bad(p,f'Product offer: no {f}')
                    if 'availability' not in x: bad(p,'Product offer: no availability (merchant)')
                    if 'shippingDetails' not in x: bad(p,'Product offer: no shippingDetails (merchant, recommended)')
                    if 'hasMerchantReturnPolicy' not in x: bad(p,'Product offer: no hasMerchantReturnPolicy (merchant, recommended)')
            if 'AggregateRating' in t:
                for f in ('ratingValue',):
                    if f not in o: bad(p,'AggregateRating: no ratingValue')
                if not (o.get('ratingCount') or o.get('reviewCount')): bad(p,'AggregateRating: no ratingCount/reviewCount')
            if 'ImageObject' in t and path in ('',):
                if not o.get('contentUrl'): bad(p,'ImageObject: no contentUrl')
                c=o.get('creator')
                if c is not None and not (isinstance(c,dict) and c.get('@type') and c.get('name')): bad(p,'ImageObject: creator not typed+named')
            if 'Quiz' in t and o.get('hasPart') is not None:
                for q in o['hasPart']:
                    if not q.get('text'): bad(p,'Quiz: question without text')
                    if not q.get('suggestedAnswer'): bad(p,'Quiz: question without suggestedAnswer')
                    for f in ('educationalAlignment','typicalAgeRange','comment'):
                        if f not in q: bad(p,f'Quiz warn: question without {f}')
                    for a in [q.get('acceptedAnswer') or {}]+(q.get('suggestedAnswer') or []):
                        if 'comment' not in a: bad(p,'Quiz warn: answer without comment'); break
                    if 'answerExplanation' not in (q.get('acceptedAnswer') or {}): bad(p,'Quiz warn: no answerExplanation')
            if t & {'EducationalOrganization','LocalBusiness'} and o.get('@id','').endswith('#organization') and o.get('address'):
                for f in ('name','address','telephone'):
                    if not o.get(f): bad(p,f'LocalBusiness: missing {f}')
            if 'ProfilePage' in t and not o.get('mainEntity'): bad(p,'ProfilePage: no mainEntity')
for k,v in sorted(issues.items(), key=lambda x:-len(set(x[1]))):
    u=sorted(set(v)); print(f'{len(u):4d} pages  {len(v):5d}x  {k}   e.g. {u[0]}')

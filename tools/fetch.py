import json,re,io,os,html,time,urllib.parse,hashlib
from concurrent.futures import ThreadPoolExecutor
import requests
from PIL import Image
UA={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36','Accept-Language':'fr-FR,fr;q=0.9,en;q=0.8'}
P=json.load(open('tools/products.json'));os.makedirs('img',exist_ok=True)
ONLY=json.load(open('tools/only.json')) if os.path.exists('tools/only.json') else None
if ONLY:
    P=[p for p in P if p['id'] in ONLY]
    for p in P:
        for f in [f'img/{p["id"]}.jpg']+[f'img/{p["id"]}-{n}.jpg' for n in (2,3,4)]:
            if os.path.exists(f): os.remove(f)
else:
    for f in os.listdir('img'): os.remove('img/'+f)
MAX=4
def get(u,**k):
    try:
        r=requests.get(u,headers={**UA,**k.pop('h',{})},timeout=20,**k)
        return r if r.ok else None
    except Exception: return None
def page_imgs(u):
    if not u or any(x in u for x in('offre','recherche','search','?q=','/s/','catalogue')) or not re.search(r'(/p/|\.prd|\.html|/products/|/produit)',u) or re.search(r'/produits/[a-z-]+(/[a-z-]+)*(/\d+)?/?$',u): return []
    r=get(u)
    if not r: return []
    t=r.text;out=[]
    for pat in [r'property="og:image"\s+content="([^"]+)"',r'content="([^"]+)"\s+property="og:image"',r'name="twitter:image"\s+content="([^"]+)"']:
        out+=re.findall(pat,t)
    for blk in re.findall(r'"image"\s*:\s*(\[[^\]]*\]|"[^"]+")',t):
        out+=re.findall(r'"(https?://[^"]+)"',blk)
    if 'ikea.com' in u: out+=re.findall(r'(https://www\.ikea\.com/fr/fr/images/products/[^"\s?]+\.(?:jpg|avif|webp))',t)
    seen=[];[seen.append(html.unescape(x).replace('\\/','/')) for x in out if x not in seen];return seen
def ikea(q):
    r=get('https://sik.search.blue.cdtapps.com/fr/fr/search-result-page?types=PRODUCT&size=3&q='+urllib.parse.quote(q))
    try:
        it=r.json()['searchResultPage']['products']['main']['items'][0]['product']
        out=[it.get('mainImageUrl'),it.get('contextualImageUrl')]
        if it.get('pipUrl'): out+=page_imgs(it['pipUrl'])
        return [x for x in out if x]
    except Exception: return []
def bing(q):
    r=get('https://www.bing.com/images/search?form=HDRSC2&first=1&setlang=fr&cc=FR&q='+urllib.parse.quote(q),h={'Cookie':'SRCHHPGUSR=ADLT=OFF'})
    if not r: return []
    t=html.unescape(r.text)
    return re.findall(r'"murl":"(https?://[^"]+)"',t)[:10]
def ddg(q):
    r=get('https://duckduckgo.com/?ia=images&iax=images&q='+urllib.parse.quote(q))
    if not r: return []
    m=re.search(r"vqd=['\"]?([\d-]+)",r.text)
    if not m: return []
    r=get('https://duckduckgo.com/i.js?l=fr-fr&o=json&f=,,,&p=1&q='+urllib.parse.quote(q)+'&vqd='+m.group(1),h={'Referer':'https://duckduckgo.com/'})
    try: return [x['image'] for x in r.json()['results'][:10]]
    except Exception: return []
def ahash(im):
    g=im.convert('L').resize((8,8));px=list(g.getdata());a=sum(px)/64;return sum(1<<i for i,p in enumerate(px) if p>a)
def load(u):
    r=get(u)
    if not r: return None
    try:
        im=Image.open(io.BytesIO(r.content));im.load()
        if im.width<200 or im.height<200: return None
        if im.mode in('RGBA','LA','P'):
            im=im.convert('RGBA');bg=Image.new('RGB',im.size,'white');bg.paste(im,mask=im.split()[-1]);im=bg
        return im.convert('RGB')
    except Exception: return None
def save(im,path):
    im=im.copy();im.thumbnail((480,480),Image.LANCZOS)
    c=Image.new('RGB',(480,480),'white');c.paste(im,((480-im.width)//2,(480-im.height)//2))
    c.save(path,'JPEG',quality=74,optimize=True,progressive=True)
def one(p):
    pid=p['id'];name=re.sub(r'[«»]','',p['name']).strip();brand=p['brand'] if p['brand'] not in('Divers','') else ''
    q=(ONLY or {}).get(pid) or (name+' '+brand).strip()
    src=[('page',u) for u in page_imgs(p['url'])]
    if brand=='IKEA' or 'ikea' in p['url']: src+=[('ikea',u) for u in ikea(' '.join(name.split(' ')[:4]))]
    b=bing(q); src+=[('bing',u) for u in b]
    if len(src)<MAX: src+=[('ddg',u) for u in ddg(q)]
    got=[];hs=[];used=set()
    for k,u in src:
        if len(got)>=MAX: break
        if u in used: continue
        used.add(u);im=load(u)
        if not im: continue
        h=ahash(im)
        if any(bin(h^x).count('1')<6 for x in hs): continue
        hs.append(h);n=len(got);save(im,f'img/{pid}.jpg' if n==0 else f'img/{pid}-{n+1}.jpg');got.append(k)
    print(pid,got,flush=True);return pid,got
with ThreadPoolExecutor(6) as ex: rep=dict(ex.map(one,P))
old=json.load(open('img/report.json')) if ONLY and os.path.exists('img/report.json') else {}
old.update(rep);rep=old
json.dump(rep,open('img/report.json','w'),indent=1,ensure_ascii=False)
print('OK',sum(1 for v in rep.values() if v),'/',len(rep),'photos',sum(len(v) for v in rep.values()))

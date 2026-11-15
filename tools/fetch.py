import json,re,io,os,html,time,urllib.parse
import requests
from PIL import Image
UA={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36','Accept-Language':'fr-FR,fr;q=0.9'}
P=json.load(open('tools/products.json'));os.makedirs('img',exist_ok=True);rep={}
def get(u,**k):
    try:
        r=requests.get(u,headers=UA,timeout=20,**k)
        return r if r.ok else None
    except Exception: return None
def page_img(u):
    if not u or 'offre' in u or 'recherche' in u or 'search' in u: return []
    r=get(u)
    if not r: return []
    t=r.text;out=[]
    for pat in [r'property="og:image"\s+content="([^"]+)"',r'content="([^"]+)"\s+property="og:image"',r'name="twitter:image"\s+content="([^"]+)"',r'"image"\s*:\s*\[?\s*"(https?://[^"]+)"']:
        out+=re.findall(pat,t)
    return [html.unescape(x) for x in out]
def ikea(q):
    r=get('https://sik.search.blue.cdtapps.com/fr/fr/search-result-page?types=PRODUCT&size=3&q='+urllib.parse.quote(q))
    try:
        return [it['product']['mainImageUrl'] for it in r.json()['searchResultPage']['products']['main']['items'][:2]]
    except Exception: return []
def bing(q):
    r=get('https://www.bing.com/images/search?form=HDRSC2&first=1&q='+urllib.parse.quote(q))
    if not r: return []
    return [html.unescape(x) for x in re.findall(r'murl&quot;:&quot;(.*?)&quot;',r.text)][:6]
def save(u,pid):
    r=get(u)
    if not r: return False
    try:
        im=Image.open(io.BytesIO(r.content));im.load()
        if im.width<120 or im.height<120: return False
        if im.mode in('RGBA','LA','P'):
            im=im.convert('RGBA');bg=Image.new('RGB',im.size,'white');bg.paste(im,mask=im.split()[-1]);im=bg
        im=im.convert('RGB');im.thumbnail((320,320),Image.LANCZOS)
        c=Image.new('RGB',(320,320),'white');c.paste(im,((320-im.width)//2,(320-im.height)//2))
        c.save(f'img/{pid}.jpg','JPEG',quality=80,optimize=True,progressive=True);return True
    except Exception: return False
import re as _r
for p in P:
    pid=p['id'];name=_r.sub(r'[«»]','',p['name']);q=(name+' '+(p['brand'] if p['brand'] not in('Divers','') else '')).strip()
    src=[('page',u) for u in page_img(p['url'])]
    if p['brand']=='IKEA' or 'ikea' in p['url']: src+=[('ikea',u) for u in ikea(name.split(' ')[0]+' '+' '.join(name.split(' ')[1:4]))]
    src+=[('bing',u) for u in bing(q)]
    ok=None
    for k,u in src:
        if save(u,pid): ok=(k,u);break
    rep[pid]=ok;print(pid,ok and ok[0]);time.sleep(.4)
json.dump(rep,open('img/report.json','w'),indent=1,ensure_ascii=False)
print('OK',sum(1 for v in rep.values() if v),'/',len(rep))

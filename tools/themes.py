import json,os,sys
sys.argv=['x'];os.environ['NOFETCH']='1'
src=open('tools/fetch.py').read().split('def one(p):')[0].replace("for f in os.listdir('img'): os.remove('img/'+f)","pass").replace("ONLY=json.load(open('tools/only.json')) if os.path.exists('tools/only.json') else None","ONLY=None")
exec(src)
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
J=json.load(open('tools/themes.json'));os.makedirs('th',exist_ok=True);os.makedirs('v',exist_ok=True)
def fit(im):
    W,H=480,360;r=max(W/im.width,H/im.height);im=im.resize((max(W,int(im.width*r)),max(H,int(im.height*r))),Image.LANCZOS)
    x=(im.width-W)//2;y=(im.height-H)//2;return im.crop((x,y,x+W,y+H))
def good(im): return im.width>=300 and im.height>=220 and 0.6<im.width/im.height<2.2
def grab(qs,n,hs,used):
    out=[]
    for q in qs:
        for u in bing(q)+ddg(q):
            if len(out)>=n: return out
            if u in used: continue
            used.add(u);im=load(u)
            if not im or not good(im): continue
            h=ahash(im)
            if any(bin(h^x).count('1')<8 for x in hs): continue
            hs.append(h);out.append(fit(im))
    return out
def strip(ims,f):
    if not ims: return 0
    S=Image.new('RGB',(480*len(ims),360));[S.paste(im,(k*480,0)) for k,im in enumerate(ims)]
    S.save(f+'.jpg','JPEG',quality=72,optimize=True,progressive=True);return len(ims)
def job(j):
    hs=[];used=set()
    if 'q' in j: n=strip(grab(j['q'],j['n'],hs,used),j['f'])
    else:
        ims=[]
        for q in j['vq']:
            g=grab([q],1,hs,used);ims.append(g[0] if g else None)
        if all(ims): n=strip(ims,j['f'])
        else: n=0
    print(j['f'],n,flush=True);return j['f'],n
with ThreadPoolExecutor(6) as ex: rep=dict(ex.map(job,J))
json.dump(rep,open('th/report.json','w'),indent=0)
print('done',sum(1 for v in rep.values() if v),'/',len(rep))

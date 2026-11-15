import requests,re,html,urllib.parse,json
UA={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36','Accept-Language':'fr-FR,fr;q=0.9'}
Q=['Canapé 3 places velours côtelé terracotta Maisons du Monde','Grohe Essence mitigeur lavabo noir mat','Samsung The Frame 55']
def t(name,u,f,h={}):
    try:
        r=requests.get(u,headers={**UA,**h},timeout=20);n=f(r)
        print(name,r.status_code,len(r.text),'->',len(n),n[:2],flush=True)
    except Exception as e: print(name,'ERR',e)
for q in Q:
    e=urllib.parse.quote(q);print('==',q)
    t('bing',f'https://www.bing.com/images/search?q={e}&form=HDRSC2&first=1',lambda r:re.findall(r'"murl":"(https?://[^"]+)"',html.unescape(r.text)))
    t('bing-async',f'https://www.bing.com/images/async?q={e}&first=0&count=35&mmasync=1',lambda r:re.findall(r'"murl":"(https?://[^"]+)"',html.unescape(r.text)))
    t('qwant',f'https://api.qwant.com/v3/search/images?q={e}&count=10&locale=fr_FR&offset=0&device=desktop&safesearch=1',lambda r:[x['media'] for x in r.json()['data']['result']['items']])
    t('yandex',f'https://yandex.com/images/search?text={e}',lambda r:re.findall(r'"origUrl":"(https?://[^"]+)"',r.text.replace('&quot;','"')))
    t('ddg-html',f'https://duckduckgo.com/?q={e}&iax=images&ia=images',lambda r:re.findall(r"vqd=['\"]?([\d-]+)",r.text))
    t('startpage',f'https://www.startpage.com/sp/search?query={e}&cat=images',lambda r:re.findall(r'"clickUrl":"(https?://[^"]+)"',r.text))
    t('brave',f'https://search.brave.com/images?q={e}',lambda r:re.findall(r'src:"(https?://[^"]+)"',r.text)+re.findall(r'"original":"(https?://[^"]+)"',r.text))
    t('ecosia',f'https://www.ecosia.org/images?q={e}',lambda r:re.findall(r'"url":"(https?://[^"]+\.(?:jpg|jpeg|png|webp))"',r.text))

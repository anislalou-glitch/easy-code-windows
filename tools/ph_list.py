import requests,json
UA={'User-Agent':'renov3d-prototype/1.0'}
a=requests.get('https://api.polyhaven.com/assets?t=models',headers=UA,timeout=60).json()
out={k:{'name':v.get('name'),'cat':v.get('categories'),'tags':v.get('tags'),'dim':v.get('dimensions'),'poly':v.get('polycount')} for k,v in a.items()}
json.dump(out,open('ph/list.json','w'),indent=0,ensure_ascii=False)
print(len(out))

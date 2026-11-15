import requests,json,os,subprocess,shutil
UA={'User-Agent':'renov3d-prototype/1.0'}
IDS=json.load(open('tools/ph_ids.json'))
os.makedirs('ph/glb',exist_ok=True);rep={}
for pid in IDS:
    try:
        f=requests.get(f'https://api.polyhaven.com/files/{pid}',headers=UA,timeout=60).json()
        g=f['gltf'];res='1k' if '1k' in g else sorted(g)[0];gl=g[res]['gltf']
        d=f'tmp/{pid}';os.makedirs(d,exist_ok=True)
        open(f'{d}/m.gltf','wb').write(requests.get(gl['url'],headers=UA,timeout=120).content)
        for path,inc in (gl.get('include') or {}).items():
            os.makedirs(os.path.dirname(f'{d}/{path}') or d,exist_ok=True)
            open(f'{d}/{path}','wb').write(requests.get(inc['url'],headers=UA,timeout=120).content)
        out=f'ph/glb/{pid}.glb'
        subprocess.run(['npx','-y','@gltf-transform/cli@4','resize',f'{d}/m.gltf',f'{d}/r.glb','--width','1024','--height','1024'],check=True)
        subprocess.run(['npx','-y','@gltf-transform/cli@4','dedup',f'{d}/r.glb',out],check=True)
        rep[pid]=os.path.getsize(out);print(pid,rep[pid],flush=True)
    except Exception as e:
        rep[pid]=str(e)[:200];print(pid,'ERR',e,flush=True)
json.dump(rep,open('ph/glb/report.json','w'),indent=0)

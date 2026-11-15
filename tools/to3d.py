import os, glob, shutil, traceback
from gradio_client import Client, handle_file
os.makedirs('m3d', exist_ok=True)
imgs = sorted(glob.glob('tools/in3d/*.jpg'))

def save(name, tag, res):
    # res may be a path, tuple, dict...
    paths = []
    def walk(x):
        if isinstance(x, str) and os.path.exists(x): paths.append(x)
        elif isinstance(x, dict):
            for v in x.values(): walk(v)
        elif isinstance(x, (list, tuple)):
            for v in x: walk(v)
    walk(res)
    print(tag, name, 'outputs:', paths)
    for p in paths:
        if p.lower().endswith(('.glb', '.gltf', '.obj', '.ply')):
            dst = f'm3d/{name}-{tag}{os.path.splitext(p)[1]}'
            shutil.copy(p, dst); print('SAVED', dst, os.path.getsize(dst)); return True
    return False

def hunyuan(c, img, name):
    for api, kw in [('/generation_all', dict(caption=None, image=handle_file(img), mv_image_front=None, mv_image_back=None, mv_image_left=None, mv_image_right=None, steps=30, guidance_scale=5, seed=1234, octree_resolution=256, check_box_rembg=True, num_chunks=8000, randomize_seed=False)),
                    ('/generation_all', dict(caption=None, image=handle_file(img), steps=30, guidance_scale=5.5, seed=1234, octree_resolution=256, check_box_rembg=True)),
                    ('/shape_generation', dict(caption=None, image=handle_file(img), steps=30, guidance_scale=5, seed=1234, octree_resolution=256, check_box_rembg=True))]:
        try:
            r = c.predict(api_name=api, **kw)
            if save(name, 'hunyuan', r): return True
        except Exception as e: print('hunyuan fail', api, repr(e)[:300])
    return False

def trellis(c, img, name):
    try:
        try: c.predict(api_name='/start_session')
        except Exception as e: print('start_session', repr(e)[:150])
        pre = c.predict(image=handle_file(img), api_name='/preprocess_image')
        c.predict(image=handle_file(pre) if isinstance(pre, str) else pre, multiimages=[], seed=0, ss_guidance_strength=7.5, ss_sampling_steps=12, slat_guidance_strength=3, slat_sampling_steps=12, multiimage_algo='stochastic', api_name='/image_to_3d')
        r = c.predict(mesh_simplify=0.95, texture_size=1024, api_name='/extract_glb')
        return save(name, 'trellis', r)
    except Exception as e:
        print('trellis fail', repr(e)[:400]); return False

SPACES = [('tencent/Hunyuan3D-2.1', hunyuan), ('tencent/Hunyuan3D-2', hunyuan), ('trellis-community/TRELLIS', trellis), ('JeffreyXiang/TRELLIS', trellis)]
for img in imgs:
    name = os.path.splitext(os.path.basename(img))[0]
    for sp, fn in SPACES:
        print('=====', name, sp)
        try:
            c = Client(sp, verbose=False)
            if name == os.path.splitext(os.path.basename(imgs[0]))[0]:
                try: print(c.view_api(return_format='str', print_info=False)[:3000])
                except Exception as e: print('view_api', e)
            if fn(c, img, name): break
        except Exception:
            traceback.print_exc()

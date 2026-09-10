"""Download selected CC0 material maps. No account or API key required."""
import urllib.request,zipfile,io,json,hashlib
from pathlib import Path
OUT=Path(__file__).resolve().parents[1]/'weathering';TEX=OUT/'textures';TEX.mkdir(parents=True,exist_ok=True)
rows=[]
def fetch(url):
 return urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'MaldekKitchenMaterialStudy/1.0'}),timeout=90).read()
meta=json.loads((OUT/'ambientcg_metadata.json').read_text(encoding='utf-8-sig'))
for asset in meta:
 info=next(d for d in asset['downloadFolders']['default']['downloadFiletypeCategories']['zip']['downloads'] if d['attribute']=='2K-JPG')
 with zipfile.ZipFile(io.BytesIO(fetch(info['downloadLink']))) as z:
  names=z.namelist();print(asset['assetId'],names,flush=True)
  for name in names:
   if name.lower().endswith('.jpg') and any(k in name.lower() for k in ['roughness','color','opacity']):
    data=z.read(name);dst=TEX/Path(name).name;dst.write_bytes(data);rows.append({'provider':'ambientCG','asset':asset['assetId'],'page':asset['shortLink'],'download':info['downloadLink'],'file':dst.name,'sha256':hashlib.sha256(data).hexdigest(),'license':'CC0-1.0'})
poly=json.loads((OUT/'polyhaven_metadata.json').read_text(encoding='utf-8-sig'))
for key in ['Diffuse','Rough','nor_gl']:
 url=poly[key]['2k']['jpg']['url'];dst=TEX/url.rsplit('/',1)[-1];data=fetch(url);dst.write_bytes(data);rows.append({'provider':'Poly Haven','asset':'wood_cabinet_worn_long','page':'https://polyhaven.com/a/wood_cabinet_worn_long','download':url,'file':dst.name,'sha256':hashlib.sha256(data).hexdigest(),'license':'CC0-1.0'});print(dst.name,flush=True)
(OUT/'texture_sources.json').write_text(json.dumps(rows,indent=2))

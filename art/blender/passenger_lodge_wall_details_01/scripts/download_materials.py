"""Re-fetch only licensed map files actually used by the material, no executable asset import."""
from pathlib import Path
import urllib.request,zipfile,io,hashlib,json
P=Path(__file__).resolve().parents[1]
url='https://ambientcg.com/get?file=Cork001_1K-JPG.zip'
req=urllib.request.Request(url,headers={'User-Agent':'MaldekStation-asset-authoring'})
data=urllib.request.urlopen(req).read();z=zipfile.ZipFile(io.BytesIO(data));files=[]
for channel in ['Color','Roughness']:
 name='Cork001_1K-JPG_'+channel+'.jpg';target=P/'materials'/'Cork001'/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(z.read(name));files.append({'path':str(target.relative_to(P)),'sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
(P/'materials'/'provenance.json').write_text(json.dumps(dict(asset='Cork001',author='ambientCG / Lennart Demes',source='https://ambientcg.com/view?id=Cork001',download=url,license='CC0-1.0',license_url='https://docs.ambientcg.com/license/',retrieved='2026-09-10',files=files,adaptation='Color tinted warm brown in Blender; source pixels unchanged. UV one repeat/metre; roughness non-color.'),indent=2))

"""Retrieve the single CC0 map used by this package, without extracting other files."""
from pathlib import Path
from urllib.request import urlopen
import zipfile,io,hashlib,json
out=Path(__file__).resolve().parents[1]/'textures';out.mkdir(exist_ok=True)
name='PaintedMetal012_1K-JPG_Roughness.jpg'
with urlopen('https://ambientcg.com/get?file=PaintedMetal012_1K-JPG.zip') as response:
 data=zipfile.ZipFile(io.BytesIO(response.read())).read(name)
if (out/'sources.json').exists():assert hashlib.sha256(data).hexdigest()==json.loads((out/'sources.json').read_text())['sha256']
(out/name).write_bytes(data)

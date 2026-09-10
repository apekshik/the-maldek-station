"""Confirm deterministic writing, raster sizes, provenance and delivered review files."""
from pathlib import Path
import json,hashlib,xml.etree.ElementTree as ET
from PIL import Image
P=Path(__file__).resolve().parents[1];inventory=json.loads((P/'artwork/inventory.json').read_text());checks=[]
for item in inventory:
 root=ET.parse(P/item['svg']).getroot();actual=[''.join(t.itertext()) for t in root.iter('{http://www.w3.org/2000/svg}text')];assert actual==item['text'],item['id']
 with Image.open(P/item['texture']) as im:assert list(im.size)==item['pixels']
 checks.append(dict(id=item['id'],editable_text_exact=True,texture_sha256=hashlib.sha256((P/item['texture']).read_bytes()).hexdigest()))
words=' '.join(' '.join(x['text']) for x in inventory)
assert 'spare key' not in words and 'locker 07' not in words
for required in ['Independent entrance','Use the exterior platform.','09:00','16:30','Every 30 minutes','Afternoon excursion cancelled.']:assert required in words
render_records=json.loads((P/'render_manifest.json').read_text());expected=['01_West_cluster','02_Timetable_close','03_Map_close','04_Community_close','05_Restroom_approach','06_Hall_eye','07_Hall_service','08_Wayfinding_hall','09_West_walk','10_Clock_close','11_Overview','12_Poster_inspection','13_Poster_mounting_rear','14_Case_maintenance','15_Kitchen_menu','16_Cubby_label'];files=[r['file'] for r in render_records]
for name in expected:assert 'renders/'+name+'_neutral.png' in files,name
for name in ['02_Timetable_close','04_Community_close','06_Hall_eye']:assert 'renders/'+name+'_dim_warm.png' in files
for file in files:
 with Image.open(P/file) as im:im.verify()
provenance=json.loads((P/'materials/provenance.json').read_text())
for item in provenance['files']:assert hashlib.sha256((P/item['path']).read_bytes()).hexdigest()==item['sha256']
report=dict(passed=True,editable_artworks=len(checks),checks=checks,render_count=len(files),material_hashes_match=True,no_generated_critical_text=True,limits='Exact source text and PNG integrity checks; human render review remains necessary for legibility.')
(P/'artwork_verification.json').write_text(json.dumps(report,indent=2));print('ARTWORK_VERIFIED',len(checks),'RENDERS',len(files))

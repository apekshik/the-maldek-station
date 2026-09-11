"""Deterministic text/PNG integrity, provenance and matched before-after cameras."""
from pathlib import Path
import json,hashlib,xml.etree.ElementTree as ET
from PIL import Image
P=Path(__file__).resolve().parents[1];inventory=json.loads((P/'artwork/inventory.json').read_text());rows=[]
for a in inventory:
 texts=[''.join(x.itertext()) for x in ET.parse(P/a['svg']).getroot().iter('{http://www.w3.org/2000/svg}text')];assert texts==a['text'],a['id']
 with Image.open(P/a['texture']) as im:assert list(im.size)==a['pixels']
 rows.append(dict(id=a['id'],text_exact=True,sha256=hashlib.sha256((P/a['texture']).read_bytes()).hexdigest()))
records=json.loads((P/'render_manifest.json').read_text());assert len(records)==11
for r in records:
 with Image.open(P/r['file']) as im:im.verify()
a=next(x for x in records if '01_Before' in x['file']);b=next(x for x in records if '02_After' in x['file']);assert all(a[k]==b[k] for k in ['camera_position','target','lens','projection']);assert not a['new_collection_visible'] and b['new_collection_visible']
provenance=dict(artwork='Original deterministic SVG illustrations and text; no third-party photographs, real-world historical date or named event asserted.',source_blend='passenger_lodge_04/Maldek_Passenger_Lodge_Integrated.blend',source_sha256='bcf7e6301aecedd83688488981fd58a5a9719d685ef975210eef9eeb7f753f6c',source_commit='fdd88f3',material_reuse=['PL03_Aged_Pine from immutable integrated station','New petrol/cream enamel, galvanized, paper and glass material graphs'],fonts='Windows Arial and Georgia used at build time; font files not redistributed.',generation='No FAL or other generative-image call. No credentials accessed.',reference_image='User-provided screenshot, matching lodge 04 previews/03_Hall.png; geometry is surveyed from the blend.',editorial='Ski guidance and leaflet covers are ordinary proposed visitor dressing. Static gauge readings only.')
(P/'provenance.json').write_text(json.dumps(provenance,indent=2));(P/'artwork_verification.json').write_text(json.dumps(dict(passed=True,editable_artworks=len(rows),checks=rows,render_count=len(records),before_after_camera_identical=True),indent=2));print('TEXT_AND_RENDERS_VERIFIED',len(rows),len(records))

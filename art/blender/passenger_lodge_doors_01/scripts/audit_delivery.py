"""Validate the complete render set and save its link to the verified blend."""
import json,hashlib,struct
from pathlib import Path
OUT=Path(__file__).resolve().parents[1]
assert json.loads((OUT/'verification.json').read_text())['passed']
assert json.loads((OUT/'patch_replay_verification.json').read_text())['passed']
records=[]
for v in json.loads((OUT/'review_views.json').read_text()):
 p=OUT/'previews'/(v['name']+'.png');raw=p.read_bytes();assert raw[:8]==b'\x89PNG\r\n\x1a\n'
 width,height=struct.unpack('>II',raw[16:24]);assert (width,height)==(1200,1000)
 records.append(dict(v,path='previews/'+p.name,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),dimensions=[width,height]))
assert len(records)==27
data=dict(blend_sha256=hashlib.sha256((OUT/'Maldek_Passenger_Lodge_Doors.blend').read_bytes()).hexdigest(),render_count=len(records),renders=records)
(OUT/'preview_manifest.json').write_text(json.dumps(data,indent=2))
print('Delivery verified:',len(records),'renders; geometry and patch replay passed')

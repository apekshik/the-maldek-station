import json,hashlib,math
from pathlib import Path
root=Path(__file__).resolve().parents[4];out=root/'art/unreal_handoff/revision12/parking'
m=json.loads((out/'handoff.json').read_text());base=json.loads((root/'art/unreal_handoff/revision13/terrain_grid.json').read_text())['vertices'];vs=json.loads((out/'terrain_grid.json').read_text())['vertices']
outside=[]
for a,b in zip(base,vs):
 x,y,z=a;d=math.hypot(max(-44.6-x,0,x+29.9),max(-64.1-y,0,y+51.9))
 if d>=2 and a!=b:outside.append([a,b])
assert not outside
for r in m['chunks']:assert hashlib.sha256((out/r['file']).read_bytes()).hexdigest()==r['sha256']
report={'outside_mask_changes':0,'verified_fbx_files':len(m['chunks']),'passed':True,'landscape_clearance':'Requires live collision trace in parking_audit.py'}
(out/'offline_validation.json').write_text(json.dumps(report,indent=2));print(report)

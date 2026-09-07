"""Regression checks plus access checks for new utility connections."""
from pathlib import Path
source=Path(__file__).resolve().parents[2]/'visual_fidelity_03/scripts/verify_revision.py'
exec(compile(source.read_text(),__file__,'exec'))
checks=[]
for y in [.55,1.1,1.8,6.5,7.2,7.7]:
 for z in [.5,1,1.7]:
  r=hit((9.1,y,z),(1,0,0),1.55)
  add('Utility gateway clear',not r[0],y=y,z=z,hit=r[4].name if r[0] else None)
for z in [6.8,7.35]:
 r=hit((18,14.96,z),(0,-1,0),.65);add('Ladder exit guard opening',not r[0],z=z)
r=hit((18,13.3,6.5),(0,0,-1),.5)
add('Tank has closed lid',r[0] and 6.2<r[1].z<6.4)
for o in bpy.data.collections['09_Water_Tower'].objects:
 if o.name.startswith('Tank_column'):
  top=max((o.matrix_world@Vector(v)).z for v in o.bound_box);add('Tank column reaches bearing',top>=3.0)
for y in [9.0,9.6,10.2]:
 r=hit((10.1,y,.15),(0,0,-1),.2);add('Relay connector floor',r[0])
report={'count':len(checks),'passed':all(c['passed'] for c in checks),'failures':[c for c in checks if not c['passed']],'checks':checks,'limits':'Blender sampled checks; no engine collision or structural certification.'}
(out/'utility_verification.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='checks'}));assert report['passed']

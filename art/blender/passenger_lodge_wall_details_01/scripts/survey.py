import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1]
S=Path('C:/Users/apek-anna/Developer/the-maldek-station/art/blender/passenger_lodge_03/Maldek_Passenger_Lodge_Materials.blend')
bpy.ops.wm.open_mainfile(filepath=str(S)); s=bpy.data.scenes['05_Material_Study'];bpy.context.window.scene=s
r=[]
for o in s.objects:
 if o.type not in {'MESH','FONT'}:continue
 pts=[o.matrix_world@Vector(v) for v in o.bound_box];lo=[min(p[i] for p in pts) for i in range(3)];hi=[max(p[i] for p in pts) for i in range(3)]
 if o.name.startswith('FIT_') or o.type=='FONT' or ('Control' in o.name or 'control' in o.name or 'Platform' in o.name or 'Door' in o.name):
  r.append(dict(name=o.name,lo=lo,hi=hi,text=o.data.body if o.type=='FONT' else None))
(P/'survey.json').write_text(json.dumps({'source_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'objects':r},indent=2))
print('SURVEY_DONE',len(r))

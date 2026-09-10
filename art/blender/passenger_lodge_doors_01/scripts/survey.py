import bpy, json, hashlib
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1]
SOURCE=OUT.parent/'passenger_lodge_03/Maldek_Passenger_Lodge_Materials.blend'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
s=bpy.data.scenes['05_Material_Study'];bpy.context.window.scene=s
bpy.context.view_layer.update()
objects=[]
for o in s.objects:
 if o.type not in {'MESH','CURVE'}:continue
 ps=[o.matrix_world@Vector(p) for p in o.bound_box]
 lo=[min(p[i] for p in ps) for i in range(3)];hi=[max(p[i] for p in ps) for i in range(3)]
 if o.name.startswith(('FIT_','PL03_Cladding')) or (lo[0]<-16 and hi[0]>-20 and lo[1]<6 and hi[1]>-12 and hi[2]>4 and lo[2]<7):
  objects.append(dict(name=o.name,lo=lo,hi=hi,visible=o.visible_get(),hide_render=o.hide_render,collections=[c.name for c in o.users_collection]))
(OUT/'source_survey.json').write_text(json.dumps(dict(sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),objects=objects),indent=2))
print('SURVEY',len(objects))

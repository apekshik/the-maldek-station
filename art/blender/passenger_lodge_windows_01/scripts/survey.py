import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1]
SRC=OUT.parent/'passenger_lodge_03/Maldek_Passenger_Lodge_Materials.blend'
bpy.ops.wm.open_mainfile(filepath=str(SRC))
s=bpy.data.scenes['05_Material_Study'];bpy.context.window.scene=s
def bounds(o):
    p=[o.matrix_world@Vector(v) for v in o.bound_box]
    return [[min(v[i] for v in p) for i in range(3)],[max(v[i] for v in p) for i in range(3)]]
rows=[]
for o in s.objects:
    if o.type!='MESH':continue
    lo,hi=bounds(o)
    if (hi[0]>-24 and lo[0]<-8 and hi[1]>3.5 and lo[1]<4.5 and hi[2]>4.5 and lo[2]<7) or ('Control' in o.name and 'window' in o.name.lower()):
        rows.append(dict(name=o.name,bounds=[lo,hi],materials=[m.name for m in o.data.materials],collections=[c.name for c in o.users_collection],hide_render=o.hide_render,visible=o.visible_get(),modifiers=[m.type for m in o.modifiers]))
(OUT/'source_survey.json').write_text(json.dumps(dict(source_sha256=hashlib.sha256(SRC.read_bytes()).hexdigest(),objects=rows,collections=[(c.name,c.hide_render,c.hide_viewport) for c in bpy.data.collections]),indent=2))
print(json.dumps(rows,indent=2))

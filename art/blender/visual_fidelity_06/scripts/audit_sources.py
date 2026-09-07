import bpy,json
from pathlib import Path
from mathutils import Vector
ROOT=Path('C:/Users/apek-anna/Developer/the-maldek-station')
OUT=ROOT/'art/blender/visual_fidelity_06'
def audit(path,name):
 bpy.ops.wm.open_mainfile(filepath=str(path))
 bpy.context.view_layer.update()
 rows=[]
 for o in bpy.data.objects:
  pts=[o.matrix_world@Vector(p) for p in o.bound_box]
  rows.append(dict(name=o.name,type=o.type,collections=[c.name for c in o.users_collection],bounds=[[round(min(p[i] for p in pts),4) for i in range(3)],[round(max(p[i] for p in pts),4) for i in range(3)]],hide=o.hide_render))
 (OUT/(name+'.json')).write_text(json.dumps(rows,indent=2))
audit(ROOT/'art/unreal_handoff/revision11/station_layout.blend','r11_objects')
audit(ROOT/'art/blender/visual_fidelity_05/Maldek_Architecture_Redesign.blend','v5_objects')

import bpy,json
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(OUT/'Maldek_Combined_Station_Blockout.blend'))
s=bpy.data.scenes['04_Combined_Station_Blockout'];bpy.context.window.scene=s
items=[]
for o in s.objects:
 if o.type!='MESH' or not o.visible_get():continue
 p=[o.matrix_world@Vector(v) for v in o.bound_box];lo=[min(v[i] for v in p) for i in range(3)];hi=[max(v[i] for v in p) for i in range(3)]
 if lo[0]<-6.2 and hi[0]>-10.2 and lo[1]<-5.6 and hi[1]>-16.3 and lo[2]>3.95:items.append({'name':o.name,'lo':lo,'hi':hi,'collections':[c.name for c in o.users_collection]})
(OUT/'stair_rail_survey.json').write_text(json.dumps(items,indent=2))
for name,pos,target,scale in [('Stair_Before',(-16,-21,13),(-8,-10.5,3.5),15)]:
 d=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=scale;s.camera=o
 s.render.resolution_x=1400;s.render.resolution_y=1200;s.render.filepath=str(OUT/'previews'/f'{name}.png');bpy.ops.render.render(write_still=True,scene=s.name)

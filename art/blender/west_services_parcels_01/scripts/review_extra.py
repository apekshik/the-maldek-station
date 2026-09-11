import bpy,json,math,hashlib,sys
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1];O=Vector((-37.45,-5,4.6));a=json.loads((P/'assembly.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(P/'Maldek_Parcels_Fitted_Review.blend'));s=bpy.context.scene;c=bpy.data.collections['WSP_ASSETS'];cam=s.camera;d=cam.data
def rest_except_door():
 s.frame_set(40)
 for m in a['mechanisms']:
  if m['object']!='WSP_Door_hinge':
   ob=bpy.data.objects[m['object']]
   if ob.animation_data:ob.animation_data.action=None
   getattr(ob,'rotation_euler' if m['kind']=='ROTATION' else 'location')[m['axis']]=m['rest']
 bpy.context.view_layer.update()
def shot(name,p,target):
 cam.location=Vector(p)+O;cam.rotation_euler=(Vector(target)+O-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(P/'previews'/f'{name}.png');bpy.ops.render.render(write_still=True)
rest_except_door();e=bpy.data.objects['WSP_Belonging_1'];children=list(e.children_recursive)
def shelfhash():return hashlib.sha256(repr([(ob.name,[tuple(v.co) for v in ob.data.vertices]) for ob in c.objects if ob.type=='MESH' and ob.name.startswith('WSP_Shelf_')]).encode()).hexdigest()
before=shelfhash()
for ob in children:ob.hide_render=True
d.type='PERSP';d.lens=23
if '--plans-only' not in sys.argv:shot('11_deposit_removed',(4.48,2.75,1.65),(.65,2.5,1.13))
after=shelfhash()
for ob in children:ob.hide_render=False
(P/'deposit_demonstration.json').write_text(json.dumps({'deposited_image':'previews/03_rear_shelves.png','removed_image':'previews/11_deposit_removed.png','independent_root':e.name,'hidden_children':[ob.name for ob in children],'shelving_hash_before':before,'shelving_hash_after':after,'shelving_unchanged':before==after},indent=2));assert before==after
for ob in list(bpy.data.collections['WS_SHARED_ROOF'].all_objects):
 if ob:ob.hide_render=True
d.type='ORTHO';d.ortho_scale=8.6;shot('12_handling_plan',(4.1,2.5,10),(4.1,2.5,0))
t=bpy.data.objects['WSP_Trolley_root'];t.location=(3.15,2.75,0);t.rotation_euler.z=math.pi/2;bpy.context.view_layer.update();shot('13_trolley_turned',(4.1,2.5,10),(4.1,2.5,0))
t.location=(6.85,1.99,0);bpy.context.view_layer.update();shot('14_trolley_porch_turn',(4.1,2.5,10),(4.1,2.5,0))
print('EXTRA_REVIEW_COMPLETE')

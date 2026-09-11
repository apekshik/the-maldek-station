import bpy,json,math,sys,hashlib
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1];SRC=P.parent/'west_services_01/Maldek_West_Services_Blockout.blend';O=Vector((-37.45,-5,4.6))
bpy.ops.wm.open_mainfile(filepath=str(SRC));s=bpy.data.scenes['West_Services_Combined'];bpy.context.window.scene=s;s.frame_set(1)
a=json.loads((P/'assembly.json').read_text())
for n in a['delete_exact']:bpy.data.objects.remove(bpy.data.objects[n],do_unlink=True)
with bpy.data.libraries.load(str(P/'Maldek_Parcels_Office.blend'),link=False) as (src,dst):dst.collections=['WSP_ASSETS']
c=dst.collections[0];s.collection.children.link(c)
root=bpy.data.objects.new('WSP_REVIEW_PLACEMENT',None);s.collection.objects.link(root);root.location=O
for o in c.objects:
 if not o.parent:o.parent=root
# No shell patches needed: jamb outer faces lie inside shell; exposed reveals have a single frame owner.
# Adjacent shell/frame contact is concealed by casing; no duplicate wall or slab.
for o in s.objects:
 if o.type=='LIGHT':o.hide_render=True
 if o.type in ['MESH','CURVE','FONT'] and not o.name.startswith(('WSP_','WS_')):
  pts=[o.matrix_world@Vector(v) for v in o.bound_box]
  if min(p.x for p in pts)>-25 or max(p.x for p in pts)<-43 or min(p.y for p in pts)>10 or max(p.y for p in pts)<-12:o.hide_render=True
for cn in ['WS_REVIEW_ONLY']:
 if bpy.data.collections.get(cn):
  for o in bpy.data.collections[cn].all_objects:o.hide_render=True
def light(n,p,power,size):
 d=bpy.data.lights.new(n,'AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new(n,d);s.collection.objects.link(o);o.location=Vector(p)+O;o.rotation_euler=(Vector((3,2.5,1))+O-o.location).to_track_quat('-Z','Y').to_euler()
light('WSP_REVIEW_room',(3,2.5,2.63),330,3);light('WSP_REVIEW_window',(5.4,4,2.5),140,1.6);light('WSP_REVIEW_porch',(7,1,4.8),1200,5)
light('WSP_REVIEW_front',(7.7,2.5,2.4),350,2)
s.world=bpy.data.worlds.new('WSP_Neutral');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.45,.5,.55,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.5
s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True;s.render.resolution_x=1200;s.render.resolution_y=900;s.render.resolution_percentage=100
s.render.use_persistent_data=True
s.view_settings.view_transform='AgX'
d=bpy.data.cameras.new('WSP_REVIEW_camera');cam=bpy.data.objects.new(d.name,d);s.collection.objects.link(cam);s.camera=cam;d.clip_start=.03;d.clip_end=500
def render(n,p,target,lens=25,frame=40):
 s.frame_set(frame)
 restore=[]
 if n!='07_secure_open':
  for m in a['mechanisms']:
   if m['object']=='WSP_Secure_door_hinge' or m['object'].startswith('WSP_Secure_tray'):
    ob=bpy.data.objects[m['object']]
    if ob.animation_data and ob.animation_data.action:
     restore.append((ob,ob.animation_data.action,ob.animation_data.action_slot));ob.animation_data.action=None
    getattr(ob,'rotation_euler' if m['kind']=='ROTATION' else 'location')[m['axis']]=m['rest']
 bpy.context.view_layer.update();cam.location=Vector(p)+O;cam.rotation_euler=(Vector(target)+O-cam.location).to_track_quat('-Z','Y').to_euler();d.lens=lens;s.render.filepath=str(P/'previews'/f'{n}.png');bpy.ops.render.render(write_still=True)
 for ob,act,slot in restore:ob.animation_data.action=act;ob.animation_data.action_slot=slot
s.frame_set(1);cam.location=Vector((7.75,2.45,1.65))+O;cam.rotation_euler=(Vector((5.8,2.65,1.4))+O-cam.location).to_track_quat('-Z','Y').to_euler();d.lens=14
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA'
bpy.ops.wm.save_as_mainfile(filepath=str(P/'Maldek_Parcels_Fitted_Review.blend'))
shots=[('01_porch_closed',(7.75,2.45,1.65),(5.8,2.65,1.4),14,1),('02_door_open',(6.9,2.12,1.65),(3,2.25,1.15),22,40),('03_rear_shelves',(4.48,2.75,1.65),(.65,2.5,1.13),23,40),('04_counter_reverse',(2.8,2.9,1.65),(5.22,3.86,1.23),28,40),('05_tag_station',(4.1,3.25,1.5),(5.1,3.79,1.04),44,40),('06_secure_closed',(2.32,2.70,1.6),(2.2,.65,1.1),37,1),('07_secure_open',(3.12,2.72,1.6),(2.10,.65,1.05),34,40),('08_window_closed',(4.18,3.5,1.65),(5.9,3.9,1.53),35,1),('09_door_inside_closed',(3.86,2.28,1.65),(5.9,1.85,1.15),26,1),('10_threshold',(5.05,2.16,.6),(5.95,1.85,.08),35,40)]
selected=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
for shot in shots:
 if not selected or shot[0] in selected:render(*shot)
if not selected or '11_deposit_removed' in selected:
 e=bpy.data.objects['WSP_Belonging_1'];children=list(e.children_recursive)
 shelf_state=lambda:hashlib.sha256(repr([(ob.name,[tuple(v.co) for v in ob.data.vertices]) for ob in c.objects if ob.type=='MESH' and ob.name.startswith('WSP_Shelf_')]).encode()).hexdigest()
 before=shelf_state()
 for o in children:o.hide_render=True
 render('11_deposit_removed',(4.48,2.75,1.65),(.65,2.5,1.13),23,40)
 for o in children:o.hide_render=False
 after=shelf_state();assert before==after
 (P/'deposit_demonstration.json').write_text(json.dumps({'deposited_image':'previews/03_rear_shelves.png','removed_image':'previews/11_deposit_removed.png','independent_root':e.name,'hidden_children':[ob.name for ob in children],'shelving_hash_before':before,'shelving_hash_after':after,'shelving_unchanged':before==after},indent=2))
if not selected or '12_handling_plan' in selected:
 for ob in list(bpy.data.collections['WS_SHARED_ROOF'].all_objects):
  if ob:ob.hide_render=True
 d.type='ORTHO';d.ortho_scale=8.6
 render('12_handling_plan',(4.1,2.5,10),(4.1,2.5,0),25,40)
 trolley=bpy.data.objects['WSP_Trolley_root'];old=trolley.location.copy();rot=trolley.rotation_euler.copy();trolley.location=(3.15,2.75,0);trolley.rotation_euler.z=math.pi/2
 render('13_trolley_turned',(4.1,2.5,10),(4.1,2.5,0),25,40)
 trolley.location=old;trolley.rotation_euler=rot
s.frame_set(1)
print('REVIEW_COMPLETE')


import bpy,json,math,sys,hashlib
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1]; origin=Vector((-37.45,0,4.6)); R=P.parent/'west_services_01'
assert hashlib.sha256((R/'Maldek_West_Services_Blockout.blend').read_bytes()).hexdigest()==json.loads((R/'delivery.json').read_text())['sha256']
bpy.ops.wm.open_mainfile(filepath=str(R/'Maldek_West_Services_Blockout.blend'))
S=bpy.context.scene
for name in json.loads((P/'assembly.json').read_text())['delete_exactly']: bpy.data.objects.remove(bpy.data.objects[name],do_unlink=True)
with bpy.data.libraries.load(str(P/'Maldek_Rescue_Hut_Editable.blend'),link=False) as (src,dst): dst.collections=['WSR_ASSETS']
C=dst.collections[0]; S.collection.children.link(C)
root=bpy.data.objects.new('REVIEW_ONLY_WSR_Assembly',None); S.collection.objects.link(root); root.location=origin
for o in C.objects:
 if not o.parent: o.parent=root
S.name='WSR_Fitted_Immutable_Master_Copy'
# Inherited distant lodge/terrain are retained, hidden for efficient close room reviews.
for o in S.objects:
 if not o.name.startswith(('WS_','WSR_','REVIEW_ONLY')): o.hide_render=True
 if o.type in ['LIGHT','CAMERA']: o.hide_render=True
for c in bpy.data.collections:
 if c.name.startswith('WS_'): c.hide_render=False
for o in bpy.data.collections['WS_SHARED_STRUCTURE'].objects: o.hide_render=False
for o in C.objects: o.hide_render=False
S.render.engine='CYCLES'; S.cycles.samples=24; S.cycles.use_denoising=True
S.render.resolution_x=1200; S.render.resolution_y=900; S.render.resolution_percentage=100
S.world.use_nodes=True; S.world.node_tree.nodes['Background'].inputs[0].default_value=(.32,.36,.42,1); S.world.node_tree.nodes['Background'].inputs[1].default_value=.65
S.view_settings.view_transform='AgX'
def area(n,p,power,size,target):
 d=bpy.data.lights.new(n,'AREA'); d.energy=power; d.shape='DISK'; d.size=size; o=bpy.data.objects.new(n,d); S.collection.objects.link(o); o.location=origin+Vector(p); o.rotation_euler=(Vector(target)-Vector(p)).to_track_quat('-Z','Y').to_euler()
area('REVIEW_ONLY_Softbox',(3,2.5,2.62),350,3,(3,2,0))
area('REVIEW_ONLY_East_fill',(8,2.0,3.6),550,4,(4,2,1))
area('REVIEW_ONLY_West_fill',(.9,2.7,2.6),180,2,(2,2,1))
d=bpy.data.cameras.new('REVIEW_ONLY_Camera'); cam=bpy.data.objects.new('REVIEW_ONLY_Camera',d); S.collection.objects.link(cam); S.camera=cam
roof=list(bpy.data.collections['WS_SHARED_ROOF'].all_objects)
def view(n,p,t,frame=1,lens=28,ortho=None,cut=False):
 S.frame_set(frame); cam.location=origin+Vector(p); cam.rotation_euler=(Vector(t)-Vector(p)).to_track_quat('-Z','Y').to_euler(); d.type='ORTHO' if ortho else 'PERSP'; d.lens=lens
 if ortho:d.ortho_scale=ortho
 for o in roof: o.hide_render=cut
 S.render.filepath=str(P/'previews'/f'{n}.png'); bpy.ops.render.render(write_still=True)
views=[('01_Porch_closed',(7.8,.4,1.68),(5.85,2.50,1.35),1,20,None,False),('02_Porch_open',(7.65,2.05,1.65),(2.9,2.35,1.1),40,23,None,False),('03_Inside_door',(3.2,2.1,1.65),(5.9,2.6,1.3),1,26,None,False),('04_Room_toward_cot',(5.35,3.0,1.65),(1.55,2.25,1.05),1,24,None,False),('05_Cupboards_open',(3.2,2.3,1.65),(.49,2.0,1.05),80,21,None,False),('06_Stretcher_folded',(4.0,2.6,1.65),(3.07,.45,1.73),1,35,None,False),('07_Stretcher_deployed',(5.2,4.0,2.15),(3.8,2.25,.55),40,26,None,True),('08_Handling_overhead',(3.9,2.0,10),(3.9,2.0,0),40,35,8.7,True),('09_Window_inside',(4.4,3.0,1.68),(5.86,3.9,1.53),1,35,None,False),('10_Threshold_inside',(5.0,1.95,.55),(5.94,2.10,.14),40,34,None,False),('11_Radio_heater',(3.30,2.7,1.64),(4.23,4.62,1.04),1,28,None,False)]
S.frame_start=1; S.frame_end=80
for name,f in [('NORMAL_EMPTY',1),('READY_FOR_ARRIVAL',40),('EQUIPMENT_OPEN',80)]: S.timeline_markers.new(name,frame=f)
S.frame_set(1); cam.location=origin+Vector(views[3][1]); cam.rotation_euler=(Vector(views[3][2])-Vector(views[3][1])).to_track_quat('-Z','Y').to_euler(); d.lens=24
for o in roof:o.hide_render=False
bpy.ops.wm.save_as_mainfile(filepath=str(P/'Maldek_Rescue_Hut_Fitted_Review.blend'))
only=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
for v in views:
 if not only or any(v[0].startswith(x) for x in only): view(*v)
print('REVIEW COMPLETE')




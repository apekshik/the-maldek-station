import bpy,json,sys
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(OUT/'Maldek_Integrated_Station.blend'))
s=bpy.context.scene
def bounds(o):
 p=[o.matrix_world@Vector(v) for v in o.bound_box]
 return [Vector([min(v[i] for v in p) for i in range(3)]),Vector([max(v[i] for v in p) for i in range(3)])]
bpy.context.view_layer.update()
original={o:o.hide_render for o in bpy.data.objects}
bb={o:bounds(o) for o in bpy.data.objects if o.type in ['MESH','FONT']}
cams=sorted([o for o in bpy.data.objects if o.type=='CAMERA' and o.name[:2].isdigit()],key=lambda o:o.name)
requested=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
notes=[]
def note(text,loc,size=.45,rotation=(0,0,0)):
 cu=bpy.data.curves.new(text,'FONT');cu.body=text;cu.size=size;cu.align_x='CENTER';cu.align_y='CENTER';o=bpy.data.objects.new(text,cu);s.collection.objects.link(o);o.location=loc;o.rotation_euler=rotation
 m=bpy.data.materials.get('VF06_Plan_Ink')
 if not m:
  m=bpy.data.materials.new('VF06_Plan_Ink');m.diffuse_color=(.012,.018,.019,1);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.012,.018,.019,1)
 cu.materials.append(m);notes.append(o)
if requested:cams=[o for o in cams if o.name[:2] in requested]
(OUT/'previews').mkdir(exist_ok=True)
for cam in cams:
 for o in notes:o.hide_render=True
 for o,h in original.items():o.hide_render=h
 s.camera=cam
 if cam.name.startswith(('07','08')):
  cutoff=5.1 if cam.name.startswith('07') else 1.5
  for o,(a,b) in bb.items():
   if a.z>cutoff or (a.z>=cutoff-.3 and b.z>cutoff):o.hide_render=True
   if o.type=='FONT':o.hide_render=True
  # Roof/wall panels straddling the cut plane are hidden for an open plan.
  for o,(a,b) in bb.items():
   if b.z>cutoff and b.z-a.z>.8:o.hide_render=True
  if cam.name.startswith('07'):
   for text,p in [('WAITING HALL',(-13,-4.8,4.3)),('CONTROL',(-5,-2.8,4.3)),('GONDOLA',(0,8.3,4.3)),('DOCK',(-3,3.1,4.3)),('PLATE / 3.6 m',(-21.3,1,4.3)),('UP TO QUARTERS',(-4.8,-8.2,4.3)),('DOWN TO DRIVE',(9.5,2,4.3)),('ARRIVAL',(-12.8,-16.5,4.3)),('PUBLIC LEVEL +4.00 m',(-5,13.7,4.3))]:note(text,p,.38)
  else:
   for text,p in [('DRIVE / 0.00 m',(1.8,2.7,.12)),('SERVICE / STORES',(1.8,-3,.15)),('DRIVE MACHINERY',(0,9.4,.12)),('STAIR TO +4 m',(8.7,3,.15))]:note(text,p,.3)
 if cam.name.startswith('09'):
  cam.location=(32,2,5);cam.rotation_euler=(Vector((-4,2,5))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.clip_start=30
  for o,(a,b) in bb.items():
   if b.y>15 or a.y<-16 or a.z<-2:o.hide_render=True
  # Stage fill makes the exposed lower section legible independently of practicals.
  d=bpy.data.lights.new('Section_fill','AREA');d.energy=1600;d.size=12;o=bpy.data.objects.new('Section_fill',d);s.collection.objects.link(o);o.location=(12,2,6);o.rotation_euler=(Vector((-4,2,3))-o.location).to_track_quat('-Z','Y').to_euler();notes.append(o)
  import math
  for text,y,z in [('QUARTERS +7.65 m',-10,8.2),('PUBLIC +4.00 m',-10,4.4),('DRIVE 0.00 m',-10,.4)]:note(text,(1.8,y,z),.38,(math.pi/2,0,math.pi/2))
 if cam.name.startswith('10'):
  d=bpy.data.lights.new('Quarters_practical_fill','AREA');d.energy=120;d.size=2;o=bpy.data.objects.new('Quarters_practical_fill',d);s.collection.objects.link(o);o.location=(-4,-2.3,10.15);notes.append(o)
 s.render.filepath=str(OUT/'previews'/f'{cam.name}.png')
 print('VF06_RENDER',cam.name,flush=True);bpy.ops.render.render(write_still=True)

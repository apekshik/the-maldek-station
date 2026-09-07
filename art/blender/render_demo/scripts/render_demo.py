import bpy, json, sys, time
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
mode=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'proof'
scene=bpy.context.scene
p=bpy.context.preferences.addons['cycles'].preferences
p.compute_device_type='OPTIX'; p.refresh_devices()
for d in p.devices:d.use=d.type=='OPTIX'
scene.render.engine='CYCLES';scene.cycles.device='GPU'
scene.cycles.samples=48;scene.cycles.use_denoising=True
scene.cycles.use_animated_seed=False
scene.render.resolution_x=1280;scene.render.resolution_y=720;scene.render.resolution_percentage=100
scene.render.fps=24;scene.render.image_settings.file_format='PNG'
scene.render.use_persistent_data=True
scene.view_settings.exposure=.15
for l in scene.view_layers:l.use=l.name=='02_Full_Shell'
bpy.context.window.view_layer=scene.view_layers['02_Full_Shell']
shots=[
 dict(name='01_exterior',a=(25,34,13),b=(23,33,12.7),target=(0,4,3),lens=43,fstop=8),
 dict(name='02_platform',a=(-7,1,4.9),b=(-6.3,1.5,5),target=(0,9,5.2),lens=28,fstop=5.6),
 dict(name='03_operator',a=(-6.4,-1.9,5.65),b=(-6,-1.65,5.65),target=(-.4,10,5.1),lens=25,fstop=4),
 dict(name='04_forest',a=(23,25,9),b=(21.5,25,9),target=(0,5,4),lens=45,fstop=2.8),
]
# A linked source pine is staged only in the film copy for foreground parallax.
tree=bpy.data.objects['Distant_Pine_0'].copy()
tree.name='DEMO_Foreground_Pine';scene.collection.objects.link(tree)
tree.location=(20.5,20.2,-1.4);tree.hide_render=True
for s in shots:
 data=bpy.data.cameras.new('DEMO_'+s['name']);cam=bpy.data.objects.new(data.name,data);scene.collection.objects.link(cam)
 data.lens=s['lens'];data.dof.use_dof=True;data.dof.aperture_fstop=s['fstop']
 for frame,pos in [(1,s['a']),(60,s['b'])]:
  cam.location=pos;cam.rotation_euler=(Vector(s['target'])-cam.location).to_track_quat('-Z','Y').to_euler()
  data.dof.focus_distance=(Vector(s['target'])-cam.location).length
  cam.keyframe_insert(data_path='location',frame=frame);cam.keyframe_insert(data_path='rotation_euler',frame=frame)
  data.keyframe_insert(data_path='dof.focus_distance',frame=frame)
 s['camera']=cam.name
scene.frame_start=1;scene.frame_end=60
(ROOT/'proofs').mkdir(exist_ok=True)
(ROOT/'shots.json').write_text(json.dumps(shots,indent=2))
if mode in ('proof','forest_proof'):
 scene.cycles.samples=32
 for s in shots:
  if mode=='forest_proof' and s['name']!='04_forest':continue
  tree.hide_render=s['name']!='04_forest'
  scene.camera=bpy.data.objects[s['camera']]
  for frame in [1,60]:
   scene.frame_set(frame);scene.render.filepath=str(ROOT/'proofs'/f"{s['name']}_{frame:04}.png")
   bpy.ops.render.render(write_still=True,layer='02_Full_Shell')
else:
 scene.camera=bpy.data.objects[shots[0]['camera']]
 scene.frame_set(1)
 bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'maldek_render_demo.blend'))
 for s in shots:
  tree.hide_render=s['name']!='04_forest'
  scene.camera=bpy.data.objects[s['camera']]
  folder=ROOT/'frames'/s['name'];folder.mkdir(parents=True,exist_ok=True)
  for frame in range(1,61):
   path=folder/f'{frame:04}.png'
   if path.exists():continue
   scene.frame_set(frame);scene.render.filepath=str(path)
   start=time.time();bpy.ops.render.render(write_still=True,layer='02_Full_Shell')
   print('FRAME_DONE',s['name'],frame,round(time.time()-start,2),flush=True)

# SPDX-License-Identifier: GPL-3.0-or-later
"""Fast scene captures in a separate Blender process; never saves the source."""
import argparse, hashlib, json, sys, time
from pathlib import Path
import bpy
from mathutils import Vector

p=argparse.ArgumentParser();p.add_argument('--config',required=True);p.add_argument('--output',required=True)
p.add_argument('--shot',default='exterior');p.add_argument('--ffmpeg',required=True)
args=p.parse_args(sys.argv[sys.argv.index('--')+1:])
config_path=Path(args.config).resolve();config=json.loads(config_path.read_text())
out=Path(args.output).resolve();out.mkdir(parents=True,exist_ok=True)
assert not (out/'capture.json').exists(),'Use a new capture folder'
source=Path(bpy.data.filepath);digest=hashlib.sha256(source.read_bytes()).hexdigest()
scene=bpy.context.scene
# Eevee supports the source foliage alpha and materials without a Cycles render.
scene.render.engine='BLENDER_EEVEE'
scene.eevee.taa_render_samples=8
scene.eevee.use_raytracing=False
scene.render.resolution_x=1280;scene.render.resolution_y=720;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.use_sequencer=False;scene.render.use_compositing=False
scene.view_settings.exposure=0
for layer in scene.view_layers:layer.use=layer.name=='02_Full_Shell'
bpy.context.window.view_layer=scene.view_layers['02_Full_Shell']
for n in scene.world.node_tree.nodes:
 if n.type=='BACKGROUND':n.inputs['Strength'].default_value=.5
sun=bpy.data.objects.get('Overcast_Sun')
if sun:sun.data.energy=1.5
atmosphere=bpy.data.collections.get('17_Atmosphere')
if atmosphere:
 for obj in atmosphere.all_objects:obj.hide_render=True
manifest={'source':str(source),'source_sha256':digest,'blender':bpy.app.version_string,'engine':scene.render.engine,'shots':[]}
for shot in config['shots']:
 if shot['id']!=args.shot:continue
 camera=bpy.data.objects.new('H3_INPUT_'+shot['id'],bpy.data.cameras.new('H3_INPUT_'+shot['id']))
 scene.collection.objects.link(camera);camera.location=shot['position'];camera.data.lens=shot['lens']
 camera.rotation_euler=(Vector(shot['target'])-camera.location).to_track_quat('-Z','Y').to_euler();scene.camera=camera
 path=out/(shot['id']+'.png');scene.render.filepath=str(path)
 start=time.perf_counter();bpy.ops.render.render(write_still=True,layer='02_Full_Shell')
 manifest['shots'].append({'id':shot['id'],'image':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'seconds':time.perf_counter()-start})
 # Match the accepted Cycles path, slowed to five seconds for H3 conditioning.
 camera.keyframe_insert(data_path='location',frame=1);camera.keyframe_insert(data_path='rotation_euler',frame=1)
 camera.location=shot['end_position']
 camera.rotation_euler=(Vector(shot['target'])-camera.location).to_track_quat('-Z','Y').to_euler()
 camera.keyframe_insert(data_path='location',frame=120);camera.keyframe_insert(data_path='rotation_euler',frame=120)
 scene.render.resolution_x=640;scene.render.resolution_y=360;scene.render.fps=24
 frames=out/(shot['id']+'_frames');frames.mkdir()
 for frame in range(1,121):
  scene.frame_set(frame);scene.render.filepath=str(frames/f'{frame:04}.png')
  bpy.ops.render.render(write_still=True,layer='02_Full_Shell')
 import subprocess
 video=out/(shot['id']+'_motion.mp4')
 subprocess.run([args.ffmpeg,'-y','-v','error','-framerate','24','-i',str(frames/'%04d.png'),
                 '-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(video)],check=True)
 manifest['shots'][-1].update(video=video.name,video_sha256=hashlib.sha256(video.read_bytes()).hexdigest(),video_seconds=5,video_fps=24)
assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
manifest['source_unchanged']=True
(out/'capture.json').write_text(json.dumps(manifest,indent=2))

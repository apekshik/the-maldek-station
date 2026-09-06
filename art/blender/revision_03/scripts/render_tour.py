"""Render a map tour from saved revision03. Does not save or alter the source blend."""
import bpy,json,math,os
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1]/'tour';OUT.mkdir(exist_ok=True)
s=bpy.context.scene;full=s.view_layers['02_Full_Shell'];bpy.context.window.view_layer=full
s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True;s.cycles.device='CPU'
s.render.resolution_x=1440;s.render.resolution_y=960;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
shots=[
 ('01_cliff_station','Station over the gorge',(34,39,20),(0,4,2),36,'blue_hour'),
 ('02_open_drive','Exposed flywheel gallery',(5,10.8,1.65),(1.6,5.2,1.5),28,'blue_hour'),
 ('03_under_gondola','Below the gondola',(4.7,9.5,1.65),(0,10.7,4.2),23,'night'),
 ('04_stairs_overlook','Steel stairs and overlook',(22,-1,7),(9,4,3),28,'blue_hour'),
 ('05_relay_approach','Relay hidden in the woods',(42,5,4.65),(48,13,4),32,'night'),
 ('06_arrival','Arrival from the parking area',(-18,-16,1.2),(-10,-1,5),27,'blue_hour'),
 ('07_site_cutaway','Site layout and cutaway',(58,-62,78),(14,8,1),42,'cutaway'),
 ('08_drive_machinery','Flywheel and motor',(4.7,9.6,1.65),(1.8,5.4,1.3),32,'night'),
]
original_hide={o:o.hide_render for o in s.objects}
light_state={o:o.data.energy for o in s.objects if o.type=='LIGHT'}
bg=next(n for n in s.world.node_tree.nodes if n.type=='BACKGROUND');strength=bg.inputs['Strength'].default_value
manifest=json.loads((OUT/'shots.json').read_text()) if os.environ.get('TOUR_ONLY') and (OUT/'shots.json').exists() else []
for name,title,loc,target,lens,mood in shots:
 if os.environ.get('TOUR_ONLY') and name not in os.environ['TOUR_ONLY'].split(','):continue
 for o,hidden in original_hide.items():o.hide_render=hidden
 for o,power in light_state.items():o.data.energy=power
 bg.inputs['Strength'].default_value=strength;s.view_settings.exposure=-.15
 if mood in ['blue_hour','cutaway']:
  bg.inputs['Strength'].default_value=.22 if mood=='blue_hour' else .5
  bpy.data.objects['Overcast_Sun'].data.energy=.55 if mood=='blue_hour' else 1.5
  bpy.data.objects['Sky_Fill'].data.energy=4500 if mood=='blue_hour' else 12000
  s.view_settings.exposure=.15
 if mood=='cutaway':
  for cname in ['13_Roofs','16_Forest','17_Atmosphere','19_Cable_Route','20_Rain_Detail','90_References','91_Labels','93_Upper_Scale_References']:
   for o in bpy.data.collections[cname].objects:o.hide_render=True
 if name in ['02_open_drive','08_drive_machinery']:
  for o in bpy.data.collections['90_References'].objects:o.hide_render=True
 # Avoid a trunk or branch immediately in front of the lens; retained in the source scene.
 for o in bpy.data.collections['16_Forest'].objects:
  if math.hypot(o.location.x-loc[0],o.location.y-loc[1])<(15 if name=='01_cliff_station' else 4):o.hide_render=True
 d=bpy.data.cameras.new('TOUR_'+name);cam=bpy.data.objects.new(d.name,d);s.collection.objects.link(cam);cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();d.lens=lens;d.clip_end=1500
 if mood=='cutaway':d.type='ORTHO';d.ortho_scale=87
 s.camera=cam;s.render.filepath=str(OUT/(name+'.png'));print('TOUR_RENDER',name,flush=True);bpy.ops.render.render(write_still=True,layer=full.name)
 manifest=[entry for entry in manifest if entry['file']!=name+'.png']
 manifest.append({'file':name+'.png','title':title,'camera_m':loc,'target_m':target,'lens_mm':lens,'lighting':mood})
 (OUT/'shots.json').write_text(json.dumps(manifest,indent=2))
print('TOUR_COMPLETE',flush=True)

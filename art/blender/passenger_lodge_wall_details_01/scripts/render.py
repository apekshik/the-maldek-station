"""Reopen fitted package and render neutral/dim review views."""
import bpy,json,os
from mathutils import Vector
from pathlib import Path
P=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(P/'Maldek_Passenger_Lodge_Wall_Details_Fitted.blend'));s=bpy.context.scene
s.render.resolution_x=1500;s.render.resolution_y=1125;s.cycles.samples=20
try:
 prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
 for d in prefs.devices:d.use=d.type=='OPTIX'
 if any(d.type=='OPTIX' for d in prefs.devices):s.cycles.device='GPU'
except Exception:pass
for name,pos,target,lens in [('15_Kitchen_menu',(-21.6,-4.6,6.5),(-21.6,-6.96,6.53),32),('16_Cubby_label',(-19.63,-5.7,5.22),(-19.63,-6.596,5.156),40)]:
 d=bpy.data.cameras.new('PLG_REVIEW_'+name);o=bpy.data.objects.new(d.name,d);s.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.lens=lens;d.clip_start=.025
out=P/'renders';out.mkdir(exist_ok=True);manifest=[]
choice=os.environ.get('PLG_VIEWS','').split(',')
for camera in sorted([o for o in bpy.data.objects if o.type=='CAMERA' and o.name.startswith('PLG_REVIEW_')],key=lambda o:o.name):
 name=camera.name.replace('PLG_REVIEW_','')
 if choice!=[''] and name not in choice:continue
 s.camera=camera
 bpy.data.collections['PL03_Removable_Roof'].hide_render=name=='11_Overview'
 for mode in ['neutral','dim_warm'] if name in ['02_Timetable_close','04_Community_close','06_Hall_eye'] else ['neutral']:
  for light in bpy.data.objects:
   if light.type=='LIGHT' and light.name.startswith('PLG_TEMP_'):
    light.hide_render=False;light.data.energy=180 if mode=='neutral' else 36;light.data.color=(1,.94,.84) if mode=='neutral' else (1,.57,.25)
  for light in bpy.data.objects:
   if light.type=='LIGHT' and not light.name.startswith('PLG_TEMP_'):light.hide_render=mode=='dim_warm'
  if s.world and s.world.use_nodes:
   for node in s.world.node_tree.nodes:
    if node.type=='BACKGROUND':node.inputs['Strength'].default_value=.15 if mode=='neutral' else .008
  if name in ['02_Timetable_close','03_Map_close']:
   for light in bpy.data.objects:
    if light.type=='LIGHT':light.hide_render=True
   key=bpy.data.objects.get('PLG_TEMP_CASE_KEY')
   if not key:
    kd=bpy.data.lights.new('PLG_TEMP_CASE_KEY','AREA');key=bpy.data.objects.new(kd.name,kd);s.collection.objects.link(key)
   key.hide_render=False;key.data.energy=220 if mode=='neutral' else 45;key.data.size=1.4;key.data.color=(1,.94,.84) if mode=='neutral' else (1,.57,.25)
   key.location=(-20.0,1.8,6.95) if name=='02_Timetable_close' else (-12.2,-1.65,6.95)
   target=Vector((-18.3,3.77,5.65) if name=='02_Timetable_close' else (-10.33,.4,5.68));key.rotation_euler=(target-key.location).to_track_quat('-Z','Y').to_euler()
  elif bpy.data.objects.get('PLG_TEMP_CASE_KEY'):bpy.data.objects['PLG_TEMP_CASE_KEY'].hide_render=True
  s.render.filepath=str(out/(name+'_'+mode+'.png'));bpy.ops.render.render(write_still=True)
  manifest.append(dict(file='renders/'+name+'_'+mode+'.png',camera_position=list(camera.location),lens_mm=camera.data.lens,mode=mode,temporary_review_lights=True,roof_hidden=name=='11_Overview'))
old=json.loads((P/'render_manifest.json').read_text()) if (P/'render_manifest.json').exists() else []
records={v['file']:v for v in old+manifest};(P/'render_manifest.json').write_text(json.dumps(list(records.values()),indent=2))
# Rear mounting / close inspection, with context explicitly hidden in temporary review state.
from mathutils import Vector
ref=bpy.data.collections['REFERENCE_ONLY_Source_Context'];ref.hide_render=True
owned=bpy.data.collections['PLG_Wall_Details'];cam=s.camera
for light in bpy.data.objects:
 if light.type=='LIGHT':light.hide_render=True
ld=bpy.data.lights.new('PLG_TEMP_INSPECTION','AREA');ld.energy=90;ld.size=2;lo=bpy.data.objects.new(ld.name,ld);s.collection.objects.link(lo)
for name,rootname,pos,target in [('12_Poster_inspection','PLG_Poster_1',(-22.0,1.425,5.675),(-23.87,1.425,5.675)),('13_Poster_mounting_rear','PLG_Poster_1',(-25.8,1.425,5.675),(-23.92,1.425,5.675)),('14_Case_maintenance','PLG_Timetable',(-17.15,2.3,5.75),(-18.3,3.7,5.65))]:
 root=bpy.data.objects[rootname]
 for o in owned.objects:
  par=o
  while par.parent:par=par.parent
  o.hide_render=par!=root
 cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='PERSP';cam.data.lens=30 if name=='14_Case_maintenance' else 42
 lo.location=Vector(pos)+Vector((0,0,1));lo.rotation_euler=(Vector(target)-lo.location).to_track_quat('-Z','Y').to_euler()
 if name=='14_Case_maintenance':
  bpy.data.objects['PLG_Timetable_glass'].location.z=.22
  for o in owned.objects:
   if o.name.startswith('PLG_Timetable_retainer'):o.location.z+=.23
 s.render.filepath=str(out/(name+'_neutral.png'));bpy.ops.render.render(write_still=True)
 manifest.append(dict(file='renders/'+name+'_neutral.png',camera_position=list(cam.location),mode='isolated neutral',temporary_review_lights=True,reference_hidden=True,pose='Removable glazing and retainers exploded for maintenance; illustrative only' if name=='14_Case_maintenance' else 'assembled'))
old=json.loads((P/'render_manifest.json').read_text()) if (P/'render_manifest.json').exists() else []
records={v['file']:v for v in old+manifest};(P/'render_manifest.json').write_text(json.dumps(list(records.values()),indent=2))

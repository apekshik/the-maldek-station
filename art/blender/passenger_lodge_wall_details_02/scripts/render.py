"""Paired fitted renders. Source camera matches lodge 04's 03_Hall."""
import bpy,json,math,hashlib,os
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1];file=P/'Maldek_East_Wall_Details_Fitted.blend';before=hashlib.sha256(file.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(file));s=bpy.context.scene;s.frame_set(1)
c=bpy.data.collections.new('PLG2_REVIEW_ONLY');s.collection.children.link(c);owned=bpy.data.collections['PLG2_East_Wall_Details']
s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True;s.render.resolution_x=1600;s.render.resolution_y=1100;s.render.resolution_percentage=100
try:
 prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
 for d in prefs.devices:d.use=d.type=='OPTIX'
 if any(d.use for d in prefs.devices):s.cycles.device='GPU'
except Exception:pass
energies={o.name:o.data.energy for o in s.objects if o.type=='LIGHT'}
views=[('01_Before_user_angle',(-22.7,2.4,5.65),(-14,-5.7,5.1),22),('02_After_user_angle',(-22.7,2.4,5.65),(-14,-5.7,5.1),22),('03_Wall_elevation',(-17.8,-2.15,5.67),(-10.28,-2.15,5.67),32),('04_Oblique_walk',(-12.0,1.1,5.65),(-10.3,-3.1,5.55),23),('05_Leaflet_rack',(-11.62,-3.23,5.24),(-10.40,-3.23,5.18),42),('06_Climate_gauge',(-11.12,-4.03,5.91),(-10.35,-4.03,5.91),43),('07_First_aid',(-11.44,-5.02,5.61),(-10.40,-5.02,5.61),45),('08_Cabinet_open',(-11.52,-4.76,5.64),(-10.45,-5.02,5.61),36),('09_Dim_warm',(-22.7,2.4,5.65),(-14,-5.7,5.1),22),('10_Archive_pair',(-12.0,-2.24,5.8),(-10.32,-2.24,5.8),32),('11_Safety',(-11.9,-1.12,5.78),(-10.32,-1.12,5.78),36)]
key=bpy.data.lights.new('PLG2_TEMP_KEY','AREA');key.size=1.2;key.energy=120;lamp=bpy.data.objects.new(key.name,key);c.objects.link(lamp)
pivot=bpy.data.objects['PLG2_Cabinet_LeafPivot'];pivot.animation_data_clear();out=P/'renders';out.mkdir(exist_ok=True);records=[];select=os.environ.get('PLG2_VIEWS','').split(',')
for name,pos,target,lens in views:
 if select!=[''] and name not in select:continue
 owned.hide_render=name.startswith('01_');pivot.rotation_euler.y=math.radians(-95 if 'Cabinet_open' in name else 0)
 for ln,energy in energies.items():bpy.data.objects[ln].data.energy=energy*(.23 if name=='09_Dim_warm' else 1)
 lamp.hide_render=name in ['01_Before_user_angle','02_After_user_angle','09_Dim_warm']
 lamp.location=(pos[0],pos[1]+.85,min(pos[2]+.9,6.95));lamp.rotation_euler=(Vector(target)-lamp.location).to_track_quat('-Z','Y').to_euler()
 d=bpy.data.cameras.new('PLG2_REVIEW_'+name);cam=bpy.data.objects.new(d.name,d);c.objects.link(cam);cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();d.lens=lens;d.clip_start=.02
 if name=='03_Wall_elevation':d.type='ORTHO';d.ortho_scale=8.0
 s.camera=cam;s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
 records.append(dict(file='renders/'+name+'.png',camera_position=pos,target=target,lens=lens,projection=d.type,temporary_review_lighting=True,source_preserved=True,new_collection_visible=not owned.hide_render,cabinet_open_degrees=95 if 'Cabinet_open' in name else 0))
old=json.loads((P/'render_manifest.json').read_text()) if (P/'render_manifest.json').exists() else [];merged={x['file']:x for x in old+records};(P/'render_manifest.json').write_text(json.dumps(list(merged.values()),indent=2));assert hashlib.sha256(file.read_bytes()).hexdigest()==before

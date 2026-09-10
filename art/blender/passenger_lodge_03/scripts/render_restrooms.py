"""Roof-on restroom-area review renders; no source model changes."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1];src=OUT/'Maldek_Passenger_Lodge_Materials.blend';before=hashlib.sha256(src.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.data.scenes['05_Material_Study'];bpy.context.window.scene=s
s.render.resolution_x=1800;s.render.resolution_y=1200;s.cycles.samples=48;s.cycles.use_denoising=True
bpy.data.collections['PL03_Removable_Roof'].hide_render=False
for x,y,power,size in [(-15,-5.5,160,3),(-15,-8.2,90,1.4),(-11.8,-8.2,90,1.4),(-14.6,-11,120,2),(-11.6,-11,120,2)]:
 d=bpy.data.lights.new('Temporary restroom review light','AREA');d.energy=power;d.shape='DISK';d.size=size;d.color=(1,.88,.72);o=bpy.data.objects.new(d.name,d);s.collection.objects.link(o);o.location=(x,y,7.05)
views=[
 ('PL03_Restroom_Approach',(-15.1,-5.25,5.65),(-15.1,-8.4,5.35),24),
 ('PL03_Restroom_Hallway',(-15.25,-8.25,5.65),(-11.4,-8.7,5.3),20),
 ('PL03_Restroom_Hallway_Reverse',(-11.1,-8.6,5.65),(-15,-8.3,5.3),20),
 ('PL03_Restroom_Interior',(-13.65,-9.65,5.65),(-14.7,-12,4.95),20)]
manifest=[]
for name,pos,target,lens in views:
 d=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.lens=lens;d.clip_start=.04;s.camera=o
 s.render.filepath=str(OUT/'previews'/f'{name}.png');bpy.ops.render.render(write_still=True,scene=s.name)
 manifest.append({'image':name+'.png','position':pos,'target':target,'lens_mm':lens})
assert hashlib.sha256(src.read_bytes()).hexdigest()==before
(OUT/'restroom_views.json').write_text(json.dumps({'source_unchanged':True,'source_sha256':before,'temporary_review_lighting':True,'roof_visible':True,'views':manifest},indent=2))
print('Restroom views complete; source unchanged')

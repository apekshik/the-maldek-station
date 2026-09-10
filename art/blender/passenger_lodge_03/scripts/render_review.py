"""Additional review cameras and temporary interior lighting; source unchanged."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1];src=OUT/'Maldek_Passenger_Lodge_Materials.blend';before=hashlib.sha256(src.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.data.scenes['05_Material_Study'];bpy.context.window.scene=s
s.render.resolution_x=1800;s.render.resolution_y=1200;s.render.resolution_percentage=100;s.cycles.samples=48;s.cycles.use_denoising=True
roof=bpy.data.collections['PL03_Removable_Roof'];roof.hide_render=False
lights=[]
for x,y in [(-20,-1.5),(-14,-1.5),(-20,-5.5),(-14,-5.5),(-21.5,-9.5)]:
 d=bpy.data.lights.new('Review softbox','AREA');d.energy=160;d.shape='DISK';d.size=3;d.color=(1,.84,.65);o=bpy.data.objects.new('Review softbox',d);s.collection.objects.link(o);o.location=(x,y,7.05);lights.append(o)
views=[
 ('PL03_Front_Alongside_Control',(-32,24,16),(-12,-2,5),37,False),
 ('PL03_Arrival_And_Station',(12,-34,22),(-13,-2,4),48,False),
 ('PL03_Inside_From_Entrance',(-17.1,-6.35,5.65),(-17.1,2.3,5.35),None,True),
 ('PL03_Inside_Toward_Service',(-21.8,1.9,5.65),(-15.8,-6.8,5.25),None,True),
 ('PL03_Front_Platform',(-27,12,7),(-13,1,5.7),None,False)]
manifest=[]
for name,pos,target,ortho,inside in views:
 d=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.lens=22 if inside else 25;d.clip_start=.05
 if ortho:d.type='ORTHO';d.ortho_scale=ortho
 for lamp in lights:lamp.hide_render=not inside
 s.camera=o;s.render.filepath=str(OUT/'previews'/f'{name}.png');bpy.ops.render.render(write_still=True,scene=s.name)
 manifest.append({'image':name+'.png','camera_position':pos,'target':target,'temporary_review_lights':inside,'roof_visible':True})
assert hashlib.sha256(src.read_bytes()).hexdigest()==before
(OUT/'additional_views.json').write_text(json.dumps({'source_unchanged':True,'source_sha256':before,'views':manifest},indent=2))
print('Five additional views rendered; source unchanged')

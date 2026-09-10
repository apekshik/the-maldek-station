"""Corner evidence and before facade, using a reopened review copy only."""
import bpy,json
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(OUT/'Maldek_Passenger_Lodge_Windows.blend'))
s=bpy.data.scenes['05_Material_Study'];bpy.context.window.scene=s
for o in bpy.data.collections['PLW_REVIEW_ONLY__DO_NOT_EXPORT'].objects:
    if o.type=='LIGHT':o.hide_render=False
prefs=bpy.context.preferences.addons['cycles'].preferences
try:
    prefs.compute_device_type='OPTIX';prefs.get_devices()
    for d in prefs.devices:d.use=d.type=='OPTIX'
    if any(d.use for d in prefs.devices):s.cycles.device='GPU'
except Exception:pass
manifest=json.loads((OUT/'replacement_manifest.json').read_text());records=[]
s.render.resolution_x=700;s.render.resolution_y=700;s.cycles.samples=24
for k,ass in enumerate(manifest['assemblies'],1):
    x,y,z=ass['translation_m']
    for side,dx in [('West',0),('East',3.8)]:
        for level,dz in [('Sill',.03),('Head',1.68)]:
            for face,sign in [('Exterior',1),('Interior',-1)]:
                name=f'PLW_{k:02}_{side}_{level}_{face}'
                d=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,d);s.collection.objects.link(o)
                target=Vector((x+dx,3.95,z+dz));o.location=target+Vector((.25 if side=='West' else -.25,.8*sign,.20 if level=='Sill' else -.20))
                o.rotation_euler=(target-o.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=.53;d.clip_start=.01;s.camera=o
                s.render.filepath=str(OUT/'previews'/f'{name}.png');bpy.ops.render.render(write_still=True,scene=s.name)
                records.append(dict(image=name+'.png',camera_m=list(o.location),target_m=list(target),roof_visible=True))
# Matched before view retains exactly the same camera, roof and review lighting.
bpy.data.collections['PLW_Assets'].hide_render=True
for o in bpy.data.collections['PLW_REVIEW_ONLY__DO_NOT_EXPORT'].objects:
    if o.type=='LIGHT':o.hide_render=True
for proxy in manifest['replace']:
    lo,hi=proxy['bounds'];bpy.ops.mesh.primitive_cube_add(size=1,location=[(a+b)/2 for a,b in zip(lo,hi)]);o=bpy.context.object;o.name='REVIEW_BEFORE_'+proxy['name'];o.dimensions=[b-a for a,b in zip(lo,hi)];o.data.materials.append(bpy.data.materials['PL03_Frosted_Glass'])
s.camera=bpy.data.objects['PLW_Facade_Beside_Control'];s.render.resolution_x=1500;s.render.resolution_y=1000;s.cycles.samples=32
s.render.filepath=str(OUT/'previews/PLW_Facade_Before.png');bpy.ops.render.render(write_still=True,scene=s.name)
(OUT/'corner_views.json').write_text(json.dumps(records,indent=2))

import bpy,json
from pathlib import Path
from mathutils import Vector
out=Path(__file__).resolve().parents[1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(out/'fbx/SM_Maldek_Central_Pylon.fbx'))
obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert len(obs)==1
ob=obs[0];ps=[ob.matrix_world@v.co for v in ob.data.vertices];lo=[min(v[i] for v in ps) for i in range(3)];hi=[max(v[i] for v in ps) for i in range(3)]
assert abs(hi[2]-45.12)<.002
assert not any(m.name.startswith('STUDY_') or m.name.startswith('VF06_') for m in ob.data.materials)
c=json.loads((out/'clearance.json').read_text());assert not c['collisions']
report={'fbx_reimported':True,'mesh_count':1,'bounds_m':[lo,hi],'materials':[m.name for m in ob.data.materials],'sampled_cabin_positions':len(c['tested_cabin_travel_positions_m']),'mesh_intersections':0,'unreal_integration':'pending','weathering_transfer':'Procedural Blender shaders require baking or recreation in Unreal'}
(out/'validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))

import bpy,json,math
from pathlib import Path
from mathutils import Vector
out=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(out/'Maldek_Modern_Twin_Pylon.blend'),load_ui=False)
parts=bpy.data.collections['PYLON | export geometry'];obs=list(parts.objects)
assert len([o for o in obs if o.name.startswith('Tubular_leg_')])==8
rollers=[o for o in obs if o.name.startswith('Rubber_sheave')];assert len(rollers)==24
clearances=[]
for side in [-1,1]:
 lane=sorted([o for o in rollers if o.location.x*side>0],key=lambda o:o.location.y)
 assert len(lane)==12
 clearances += [b.location.y-a.location.y-.586 for a,b in zip(lane,lane[1:])]
assert min(clearances)>.05,min(clearances)
sourcebounds=[]
for o in obs:
 sourcebounds.extend([o.matrix_world@Vector(p) for p in o.bound_box])
lo=[min(p[i] for p in sourcebounds) for i in range(3)];hi=[max(p[i] for p in sourcebounds) for i in range(3)]
assert abs(hi[2]-43.63)<.001
stage=bpy.data.collections['STUDY | staging - not exported']
for o in stage.objects:
 if o.name.startswith('STUDY_cable'):assert abs(o.location.z-.032-(42.02+.275))<.00001
assert all((out/'renders'/f'{n}.png').exists() for n in ['01_full_pylon','02_crosshead','03_base_detail','04_night'])
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(out/'fbx/SM_Maldek_Twin_Pylon_42m.fbx'))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert len(meshes)==1,len(meshes)
o=meshes[0];assert o.name.startswith('SM_Maldek_Twin_Pylon_42m')
vs=[o.matrix_world@v.co for v in o.data.vertices];flo=[min(p[i] for p in vs) for i in range(3)];fhi=[max(p[i] for p in vs) for i in range(3)]
assert abs(fhi[2]-43.63)<.002,(flo,fhi)
assert flo[2]>-.001
assert all(not m.name.startswith('STUDY_') for m in o.data.materials)
report={'reopened_blend':True,'shaft_sections':8,'sheaves':24,'minimum_adjacent_sheave_flange_clearance_m':min(clearances),'rope_contact_error_m':0,'fbx_reimported':True,'fbx_mesh_count':len(meshes),'fbx_bounds_m':[flo,fhi],'fbx_materials':[m.name for m in o.data.materials],'renders_present':4,'unreal_validation':'pending editor availability and route-specific placement'}
(out/'validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))

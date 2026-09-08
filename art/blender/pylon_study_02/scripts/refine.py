from pathlib import Path
p=Path('art/blender/pylon_study_02/scripts/build.py');s=p.read_text()
s=s.replace(" box('Head_longitudinal_carrier',(-.58,0,43.55),(.36,5.0,.28),galv,.035)","box('Head_longitudinal_carrier',(-.58,0,43.55),(.36,5.0,.28),galv,.035)")
s=s.replace(" tube('Maintenance_band',(x0+(x1-x0)*.115,0,5.78),(x0+(x1-x0)*.119,0,5.94),1.018,1.017,amber)"," t0=(5.78-a.z)/(b.z-a.z);t1=(5.94-a.z)/(b.z-a.z)\n tube('Maintenance_band',a.lerp(b,t0),a.lerp(b,t1),1.05-.34*t0+.008,1.05-.34*t1+.008,amber)")
s=s.replace("'design_height_m':45.12","'design_height_m':45.12")
insert='''# The approved cabin is a study-only reference; no production cabin asset is changed.
source=OUT.parents[2]/'art/blender/visual_fidelity_07/Maldek_Station_Cleanup.blend'
with bpy.data.libraries.load(str(source),link=False) as (available,loaded):loaded.collections=['12_Gondola','VF06_Gondola_Details']
for c in loaded.collections:stage.children.link(c)
bpy.context.view_layer.update()
cabin_objects=[];transforms={}
for c in loaded.collections:
 for ob in c.all_objects:
  if ob not in cabin_objects and ob.type in {'MESH','CURVE','FONT'}:cabin_objects.append(ob);transforms[ob]=ob.matrix_world.copy()
for ob in cabin_objects:
 ob.parent=None;ob.matrix_world=transforms[ob];ob.location+=Vector((.10,-15.05,33.45));ob.name='STUDY_CABIN_'+ob.name
# A small side-clearing upper hanger is a concept adapter; kept out of the tower FBX.
adapter=[]
for a,b in [((.1,-7,41.36),(.72,-7,41.36)),((.72,-7,41.36),(.72,-7,42.49)),((.72,-7,42.49),(.04,-7,42.49)),((.04,-7,42.49),(.04,-7,42.327))]:
 adapter.append(tube('STUDY_CABIN_hanger_adapter',a,b,.060,mat=dark,verts=16))
cabin_objects+=adapter
scene['Cabin_adapter']='Study-only side-clearing upper hanger, existing cabin body retained; production rig unchanged.'
'''
s=s.replace('# Lighting and cameras deliberately independent',insert+'\n# Lighting and cameras deliberately independent')
s=s.replace(" '05_night':camera", " '05_hanger_detail':camera('CAM_05_Hanger',(4,-12,43),(0,-7,41.9),62),\n '06_night':camera")
s=s.replace("if name=='05_night':", "if name=='06_night':")
s=s.replace("['03_base_detail','04_front_clearance']", "['03_base_detail','04_front_clearance','05_hanger_detail']")
s=s.replace(" scene.camera=cam\n", " scene.camera=cam\n if name=='04_front_clearance':\n  for ob in cabin_objects:ob.location.y+=7\n")
s=s.replace("scene.render.filepath=str(OUT/'renders'/f'{name}.png');bpy.ops.render.render(write_still=True)","scene.render.filepath=str(OUT/'renders'/f'{name}.png');bpy.ops.render.render(write_still=True)\n if name=='04_front_clearance':\n  for ob in cabin_objects:ob.location.y-=7")
p.write_text(s)

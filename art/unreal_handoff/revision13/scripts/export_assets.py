import sys,json,math,hashlib
from pathlib import Path
from collections import defaultdict
import bpy
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1];ROOT=OUT.parents[2]
sys.path.insert(0,str(OUT.parent/'revision12/scripts'));import mesh_handoff as mh
mh.OUT=OUT
source=ROOT/'art/blender/visual_fidelity_09/Maldek_Service_Apron_Refinement.blend';mh.SOURCE=source;mh.EXPECTED=hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'art/blender/visual_fidelity_07/Maldek_Station_Cleanup.blend'),load_ui=False)
o=bpy.data.objects['R11_Current_Terrain'];baseline={(round((o.matrix_world@v.co).x,4),round((o.matrix_world@v.co).y,4)):(o.matrix_world@v.co).z for v in o.data.vertices}
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);scene=bpy.context.scene;deps=bpy.context.evaluated_depsgraph_get();h=mh.Handoff(scene,deps,'fbx')
old=json.loads((OUT.parent/'revision12/handoff_manifest.json').read_text());r8=json.loads((ROOT/'art/blender/visual_fidelity_08/build_report.json').read_text());r9=json.loads((ROOT/'art/blender/visual_fidelity_09/layout.json').read_text());removed=set(r8['removed_objects']+r9['removed_objects'])
retired=[r for r in old['chunks'] if removed.intersection(r['sources'])];preserved=[]
for r in retired:
 keep=[bpy.data.objects[n] for n in r['sources'] if n not in removed and n in bpy.data.objects]
 if keep:preserved.extend(keep)
# Explicit simple collision on individual pieces, never across whole rooms.
original_kind=mh.collision_kind
def ck(o):
 n=o.name.lower()
 if 'connected_service_road' in n:return 'surface_prisms'
 if any(t in n for t in ['concrete_panel','hall_foundation','workshop_floor','inertia_plinth']):return 'floor'
 if any(t in n for t in ['insulated_wall_core','opening_jamb','opening_header','open_service_door','switchgear_cabinet','day_tank','crankcase','alternator_body','radiator_frame','dished_horizontal_shell','column','bund_side','bund_end','stem_foundation']):return 'solid'
 return original_kind(o)
mh.collision_kind=ck
jobs=defaultdict(list)
for c in bpy.data.collections:
 if not c.name.startswith(('VF08_','VF09_')) or 'Presentation' in c.name:continue
 for o in c.objects:
  if o.type not in ['MESH','CURVE','FONT'] or o.hide_render:continue
  role='grating' if 'grating_tile' in o.name.lower() else ('thin' if o.type=='CURVE' else 'solid')
  # Room facade cladding uses exterior weather; equipment and inner lining use indoor materials.
  a,b=mh.bounds(o);p=[(a[i]+b[i])/2 for i in range(3)]
  indoor=c.name in ['VF08_04_Diesel_Generator','VF08_05_Plant_Systems','VF08_03_Workshop'] or 'Insulated_wall_core' in o.name or 'Floor_panel' in o.name
  if c.name=='VF08_05_Plant_Systems' and p[2]>3.3:indoor=False
  key=(c.name,role,'Indoor' if indoor else 'Exterior')
  jobs[key].append(o)
for (cn,role,exp),obs in jobs.items():
 row=h.chunk('SM_R13_'+cn+'_'+role+'_'+exp,obs,pivot=(24,-16,0),role=role,exposure=exp);row['collection']=cn
if preserved:h.chunk('SM_R13_Preserved_Water_Valve',preserved,pivot=(0,0,0),exposure='Exterior')
# Merge only the actual VF08/09 terrain edits into R12's forest-relative surface.
o=bpy.data.objects['R11_Current_Terrain'];current={(round((o.matrix_world@v.co).x,4),round((o.matrix_world@v.co).y,4)):(o.matrix_world@v.co).z for v in o.data.vertices}
grid=json.loads((OUT.parent/'revision12/terrain_grid.json').read_text());vs=[];changes=[]
for x,y,z in grid['vertices']:
 key=(round(x,4),round(y,4));new=current[key];before=baseline[key]
 # Exact approved grade in the changed footprint; preserve current forest elsewhere.
 value=min(z,new) if abs(new-before)>.001 else z
 vs.append((x,y,value))
 if abs(value-z)>.001:changes.append([x,y,z,value])
me=bpy.data.meshes.new('R13_Terrain');me.from_pydata(vs,[],[tuple(p.vertices) for p in o.data.polygons]);me.materials.append(o.data.materials[0]);ob=bpy.data.objects.new('R13_Terrain',me);scene.collection.objects.link(ob);bpy.context.view_layer.update();h.deps=bpy.context.evaluated_depsgraph_get()
r=h.chunk('SM_R13_Terrain',[ob],role='terrain',surface='Soil');r['complex_collision']=True;r['preserve_material']=next(r for r in old['chunks'] if r['name']=='SM_R12_Terrain')['preserve_material']
m=h.save('handoff_manifest');m['retire_assets']=[r['name'] for r in retired]+['SM_R12_Terrain'];m['terrain_changes']=changes;(OUT/'handoff_manifest.json').write_text(json.dumps(m,indent=2))
(OUT/'terrain_grid.json').write_text(json.dumps({'vertices':vs}));print('R13_EXPORT_COMPLETE',len(m['chunks']),len(changes),flush=True)

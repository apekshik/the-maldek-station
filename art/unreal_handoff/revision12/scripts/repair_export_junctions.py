"""Correct two source numerical defects in export copies; approved VF07 remains immutable."""
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mesh_handoff import *
source,deps=load_source();h=Handoff(source,deps,'fbx');manifest=json.loads((OUT/'handoff_manifest.json').read_text());changed=[]
S=Matrix(((1,1/3,0,5),(0,1,0,0),(0,.1,1,1.5),(0,0,0,1)))
names=['Open_grating_tile.'+str(i) for i in range(140,144)];edits=[]
for name in names:
 o=bpy.data.objects[name];assert any(c.name=='VF06_Water_Service_Terrace' for c in o.users_collection)
 before=bounds(o);pts=[v.co.copy() for v in o.data.vertices];lo=[min(v[i] for v in pts) for i in range(3)];hi=[max(v[i] for v in pts) for i in range(3)]
 assert 19.7<lo[0]<22.3 and -15.1<lo[1]<-11.9 and abs(hi[2]+1)<.01
 o.data=o.data.copy();o.matrix_world=Matrix.Identity(4)
 for v in o.data.vertices:v.co=S@v.co
 hull=[list(S@Vector((x,y,z))) for z in [lo[2],hi[2]] for y in [lo[1]-.005,hi[1]+.005] for x in [lo[0]-.005,hi[0]+.005]]
 o['handoff_collision_vertices']=json.dumps(hull);o.data.update();edits.append({'object':name,'before':before,'operation':'Bake the original VF06 intended shear directly into vertices. Blender object TRS decomposition had displaced the world-coordinate grating geometry.','intended_matrix':[list(row) for row in S]})
for name in ['Cantilever_transfer_beam','Cantilever_transfer_beam.001']:
 o=bpy.data.objects[name];o.data=o.data.copy();top=max(v.co.z for v in o.data.vertices)
 for v in o.data.vertices:
  if abs(v.co.z-top)<.00001:v.co.z-=.003
 o.data.update();edits.append({'object':name,'operation':'Recess the beam top by 3 mm to separate its coplanar face from the finished quarters floor. Beam location, underside, supports and floor remain fixed.'})
bpy.context.view_layer.update();h.deps=bpy.context.evaluated_depsgraph_get()
for index,row in enumerate(list(manifest['chunks'])):
 if not set(row['sources'])&set(names+['Cantilever_transfer_beam','Cantilever_transfer_beam.001']):continue
 objects=[bpy.data.objects[n] for n in row['sources']+row.get('source_collision_guides',[])]
 exposure=next(v.get('exposure') for v in manifest['materials'].values() if v['slot']==row['material_slots'][0])
 new=h.chunk(row['name'],objects,pivot=row['pivot'],role=row['role'],surface=row['physical_surface'],targets=row['replacement_targets'],exposure=exposure)
 for key in ['stage','collection','source_collision_guides','material_bindings_override']:
  if key in row:new[key]=row[key]
 assert new['material_slots']==row['material_slots'];manifest['chunks'][index]=new;changed.append(row['name'])
manifest['materials'].update(h.materials);(OUT/'handoff_manifest.json').write_text(json.dumps(manifest,indent=2));h.save('junction_repairs_export')
(OUT/'export_junction_repairs.json').write_text(json.dumps({'source_sha256':EXPECTED,'approved_source_modified':False,'edits':edits,'changed_assets':changed,'water_access_centerline':[[22,-12,-.7],[21.5,-13.5,-.85],[21,-15,-1],[21,-15.7,-1]]},indent=2))

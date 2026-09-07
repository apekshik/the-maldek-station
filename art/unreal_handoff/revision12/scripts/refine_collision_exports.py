"""Update only assemblies whose collision classification changed; preserve their export identities."""
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mesh_handoff import *
source,deps=load_source();h=Handoff(source,deps,'fbx');manifest=json.loads((OUT/'handoff_manifest.json').read_text());changed=[]
for index,row in enumerate(list(manifest['chunks'])):
 if row['role']=='terrain':continue
 objects=[bpy.data.objects[n] for n in row['sources']+row.get('source_collision_guides',[])]
 old={b['source']:b['kind'] for b in row['collision_boxes']};new={o.name:collision_kind(o) for o in objects if collision_kind(o)}
 if old==new:continue
 print('REFINE_COLLISION',row['name'],flush=True)
 newrow=h.chunk(row['name'],objects,pivot=row['pivot'],role=row['role'],surface=row['physical_surface'],targets=row['replacement_targets'],exposure=manifest['materials'][next(k for k,v in manifest['materials'].items() if v['slot']==row['material_slots'][0])].get('exposure'))
 for key in ['stage','collection','source_collision_guides','material_bindings_override','retained_from_combined']:
  if key in row:newrow[key]=row[key]
 if row['collection']=='VF07_Continuous_Service_Routes':newrow['physical_surface']='Gravel';newrow['role']='floor';newrow['nanite']=False
 if row['collection']=='VF07_Service_Apron' and 'Continuous_service_apron' in row['sources']:newrow['physical_surface']='Concrete'
 manifest['chunks'][index]=newrow;changed.append({'name':row['name'],'old_hulls':row['collision_hulls'],'new_hulls':newrow['collision_hulls']})
manifest['materials'].update(h.materials);(OUT/'handoff_manifest.json').write_text(json.dumps(manifest,indent=2));h.save('collision_refinement_export')
(OUT/'collision_refinement.json').write_text(json.dumps({'changed':changed,'note':'Convex prisms follow individual road/apron faces; furniture main bodies receive collision.'},indent=2));print('COLLISION_REFINEMENT_COMPLETE',len(changed),flush=True)

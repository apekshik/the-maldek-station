"""Retain parking/car from the old combined parking-and-arrival actor; exclude its superseded arrival."""
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mesh_handoff import *
source,deps=load_source();h=Handoff(source,deps,'fbx');manifest=json.loads((OUT/'handoff_manifest.json').read_text())
inventory=json.loads((OUT/'replacement_inventory.json').read_text());target=next(r for r in inventory if r['label']=='R04_10_Parking_and_Arrival');component=target['components'][0]
rows=[]
for o in bpy.data.collections['10_Parking_and_Arrival'].objects:
 assert o.name in ['Parking','Parked_Car'],o.name
 row=h.chunk('SM_R12_Retained_'+o.name,[o],surface='Gravel' if o.name=='Parking' else 'Metal',role='floor' if o.name=='Parking' else 'solid',targets=[{'actor':target['r12_path'],'component':component['name'],'old_mesh':component['mesh']}],exposure='Exterior')
 row.update(stage='Circulation',collection='10_Parking_and_Arrival',retained_from_combined=True)
 old_slots=json.loads((OUT/'retained_asset_bindings.json').read_text())['R04_10_Parking_and_Arrival']['slots']
 old_bindings={s['name']:s['material'] for s in old_slots}
 row['material_bindings_override']={'UE_'+slug(m.name)+'__Exterior':old_bindings[m.name] for m in o.data.materials}
 rows.append(row)
for row in rows:
 manifest['chunks']=[r for r in manifest['chunks'] if r['name']!=row['name']]+[row]
manifest['materials'].update(h.materials)
manifest['excluded_collections'].pop('10_Parking_and_Arrival',None)
manifest['parking_split']='Preserve Parking and Parked_Car geometry/pivots; remove old Arrival flight/plinth and obsolete path from the combined R10 actor. Forest approach actor remains separate and intact.'
(OUT/'handoff_manifest.json').write_text(json.dumps(manifest,indent=2));h.save('parking_split_export')
print('PARKING_SPLIT_EXPORTED',len(rows),flush=True)

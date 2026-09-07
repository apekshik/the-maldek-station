import unreal,json
from pathlib import Path
base=Path(__file__).resolve().parents[1];rows=json.loads((base/'replacement_inventory.json').read_text());report={}
for label in ['R04_10_Parking_and_Arrival','R04_20_Lookout_Bridge']:
 row=next(r for r in rows if r['label']==label);c=row['components'][0];mesh=unreal.load_asset(c['mesh'])
 report[label]={'slots':[{'name':str(s.material_slot_name),'material':c['materials'][i]} for i,s in enumerate(mesh.static_materials)],'hulls':unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem).get_convex_collision_count(mesh)}
(base/'retained_asset_bindings.json').write_text(json.dumps(report,indent=2));RESULT=report

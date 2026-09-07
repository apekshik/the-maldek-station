import unreal,json
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'parking';aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert not ls.is_in_play_in_editor()
actors={a.get_actor_label():a for a in aa.get_all_level_actors()};before=json.loads((out/'live_before.json').read_text());plant=json.loads((out/'planting.json').read_text());ledger=json.loads((out/'integration.json').read_text())
moved={r['label'] for r in plant['moves']};errors=[];checked=0
for row in before['actors']:
 if row['label'] in moved:continue
 a=actors.get(row['label'])
 if not a:errors.append('Missing '+row['label']);continue
 p=a.get_actor_location()
 if max(abs(v-w) for v,w in zip([p.x,p.y,p.z],row['location']))>.01:errors.append('Moved '+row['label'])
 checked+=1
for label in ledger['retired']:
 if actors[label].static_mesh_component.static_mesh:errors.append('Old mesh remains '+label)
for name,r in ledger['assets'].items():
 a=actors[name.replace('SM_','')];c=a.static_mesh_component
 if c.static_mesh.get_path_name()!=r['mesh']:errors.append('Wrong mesh '+name)
 if any(c.get_material(i) is None for i in range(c.get_num_materials())):errors.append('Missing material '+name)
car=actors['R12_Retained_Parked_Car'];assert car.static_mesh_component.static_mesh.get_name()=='SM_R12_Retained_Parked_Car'
assert not any(a.get_actor_label()=='R12_Transient_Review_Lamp' for a in actors.values())
assert ls.save_current_level()
report={'passed':not errors,'errors':errors,'preserved_nearby_actor_transforms':checked,'car_mesh_preserved':True,'new_meshes':len(ledger['assets']),'grass_clumps':len(plant['grass']),'new_trees':len(plant['trees']),'inspection_lights_removed':True,'saved':True}
(out/'verification.json').write_text(json.dumps(report,indent=2));RESULT=report

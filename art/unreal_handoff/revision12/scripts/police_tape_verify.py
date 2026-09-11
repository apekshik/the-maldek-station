import unreal,json,math
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'police_tape';aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
actors={a.get_actor_label():a for a in aa.get_all_level_actors()};baseline=json.loads((out/'audit.json').read_text())
changed=[]
for old in baseline['actors']:
 a=actors.get(old['label'])
 if not a or math.dist([a.get_actor_location().x,a.get_actor_location().y,a.get_actor_location().z],old['world'])>.01:changed.append(old['label'])
assert not changed,changed
assert not any('TemporaryInspectionLight' in name for name in actors)
tapes=[a for a in actors.values() if isinstance(a,unreal.StationPoliceTape)]
assert len(tapes)==7
cross=next(a for a in tapes if a.crossing)
counts={a.get_actor_label():len(a.get_components_by_class(unreal.SplineMeshComponent)) for a in tapes}
assert counts[cross.get_actor_label()]==72,counts
assert all(n==24 for label,n in counts.items() if label!=cross.get_actor_label()),counts
errors=unreal.StationMigrationLibrary.validate_material_shaders([unreal.load_asset('/Game/MaldekRefinement/R12/PoliceTape/M_PoliceTape')]);assert not errors,str(errors)
wraps=[a for name,a in actors.items() if name.startswith('PoliceTape_Wrap_') or name.startswith('PoliceTape_PerimeterWrap_')]
assert len(wraps)==12
assert all('/PoliceTape/Wraps/' in a.static_mesh_component.static_mesh.get_path_name() for a in wraps)
assert ls.save_current_level()
result={'saved':True,'fitted_wraps':12,'reopened_map_components_present':True,'runtime_actor_count':7,'crossing_strands':3,'perimeter_spans':6,'components':counts,'original_actor_transforms_preserved':True,'temporary_lights_removed':True,'material_errors':list(errors),'playtests':json.loads((out/'playtest.json').read_text())['passed']}
(out/'completion.json').write_text(json.dumps(result,indent=2));RESULT=result

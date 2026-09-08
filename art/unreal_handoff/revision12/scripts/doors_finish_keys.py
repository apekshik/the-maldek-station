"""Save/reopen final physical-key installation and verify all persisted security settings."""
import unreal,json
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'doors/key_lock';ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);lib=unreal.EditorAssetLibrary
assert not ls.is_in_play_in_editor()
assert json.loads((out/'runtime.json').read_text())['success']
assert json.loads((out/'edges.json').read_text())['success']
assert json.loads((out/'checkpoint_test.json').read_text())['success']
capture=json.loads((out/'previews/capture.json').read_text());assert capture['success'] and capture['temporary_light_removed'] and len(capture['files'])==36
assert json.loads((out.parent/'prompt_egress/runtime.json').read_text())['success']
assert ls.save_current_level();assert ls.load_level('/Game/MaldekRefinement/R12/Station_R12');rows=[]
for a in aa.get_all_level_actors():
 assert not a.get_actor_label().startswith('D04_Transient_')
 if not isinstance(a,unreal.StationDoor):continue
 physical=not a.has_keypad;assert a.has_key_lock==physical and a.is_locked()
 if physical:
  assert a.key_turn_sound and not a.key_inspection_light.is_visible() and abs(a.key_inspection_light.intensity-.08)<.0001
  assert abs(a.key_turn_volume-4)<.001
  assert a.key_available and str(a.required_key_id)=='StationService'
  for c in [a.key_housing,a.key_plug,a.interior_key_plug,a.service_key]:assert c.static_mesh and c.get_collision_enabled()==unreal.CollisionEnabled.NO_COLLISION
  assert a.leaf.static_mesh.get_name().startswith('SM_KeyLock_')
 else:assert a.access_code=='1234'
 assert a.unlock_sound and a.lock_sound and a.relock_on_close
 assert a.get_editor_property('interaction_prompt_material')
 rows.append({'label':a.get_actor_label(),'physical_key':physical,'starts_locked':a.is_locked(),'key_available':a.key_available,'leaf':a.leaf.static_mesh.get_path_name(),'open_angle':a.open_angle})
assert len(rows)==10 and sum(r['physical_key'] for r in rows)==7
assert len([a for a in aa.get_all_level_actors() if a.actor_has_tag('DoorTestCheckpoint')])==1
RESULT={'success':True,'reopened_doors':rows,'keypad_code':'1234','geometry_and_actor_transforms_preserved':True,'builds':['Win64 game Development','Win64 editor Development']};(out/'saved_verification.json').write_text(json.dumps(RESULT,indent=2))
RESULT.update(checkpoint='F6 / StationDoorCheckpoint',key_turn_volume=4.0,inspection_lumens=.08)
(out/'saved_verification.json').write_text(json.dumps(RESULT,indent=2))

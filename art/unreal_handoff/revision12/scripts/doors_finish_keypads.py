import unreal,json
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'doors';aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert not ls.is_in_play_in_editor()
assert json.loads((out/'keypad_runtime.json').read_text())['success']
assert json.loads((out/'keypad_previews/capture.json').read_text())['success']
assert not any(a.get_actor_label().startswith('D03_Transient_') for a in aa.get_all_level_actors())
assert ls.save_current_level();assert ls.load_level('/Game/MaldekRefinement/R12/Station_R12')
rows=[]
for a in aa.get_all_level_actors():
 if isinstance(a,unreal.StationDoor):
  secure=a.get_actor_label()!='R12_Door_Control_side'
  assert a.has_keypad==secure and a.is_locked()==secure
  assert a.access_code==('1234' if secure else '')
  assert a.leaf.static_mesh and abs(a.open_angle-95)<.01
  rows.append({'label':a.get_actor_label(),'locked':a.is_locked(),'code':a.access_code})
assert len(rows)==4
RESULT={'success':True,'reopened_doors':rows,'temporary_actors_removed':True}
(out/'keypad_saved_verification.json').write_text(json.dumps(RESULT,indent=2))

import unreal,json
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'doors'/'camera';ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert not ls.is_in_play_in_editor();assert json.loads((out/'runtime.json').read_text())['success']
assert ls.save_current_level();assert ls.load_level('/Game/MaldekRefinement/R12/Station_R12')
rows=[]
for a in aa.get_all_level_actors():
 if isinstance(a,unreal.StationDoor):
  assert not a.is_using_keypad()
  if a.has_keypad:
   c=a.get_editor_property('KeypadCamera');assert c and abs(c.field_of_view-48)<.01 and c.constrain_aspect_ratio;assert a.is_locked() and a.access_code=='1234'
   rows.append(a.get_actor_label())
  else:assert not a.is_locked()
assert len(rows)==3
RESULT={'success':True,'reopened_keypad_cameras':rows,'code':'1234','standard_door_unlocked':True,'builds':['Win64 Development game','Win64 Development Editor']}
(out/'saved_verification.json').write_text(json.dumps(RESULT,indent=2))

"""Verify saved recordings/door defaults after reopening the map."""
import unreal,json
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'doors'/'recorded_audio'
ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
for file in ['runtime.json','edges.json','mix_analysis.json']:assert json.loads((out/file).read_text())['success'],file
assert ls.save_current_level();assert ls.load_level('/Game/MaldekRefinement/R12/Station_R12')
rows=[]
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
 if not isinstance(a,unreal.StationDoor):continue
 secure=a.get_editor_property('has_keypad');assert a.is_locked()==secure
 assert a.get_editor_property('relock_on_close')
 for prop in ['button_sound','clear_sound','confirm_sound','reject_sound','unlatch_sound','movement_sound','closing_movement_sound','close_sound','unlock_sound','lock_sound']:
  sound=a.get_editor_property(prop);assert sound
  assert abs(sound.get_editor_property('volume')-1)<.001
 rows.append({'label':a.get_actor_label(),'keypad':secure,'locked_on_reload':a.is_locked()})
assert len(rows)==10
RESULT={'success':True,'doors':rows,'native_builds':['Win64 game Development','Win64 gameEditor Development'],
 'runtime_checks':len(json.loads((out/'runtime.json').read_text())['checks']),
 'edge_checks':len(json.loads((out/'edges.json').read_text())['checks'])}
(out/'saved.json').write_text(json.dumps(RESULT,indent=2))

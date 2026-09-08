import unreal,json
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'doors';ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert not ls.is_in_play_in_editor()
for p in ['rooms/runtime.json','audio_review/runtime.json','audio_review/recording_analysis.json','room_previews/capture.json']:assert json.loads((out/p).read_text())['success'],p
assert json.loads((out/'room_previews/capture.json').read_text())['temporary_light_removed'];assert len(json.loads((out/'room_previews/capture.json').read_text())['files'])==48
assert ls.save_current_level();assert ls.load_level('/Game/MaldekRefinement/R12/Station_R12')
rows=[]
for a in aa.get_all_level_actors():
 assert not a.get_actor_label().startswith('D03_Transient_')
 if isinstance(a,unreal.StationDoor):
  secure=a.get_actor_label() in ['R12_Door_Control_front','R12_Door_Relay_north','R12_Door_Relay_south'];assert a.has_keypad==secure and a.is_locked()==secure
  if secure:assert a.access_code=='1234'
  for prop in ['button_sound','clear_sound','confirm_sound','reject_sound','unlatch_sound','movement_sound','close_sound']:assert a.get_editor_property(prop),prop
  inward=a.get_actor_label() in ['R12_Door_Quarters','R12_Door_Generator_south'];assert abs(a.open_angle-(-95 if inward else 95))<.01
  assert abs(a.leaf_collision.get_editor_property('relative_location').y-(3.5 if inward else -3.5))<.01
  rows.append({'label':a.get_actor_label(),'keypad':secure,'open_angle':a.open_angle,'audio_assigned':True})
assert len(rows)==10
RESULT={'success':True,'reopened_doors':rows,'keypad_code':'1234','temporary_actors_removed':True,'neutral_night_images':48,'builds':['Win64 Development game','Win64 Development editor']};(out/'rooms_saved_verification.json').write_text(json.dumps(RESULT,indent=2))

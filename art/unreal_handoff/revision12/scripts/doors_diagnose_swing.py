import unreal,time,json
from pathlib import Path
ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor();state={'next':time.monotonic()+6,'phase':0}
def tick(dt):
 if time.monotonic()<state['next']:return
 w=unreal.EditorLevelLibrary.get_game_world()
 if not w:return
 ds=[a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.StationDoor) if a.get_actor_label() in ['R12_Door_Quarters','R12_Door_Generator_south']]
 if state['phase']==0:
  for d in ds:d.set_editor_property('open_angle',-95);d.try_interact()
  state.update(phase=1,next=time.monotonic()+4);return
 result={d.get_actor_label():d.get_open_angle() for d in ds};(Path(__file__).resolve().parents[1]/'doors/rooms/swing_diagnosis.json').write_text(json.dumps(result,indent=2));unreal.unregister_slate_post_tick_callback(h);ls.editor_request_end_play()
h=unreal.register_slate_post_tick_callback(tick);ls.editor_request_begin_play();RESULT={'started':True}

import unreal,time,json
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'forest_test';levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert not levels.is_in_play_in_editor()
assert not any(a.get_actor_label().startswith('TEMP_Audio_') for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors())
assert levels.save_current_level()
def audio_ready_tick(dt):
 w=unreal.EditorLevelLibrary.get_game_world()
 if not w:return
 p=unreal.GameplayStatics.get_player_pawn(w,0)
 if not p:return
 p.get_components_by_class(unreal.SpotLightComponent)[0].set_visibility(True)
 c=p.get_components_by_class(unreal.SurfaceFootstepComponent)[0]
 (out/'audio_ready.json').write_text(json.dumps({'playing':True,'pawn':p.get_class().get_name(),'variants':sum(len(getattr(c,n+'_steps')) for n in ['soil','gravel','metal','concrete','wood']),'test_fixtures_removed':True},indent=2))
 unreal.unregister_slate_post_tick_callback(audio_ready_handle)
audio_ready_handle=unreal.register_slate_post_tick_callback(audio_ready_tick);levels.editor_request_begin_play()

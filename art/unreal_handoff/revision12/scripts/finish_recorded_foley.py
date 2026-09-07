"""Discard only the now-removed transient audio fixtures and close our test editor."""
import unreal,json,os
from pathlib import Path
assert os.getpid()==46508,'This cleanup belongs only to the recorded-foley test editor'
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert not levels.is_in_play_in_editor()
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert not any(a.get_actor_label().startswith('TEMP_Audio_') for a in aa.get_all_level_actors())
assert not unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()
# The test spawned then removed temporary pads. Another editor holds the map file;
# reloading discards that transient dirty flag without overwriting its saved map.
assert unreal.EditorLevelLibrary.load_level('/Game/MaldekRefinement/R12/Station_R12')
assert not any(a.get_actor_label().startswith('TEMP_Audio_') for a in aa.get_all_level_actors())
c=unreal.get_default_object(unreal.load_class(None,'/Game/MaldekRefinement/R12/Player/BP_StationWalker_Polished.BP_StationWalker_Polished_C')).get_components_by_class(unreal.SurfaceFootstepComponent)[0]
assert len(c.metal_steps)==15 and len(c.soil_steps)==18
Path(__file__).resolve().parents[1].joinpath('recorded_foley_cleanup.json').write_text(json.dumps({'success':True,'temporary_actors':0,'reloaded_saved_map':True,'saved_audio_banks_verified':True,'closed_editor_pid':os.getpid()}))
unreal.SystemLibrary.quit_editor()

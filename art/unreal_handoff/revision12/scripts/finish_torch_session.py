"""Verify the saved pawn and end the temporary unmuted validation session."""
import json,unreal
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'sensory_refine'/'torch_v2'
assert not unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).is_in_play_in_editor()
bp=unreal.EditorAssetLibrary.load_asset('/Game/MaldekRefinement/R12/Player/BP_StationWalker_Polished')
p=unreal.get_default_object(bp.generated_class());c=p.get_component_by_class(unreal.StationPlayerPresentationComponent)
foot=p.get_component_by_class(unreal.SurfaceFootstepComponent)
assert abs(foot.volume-3.5)<.001 and abs(c.idle_sway_scale-5)<.001
assert c.get_editor_property('detailed_torch_mesh').get_name()=='SM_Torch_Field_V2' and abs(c.held_motion_scale-.15)<.001
assert abs(c.head_bob_scale-1.5)<.001 and abs(c.walk_sway_cm-1.8)<.001 and abs(c.run_sway_cm-3)<.001
assert unreal.EditorAssetLibrary.save_loaded_asset(bp,False)
dirty=[v.get_name() for v in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()]
assert not dirty,dirty
RESULT={'success':True,'foot_volume':foot.volume,'idle_sway_scale':c.idle_sway_scale,'held_motion_scale':c.held_motion_scale,'mesh':c.get_editor_property('detailed_torch_mesh').get_path_name(),'map_modified':False}
(out/'saved.json').write_text(json.dumps(RESULT,indent=2))
unreal.SystemLibrary.quit_editor()

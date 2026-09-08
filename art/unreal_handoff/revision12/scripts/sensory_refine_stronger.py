"""Second listening pass: louder feet and stronger idle only; no map changes."""
import json, unreal
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'sensory_refine'/'stronger';out.mkdir(exist_ok=True)
assert not unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).is_in_play_in_editor()
lib=unreal.EditorAssetLibrary
bp=lib.load_asset('/Game/MaldekRefinement/R12/Player/BP_StationWalker_Polished')
p=unreal.get_default_object(bp.generated_class())
foot=p.get_component_by_class(unreal.SurfaceFootstepComponent)
camera=p.get_component_by_class(unreal.StationPlayerPresentationComponent)
gait={k:camera.get_editor_property(k) for k in ['head_bob_scale','walk_sway_cm','run_sway_cm','ground_height_response']}
before={'foot_volume':foot.volume,'idle_sway_scale':camera.idle_sway_scale,'gait':gait}
foot.set_editor_property('volume',3.5)
# The editor slider's soft authoring range is not a runtime motion limit.
# Increase idle alone, retaining the user's approved gait and stair response.
camera.set_editor_property('idle_sway_scale',5.0)
unreal.BlueprintEditorLibrary.compile_blueprint(bp)
assert lib.save_loaded_asset(bp,False)
p=unreal.get_default_object(bp.generated_class())
foot=p.get_component_by_class(unreal.SurfaceFootstepComponent)
camera=p.get_component_by_class(unreal.StationPlayerPresentationComponent)
assert abs(foot.volume-3.5)<.001 and abs(camera.idle_sway_scale-5)<.001
assert all(abs(camera.get_editor_property(k)-v)<.001 for k,v in gait.items())
RESULT={'success':True,'before':before,'foot_volume':foot.volume,'idle_sway_scale':camera.idle_sway_scale,'gait_preserved':gait}
(out/'settings.json').write_text(json.dumps(RESULT,indent=2))
path=b/'sensory_refine'/'setup.json';setup=json.loads(path.read_text())
setup['foot_volume']=3.5;setup['camera']['idle_sway_scale']=5.0
path.write_text(json.dumps(setup,indent=2))

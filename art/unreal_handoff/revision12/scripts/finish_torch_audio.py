"""Preserve increased footstep presence with a little mix headroom."""
import unreal,json
from pathlib import Path
b=Path(__file__).resolve().parents[1];lib=unreal.EditorAssetLibrary
assert not unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).is_in_play_in_editor()
bp=lib.load_asset('/Game/MaldekRefinement/R12/Player/BP_StationWalker_Polished')
p=unreal.get_default_object(bp.generated_class());f=p.get_component_by_class(unreal.SurfaceFootstepComponent)
f.set_editor_property('volume',3.5);unreal.BlueprintEditorLibrary.compile_blueprint(bp);assert lib.save_loaded_asset(bp,False)
path=b/'sensory_refine'/'setup.json';data=json.loads(path.read_text());data['foot_volume']=3.5;path.write_text(json.dumps(data,indent=2))
RESULT={'success':True,'foot_volume':3.5}

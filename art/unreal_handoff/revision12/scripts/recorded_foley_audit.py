import unreal,json
from pathlib import Path
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
gm=w.get_world_settings().get_editor_property('default_game_mode')
cdo=unreal.get_default_object(gm)
pawn=cdo.get_editor_property('default_pawn_class')
RESULT={'world':w.get_path_name(),'gamemode':gm.get_path_name(),'pawn':pawn.get_path_name(),'dirty':[p.get_name() for p in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()],'dirty_maps':[p.get_name() for p in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()]}
Path(__file__).resolve().parents[1].joinpath('recorded_foley_audit.json').write_text(json.dumps(RESULT,indent=2))

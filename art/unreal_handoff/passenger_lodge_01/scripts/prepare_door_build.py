import unreal,json
from pathlib import Path
OUT=Path(__file__).resolve().parents[1];ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert not ls.is_in_play_in_editor();assert unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_name()=='Station_Lodge_Migration';assert ls.save_current_level()
dirty=[p.get_name() for p in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()]+[p.get_name() for p in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()]
RESULT={'dirty_packages':dirty,'ready':not dirty};(OUT/'doors/restart.json').write_text(json.dumps(RESULT,indent=2));assert not dirty,dirty

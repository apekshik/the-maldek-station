import unreal,json
from pathlib import Path
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not levels.is_in_play_in_editor()
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert world.get_name() in ['Station_R12','Forest_Approach_Test']
if world.get_name()=='Station_R12':assert levels.save_current_level()
for path in unreal.EditorAssetLibrary.list_assets('/Game/MaldekRefinement/R12',True,False):
 unreal.EditorAssetLibrary.save_asset(path,True)
(Path(__file__).resolve().parents[1]/'editor_saved.json').write_text(json.dumps({'saved':True,'level':world.get_path_name()}))
unreal.SystemLibrary.quit_editor()

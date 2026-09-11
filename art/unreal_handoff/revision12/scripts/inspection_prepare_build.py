import unreal,runpy
from pathlib import Path
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
assert not unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages(),'Unsaved map remains'
assert not unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages(),'Unsaved content remains'
RESULT={'saved':True,'closing_for_inspection_build':True}
unreal.SystemLibrary.quit_editor()

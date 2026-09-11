import unreal
assert not unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).is_in_play_in_editor()
assert not unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
assert not unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()
RESULT={'closing_clean_editor':True};unreal.SystemLibrary.quit_editor()

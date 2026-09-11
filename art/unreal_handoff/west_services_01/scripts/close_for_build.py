import unreal
assert not unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).is_in_play_in_editor()
for p in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages():
 assert p.get_name().startswith('/Game/MaldekRefinement/WestServices/');assert unreal.EditorAssetLibrary.save_asset(p.get_name())
assert not unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
unreal.SystemLibrary.quit_editor()

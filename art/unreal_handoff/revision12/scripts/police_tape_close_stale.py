import unreal,os
assert os.getpid()==3748
assert not unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages(), 'Old editor has unsaved level edits'
unreal.SystemLibrary.quit_editor();RESULT={'stale_editor_closed_without_saving':True}

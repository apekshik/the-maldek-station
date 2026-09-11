import unreal
ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert not ls.is_in_play_in_editor()
assert ls.save_current_level()
unreal.SystemLibrary.quit_editor()
RESULT={'saved':True,'quit':True}

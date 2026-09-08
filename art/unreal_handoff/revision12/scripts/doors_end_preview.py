import unreal
ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
RESULT={'was_playing':ls.is_in_play_in_editor()}
if RESULT['was_playing']:ls.editor_request_end_play()

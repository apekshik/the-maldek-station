import unreal
ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
RESULT={'pie':ls.is_in_play_in_editor(),'editor':str(unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()),'game':str(unreal.EditorLevelLibrary.get_game_world())}
if ls.is_in_play_in_editor():ls.editor_request_end_play();RESULT['ending_play_for_authorized_integration']=True

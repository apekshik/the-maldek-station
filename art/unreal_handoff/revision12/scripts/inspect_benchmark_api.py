import unreal
ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
RESULT={'realtime_doc':ls.editor_set_viewport_realtime.__doc__,'keys':[str(k) for k in ls.get_viewport_config_keys()],'active_key':str(ls.get_active_viewport_config_key())}

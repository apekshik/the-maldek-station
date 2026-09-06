import unreal
level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert level.load_level('/Game/MaldekRefinement/Maps/BlockOut_R04')
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
 if a.get_actor_label().startswith('R04_'):a.set_actor_rotation(unreal.Rotator(pitch=0,yaw=180,roll=0),True)
 if a.get_class().get_name()=='PlayerStart':a.set_actor_rotation(unreal.Rotator(pitch=0,yaw=135,roll=0),True)
 if a.get_class().get_name()=='CineCameraActor':a.set_actor_rotation(unreal.Rotator(pitch=-25,yaw=-45,roll=0),True)
assert level.save_current_level()

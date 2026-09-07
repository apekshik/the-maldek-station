import unreal,gc
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert not levels.is_in_play_in_editor()
gc.collect()
assert levels.load_level('/Game/MaldekRefinement/ForestTest/Forest_Approach_Test')
RESULT={'loaded':'Forest_Approach_Test','saved':False}

import unreal
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_name()=='Forest_Approach_Test'
metal=unreal.EditorAssetLibrary.load_asset('/Game/MaldekRefinement/ForestTest/Audio/Surfaces/PM_Metal')
for a in aa.get_all_level_actors():
 if a.get_actor_label()=='R04_20_Lookout_Bridge':a.static_mesh_component.set_phys_material_override(metal)
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
unreal.SystemLibrary.quit_editor()

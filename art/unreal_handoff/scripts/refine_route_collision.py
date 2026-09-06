import unreal,runpy
from pathlib import Path
lib=unreal.EditorAssetLibrary;actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors();a=next(a for a in actors if a.get_actor_label()=='R04_08_Fuel_Yard')
mesh=lib.duplicate_asset(a.static_mesh_component.static_mesh.get_path_name(),'/Game/MaldekRefinement/R05/Meshes/SM_R05_08_Fuel_Yard')
mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
lib.save_loaded_asset(mesh);a.static_mesh_component.set_static_mesh(mesh);a.static_mesh_component.set_collision_profile_name('BlockAll')
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
runpy.run_path(str(Path(__file__).with_name('verify_complete_route.py')))

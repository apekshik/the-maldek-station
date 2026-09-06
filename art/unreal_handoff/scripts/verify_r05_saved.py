import unreal,json
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'revision05';lib=unreal.EditorAssetLibrary;ml=unreal.MaterialEditingLibrary
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
a=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors();mi=lib.load_asset('/Game/MaldekRefinement/R05/Materials/MI_Landscape_CohesiveSnow')
r={'map':world.get_name(),'snow_altitude_cm':ml.get_material_instance_scalar_parameter_value(mi,'MW_SnowWorldPosition'),'actors':{x.get_actor_label():x.static_mesh_component.static_mesh.get_path_name() for x in a if isinstance(x,unreal.StaticMeshActor) and x.get_actor_label() in ['R04_07_Overlook','R04_09_Relay_and_Paths','R04_13_Roofs','R04_Local_Terrain']},'saved':unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()}
(out/'final_scene_verification.json').write_text(json.dumps(r,indent=2))

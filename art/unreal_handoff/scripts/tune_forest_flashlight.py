import unreal,json
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'forest_test';root='/Game/MaldekRefinement/ForestTest';lib=unreal.EditorAssetLibrary
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert world.get_name()=='Forest_Approach_Test'
bp=lib.load_asset(root+'/BP_ForestWalker') or lib.duplicate_asset('/Game/MaldekRefinement/R10/BP_StationWalker',root+'/BP_ForestWalker');unreal.BlueprintEditorLibrary.compile_blueprint(bp)
c=unreal.get_default_object(bp.generated_class()).get_components_by_class(unreal.SpotLightComponent)[0]
c.set_intensity(1.2);c.set_attenuation_radius(1500);c.set_inner_cone_angle(0);c.set_outer_cone_angle(42);c.set_relative_rotation(unreal.Rotator(pitch=-12,yaw=-1.3,roll=0),False,False);c.set_visibility(True);lib.save_loaded_asset(bp,False)
gm=lib.load_asset(root+'/BP_ForestGameMode') or lib.duplicate_asset('/Game/MaldekRefinement/R10/BP_StationWalkGameMode',root+'/BP_ForestGameMode');unreal.get_default_object(gm.generated_class()).set_editor_property('default_pawn_class',bp.generated_class());lib.save_loaded_asset(gm,False);world.get_world_settings().set_editor_property('default_game_mode',gm.generated_class())
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
 if a.get_actor_label().startswith('FT_Marker_') and isinstance(a,unreal.SpotLight):a.light_component.set_intensity(.18)
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
(out/'flashlight_settings.json').write_text(json.dumps({'test_only':True,'intensity':1.2,'radius_cm':1500,'outer_cone':42,'pitch':-12,'game_mode':gm.get_path_name()},indent=2))

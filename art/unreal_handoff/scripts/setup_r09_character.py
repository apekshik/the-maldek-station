"""First-person walking and a restrained held flashlight for the R09 review map."""
import unreal,json
from pathlib import Path
lib=unreal.EditorAssetLibrary;root='/Game/MaldekRefinement/R09';out=Path(__file__).resolve().parents[1]/'revision09'
bp=lib.load_asset(root+'/BP_StationWalker') or lib.duplicate_asset('/Game/Variant_Horror/Blueprints/BP_HorrorCharacter',root+'/BP_StationWalker')
sub=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem);f=unreal.SubobjectDataBlueprintFunctionLibrary
handles=sub.k2_gather_subobject_data_for_blueprint(bp)
cam=next(h for h in handles if isinstance(f.get_object(f.get_data(h)),unreal.CameraComponent))
metal=lib.load_asset('/Game/MaldekRefinement/Materials/M_R04_Painted_Charcoal')
trim=lib.load_asset('/Game/MaldekRefinement/Materials/M_R04_Galvanized_Fittings')
lens=lib.load_asset('/Game/MaldekRefinement/R08/Materials/M_WallLamp_Diffuser')
parts=[('TorchBody','Cylinder',[27,17.5,-11],[4.8,4.8,21],90,metal),('TorchHead','Cylinder',[39,17.5,-11],[7,7,4.5],90,metal),('TorchLens','Cylinder',[41.4,17.5,-11],[5.9,5.9,.4],90,lens),('TorchRim','Cylinder',[40.7,17.5,-11],[7.2,7.2,.7],90,trim),('GlovedPalm','Sphere',[20,18,-15],[10,7,6],0,metal),('GlovedThumb','Sphere',[23,14.5,-12],[5,3.5,4],0,metal),('JacketSleeve','Sphere',[8,24,-24],[28,10,10],35,metal)]
for i in range(4):parts.append(('GlovedFinger'+str(i),'Sphere',[21+i*1.6,20,-12.5],[1.5,4,5],0,metal))
for name,shape,pos,size,pitch,mat in parts:
 hs=sub.k2_gather_subobject_data_for_blueprint(bp)
 h=next((h for h in hs if f.get_object(f.get_data(h)).get_name().startswith(name)),None)
 if h is None:
  h,reason=sub.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=cam,new_class=unreal.StaticMeshComponent,blueprint_context=bp))
  assert not str(reason),str(reason)
  sub.rename_subobject(h,unreal.Text(name))
 c=f.get_object(f.get_data(h))
 c.set_static_mesh(lib.load_asset('/Engine/BasicShapes/'+shape));c.set_material(0,mat)
 c.set_editor_property('relative_location',unreal.Vector(*pos));c.set_editor_property('relative_rotation',unreal.Rotator(pitch=pitch,yaw=0,roll=0));c.set_editor_property('relative_scale3d',unreal.Vector(*[v/100 for v in size]))
 c.set_collision_profile_name('NoCollision');c.set_editor_property('only_owner_see',True);c.set_editor_property('cast_shadow',False)
unreal.BlueprintEditorLibrary.compile_blueprint(bp)
cdo=unreal.get_default_object(bp.generated_class())
light=cdo.get_components_by_class(unreal.SpotLightComponent)[0]
light.set_editor_property('relative_location',unreal.Vector(42,17.5,-11));light.set_editor_property('relative_rotation',unreal.Rotator(pitch=0,yaw=-1.5,roll=0))
light.set_intensity(.2);light.set_attenuation_radius(650);light.set_inner_cone_angle(10);light.set_outer_cone_angle(24)
light.set_editor_property('volumetric_scattering_intensity',.06);light.set_editor_property('use_temperature',True);light.set_temperature(4300);light.set_editor_property('cast_shadows',True)
fp=next(c for c in cdo.get_components_by_class(unreal.SkeletalMeshComponent) if c.get_name()=='First Person Mesh')
fp.set_editor_property('hidden_in_game',True)
cdo.set_editor_property('walk_speed',350.)
lib.save_loaded_asset(bp,False)
gm=lib.load_asset(root+'/BP_StationWalkGameMode') or lib.duplicate_asset('/Game/Variant_Horror/Blueprints/BP_HorrorGameMode',root+'/BP_StationWalkGameMode')
unreal.get_default_object(gm.generated_class()).set_editor_property('default_pawn_class',bp.generated_class());lib.save_loaded_asset(gm,False)
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert world.get_name()=='BlockOut_R09'
world.get_world_settings().set_editor_property('default_game_mode',gm.generated_class())
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
(out/'character_setup.json').write_text(json.dumps({'pawn':bp.get_path_name(),'game_mode':gm.get_path_name(),'walk_speed_cm_s':350,'flashlight_lumens':.2,'flashlight_radius_cm':650,'outer_cone_degrees':24,'held_mesh_parts':len(parts),'controls':'WASD + mouse, Shift sprint, Space jump; flashlight starts on'},indent=2))

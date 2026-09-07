"""Replace unsupported upper-floor light sources with hooded wall lamps in R08."""
import unreal,json
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'revision08'
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert world.get_name()=='BlockOut_R08'
lib=unreal.EditorAssetLibrary
report={'disabled':[],'fixtures':[]}
sky=next(a for a in actors.get_all_level_actors() if a.get_actor_label()=='Ultra_Dynamic_Sky')
sky.set_editor_property('Time of Day',2300.)
report['time_of_day']=2300.
for a in actors.get_all_level_actors():
 if a.get_actor_label() in ['R07_TestLight_Main_Platform_West','R07_TestLight_Main_Platform_East','PointLight3']:
  for c in a.get_components_by_class(unreal.PointLightComponent):c.set_intensity(0.)
  a.set_folder_path('R08_Disabled_Upper_Light_Tests');report['disabled'].append(a.get_actor_label())
root='/Game/MaldekRefinement/R08/Materials'
ml=unreal.MaterialEditingLibrary
lens=lib.load_asset(root+'/M_WallLamp_Diffuser')
if lens is None:
 lens=unreal.AssetToolsHelpers.get_asset_tools().create_asset('M_WallLamp_Diffuser',root,unreal.Material,unreal.MaterialFactoryNew())
 base=ml.create_material_expression(lens,unreal.MaterialExpressionConstant3Vector);base.constant=unreal.LinearColor(.45,.4,.3,1);ml.connect_material_property(base,'',unreal.MaterialProperty.MP_BASE_COLOR)
 glow=ml.create_material_expression(lens,unreal.MaterialExpressionConstant3Vector);glow.constant=unreal.LinearColor(.025,.018,.01,1);ml.connect_material_property(glow,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
 rough=ml.create_material_expression(lens,unreal.MaterialExpressionConstant);rough.r=.6;ml.connect_material_property(rough,'',unreal.MaterialProperty.MP_ROUGHNESS)
 ml.recompile_material(lens);lib.save_loaded_asset(lens)
metal=lib.load_asset('/Game/MaldekRefinement/Materials/M_R04_Painted_Charcoal')
cube=lib.load_asset('/Engine/BasicShapes/Cube')

def part(label,location,size,material):
 a=next((a for a in actors.get_all_level_actors() if a.get_actor_label()==label),None)
 if a is None:a=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(*location))
 a.set_actor_label(label);a.set_folder_path('R08_Wall_Lamps')
 a.set_actor_location(unreal.Vector(*location),False,False)
 a.set_actor_scale3d(unreal.Vector(*[v/100 for v in size]))
 c=a.static_mesh_component;c.set_static_mesh(cube);c.set_material(0,material);c.set_collision_profile_name('NoCollision')
 return a

for name,x,lumens in [('Control_Entry',-43902.305975,1.5),('Waiting_Hall_Entry',-43132.305975,1.2)]:
 y=18487.70755;z=10553.5
 pieces=[('Backplate',(0,1.5,0),(28,3,34),metal),('Housing',(0,8,0),(24,11,28),metal),('Hood',(0,10,15),(30,22,4),metal),('Diffuser',(0,14,-2),(18,1.5,18),lens),('Guard_Left',(-6,15.3,-2),(1,1.3,20),metal),('Guard_Right',(6,15.3,-2),(1,1.3,20),metal),('Guard_Crossbar',(0,15.5,-2),(20,1.3,1),metal)]
 for suffix,offset,size,mat in pieces:part('R08_'+name+'_'+suffix,[x+offset[0],y+offset[1],z+offset[2]],size,mat)
 # Feed runs up to the ceiling, directly on the same wall as the mounting plate.
 part('R08_'+name+'_Conduit',[x,y+1.5,10602],[1.5,2,64],metal)
 loc=[x,y+19,z-10];target=[x,y+130,10298.5]
 label='R08_WallLight_'+name
 a=next((a for a in actors.get_all_level_actors() if a.get_actor_label()==label),None)
 if a is None:a=actors.spawn_actor_from_class(unreal.SpotLight,unreal.Vector(*loc))
 a.set_actor_label(label);a.set_folder_path('R08_Wall_Lamps')
 a.set_actor_location(unreal.Vector(*loc),False,False)
 a.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(unreal.Vector(*loc),unreal.Vector(*target)),False)
 c=a.get_components_by_class(unreal.SpotLightComponent)[0];c.set_mobility(unreal.ComponentMobility.MOVABLE)
 c.set_editor_property('intensity_units',unreal.LightUnits.LUMENS);c.set_intensity(lumens)
 c.set_attenuation_radius(420);c.set_inner_cone_angle(20);c.set_outer_cone_angle(34)
 c.set_editor_property('use_temperature',True);c.set_temperature(3600)
 c.set_editor_property('source_radius',3.);c.set_editor_property('volumetric_scattering_intensity',.12)
 c.set_editor_property('cast_shadows',True);c.set_editor_property('cast_volumetric_shadow',False)
 report['fixtures'].append({'name':label,'wall_mount_cm':[x,y,z],'light_cm':loc,'target_cm':target,'intensity_lumens':lumens,'outer_cone_degrees':34,'radius_cm':420,'kelvin':3600})
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
(out/'wall_lights.json').write_text(json.dumps(report,indent=2))

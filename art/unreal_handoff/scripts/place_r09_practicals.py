"""Small, physically placed practical lights for the parked gondola."""
import unreal,json
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'revision09';lib=unreal.EditorAssetLibrary
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert world.get_name()=='BlockOut_R09'
metal=lib.load_asset('/Game/MaldekRefinement/Materials/M_R04_Painted_Charcoal');lens=lib.load_asset('/Game/MaldekRefinement/R08/Materials/M_WallLamp_Diffuser')
def material(name,color,emission):
 path='/Game/MaldekRefinement/R09/Materials/'+name;m=lib.load_asset(path)
 if m:return m
 m=unreal.AssetToolsHelpers.get_asset_tools().create_asset(name,'/Game/MaldekRefinement/R09/Materials',unreal.Material,unreal.MaterialFactoryNew());ml=unreal.MaterialEditingLibrary
 for value,pin in [(color,unreal.MaterialProperty.MP_BASE_COLOR),(emission,unreal.MaterialProperty.MP_EMISSIVE_COLOR)]:
  c=ml.create_material_expression(m,unreal.MaterialExpressionConstant3Vector);c.constant=unreal.LinearColor(*value,1);ml.connect_material_property(c,'',pin)
 ml.recompile_material(m);lib.save_loaded_asset(m);return m
green=material('M_Boarding_Green',(.01,.15,.03),(.003,.04,.008));red=material('M_Hold_Red_Off',(.15,.006,.002),(0,0,0))
def mesh(name,p,size,mat,shape='Cube'):
 label='R09_'+name;a=next((a for a in actors.get_all_level_actors() if a.get_actor_label()==label),None)
 if a is None:a=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(*p))
 a.set_actor_label(label);a.set_folder_path('R09_Gondola_Practicals');a.set_actor_location(unreal.Vector(*p),False,False);a.set_actor_scale3d(unreal.Vector(*[v/100 for v in size]))
 c=a.static_mesh_component;c.set_static_mesh(lib.load_asset('/Engine/BasicShapes/'+shape));c.set_material(0,mat);c.set_collision_profile_name('NoCollision')
 return a
specs=[('Cabin_Ceiling',[-44282.306,19279.708,10509],[-44282.306,19279.708,10298.5],.35,3200,340,65),('Canopy_Left',[-44442.306,18875,10634],[-44362.306,18970,10298.5],.45,3900,470,22),('Canopy_Right',[-44122.306,18875,10634],[-44202.306,18970,10298.5],.45,3900,470,22)]
for name,p,target,power,temp,radius,cone in specs:
 if name=='Cabin_Ceiling':
  mesh(name+'_Housing',[p[0],p[1],10522],[16,62,5],metal);mesh(name+'_Diffuser',[p[0],p[1],10519],[12,57,1],lens)
 else:
  mesh(name+'_Housing',[p[0],p[1],10643.5],[16,16,10],metal);mesh(name+'_Lens',[p[0],p[1],10638],[10,10,1],lens)
 label='R09_Light_'+name;a=next((a for a in actors.get_all_level_actors() if a.get_actor_label()==label),None)
 if a is None:a=actors.spawn_actor_from_class(unreal.SpotLight,unreal.Vector(*p))
 a.set_actor_label(label);a.set_folder_path('R09_Gondola_Practicals');a.set_actor_location(unreal.Vector(*p),False,False);a.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(unreal.Vector(*p),unreal.Vector(*target)),False)
 c=a.get_components_by_class(unreal.SpotLightComponent)[0];c.set_mobility(unreal.ComponentMobility.MOVABLE);c.set_editor_property('intensity_units',unreal.LightUnits.LUMENS);c.set_intensity(power);c.set_attenuation_radius(radius);c.set_inner_cone_angle(cone*.45);c.set_outer_cone_angle(cone);c.set_editor_property('use_temperature',True);c.set_temperature(temp);c.set_editor_property('volumetric_scattering_intensity',.06);c.set_editor_property('cast_shadows',True);c.set_editor_property('cast_volumetric_shadow',False);c.set_editor_property('source_radius',4.)
mesh('Boarding_Panel',[-44365,18965,10453],[16,7,30],metal)
mesh('Boarding_Green_Lens',[-44365,18960.5,10460],[6,2,6],green,'Sphere')
mesh('Boarding_Red_Lens_Off',[-44365,18960.5,10447],[6,2,6],red,'Sphere')
label='R09_Boarding_Indicator_Glow';a=next((a for a in actors.get_all_level_actors() if a.get_actor_label()==label),None)
if a is None:a=actors.spawn_actor_from_class(unreal.PointLight,unreal.Vector(-44365,18957,10460))
a.set_actor_label(label);a.set_folder_path('R09_Gondola_Practicals');c=a.get_components_by_class(unreal.PointLightComponent)[0];c.set_editor_property('intensity_units',unreal.LightUnits.CANDELAS);c.set_intensity(.002);c.set_light_color(unreal.LinearColor(.04,1,.12,1));c.set_attenuation_radius(65);c.set_editor_property('cast_shadows',False);c.set_editor_property('volumetric_scattering_intensity',0.)
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
(out/'practical_lights.json').write_text(json.dumps({'spots':[{'name':s[0],'position':s[1],'target':s[2],'lumens':s[3],'temperature':s[4],'radius_cm':s[5],'outer_cone':s[6]} for s in specs],'boarding':'Green on; red lens unlit while the cabin is parked','removed_user_lights_restored':False},indent=2))

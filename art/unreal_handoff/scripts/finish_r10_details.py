import unreal,json
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'revision10';aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);lib=unreal.EditorAssetLibrary;world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert world.get_name()=='BlockOut_R10'
for a in aa.get_all_level_actors():
 if 'Waiting_Hall_Entry' in a.get_actor_label():
  p=a.get_actor_location();p.x=-42992.305975+(p.x+43132.305975);a.set_actor_location(p,False,False)
sky=next(a for a in aa.get_all_level_actors() if a.get_actor_label()=='Ultra_Dynamic_Sky')
sky.set_editor_property('Manually Position Moon Target',False);sky.set_editor_property('Moon Yaw',255.);sky.set_editor_property('Moon Pitch',20.)
origin=json.loads((out.parent/'working_level_report.json').read_text())['station_origin']
for i,(x,y) in enumerate([(-17.3,-7.3),(-17.3,-.5),(-12.9,-7.3)]):
 a=aa.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(origin[0]-100*x,origin[1]+100*y,origin[2]+180));a.set_actor_label('R10_Hall_Foundation_'+str(i));a.static_mesh_component.set_static_mesh(lib.load_asset('/Engine/BasicShapes/Cube'));a.static_mesh_component.set_material(0,lib.load_asset('/Game/MaldekRefinement/Materials/M_R02_Weathered_Concrete'));a.set_actor_scale3d(unreal.Vector(.5,.5,4.3))
# A local copy allows the ambience bed to loop without modifying the purchased source.
sound=lib.load_asset('/Game/MaldekRefinement/R10/Audio/Forest_Wind_Loop') or lib.duplicate_asset('/Game/UltraDynamicSky/Sound/Environment/Forest_Example/Waves/TreeWind/TreeWind_Light','/Game/MaldekRefinement/R10/Audio/Forest_Wind_Loop');sound.set_editor_property('looping',True);lib.save_loaded_asset(sound)
wind=next(a for a in aa.get_all_level_actors() if a.get_actor_label()=='R10_Forest_Wind');wind.audio_component.set_sound(sound)
world.get_world_settings().set_editor_property('kill_z',0.)
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
(out/'details_complete.json').write_text(json.dumps({'hall_lamp_shift_cm':140,'foundation_piers':3,'wind_loop':sound.get_path_name(),'moon_yaw':255,'moon_pitch':20}))

import unreal,json
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'forest_test';lib=unreal.EditorAssetLibrary;aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_name()=='Forest_Approach_Test'
origin=json.loads((out.parent/'working_level_report.json').read_text())['station_origin'];report=json.loads((out/'build.json').read_text());cube=lib.load_asset('/Engine/BasicShapes/Cylinder');n=0
for t in report['trees']:
 if t['species']=='Goat_Willow':continue
 a=aa.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(origin[0]-100*t['x'],origin[1]+100*t['y'],origin[2]+100*t['z']+130));a.set_actor_label('FT_TrunkCollision_'+str(n));a.set_folder_path('ForestTest/Collision');a.static_mesh_component.set_static_mesh(cube);a.static_mesh_component.set_collision_profile_name('BlockAll');a.static_mesh_component.set_editor_property('cast_shadow',False);a.set_actor_scale3d(unreal.Vector(.28,.28,2.6));a.set_actor_hidden_in_game(True);a.set_is_temporarily_hidden_in_editor(True);n+=1
report['trunk_collision_proxies']=n;(out/'build.json').write_text(json.dumps(report,indent=2));assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()

import unreal,json
from pathlib import Path
b=Path(__file__).resolve().parents[1];info=json.loads((b/'police_tape/installation.json').read_text());aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);actors={a.get_actor_label():a for a in aa.get_all_level_actors()}
for i,z in enumerate(info['tree_ground_world_z']):
 p=actors[f'PoliceTape_AnchorTree_{i}'].get_actor_location();label=f'PoliceTape_AnchorCollision_{i}';proxy=actors.get(label) or aa.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(p.x,p.y,z+400));proxy.set_actor_label(label);proxy.set_folder_path('R12/PoliceTape');proxy.static_mesh_component.set_static_mesh(unreal.load_asset('/Engine/BasicShapes/Cylinder'));proxy.set_actor_scale3d(unreal.Vector(.3,.3,8));proxy.set_actor_location(unreal.Vector(p.x,p.y,z+400),False,True);proxy.static_mesh_component.set_collision_profile_name('BlockAll');proxy.set_actor_hidden_in_game(True);proxy.set_is_temporarily_hidden_in_editor(True)
RESULT={'trunk_collision_proxies':2}

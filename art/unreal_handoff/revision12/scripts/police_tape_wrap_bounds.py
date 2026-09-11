import unreal,json
from pathlib import Path
b=Path(__file__).resolve().parents[1];aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);a={a.get_actor_label():a for a in aa.get_all_level_actors()};report={}
for name in ['PoliceTape_AnchorTree_0','PoliceTape_Wrap_0_0','PoliceTape_Wrap_0_1']:
 ob=a[name];mesh=ob.skeletal_mesh_component.get_skeletal_mesh_asset() if isinstance(ob,unreal.SkeletalMeshActor) else ob.static_mesh_component.static_mesh
 bounds=mesh.get_bounds();report[name]={'origin':str(bounds.origin),'extent':str(bounds.box_extent),'rotation':str(ob.get_actor_rotation()),'component_transform':str(ob.skeletal_mesh_component.get_world_transform()) if isinstance(ob,unreal.SkeletalMeshActor) else ''}
(b/'police_tape/wrap_fit/bounds.json').write_text(json.dumps(report));RESULT=report

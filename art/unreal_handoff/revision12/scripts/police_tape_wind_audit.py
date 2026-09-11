import unreal,json
from pathlib import Path
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);a=next(a for a in aa.get_all_level_actors() if a.get_actor_label()=='PoliceTape_AnchorTree_0');c=a.skeletal_mesh_component;r={'components':[str(x.get_class().get_name()) for x in a.get_components_by_class(unreal.ActorComponent)]}
for p in ['animation_mode','anim_class','disable_post_process_blueprint','skeletal_mesh_asset']:
 try:r[p]=str(c.get_editor_property(p))
 except Exception as e:r[p]=str(e)
r['postprocess']=str(c.get_post_process_instance());r['anim']=str(c.get_anim_instance());r['bone_positions']={str(n):str(c.get_socket_transform(n,unreal.RelativeTransformSpace.RTS_COMPONENT).translation) for n in c.get_all_socket_names()[:8]};Path(__file__).resolve().parents[1].joinpath('police_tape/wrap_fit/wind.json').write_text(json.dumps(r));RESULT=r

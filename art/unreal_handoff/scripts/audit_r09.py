import unreal,json
from pathlib import Path
r={'foliage_api':[k for k in dir(unreal.InstancedFoliageActor) if 'instance' in k or 'foliage' in k],'subobject_api':[k for k in dir(unreal.SubobjectDataSubsystem) if not k.startswith('_') and any(s in k for s in ['add','gather','attach'])]}
r['add_doc']=unreal.SubobjectDataSubsystem.add_new_subobject.__doc__
r['foliage_remove_doc']=unreal.InstancedFoliageActor.remove_all_instances.__doc__
r['components']=[]
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
 for c in a.get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent):r['components'].append({'actor':a.get_actor_label(),'component':c.get_name(),'mesh':str(c.get_editor_property('static_mesh')),'count':c.get_instance_count()})
bp=unreal.EditorAssetLibrary.load_asset('/Game/Variant_Horror/Blueprints/BP_HorrorCharacter')
r['bp_default']=str(unreal.get_default_object(bp.generated_class()))
for c in unreal.get_default_object(bp.generated_class()).get_components_by_class(unreal.ActorComponent):
 if isinstance(c,unreal.SkeletalMeshComponent):r[c.get_name()]={'anim':str(c.get_editor_property('anim_class'))}
(Path(__file__).resolve().parents[1]/'revision09/api_audit.json').write_text(json.dumps(r,indent=2))

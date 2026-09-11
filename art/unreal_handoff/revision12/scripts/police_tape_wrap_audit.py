import unreal,json
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'police_tape/wrap_fit';out.mkdir(exist_ok=True);aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);actors=aa.get_all_level_actors();rows=[];exported={}
def xyz(v):return [v.x,v.y,v.z]
trees=[a for a in actors if isinstance(a,unreal.SkeletalMeshActor) and a.skeletal_mesh_component.get_editor_property('skeletal_mesh_asset')]
for wrap in actors:
 label=wrap.get_actor_label()
 if not (label.startswith('PoliceTape_Wrap_') or label.startswith('PoliceTape_PerimeterWrap_')):continue
 p=wrap.get_actor_location();tree=min(trees,key=lambda a:(a.get_actor_location().x-p.x)**2+(a.get_actor_location().y-p.y)**2);q=tree.get_actor_location();assert (q.x-p.x)**2+(q.y-p.y)**2<4
 mesh=tree.skeletal_mesh_component.get_editor_property('skeletal_mesh_asset');path=mesh.get_path_name()
 if path not in exported:
  filename=out/(mesh.get_name()+'.fbx');task=unreal.AssetExportTask();task.object=mesh;task.filename=str(filename);task.automated=True;task.prompt=False;task.replace_identical=True;task.exporter=unreal.SkeletalMeshExporterFBX();assert unreal.Exporter.run_asset_export_task(task);exported[path]=str(filename)
 rot=tree.get_actor_rotation()
 rows.append({'wrap':label,'tree':tree.get_actor_label(),'mesh':path,'fbx':exported[path],'tree_position':xyz(q),'tree_scale':xyz(tree.get_actor_scale3d()),'tree_rotation':[rot.pitch,rot.yaw,rot.roll],'wrap_position':xyz(p)})
(out/'survey.json').write_text(json.dumps(rows,indent=2));RESULT={'wraps':len(rows),'tree_meshes':len(exported)}

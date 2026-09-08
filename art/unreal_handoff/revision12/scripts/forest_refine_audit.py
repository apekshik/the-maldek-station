"""Read-only inventory for the user's brighter-light forest review."""
import unreal,json
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'forest_refine';out.mkdir(exist_ok=True)
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert not ls.is_in_play_in_editor(),'End user play session before running review jobs'
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert w.get_name()=='Station_R12'
o=json.loads((b.parent/'working_level_report.json').read_text())['station_origin']
def xyz(v):return [v.x,v.y,v.z]
def local(v):return [(o[0]-v.x)/100,(v.y-o[1])/100,(v.z-o[2])/100]
rows=[]
for a in aa.get_all_level_actors():
 p=local(a.get_actor_location());label=a.get_actor_label()
 cs=[]
 for c in a.get_components_by_class(unreal.StaticMeshComponent):
  if c.static_mesh:
   cs.append({'mesh':c.static_mesh.get_path_name(),'materials':[c.get_material(i).get_path_name() if c.get_material(i) else None for i in range(c.get_num_materials())],'instances':c.get_instance_count() if isinstance(c,unreal.InstancedStaticMeshComponent) else None})
 if cs or isinstance(a,unreal.SkeletalMeshActor) or 'Sky' in label or 'Weather' in label:
  row={'label':label,'path':a.get_path_name(),'local':p,'rotation':str(a.get_actor_rotation()),'scale':xyz(a.get_actor_scale3d()),'components':cs}
  if isinstance(a,unreal.SkeletalMeshActor):row['skeletal']=str(a.skeletal_mesh_component.get_editor_property('skeletal_mesh_asset'))
  rows.append(row)
assets=[]
for species in ['Common_Hazel','Goat_Willow','European_Beech']:
 for v in 'ABCD':
  p=f'/Game/Megaplant_Library/Tree_{species}/Tree_{species}_01/SK_{species}_01_{v}';m=unreal.load_asset(p)
  if m:assets.append({'path':p,'bounds':str(m.get_bounds())})
for folder in ['/Game/MWLandscapeAutoMaterial/Meshes/Plants','/Game/MWLandscapeAutoMaterial/Meshes/Cover']:
 for p in unreal.EditorAssetLibrary.list_assets(folder,True,False):
  m=unreal.load_asset(p)
  if isinstance(m,unreal.StaticMesh):assets.append({'path':p,'origin':xyz(m.get_bounds().origin),'extent':xyz(m.get_bounds().box_extent)})
camera=unreal.EditorLevelLibrary.get_level_viewport_camera_info()
(out/'live_before.json').write_text(json.dumps({'world':w.get_path_name(),'origin':o,'camera':str(camera),'actors':rows,'assets':assets},indent=2))
RESULT={'actors':len(rows),'assets':len(assets),'camera':str(camera)}

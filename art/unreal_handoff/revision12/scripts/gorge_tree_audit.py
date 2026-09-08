"""Inventory tree bounds and station geometry for player-view foliage review."""
import unreal,json
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'gorge'/'density';out.mkdir(exist_ok=True)
ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);actors=aa.get_all_level_actors()
o=json.loads((b.parent/'working_level_report.json').read_text())['station_origin']
def local(p):return [(o[0]-p.x)/100,(p.y-o[1])/100,(p.z-o[2])/100]
rows=[];fol=[]
for a in actors:
 p=local(a.get_actor_location());label=a.get_actor_label()
 if isinstance(a,unreal.InstancedFoliageActor):
  for key,t in unreal.StationMigrationLibrary.get_foliage_instance_transforms(a).items():
   p=local(t.translation)
   if abs(p[0])<140 and -120<p[1]<190:fol.append({'actor':label,'key':key,'p':p,'scale':[t.scale3d.x,t.scale3d.y,t.scale3d.z]})
  continue
 if abs(p[0])>150 or not -130<p[1]<190:continue
 bd=a.get_actor_bounds(False)
 mesh=None
 if isinstance(a,unreal.StaticMeshActor):mesh=a.static_mesh_component.static_mesh
 if isinstance(a,unreal.SkeletalMeshActor):mesh=a.skeletal_mesh_component.get_editor_property('skeletal_mesh_asset')
 rows.append({'label':label,'class':a.get_class().get_name(),'p':p,'center':local(bd[0]),'extent':[bd[1].x/100,bd[1].y/100,bd[1].z/100],'mesh':mesh.get_path_name() if mesh else None})
(out/'inventory.json').write_text(json.dumps({'actors':rows,'foliage':fol},indent=2))
RESULT={'actors':len(rows),'foliage':len(fol),'world':unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_name()}

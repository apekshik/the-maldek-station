"""Ground all placed tree bases against live collision, including their proxies."""
import unreal,json,math
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'forest_refine';aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
actors=aa.get_all_level_actors();w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();o=json.loads((b.parent/'working_level_report.json').read_text())['station_origin']
ground_actors=[a for a in actors if isinstance(a,unreal.Landscape) or a.get_actor_label() in ['VF10_Parking_Terrain','VF10_Parking_Ground','VF10_Parking_Forest_Connector']];ignore=[a for a in actors if a not in ground_actors]
def xyz(p):return [p.x,p.y,p.z]
def floor(p):
 hit=unreal.SystemLibrary.line_trace_single(w,p+unreal.Vector(0,0,50000),p-unreal.Vector(0,0,60000),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,ignore,unreal.DrawDebugTrace.NONE,True)
 return hit.to_tuple()[5].z if hit else None
moves=[];painted=[];checks=[];proxies=[a for a in actors if a.get_actor_label().startswith('FT_TrunkCollision_')]
for a in actors:
 if not isinstance(a,unreal.SkeletalMeshActor):continue
 mesh=a.skeletal_mesh_component.get_editor_property('skeletal_mesh_asset')
 if not mesh or '/Megaplant_Library/' not in mesh.get_path_name():continue
 p=a.get_actor_location();z=floor(p)
 if z is None:continue
 scale=a.get_actor_scale3d();bounds=mesh.get_bounds();bottom=(bounds.origin.z-bounds.box_extent.z)*scale.z;target=z-bottom-22
 new=unreal.Vector(p.x,p.y,target);a.set_actor_location(new,False,True)
 moves.append({'label':a.get_actor_label(),'old':xyz(p),'new':xyz(new),'mesh_bottom_cm':bottom,'ground_cm':z,'base_burial_cm':22})
 for proxy in proxies:
  q=proxy.get_actor_location()
  if math.hypot(q.x-p.x,q.y-p.y)<2:
   newq=unreal.Vector(q.x,q.y,q.z+target-p.z);proxy.set_actor_location(newq,False,True);moves.append({'label':proxy.get_actor_label(),'old':xyz(q),'new':xyz(newq),'collision_proxy':True})
 checks.append({'label':a.get_actor_label(),'base_below_ground_cm':z-(a.get_actor_location().z+bottom)})
for a in actors:
 if not isinstance(a,unreal.InstancedFoliageActor):continue
 before=unreal.StationMigrationLibrary.get_foliage_instance_transforms(a)
 for key,t in before.items():
  if 'FT_R06_Pine_' not in key:continue
  p=t.translation;z=floor(p)
  if z is None:continue
  ft,index=key.rsplit('|',1);asset=unreal.load_asset(ft);mesh=asset.get_editor_property('mesh');bounds=mesh.get_bounds();bottom=(bounds.origin.z-bounds.box_extent.z)*t.scale3d.z;target=z-bottom-25
  if abs(target-p.z)<.5:continue
  new=unreal.Vector(p.x,p.y,target);assert unreal.StationMigrationLibrary.move_r12_foliage_instance(a,ft,int(index),p,new)
  painted.append({'actor':a.get_path_name(),'key':key,'old':xyz(p),'new':xyz(new),'base_burial_cm':25})
 after=unreal.StationMigrationLibrary.get_foliage_instance_transforms(a);assert len(before)==len(after)
 for key,t in before.items():assert t.rotation==after[key].rotation and t.scale3d==after[key].scale3d
plant=json.loads((out/'planting.json').read_text());bylabel={a.get_actor_label():a for a in actors}
for row in plant['plants']+plant['trees']:
 p=bylabel[row['label']].get_actor_location();row['local']=[(o[0]-p.x)/100,(p.y-o[1])/100,(p.z-o[2])/100]
(out/'planting.json').write_text(json.dumps(plant,indent=2));assert ls.save_current_level();report={'actor_moves':moves,'painted_moves':painted,'checks':checks,'rotations_scales_counts_preserved':True,'saved':True};(out/'rooting.json').write_text(json.dumps(report,indent=2));RESULT={'trees_grounded':len(checks),'painted_trees_grounded':len(painted),'saved':True}

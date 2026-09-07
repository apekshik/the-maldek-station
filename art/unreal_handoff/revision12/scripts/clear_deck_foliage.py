"""Relocate only the three surveyed painted pines penetrating the widened west deck."""
import unreal,json,math
from pathlib import Path
b=Path(__file__).resolve().parents[1];aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not levels.is_in_play_in_editor()
inventory=json.loads((b/'foliage_instance_inventory.json').read_text());actors={a.get_path_name():a for a in aa.get_all_level_actors()};a=actors[inventory['actor']]
origin=json.loads((b.parent/'working_level_report.json').read_text())['station_origin'];world=a.get_world()
def wp(p):return unreal.Vector(origin[0]-100*p[0],origin[1]+100*p[1],origin[2]+100*p[2])
def vec(v):return [v.x,v.y,v.z]
def local(v):return [(origin[0]-v.x)/100,(v.y-origin[1])/100,(v.z-origin[2])/100]
before=unreal.StationMigrationLibrary.get_foliage_instance_transforms(a)
conflicts=[r for r in inventory['instances'] if r['deck_conflict']];assert len(conflicts)==3
out=b/'foliage_relocations.json'
if out.exists():
 previous=json.loads(out.read_text())
 assert all((before[r['key']].translation-unreal.Vector(*r['new_world'])).length()<.1 for r in previous['moves'])
 RESULT={'success':True,'already_applied':True}
else:
 occupied=[r['local'][:2] for r in inventory['instances'] if not r['deck_conflict']]
 terrain=next(v for v in actors.values() if v.get_actor_label()=='R12_Terrain');ignore=[v for v in actors.values() if v!=terrain]
 path=json.loads((b/'forest_arrival_alignment.json').read_text())['path'];moves=[]
 for r in conflicts:
  ox,oy,oz=r['local'];candidates=[]
  for x in [-29.75,-30.75,-31.75,-32.75,-33.75,-34.75]:
   for dy in [0,-1,1,-2,2,-3,3,-4,4]:
    y=oy+dy
    if min(math.hypot(x-p[0],y-p[1]) for p in occupied)<2.4:continue
    if min(math.hypot(x-p[0],y-p[1]) for p in path)<3:continue
    candidates.append((math.hypot(x-ox,y-oy),x,y))
  target=None
  for _,x,y in sorted(candidates):
   hit=unreal.SystemLibrary.line_trace_single(world,wp((x,y,5)),wp((x,y,-6)),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,ignore,unreal.DrawDebugTrace.NONE,True)
   if not hit:continue
   p=local(hit.to_tuple()[5])
   if -3<p[2]<2:target=[x,y,p[2]-.05];break
  assert target,('No grounded clearing for',r['key'])
  type_path,index=r['key'].rsplit('|',1);old=unreal.Vector(*r['world']);new=wp(target)
  assert unreal.StationMigrationLibrary.move_r12_foliage_instance(a,type_path,int(index),old,new),r['key']
  moves.append({'key':r['key'],'old_world':r['world'],'new_world':vec(new),'old_local':r['local'],'new_local':target,'reason':'Trunk intersects widened platform; preserve the tree in adjacent forest clearing.'});occupied.append(target[:2])
 after=unreal.StationMigrationLibrary.get_foliage_instance_transforms(a);changed={r['key'] for r in moves}
 assert len(before)==len(after)
 for key,t in before.items():
  assert t.rotation==after[key].rotation and t.scale3d==after[key].scale3d,key
  if key not in changed:assert (t.translation-after[key].translation).length()<.001,key
 assert levels.save_current_level()
 report={'success':True,'actor':a.get_path_name(),'moves':moves,'instance_count_preserved':len(after),'untouched_instances':len(after)-len(moves),'rotation_scale_and_species_preserved':True,'reopen_verification_pending':True};out.write_text(json.dumps(report,indent=2));RESULT=report

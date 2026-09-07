import unreal,json
from pathlib import Path
b=Path(__file__).resolve().parents[2]/'revision13';aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=aa.get_all_level_actors();w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();o=json.loads((b.parent/'working_level_report.json').read_text())['station_origin']
assert not ls.is_in_play_in_editor()
def wp(p):return unreal.Vector(o[0]-100*p[0],o[1]+100*p[1],o[2]+100*p[2])
def local(p):return [(o[0]-p.x)/100,(p.y-o[1])/100,(p.z-o[2])/100]
terrain=next(a for a in actors if a.get_actor_label()=='R13_Terrain');land=next(a for a in actors if isinstance(a,unreal.Landscape))
ignore=[a for a in actors if a!=land];rows=[]
for x,y,old,z in json.loads((b/'handoff_manifest.json').read_text())['terrain_changes']:
 hit=unreal.SystemLibrary.line_trace_single(w,wp((x,y,20)),wp((x,y,-100)),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,ignore,unreal.DrawDebugTrace.NONE,True)
 if hit:
  p=local(hit.to_tuple()[5]);rows.append({'xy':[x,y],'terrain':z,'landscape':p[2],'clearance':z-p[2]})
(b/'underlay_clearance.json').write_text(json.dumps({'samples':rows,'minimum':min(r['clearance'] for r in rows)},indent=2))
inventory=json.loads((b/'environment.json').read_text())['foliage'];moved=[];ignore=[a for a in actors if a!=terrain]
for r in inventory:
 x,y,z=r['local']
 if not (37<x<41.5 and -18.5<y<-11.5):continue
 a=next(a for a in actors if a.get_path_name()==r['actor']);tx,ty=44.5,y
 hit=unreal.SystemLibrary.line_trace_single(w,wp((tx,ty,20)),wp((tx,ty,-50)),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,ignore,unreal.DrawDebugTrace.NONE,True);assert hit
 target=local(hit.to_tuple()[5]);target[2]-=.05;tp,index=r['key'].rsplit('|',1)
 assert unreal.StationMigrationLibrary.move_r12_foliage_instance(a,tp,int(index),unreal.Vector(*r['world']),wp(target));moved.append({'key':r['key'],'before':r['local'],'after':target})
assert ls.save_current_level();(b/'foliage_moves.json').write_text(json.dumps(moved,indent=2));RESULT={'minimum_underlay_clearance':min(r['clearance'] for r in rows),'samples':len(rows),'trees_moved':len(moved)}

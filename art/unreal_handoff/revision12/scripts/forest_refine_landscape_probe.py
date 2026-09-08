import unreal,json
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'forest_refine';aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);actors=aa.get_all_level_actors();w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert w and not unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).is_in_play_in_editor()
o=json.loads((b.parent/'working_level_report.json').read_text())['station_origin'];land=next(a for a in actors if isinstance(a,unreal.Landscape));ignore=[a for a in actors if a!=land]
def wp(x,y,z):return unreal.Vector(o[0]-100*x,o[1]+100*y,o[2]+100*z)
samples=[]
for x in [-100,-40,0,40,100]:
 for y in [0,20,40,60,80,96,110,130,160,200,250,300,400,500,700,900]:
  hit=unreal.SystemLibrary.line_trace_single(w,wp(x,y,600),wp(x,y,-500),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,ignore,unreal.DrawDebugTrace.NONE,True)
  samples.append([x,y,(hit.to_tuple()[5].z-o[2])/100 if hit else None])
(out/JOB.get('report','landscape_probe.json')).write_text(json.dumps({'actor':land.get_path_name(),'transform':str(land.get_actor_transform()),'samples':samples},indent=2));RESULT={'samples':len(samples)}

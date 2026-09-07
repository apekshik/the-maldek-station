import unreal,json
from pathlib import Path
base=Path(__file__).resolve().parents[1];origin=json.loads((base.parent/'working_level_report.json').read_text())['station_origin']
def wp(p):return unreal.Vector(origin[0]-100*p[0],origin[1]+100*p[1],origin[2]+100*p[2])
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();reports=[]
for p,q in JOB['segments']:
 hit=unreal.SystemLibrary.capsule_trace_single(w,wp(p),wp(q),34,94,unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,False,[],unreal.DrawDebugTrace.NONE,True)
 row={'p':p,'q':q,'hit':[str(v) for v in hit.to_tuple()]}
 reports.append(row)
(base/'route_obstructions.json').write_text(json.dumps(reports,indent=2));RESULT=reports

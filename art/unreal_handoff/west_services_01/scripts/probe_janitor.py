import unreal,json
from pathlib import Path
P=Path(__file__).resolve().parents[1];o=json.loads((P/'baseline.json').read_text())['origin'];w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
def wp(q):return unreal.Vector(o[0]-100*q[0],o[1]+100*q[1],o[2]+100*q[2])
rows=[]
for pos in [[-12.4,-7.9,5.65],[-11.55,-7.2,5.65],[-11.5,-8,5.65],[-11.4,-7.7,5.65]]:
 h=unreal.SystemLibrary.line_trace_single(w,wp(pos),wp([-10.6,-8,5.2]),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,[],unreal.DrawDebugTrace.NONE,True).to_tuple();a=h[9];rows.append({'position':pos,'hit':a.get_actor_label() if a else None,'impact':str(h[5])})
(P/'janitor_visibility.json').write_text(json.dumps(rows,indent=2));RESULT=rows

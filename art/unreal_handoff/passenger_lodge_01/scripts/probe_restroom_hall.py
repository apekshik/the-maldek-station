import unreal,json
from pathlib import Path
OUT=Path(__file__).resolve().parents[1];o=json.loads((OUT/'before.json').read_text())['origin'];w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
def p(x,d,z):return unreal.Vector(o[0]-(x-24.1)*100,o[1]+(4-d)*100,o[2]+(4+z)*100)
rows=[]
for depth in [12.1,12.35,12.6,12.85]:
 h=unreal.SystemLibrary.line_trace_single(w,p(8.8,depth,1.2),p(15,depth,1.2),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,[],unreal.DrawDebugTrace.NONE,True).to_tuple();a=h[9];rows.append({'depth':depth,'hit':str(h),'actor':a.get_actor_label() if a else None})
RESULT=rows;(OUT/'restrooms/hall_probe.json').write_text(json.dumps(rows,indent=2))

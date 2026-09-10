import unreal,json
from pathlib import Path
OUT=Path(__file__).resolve().parents[1];b=json.loads((OUT/'before.json').read_text());o=b['origin']
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert w.get_name()=='Station_Lodge_Migration'
def wp(x,y,z):return unreal.Vector(o[0]-100*x,o[1]+100*y,o[2]+100*z)
rows=[]
for x in [-29,-27,-24.5,-23.5,-22.5,-20,-16,-12,-8.1,-7.2,-6.3]:
 for y in [-20,-18,-17,-16,-15,-14,-12,-8,0,6,8]:
  hits=unreal.SystemLibrary.line_trace_multi(w,wp(x,y,3.5),wp(x,y,-40),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,[],unreal.DrawDebugTrace.NONE,True)
  rows.append({'xy':[x,y],'hits':[{'z':(h.to_tuple()[5].z-o[2])/100,'fields':[str(v) for v in h.to_tuple()]} for h in (hits or [])]})
(OUT/'approach_probe.json').write_text(json.dumps(rows,indent=2));RESULT={'samples':len(rows)}

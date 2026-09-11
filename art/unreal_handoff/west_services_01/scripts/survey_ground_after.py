import unreal,json
from pathlib import Path
P=Path(__file__).resolve().parents[1];o=json.loads((P/'baseline.json').read_text())['origin'];w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
def wp(x,y,z):return unreal.Vector(o[0]-100*x,o[1]+100*y,o[2]+100*z)
by={a.get_actor_label():a for a in actors};terrain=[by[n] for n in ['Landscape0','VF10_Parking_Terrain','VF10_Parking_Ground']];ignore=[a for a in actors if a not in terrain];samples=[]
for x in range(-65,-26):
 for y in range(-20,23):
  h=unreal.SystemLibrary.line_trace_single(w,wp(x,y,30),wp(x,y,-80),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,ignore,unreal.DrawDebugTrace.NONE,True);t=h.to_tuple() if h else None
  samples.append({'xy':[x,y],'z':(t[5].z-o[2])/100 if t and t[0] else None,'actor':t[9].get_actor_label() if t and t[0] and t[9] else None})
(P/'ground_after.json').write_text(json.dumps({'samples':samples},indent=2));RESULT={'ground':len(samples)}

import unreal,json
from pathlib import Path
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
d=next(d for d in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.StationDoor) if d.get_actor_label()=='R12_Door_Control_front')
rows=[]
for x in [0,65,150,-150]:
 for y in [100,150,250,350,500]:
  p=unreal.MathLibrary.transform_location(d.get_actor_transform(),unreal.Vector(x,y,0))
  hit=unreal.SystemLibrary.line_trace_single(w,p+unreal.Vector(0,0,200),p-unreal.Vector(0,0,1500),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,[],unreal.DrawDebugTrace.NONE,True)
  h=hit.to_tuple() if hit else None
  rows.append({'local':[x,y],'point':str(p),'hit':str(h)})
(Path(__file__).resolve().parents[1]/'platform_floor_probe.json').write_text(json.dumps(rows,indent=2))
RESULT=rows

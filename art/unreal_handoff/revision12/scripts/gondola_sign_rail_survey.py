import unreal,json
from pathlib import Path
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);actors=aa.get_all_level_actors();g=next(a for a in actors if isinstance(a,unreal.GondolaSystem));sp=g.get_components_by_class(unreal.SplineComponent)[0];start=sp.get_location_at_spline_point(0,unreal.SplineCoordinateSpace.WORLD);w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();sign=next(a for a in actors if isinstance(a,unreal.GondolaStatusSign))
rows=[]
for x in [300,400,450,500,550,600,650]:
 for y in [-400,-250,-100,50]:
  p=start+unreal.Vector(x,y,0);h=unreal.SystemLibrary.line_trace_single(w,p+unreal.Vector(0,0,50),p-unreal.Vector(0,0,100),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,[sign],unreal.DrawDebugTrace.NONE,True)
  rows.append({'x':x,'y':y,'floor':h.to_tuple()[5].z-start.z if h else None})
rails=[]
for y in [-400,-250,-100,50]:
 h=unreal.SystemLibrary.line_trace_single(w,start+unreal.Vector(180,y,105),start+unreal.Vector(850,y,105),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,[sign],unreal.DrawDebugTrace.NONE,True)
 rails.append({'y':y,'hit':str(h.to_tuple()) if h else None})
RESULT={'floor':rows,'rails':rails};(Path(__file__).resolve().parents[1]/'gondola_sign/rail_survey.json').write_text(json.dumps(RESULT,indent=2))

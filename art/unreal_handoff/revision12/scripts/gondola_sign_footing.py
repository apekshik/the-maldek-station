import unreal,json
from pathlib import Path
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);by={a.get_actor_label():a for a in aa.get_all_level_actors()};g=by['BP_GondolaSystem'];a=by['R12_Gondola_Status_Sign'];sp=g.get_components_by_class(unreal.SplineComponent)[0];start=sp.get_location_at_spline_point(0,unreal.SplineCoordinateSpace.WORLD);w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();rows=[]
for x in [145,150,155,160,165,170,180]:
 for y in [-630,-650,-670]:
  zs=[]
  for dx,dy in [(-12,24),(12,24),(-12,7),(12,7)]:
   p=start+unreal.Vector(x+dx,y+dy,0);h=unreal.SystemLibrary.line_trace_single(w,p+unreal.Vector(0,0,60),p-unreal.Vector(0,0,100),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,[a],unreal.DrawDebugTrace.NONE,True);zs.append(h.to_tuple()[5].z-start.z if h and h.to_tuple()[0] else None)
  rows.append({'x':x,'y':y,'surface_offsets':zs})
RESULT=rows;(Path(__file__).resolve().parents[1]/'gondola_sign/footing_survey.json').write_text(json.dumps(rows,indent=2))

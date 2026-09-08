"""Read-only survey; run only after the current editor owner releases R12."""
import unreal,json,math
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'route_refine';out.mkdir(exist_ok=True)
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert not ls.is_in_play_in_editor()
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert w and w.get_name()=='Station_R12'
actors=aa.get_all_level_actors();controller=next(a for a in actors if a.get_actor_label()=='BP_GondolaSystem');sp=controller.get_components_by_class(unreal.SplineComponent)[0]
land=[a for a in actors if isinstance(a,unreal.LandscapeProxy)];assert land
ignore=[a for a in actors if a not in land]
def v(p):return [p.x,p.y,p.z]
def ground(x,y):
 h=unreal.SystemLibrary.line_trace_single(w,unreal.Vector(x,y,180000),unreal.Vector(x,y,-150000),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,False,ignore,unreal.DrawDebugTrace.NONE)
 assert h and h.to_tuple()[0],('No landscape hit',x,y)
 return h.to_tuple()[5].z
length=sp.get_spline_length();start=sp.get_location_at_distance_along_spline(0,unreal.SplineCoordinateSpace.WORLD);end=sp.get_location_at_distance_along_spline(length,unreal.SplineCoordinateSpace.WORLD)
remote=next(a for a in actors if a.get_actor_label()=='R10_Distant_Station').get_actor_location();remote_ground=ground(remote.x,remote.y)
# The existing cabin-pivot route is preserved. This pass adds the visible cable infrastructure.
rope_offset=400.;target=unreal.Vector(remote.x,remote.y-1400,remote_ground+1000)
rows=[]
for i in range(61):
 t=i/60
 if t<=.42:
  p=sp.get_location_at_distance_along_spline(length*t/.42,unreal.SplineCoordinateSpace.WORLD);p.z+=rope_offset
 else:
  f=(t-.42)/.58;p=unreal.Vector(end.x+(target.x-end.x)*f,end.y+(target.y-end.y)*f,end.z+rope_offset+(target.z-end.z-rope_offset)*f)
 rows.append({'t':t,'position':v(p),'ground_z':ground(p.x,p.y)})
# Footings need individual terrain levels on the steep valley sides.
supports=[]
for index in [6,17,29,42,54]:
 r=rows[index];p=r['position'];feet=[]
 for x in [p[0]-650,p[0]+1150]:feet.append([x,p[1],ground(x,p[1])])
 supports.append({'index':index,'rope':p,'feet':feet})
RESULT={'world':w.get_path_name(),'origin':v(start),'spline_length_cm':length,'spline_points':[v(sp.get_location_at_spline_point(i,unreal.SplineCoordinateSpace.WORLD)) for i in range(sp.get_number_of_spline_points())],'rope_offset_cm':rope_offset,'samples':rows,'supports':supports,'remote':v(remote),'remote_ground_z':remote_ground,'camera':str(unreal.EditorLevelLibrary.get_level_viewport_camera_info())}
(out/'survey.json').write_text(json.dumps(RESULT,indent=2))

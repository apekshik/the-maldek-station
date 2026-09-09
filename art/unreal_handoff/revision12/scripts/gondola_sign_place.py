"""Final player-facing left placement, with platform and approach sightline checks."""
import unreal,json
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'gondola_sign';ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);by={a.get_actor_label():a for a in aa.get_all_level_actors()};g=by['BP_GondolaSystem'];a=by['R12_Gondola_Status_Sign'];sp=g.get_components_by_class(unreal.SplineComponent)[0];start=sp.get_location_at_spline_point(0,unreal.SplineCoordinateSpace.WORLD)
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();a.set_actor_location(start+unreal.Vector(150,-630,0),False,True)
heights=[]
for x,y in [(-12,24),(12,24),(-12,7),(12,7)]:
 p=a.get_actor_location()+unreal.Vector(x,y,0);h=unreal.SystemLibrary.line_trace_single(w,p+unreal.Vector(0,0,60),p-unreal.Vector(0,0,100),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,[a],unreal.DrawDebugTrace.NONE,True)
 assert h and h.to_tuple()[0];heights.append(h.to_tuple()[5].z)
assert max(heights)-min(heights)<3
a.set_actor_location(unreal.Vector(a.get_actor_location().x,a.get_actor_location().y,sum(heights)/4),False,True)
sight=[]
for eye in [start+unreal.Vector(0,-1050,170),start+unreal.Vector(0,-850,170)]:
 for x,z in [(-55,180),(55,180),(-55,260),(55,260),(0,220)]:
  target=a.get_actor_location()+unreal.Vector(x,-5,z);h=unreal.SystemLibrary.line_trace_single(w,eye,target,unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,[a],unreal.DrawDebugTrace.NONE,True);sight.append(h is None or not h.to_tuple()[0])
assert all(sight),('Approach sightline blocked',sight)
assert ls.save_current_level()
RESULT={'success':True,'position':a.get_actor_location().to_tuple(),'support_heights':heights,'approach_sightlines_clear':sight,'placement':'Left in player view facing mountains; forward of the machinery column'};(out/'placement.json').write_text(json.dumps(RESULT,indent=2))

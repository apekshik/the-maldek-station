"""Read-only vehicle surface survey for placing the inspection sample."""
import unreal,json
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'inspection';out.mkdir(exist_ok=True)
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
actors=list(aa.get_all_level_actors())
rows=[]
for actor in actors:
 if actor.get_actor_label() not in ['FR_Parked_Pickup','FR_Parked_Hatchback']:continue
 samples=[]
 for x in [-175,-130,-70,0,70,130,175]:
  for y in [-50,0,50]:
   p=unreal.MathLibrary.transform_location(actor.get_actor_transform(),unreal.Vector(x,y,0))
   hit=unreal.SystemLibrary.line_trace_single(world,p+unreal.Vector(0,0,350),p-unreal.Vector(0,0,50),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,[a for a in actors if a!=actor],unreal.DrawDebugTrace.NONE,True)
   if hit and hit.to_tuple()[0]:
    t=hit.to_tuple();samples.append({'local_xy':[x,y],'world':t[5].to_tuple(),'normal':t[6].to_tuple(),'height':t[5].z-actor.get_actor_location().z})
 rows.append({'label':actor.get_actor_label(),'location':actor.get_actor_location().to_tuple(),'rotation':actor.get_actor_rotation().to_tuple(),'bounds':str(actor.get_actor_bounds(False)),'samples':samples})
RESULT={'world':world.get_path_name(),'vehicles':rows}
(out/'parking_survey.json').write_text(json.dumps(RESULT,indent=2))

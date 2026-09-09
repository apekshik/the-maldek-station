import unreal,json
from pathlib import Path
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);actors=aa.get_all_level_actors();g=next(a for a in actors if isinstance(a,unreal.GondolaSystem));start=g.get_components_by_class(unreal.SplineComponent)[0].get_location_at_spline_point(0,unreal.SplineCoordinateSpace.WORLD)
rows=[]
for a in actors:
 c,e=a.get_actor_bounds(False);p=c-start
 if a.get_actor_label() in ['R12_13_Roofs_001_solid','R12_VF06_Service_Hardware_000_solid','R12_01_Upper_Platform_001_solid','R12_Gondola_Status_Sign'] or isinstance(a,unreal.PlayerStart):
  rows.append({'label':a.get_actor_label(),'position':(a.get_actor_location()-start).to_tuple(),'center':p.to_tuple(),'extent':e.to_tuple(),'rotation':a.get_actor_rotation().to_tuple()})
RESULT={'start':start.to_tuple(),'actors':rows};(Path(__file__).resolve().parents[1]/'gondola_sign/roof_survey.json').write_text(json.dumps(RESULT,indent=2))

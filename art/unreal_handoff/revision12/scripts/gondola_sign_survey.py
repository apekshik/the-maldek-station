import unreal,json
from pathlib import Path
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);w=unreal.EditorLevelLibrary.get_game_world();by={a.get_actor_label():a for a in (unreal.GameplayStatics.get_all_actors_of_class(w,unreal.Actor) if w else aa.get_all_level_actors())};g=next(a for a in by.values() if isinstance(a,unreal.GondolaSystem));sp=g.get_components_by_class(unreal.SplineComponent)[0];start=sp.get_location_at_spline_point(0,unreal.SplineCoordinateSpace.WORLD);rows=[]
for a in by.values():
 center,ext=a.get_actor_bounds(False);p=center-start
 if abs(p.x)<650 and -950<p.y<0 and ext.z>120 and ext.x<150 and ext.y<150:rows.append({'label':a.get_actor_label(),'center':p.to_tuple(),'extent':ext.to_tuple()})
RESULT={'nearby_columns':rows,'heading':(sp.get_location_at_distance_along_spline(2000,unreal.SplineCoordinateSpace.WORLD)-start).to_tuple()};(Path(__file__).resolve().parents[1]/'gondola_sign/survey.json').write_text(json.dumps(RESULT,indent=2))

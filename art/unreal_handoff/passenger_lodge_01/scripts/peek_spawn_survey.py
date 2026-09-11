import unreal,json
from pathlib import Path
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
actors=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.Actor)
rows=[]
for a in actors:
 if isinstance(a,unreal.PlayerStart) or isinstance(a,unreal.StationDoor) or 'platform' in a.get_actor_label().lower():
  p=a.get_actor_location();r=a.get_actor_rotation()
  rows.append({'name':a.get_actor_label(),'class':a.get_class().get_name(),'location':[p.x,p.y,p.z],'rotation':[r.pitch,r.yaw,r.roll]})
RESULT={'world':w.get_path_name(),'actors':rows}
(Path(__file__).resolve().parents[1]/'peek_spawn_survey.json').write_text(json.dumps(RESULT,indent=2))

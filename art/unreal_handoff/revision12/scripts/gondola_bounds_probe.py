import unreal,json
from pathlib import Path
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);r=[]
for a in aa.get_all_level_actors():
 if a.get_actor_label().startswith('R12_Route_Cable'):
  c,e=a.get_actor_bounds(False);r.append({'label':a.get_actor_label(),'rotation':str(a.get_actor_rotation()),'position':str(a.get_actor_location()),'bounds':[[c.x,c.y,c.z],[e.x,e.y,e.z]],'matrix':str(a.get_actor_transform())})
RESULT=r;(Path(__file__).resolve().parents[1]/'gondola_route/bounds_probe.json').write_text(json.dumps(r,indent=2))

import unreal,json
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'machinery_audio';out.mkdir(exist_ok=True)
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
rows=[]
for a in aa.get_all_level_actors():
 if any(s in a.get_actor_label().lower() for s in ['gondola','cable']) or isinstance(a,unreal.GondolaSystem):
  center,extent=a.get_actor_bounds(False)
  rows.append({'label':a.get_actor_label(),'class':a.get_class().get_path_name(),'location':list(a.get_actor_location().to_tuple()),'center':list(center.to_tuple()),'extent':list(extent.to_tuple())})
(out/'anchors.json').write_text(json.dumps(rows,indent=2))
(out/'api.txt').write_text(str(unreal.SoundAttenuationSettings.__doc__)+'\n'+str(unreal.AudioComponent.__doc__))
RESULT={'actors':len(rows)}

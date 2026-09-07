import unreal,json,runpy
from pathlib import Path
r=[]
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
 if a.get_actor_label().startswith(('R04_','R05_')) and 'Terrain' not in a.get_actor_label():
  center,extent=a.get_actor_bounds(False);r.append({'name':a.get_actor_label(),'center':[center.x,center.y,center.z],'extent':[extent.x,extent.y,extent.z]})
(Path(__file__).resolve().parents[1]/'revision07/fixture_bounds.json').write_text(json.dumps(r,indent=2))
runpy.run_path(str(Path(__file__).with_name('review_session.py')))

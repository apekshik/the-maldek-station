import unreal,json,runpy
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'police_tape';aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);actors={a.get_actor_label():a for a in aa.get_all_level_actors()}
def xyz(p):return [p.x,p.y,p.z]
for filename in ['survey.json','fitted.json']:
 rows=json.loads((out/'wrap_fit'/filename).read_text())
 for r in rows:
  if r['wrap'].startswith('PoliceTape_PerimeterWrap_'):r['tree']=r['wrap'].replace('PerimeterWrap','PerimeterTree')
  tree=actors[r['tree']];wrap=actors[r['wrap']];r.update(tree_position=xyz(tree.get_actor_location()),wrap_position=xyz(wrap.get_actor_location()),tree_rotation=[tree.get_actor_rotation().pitch,tree.get_actor_rotation().yaw,tree.get_actor_rotation().roll])
 (out/'wrap_fit'/filename).write_text(json.dumps(rows,indent=2))
runpy.run_path(str(b/'scripts/police_tape_fit_anchors.py'));RESULT={'updated':True}

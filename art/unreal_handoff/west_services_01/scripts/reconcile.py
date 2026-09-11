import unreal,json
from pathlib import Path
P=Path(__file__).resolve().parents[1];ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor();aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
def capture():
 rows=[]
 for a in aa.get_all_level_actors():
  p=a.get_actor_location();r=a.get_actor_rotation();s=a.get_actor_scale3d();rows.append({'label':a.get_actor_label(),'name':a.get_name(),'class':a.get_class().get_path_name(),'position':[p.x,p.y,p.z],'rotation':[r.pitch,r.yaw,r.roll],'scale':[s.x,s.y,s.z],'meshes':[{'component':c.get_name(),'mesh':c.static_mesh.get_path_name()} for c in a.get_components_by_class(unreal.StaticMeshComponent) if c.static_mesh]})
 return rows
migration=capture();assert ls.load_level('/Game/MaldekRefinement/R12/Station_R12');r12=capture();assert ls.load_level('/Game/MaldekRefinement/PassengerLodge/Station_Lodge_Migration');m={r['name']:r for r in migration};old=json.loads((P.parent/'passenger_lodge_01/before.json').read_text());old={r['name']:r for r in old['actors']};diff=[]
for r in r12:
 b=old.get(r['name'])
 if not b:diff.append({'kind':'new_since_lodge','r12':r,'migration':m.get(r['name'])});continue
 issues=[]
 for key,k in [('position','location'),('rotation','rotation'),('scale','scale')]:
  if k in b and max(abs(x-y) for x,y in zip(r[key],b[k]))>.01:issues.append(key)
 if issues:diff.append({'kind':'changed_since_lodge','changes':issues,'r12':r,'migration':m.get(r['name']),'original':b})
(P/'r12_reconciliation.json').write_text(json.dumps({'r12':r12,'migration':migration,'changes':diff},indent=2));RESULT={'r12_actors':len(r12),'changes':len(diff),'summary':[[r['kind'],r['r12']['label'],r.get('changes')] for r in diff]}

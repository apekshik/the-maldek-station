import unreal,json
from pathlib import Path
OUT=Path(__file__).resolve().parents[1];o=json.loads((OUT/'before.json').read_text())['origin'];w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert w.get_name()=='Station_Lodge_Migration'
def src(p):return [-(p.x-o[0])/100,(p.y-o[1])/100,(p.z-o[2])/100]
rows=[]
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
 c,e=a.get_actor_bounds(False);lo=[src(c)[i]-[e.x,e.y,e.z][i]/100 for i in range(3)];hi=[src(c)[i]+[e.x,e.y,e.z][i]/100 for i in range(3)]
 if lo[0]>-5 or hi[0]<-35 or lo[1]>12 or hi[1]<-23 or hi[2]<3.8:continue
 if a.get_actor_label().startswith('MIG_'):continue
 rows.append({'label':a.get_actor_label(),'name':a.get_name(),'class':a.get_class().get_name(),'position':src(a.get_actor_location()),'lo':lo,'hi':hi,'parent':str(a.get_attach_parent_actor()),'components':[{'name':p.get_name(),'mesh':str(p.static_mesh)} for p in a.get_components_by_class(unreal.StaticMeshComponent)]})
(OUT/'cleanup_audit.json').write_text(json.dumps(rows,indent=2));RESULT={'candidates':len(rows)}

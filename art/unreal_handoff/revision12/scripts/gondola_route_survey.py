import unreal,json,shutil
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'gondola_route';out.mkdir(exist_ok=True)
ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);actors=aa.get_all_level_actors()
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert w.get_name()=='Station_R12'
def v(p):return [p.x,p.y,p.z]
terrain=[a for a in actors if isinstance(a,unreal.LandscapeProxy) or any(s in a.get_actor_label().lower() for s in ['terrain','gorge','bedrock']) and isinstance(a,unreal.StaticMeshActor) and a.static_mesh_component.static_mesh]
ignore=[a for a in actors if a not in terrain]
def ground(x,y):
 h=unreal.SystemLibrary.line_trace_single(w,unreal.Vector(x,y,180000),unreal.Vector(x,y,-150000),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,ignore,unreal.DrawDebugTrace.NONE)
 return v(h.to_tuple()[5]) if h and h.to_tuple()[0] else None
start=next(a for a in actors if a.get_actor_label()=='R12_12_Gondola_003_solid').get_actor_location()
remote=next(a for a in actors if a.get_actor_label()=='R10_Distant_Station').get_actor_location()
rows=[]
for i in range(281):
 t=i/280;x=start.x+(remote.x-start.x)*t;y=start.y+(remote.y-700-start.y)*t
 rows.append({'t':t,'centre':ground(x,y),'left':ground(x-620,y),'right':ground(x+620,y),'xy':[x,y]})
related=[]
for a in actors:
 if any(k in a.get_actor_label().lower() for k in ['gondola','cable','fog','playerstart']):
  related.append({'label':a.get_actor_label(),'class':a.get_class().get_name(),'position':v(a.get_actor_location()),'rotation':str(a.get_actor_rotation()),'bounds':[v(p) for p in a.get_actor_bounds(False)],'components':[{'name':c.get_name(),'class':c.get_class().get_name(),'position':v(c.get_world_location())} for c in a.get_components_by_class(unreal.SceneComponent)]})
assert ls.save_current_level()
backup=out/'Station_R12_before_gondola.umap'
if not backup.exists():shutil.copy2(b.parents[2]/'game/Content/MaldekRefinement/R12/Station_R12.umap',backup)
RESULT={'start':v(start),'remote':v(remote),'samples':rows,'related':related,'terrain':[a.get_actor_label() for a in terrain]}
(out/'survey.json').write_text(json.dumps(RESULT,indent=2))

import unreal,json
from pathlib import Path
b=Path(__file__).resolve().parents[1];aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert w.get_name()=='Station_R12'
origin=json.loads((b.parent/'working_level_report.json').read_text())['station_origin']
def wp(p):return unreal.Vector(origin[0]-100*p[0],origin[1]+100*p[1],origin[2]+100*p[2])
def loc(p):return [(origin[0]-p.x)/100,(p.y-origin[1])/100,(p.z-origin[2])/100]
foliage=next(a for a in aa.get_all_level_actors() if a.get_actor_label()=='InstancedFoliageActor0')
instances=unreal.StationMigrationLibrary.get_foliage_instance_transforms(foliage)
rows=[];deck=json.loads((b.parents[2]/'art/blender/visual_fidelity_07/layout.json').read_text())['deck_rects']
for key,t in instances.items():
 p=loc(t.translation);conflict=any(x0-.75<=p[0]<=x1+.75 and y0-.75<=p[1]<=y1+.75 and p[2]<z+1 for x0,x1,y0,y1,z,kind in deck)
 rows.append({'key':str(key),'local':p,'world':[t.translation.x,t.translation.y,t.translation.z],'rotation':str(t.rotation),'scale':str(t.scale3d),'deck_conflict':conflict})
(b/'foliage_instance_inventory.json').write_text(json.dumps({'actor':foliage.get_path_name(),'instances':rows},indent=2))
layers=[]
for x,y in [(7,-3),(8,-3),(9,-3),(8,-1),(8,-5),(10,-3),(12,-3)]:
 ignore=[];hits=[]
 for i in range(8):
  hit=unreal.SystemLibrary.line_trace_single(w,wp((x,y,1)),wp((x,y,-2)),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,ignore,unreal.DrawDebugTrace.NONE,True)
  if not hit:break
  t=hit.to_tuple()
  if not t[0]:break
  actor=t[9];hits.append({'actor':actor.get_path_name(),'label':actor.get_actor_label(),'impact':loc(t[5])});ignore.append(actor)
 layers.append({'xy':[x,y],'layers':hits})
(b/'apron_surface_layers.json').write_text(json.dumps(layers,indent=2));RESULT={'foliage_instances':len(rows),'deck_conflicts':[r for r in rows if r['deck_conflict']],'apron_layers':layers}

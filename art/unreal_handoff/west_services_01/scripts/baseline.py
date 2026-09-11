import unreal,json,hashlib,shutil
from pathlib import Path
P=Path(__file__).resolve().parents[1];R=P.parents[2];o=json.loads((P.parent/'passenger_lodge_01/before.json').read_text())['origin'];ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert w and w.get_name()=='Station_Lodge_Migration' and not ls.is_in_play_in_editor()
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);actors=aa.get_all_level_actors()
def xyz(v):return [v.x,v.y,v.z]
def src(p):return [-(p.x-o[0])/100,(p.y-o[1])/100,(p.z-o[2])/100]
def wp(x,y,z):return unreal.Vector(o[0]-100*x,o[1]+100*y,o[2]+100*z)
rows=[];vegetation=[]
for a in actors:
 cs=[]
 for c in a.get_components_by_class(unreal.StaticMeshComponent):
  if not c.static_mesh:continue
  cs.append({'component':c.get_name(),'mesh':c.static_mesh.get_path_name()})
  if isinstance(c,unreal.InstancedStaticMeshComponent):
   ts=[(i,c.get_instance_transform(i,world_space=True)) for i in range(c.get_instance_count())]
  else:ts=[(None,c.get_world_transform())]
  for i,t in ts:
   p=src(t.translation)
   if not (-75<p[0]<-24 and -30<p[1]<35):continue
   if not any(k in c.static_mesh.get_path_name().lower() for k in ['tree','pine','alder','spruce','bush','grass','fern','foliage','shrub']):continue
   b=c.static_mesh.get_bounds();bb=[src(unreal.MathLibrary.transform_location(t,b.origin+unreal.Vector(x*b.box_extent.x,y*b.box_extent.y,z*b.box_extent.z))) for x in [-1,1] for y in [-1,1] for z in [-1,1]]
   vegetation.append({'actor':a.get_actor_label(),'component':c.get_name(),'index':i,'mesh':c.static_mesh.get_path_name(),'position':p,'world':xyz(t.translation),'lo':[min(v[j] for v in bb) for j in range(3)],'hi':[max(v[j] for v in bb) for j in range(3)]})
 rows.append({'label':a.get_actor_label(),'name':a.get_name(),'class':a.get_class().get_name(),'position':xyz(a.get_actor_location()),'rotation':[a.get_actor_rotation().pitch,a.get_actor_rotation().yaw,a.get_actor_rotation().roll],'scale':xyz(a.get_actor_scale3d()),'meshes':cs})
assert not (P/'baseline.json').exists()
assert ls.save_current_level()
bak=P/'baseline_backup';bak.mkdir(exist_ok=True)
mp=R/'game/Content/MaldekRefinement/PassengerLodge/Station_Lodge_Migration.umap';shutil.copy2(mp,bak/mp.name)
(P/'baseline.json').write_text(json.dumps({'origin':o,'world':w.get_path_name(),'actors':rows,'map_sha256':hashlib.sha256(mp.read_bytes()).hexdigest(),'r12_sha256':hashlib.sha256((R/'game/Content/MaldekRefinement/R12/Station_R12.umap').read_bytes()).hexdigest(),'dirty_content':[str(p) for p in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()]},indent=2))
(P/'vegetation_baseline.json').write_text(json.dumps(vegetation,indent=2))
by={a.get_actor_label():a for a in actors};terrain=[by[n] for n in ['Landscape0','VF10_Parking_Terrain','VF10_Parking_Ground']];ignore=[a for a in actors if a not in terrain];samples=[]
for x in range(-65,-26):
 for y in range(-20,23):
  h=unreal.SystemLibrary.line_trace_single(w,wp(x,y,30),wp(x,y,-80),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,ignore,unreal.DrawDebugTrace.NONE,True);t=h.to_tuple() if h else None
  samples.append({'xy':[x,y],'z':(t[5].z-o[2])/100 if t and t[0] else None,'actor':t[9].get_actor_label() if t and t[0] and t[9] else None})
(P/'ground_survey.json').write_text(json.dumps({'samples':samples},indent=2));RESULT={'actors':len(rows),'vegetation':len(vegetation),'ground':len(samples)}

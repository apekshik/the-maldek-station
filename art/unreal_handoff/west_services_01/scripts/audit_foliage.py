import unreal,json,math
from pathlib import Path
P=Path(__file__).resolve().parents[1];B=json.loads((P/'baseline.json').read_text());o=B['origin'];w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert w.get_name()=='Station_Lodge_Migration';aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);actors=aa.get_all_level_actors();rows=[]
def src(p):return [-(p.x-o[0])/100,(p.y-o[1])/100,(p.z-o[2])/100]
for a in actors:
 for c in a.get_components_by_class(unreal.StaticMeshComponent):
  if not c.static_mesh:continue
  if not isinstance(c,unreal.InstancedStaticMeshComponent) and not a.get_actor_label().startswith('MIG_WS_Screening'):continue
  b=c.static_mesh.get_bounds()
  for i in range(c.get_instance_count() if isinstance(c,unreal.InstancedStaticMeshComponent) else 1):
   t=c.get_instance_transform(i,world_space=True) if isinstance(c,unreal.InstancedStaticMeshComponent) else c.get_world_transform();p=src(t.translation)
   if not (-60<p[0]<-25 and -25<p[1]<25):continue
   bb=[src(unreal.MathLibrary.transform_location(t,b.origin+unreal.Vector(x*b.box_extent.x,y*b.box_extent.y,z*b.box_extent.z))) for x in [-1,1] for y in [-1,1] for z in [-1,1]];lo=[min(v[j] for v in bb) for j in range(3)];hi=[max(v[j] for v in bb) for j in range(3)]
   # New platform, upper passage and service stair volume. Conservative foliage bounds.
   conflict=lo[0]<-28.75 and hi[0]>-40.65 and lo[1]<10.8 and hi[1]>-7.7 and lo[2]<8.7 and hi[2]>.95
   ramp=lo[0]<-29.3 and hi[0]>-31.6 and lo[1]<-5 and hi[1]>-13.6 and lo[2]<6.4 and hi[2]>3.65
   if conflict or ramp:rows.append({'actor':a.get_actor_label(),'component':c.get_name(),'index':i,'position':p,'world':[t.translation.x,t.translation.y,t.translation.z],'mesh':c.static_mesh.get_path_name(),'lo':lo,'hi':hi})
(P/'foliage_conflicts.json').write_text(json.dumps(rows,indent=2));RESULT={'conflicts':len(rows)}

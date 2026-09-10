import unreal,json
from pathlib import Path
OUT=Path(__file__).resolve().parents[1];o=json.loads((OUT/'before.json').read_text())['origin'];assert unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_name()=='Station_Lodge_Migration'
def src(p):return [-(p.x-o[0])/100,(p.y-o[1])/100,(p.z-o[2])/100]
rows=[]
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
 for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
  if not c.static_mesh:continue
  b=c.static_mesh.get_bounds()
  for i in range(c.get_instance_count()):
   t=c.get_instance_transform(i,world_space=True);p=src(t.translation)
   if not (-50<p[0]<10 and -35<p[1]<30):continue
   points=[src(unreal.MathLibrary.transform_location(t,b.origin+unreal.Vector(x*b.box_extent.x,y*b.box_extent.y,z*b.box_extent.z))) for x in [-1,1] for y in [-1,1] for z in [-1,1]]
   lo=[min(p[j] for p in points) for j in range(3)];hi=[max(p[j] for p in points) for j in range(3)]
   if lo[0]<-9.5 and hi[0]>-30 and lo[1]<8 and hi[1]>-16 and hi[2]>4 and lo[2]<9:
    rows.append({'actor':a.get_actor_label(),'component':c.get_name(),'index':i,'mesh':c.static_mesh.get_path_name(),'position':p,'lo':lo,'hi':hi})
(OUT/('foliage_audit_after.json' if globals().get('JOB',{}).get('after') else 'foliage_audit.json')).write_text(json.dumps(rows,indent=2));RESULT={'overlaps':len(rows)}

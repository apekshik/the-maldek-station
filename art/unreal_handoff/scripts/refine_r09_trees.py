"""Keep visible pines rooted while raising the canopy and removing low silhouettes."""
import unreal,json,math
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'revision09';baseline=out/'tree_baseline.json'
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert world.get_name()=='BlockOut_R09'
if baseline.exists(): rows=json.loads(baseline.read_text())
else:
 rows=[]
 for a in actors.get_all_level_actors():
  for c in a.get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent):
   mesh=c.get_editor_property('static_mesh')
   if not mesh or not mesh.get_name().startswith('SM_R06_Pine_'):continue
   variant=int(mesh.get_name()[-1]);bounds=mesh.get_bounds()
   for i in range(c.get_instance_count()):
    t=c.get_instance_transform(i,True);p=t.translation;s=t.scale3d;q=t.rotation
    rows.append({'variant':variant,'location':[p.x,p.y,p.z],'scale':[s.x,s.y,s.z],'rotation':[q.x,q.y,q.z,q.w],'local_top':bounds.origin.z+bounds.box_extent.z})
 baseline.write_text(json.dumps(rows,indent=2))
transforms=[[],[],[]];removed=[];raised=0
for i,row in enumerate(rows):
 p=row['location'];s=list(row['scale']);oldtop=p[2]+row['local_top']*s[2]
 if oldtop<9898:removed.append(i);continue
 distance=math.hypot(p[0]+44282.306,p[1]-18474.708)
 if distance<6500:
  factor=min(2.3,max(1.35,(11550-p[2])/max(1,row['local_top']*s[2])))
  s=[s[0]*1.12,s[1]*1.12,s[2]*factor];raised+=1
 transforms[row['variant']].append(unreal.Transform(location=unreal.Vector(*p),rotation=unreal.Quat(*row['rotation']).rotator(),scale=unreal.Vector(*s)))
for i,ts in enumerate(transforms):
 ft=unreal.EditorAssetLibrary.load_asset('/Game/MaldekRefinement/R06/Foliage/FT_R06_Pine_'+str(i))
 unreal.InstancedFoliageActor.remove_all_instances(world,ft)
 unreal.InstancedFoliageActor.add_instances(world,ft,ts)
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
(out/'tree_changes.json').write_text(json.dumps({'before':len(rows),'after':sum(map(len,transforms)),'removed_below_visible_decks':len(removed),'raised_near_station':raised,'removed_indices':removed,'roots_moved':False},indent=2))

"""Clustered, deterministic understorey with protected routes and service areas."""
import unreal,json,math,random
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'forest_refine';root='/Game/MaldekRefinement/R12/ForestRefine'
ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);lib=unreal.EditorAssetLibrary;at=unreal.AssetToolsHelpers.get_asset_tools();w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
o=json.loads((b.parent/'working_level_report.json').read_text())['station_origin'];grid={(x,y):z for x,y,z in json.loads((out/'terrain_grid.json').read_text())['vertices']}
path=json.loads((b.parent/'revision10/approach_path.json').read_text())['points']
def wp(x,y,z):return unreal.Vector(o[0]-100*x,o[1]+100*y,o[2]+100*z)
def ground(x,y):
 i=math.floor(x);j=math.floor(y);u=x-i;v=y-j
 return (1-v)*((1-u)*grid[i,j]+u*grid[i+1,j])+v*((1-u)*grid[i,j+1]+u*grid[i+1,j+1])
def allowed(x,y,r=.6):
 if not (-65<x<70 and -69<y<66):return False
 if -48-r<x<-26+r and -68-r<y<-48+r:return False
 if -18-r<x<18+r and -21-r<y<10+r:return False
 if 18-r<x<40+r and -25-r<y<10+r:return False
 if 19-r<x<58+r and -11-r<y<31+r:return False
 if abs(x)<8+r and y>5:return False # moving cabin and uninterrupted valley view
 if min(math.hypot(x-p[0],y-p[1]) for p in path)<1.65+r:return False
 z=ground(x,y)
 return z>-78 and math.hypot(ground(x+.3,y)-ground(x-.3,y),ground(x,y+.3)-ground(x,y-.3))/.6<2.2
rng=random.Random(1709);seeds=[(-40,-43),(-20,-43),(-39,-29),(-16,-31),(-4,-26),(9,-26),(9,-35),(24,-32),(41,-32),(-27,-17),(-32,-7),(-33,4),(49,-25),(61,-10),(-22,17),(-38,22),(-20,34),(15,22),(28,38),(46,46)]
for idx in range(24,97,8):
 p=path[idx];q=path[idx+1];dx=q[0]-p[0];dy=q[1]-p[1];length=math.hypot(dx,dy)
 for side in [-1,1]:
  distance=rng.uniform(4.5,8);seeds.append((p[0]-dy/length*distance*side,p[1]+dx/length*distance*side))
centres=[]
for sx,sy in seeds:
 for j in range(5):
  x=sx+rng.uniform(-6,6);y=sy+rng.uniform(-5,5)
  if allowed(x,y,1.3) and all(math.hypot(x-cx,y-cy)>2.8 for cx,cy in centres):centres.append((x,y))
actors={a.get_actor_label():a for a in aa.get_all_level_actors()};plants=[];grass=[[] for i in range(4)];stones=[[] for i in range(4)]
for k,(x,y) in enumerate(centres):
 for j in range(2 if k%3==0 else 1):
  px=x+j*rng.uniform(-1.6,1.6);py=y+j*rng.uniform(-1.6,1.6)
  if not allowed(px,py,1.3):continue
  variant=rng.choice('DDCCC') if j==0 else 'D';species='Common_Hazel'
  if k%9==0 and j==0:species='Goat_Willow';variant='D'
  p=f'/Game/Megaplant_Library/Tree_{species}/Tree_{species}_01/SK_{species}_01_{variant}';mesh=lib.load_asset(p);assert mesh
  scale=rng.uniform(.72,1.12);z=ground(px,py)-.18;label=f'FR_Understorey_{k:03}_{j}'
  a=actors.get(label) or aa.spawn_actor_from_class(unreal.SkeletalMeshActor,wp(px,py,z));a.set_actor_label(label);a.set_folder_path('R12/ForestRefine/Understorey');a.set_actor_location(wp(px,py,z),False,True);a.set_actor_rotation(unreal.Rotator(yaw=rng.uniform(0,360)),False);a.set_actor_scale3d(unreal.Vector(scale,scale,scale));c=a.skeletal_mesh_component;c.set_skeletal_mesh_asset(mesh);c.set_collision_profile_name('NoCollision');c.set_editor_property('ld_max_draw_distance',13000.)
  plants.append({'label':label,'mesh':p,'local':[px,py,z],'scale':scale})
 for j in range(44):
  angle=rng.uniform(0,math.tau);rad=3.5*math.sqrt(rng.random());px=x+math.cos(angle)*rad;py=y+math.sin(angle)*rad
  if not allowed(px,py,.35):continue
  variant=rng.randrange(4);scale=rng.uniform(.75,1.7);z=ground(px,py)-.045
  grass[variant].append(unreal.Transform(location=wp(px,py,z),rotation=unreal.Rotator(yaw=rng.uniform(0,360)),scale=unreal.Vector(scale,scale,scale*rng.uniform(.75,1.0))))
 # Small stones occur in groups, mostly recessed, rather than isolated disks.
 if k%3==0:
  for j in range(6):
   px=x+rng.uniform(-1.2,1.2);py=y+rng.uniform(-1.2,1.2)
   if not allowed(px,py,.5):continue
   scale=rng.uniform(1.1,3.2);z=ground(px,py)-.035
   stones[rng.randrange(4)].append(unreal.Transform(location=wp(px,py,z),rotation=unreal.Rotator(pitch=rng.uniform(-10,10),yaw=rng.uniform(0,360),roll=rng.uniform(-10,10)),scale=unreal.Vector(scale,scale*.8,scale)))
counts={}
for kind,batches in [('Grass',grass),('Stone',stones)]:
 for i,transforms in enumerate(batches):
  letter='ABCD'[i];name=f'FT_Woodland_{kind}_{letter}';ft=lib.load_asset(root+'/Foliage/'+name) or at.create_asset(name,root+'/Foliage',unreal.FoliageType_InstancedStaticMesh,unreal.FoliageType_InstancedStaticMeshFactory())
  folder='Plants' if kind=='Grass' else 'Cover';mesh=lib.load_asset(f'/Game/MWLandscapeAutoMaterial/Meshes/{folder}/SM_MWAM_{kind}{letter}');assert mesh
  ft.set_editor_property('mesh',mesh);ft.set_editor_property('cull_distance',unreal.Int32Interval(min=8500,max=11500));lib.save_loaded_asset(ft)
  unreal.InstancedFoliageActor.remove_all_instances(w,ft);unreal.InstancedFoliageActor.add_instances(w,ft,transforms);counts[name]=len(transforms)
# Smaller trees break up the bare downhill silhouette; keep cabin centre open.
trees=[]
for i,(x,y) in enumerate([(-41,18),(-31,26),(-19,24),(-28,38),(-48,33),(-37,43),(17,25),(17,37),(29,43),(41,48),(55,42),(-50,-18),(-47,-4),(62,3),(-45,-34)]):
 if not allowed(x,y,2.2):continue
 species='European_Beech';v='CD'[i%2];p=f'/Game/Megaplant_Library/Tree_{species}/Tree_{species}_01/SK_{species}_01_{v}';mesh=lib.load_asset(p);scale=rng.uniform(.95,1.3);z=ground(x,y)-.045;label=f'FR_Slope_Tree_{i:02}'
 a=actors.get(label) or aa.spawn_actor_from_class(unreal.SkeletalMeshActor,wp(x,y,z));a.set_actor_label(label);a.set_folder_path('R12/ForestRefine/Trees');a.set_actor_location(wp(x,y,z),False,True);a.set_actor_rotation(unreal.Rotator(yaw=i*137),False);a.set_actor_scale3d(unreal.Vector(scale,scale,scale));a.skeletal_mesh_component.set_skeletal_mesh_asset(mesh);a.skeletal_mesh_component.set_collision_profile_name('NoCollision');trees.append({'label':label,'local':[x,y,z]})
# Mixed-age alder groups reinforce the wet forest along the raised path banks.
occupied=[(p['local'][0],p['local'][1]) for p in trees]
for a in actors.values():
 if isinstance(a,unreal.SkeletalMeshActor) and not a.get_actor_label().startswith('FR_'):
  p=a.get_actor_location();occupied.append(((o[0]-p.x)/100,(p.y-o[1])/100))
for idx in range(24,97,7):
 p=path[idx];q=path[idx+1];dx=q[0]-p[0];dy=q[1]-p[1];length=math.hypot(dx,dy)
 for side in [-1,1]:
  distance=rng.uniform(6,11);x=p[0]-dy/length*distance*side;y=p[1]+dx/length*distance*side
  if not allowed(x,y,2) or any(math.hypot(x-px,y-py)<2 for px,py in occupied):continue
  variant=rng.choice('BCDD');asset=f'/Game/Megaplant_Library/Tree_Black_Alder/Tree_Black_Alder_01/SK_Black_Alder_01_{variant}';mesh=lib.load_asset(asset);assert mesh
  scale=rng.uniform(.85,1.1);z=ground(x,y)-.22;label=f'FR_Black_Alder_{idx:03}_{side+1}'
  a=actors.get(label) or aa.spawn_actor_from_class(unreal.SkeletalMeshActor,wp(x,y,z));a.set_actor_label(label);a.set_folder_path('R12/ForestRefine/Alder');a.set_actor_location(wp(x,y,z),False,True);a.set_actor_rotation(unreal.Rotator(yaw=rng.uniform(0,360)),False);a.set_actor_scale3d(unreal.Vector(scale,scale,scale));c=a.skeletal_mesh_component;c.set_skeletal_mesh_asset(mesh);c.set_collision_profile_name('NoCollision');trees.append({'label':label,'local':[x,y,z],'mesh':asset});occupied.append((x,y))
assert ls.save_current_level();report={'seed':1709,'clusters':centres,'plants':plants,'foliage_counts':counts,'trees':trees,'saved':True};(out/'planting.json').write_text(json.dumps(report,indent=2));RESULT={'clusters':len(centres),'shrubs':len(plants),'trees':len(trees),'instances':sum(counts.values()),'saved':True}

"""Add visible crest and side forest layers; remove the rear landing intruder."""
import unreal,json,random,math,sys
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'gorge'/'density';out.mkdir(exist_ok=True)
sys.path.insert(0,str(Path(__file__).resolve().parent));from gorge_shape import lip
ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);actors=aa.get_all_level_actors();w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert w.get_name()=='Station_R12'
o=json.loads((b.parent/'working_level_report.json').read_text())['station_origin']
def local(p):return [(o[0]-p.x)/100,(p.y-o[1])/100,(p.z-o[2])/100]
def wp(x,y,z):return unreal.Vector(o[0]-100*x,o[1]+100*y,o[2]+100*z)
ground=[a for a in actors if isinstance(a,unreal.Landscape) or a.get_actor_label()=='VF10_Parking_Terrain'];ignore=[a for a in actors if a not in ground]
def floor(x,y):
 h=unreal.SystemLibrary.line_trace_single(w,wp(x,y,100),wp(x,y,-250),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,ignore,unreal.DrawDebugTrace.NONE,True)
 return local(h.to_tuple()[5])[2] if h else None
old=json.loads((out/'installation.json').read_text()) if (out/'installation.json').exists() else {}
removed=old.get('removed',[])
for a in actors:
 if a.get_actor_label() in {'FR_Black_Alder_080_2','FR_Understorey_087_0','FR_Understorey_087_1'}:
  p=local(a.get_actor_location());removed.append({'label':a.get_actor_label(),'position':p,'transform':str(a.get_actor_transform())})
  for proxy in actors:
   q=local(proxy.get_actor_location())
   if proxy.get_actor_label().startswith('FT_TrunkCollision_') and math.hypot(q[0]-p[0],q[1]-p[1])<.1:
    removed.append({'label':proxy.get_actor_label(),'position':q,'transform':str(proxy.get_actor_transform())});aa.destroy_actor(proxy)
  assert aa.destroy_actor(a)
# Conservative full-crown bounds keep additions clear of all station structures.
structures=[]
for a in aa.get_all_level_actors():
 if not isinstance(a,unreal.StaticMeshActor):continue
 m=a.static_mesh_component.static_mesh
 if not m or '/R12/Meshes/SM_R12_' not in m.get_path_name():continue
 bd=a.get_actor_bounds(False);c=local(bd[0]);e=[bd[1].x/100,bd[1].y/100,bd[1].z/100]
 structures.append((a.get_actor_label(),c,e))
existing=[]
for a in aa.get_all_level_actors():
 if isinstance(a,unreal.InstancedFoliageActor):
  for key,t in unreal.StationMigrationLibrary.get_foliage_instance_transforms(a).items():
   if 'Pine' in key and 'Density' not in key:existing.append(local(t.translation)[:2])
 elif isinstance(a,unreal.SkeletalMeshActor):
  bd=a.get_actor_bounds(False)
  if bd[1].z>300:existing.append(local(a.get_actor_location())[:2])
lib=unreal.EditorAssetLibrary;rng=random.Random(90814);fts=[];bds=[];groups=[[],[],[]];rows=[];rejected={}
for v in range(3):
 src=unreal.load_asset(f'/Game/MaldekRefinement/R06/Foliage/FT_R06_Pine_{v}')
 path=f'/Game/MaldekRefinement/R12/Gorge/Foliage/FT_Gorge_Density_{v}'
 ft=unreal.load_asset(path) or lib.duplicate_asset(src.get_path_name(),path)
 ft.set_editor_property('cull_distance',unreal.Int32Interval(min=30000,max=40000));lib.save_loaded_asset(ft)
 fts.append(ft);bds.append(ft.get_editor_property('mesh').get_bounds())
def plant(x,y,kind):
 if any(math.hypot(x-a,y-b)<(3.7 if kind=='crest' else 4.3) for a,b in existing):return
 z=floor(x,y)
 if z is None:return
 v=rng.randrange(3);bd=bds[v];base_h=2*bd.box_extent.z/100
 if kind=='crest':height=min(25,max(10,rng.uniform(3,9)-z))
 elif kind=='central':height=min(30,max(16,rng.uniform(-3,1)-z))
 else:height=rng.uniform(15,24)
 scale=height/base_h;radius=max(bd.box_extent.x,bd.box_extent.y)*scale/100
 if abs(x)<5 and z+height>1:height=max(4,1-z);scale=height/base_h;radius=max(bd.box_extent.x,bd.box_extent.y)*scale/100
 for label,c,e in structures:
  if abs(x-c[0])<e[0]+radius+1 and abs(y-c[1])<e[1]+radius+1 and z-.25<c[2]+e[2]+.6 and z+height>c[2]-e[2]-.6:
   rejected[label]=rejected.get(label,0)+1;return
 bottom=(bd.origin.z-bd.box_extent.z)*scale/100
 t=unreal.Transform(location=wp(x,y,z-bottom-.25),rotation=unreal.Rotator(yaw=rng.uniform(0,360)),scale=unreal.Vector(scale,scale,scale))
 groups[v].append(t);rows.append({'xy':[x,y],'ground':z,'top':z+height-.25,'height':height,'radius':radius,'variant':v,'kind':kind});existing.append([x,y])
# Broken, staggered near crowns above the first drop, including the gondola gap.
for x in range(-68,70,4):
 for d in [5.5,11.5]:plant(x+rng.uniform(-1.4,1.4),lip(x)+d+rng.uniform(-1.4,1.4),'crest')
for y in range(20,135,5):
 for x in [-6,0,6]:plant(x+rng.uniform(-1.5,1.5),y+rng.uniform(-1.8,1.8),'central')
# Side stands bridge the existing woodland to the descending forest.
for xmin,xmax in [(-78,-31),(40,95)]:
 for x in range(xmin,xmax,6):
  for y in range(-12,67,6):plant(x+rng.uniform(-2,2),y+rng.uniform(-2,2),'side')
for x in range(-76,89,6):
 for y in range(31,156,6):
  if rng.random()<.12:continue
  plant(x+rng.uniform(-2,2),y+rng.uniform(-2,2),'deep')
for ft,ts in zip(fts,groups):
 unreal.InstancedFoliageActor.remove_all_instances(w,ft);unreal.InstancedFoliageActor.add_instances(w,ft,ts)
assert ls.save_current_level()
RESULT={'saved':True,'added':len(rows),'removed':removed,'kinds':{k:sum(r['kind']==k for r in rows) for k in ['crest','central','side','deep']},'structure_rejections':rejected}
(out/'installation.json').write_text(json.dumps(dict(RESULT,trees=rows),indent=2))

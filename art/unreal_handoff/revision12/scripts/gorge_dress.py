"""Ground existing foliage locally and layer trees down the nighttime cliff."""
import unreal,json,math,random,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from gorge_shape import weight,lip
b=Path(__file__).resolve().parents[1];out=b/'gorge';root='/Game/MaldekRefinement/R12/Gorge'
ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert w.get_name()=='Station_R12'
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);actors=aa.get_all_level_actors();o=json.loads((b.parent/'working_level_report.json').read_text())['station_origin']
def local(p):return ((o[0]-p.x)/100,(p.y-o[1])/100,(p.z-o[2])/100)
def wp(x,y,z):return unreal.Vector(o[0]-x*100,o[1]+y*100,o[2]+z*100)
def affected(x,y):
 return weight(x,y)>0 or (-96<=x<=112 and -80<=y<=170 and min(x+96,112-x,y+80,170-y)<18)
terrain=[a for a in actors if isinstance(a,unreal.Landscape) or a.get_actor_label()=='VF10_Parking_Terrain'];ignore=[a for a in actors if a not in terrain]
def floor(x,y):
 hit=unreal.SystemLibrary.line_trace_single(w,wp(x,y,50),wp(x,y,-250),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,ignore,unreal.DrawDebugTrace.NONE,True)
 assert hit,(x,y)
 return local(hit.to_tuple()[5])[2]
moved=[]
for a in actors:
 x,y,z=local(a.get_actor_location())
 if not affected(x,y):continue
 if isinstance(a,unreal.SkeletalMeshActor):
  mesh=a.skeletal_mesh_component.get_editor_property('skeletal_mesh_asset')
  if not mesh or '/Megaplant_Library/' not in mesh.get_path_name():continue
 elif a.get_actor_label().startswith('FR_Outcrop_'):mesh=a.static_mesh_component.static_mesh
 else:continue
 # Existing placement burial is retained while terrain changes beneath it.
 bounds=a.get_actor_bounds(False);bottom=(bounds[0].z-bounds[1].z-a.get_actor_location().z)/100
 target=floor(x,y)-bottom-.22;a.set_actor_location(wp(x,y,target),False,True);moved.append(a.get_actor_label())
 for proxy in actors:
  if not proxy.get_actor_label().startswith('FT_TrunkCollision_'):continue
  px,py,pz=local(proxy.get_actor_location())
  if math.hypot(px-x,py-y)<.02:
   proxy.set_actor_location(wp(px,py,pz+target-z),False,True);moved.append(proxy.get_actor_label())
for a in actors:
 if not isinstance(a,unreal.InstancedFoliageActor):continue
 for key,t in unreal.StationMigrationLibrary.get_foliage_instance_transforms(a).items():
  x,y,z=local(t.translation)
  if not affected(x,y):continue
  ft,index=key.rsplit('|',1);asset=unreal.load_asset(ft);mesh=asset.get_editor_property('mesh');bd=mesh.get_bounds();bottom=(bd.origin.z-bd.box_extent.z)*t.scale3d.z/100
  assert unreal.StationMigrationLibrary.move_r12_foliage_instance(a,ft,int(index),t.translation,wp(x,y,floor(x,y)-bottom-.16))
rng=random.Random(708);lib=unreal.EditorAssetLibrary;at=unreal.AssetToolsHelpers.get_asset_tools();counts=[];positions=[]
for variant in range(3):
 source=unreal.load_asset(f'/Game/MaldekRefinement/R06/Foliage/FT_R06_Pine_{variant}');assert source
 path=root+f'/Foliage/FT_Gorge_Pine_{variant}';ft=unreal.load_asset(path) or lib.duplicate_asset(source.get_path_name(),path)
 ft.set_editor_property('cull_distance',unreal.Int32Interval(min=23000,max=30000));lib.save_loaded_asset(ft)
 mesh=ft.get_editor_property('mesh');bd=mesh.get_bounds();trans=[]
 for row in range(14):
  for col in range(19):
   if (row+col)%3!=variant or rng.random()<.23:continue
   x=-74+col*8+rng.uniform(-2.8,2.8);y=lip(x)+13+row*7+rng.uniform(-2,2)
   if x>72 or y>145 or abs(x)<9:continue
   if weight(x,y)<.65:continue
   z=floor(x,y);scale=rng.uniform(.65,1.05)
   # Upper canopy stays below the lip, making the descent legible from the deck.
   height=2*bd.box_extent.z/100*scale
   if z+height>-.8:scale*=max(.3,(-.8-z)/height)
   bottom=(bd.origin.z-bd.box_extent.z)/100*scale
   trans.append(unreal.Transform(location=wp(x,y,z-bottom-.3),rotation=unreal.Rotator(yaw=rng.uniform(0,360)),scale=unreal.Vector(scale,scale,scale)))
   positions.append([x,y,z])
 unreal.InstancedFoliageActor.remove_all_instances(w,ft);unreal.InstancedFoliageActor.add_instances(w,ft,trans);counts.append(len(trans))
# Embedded rock masses break up the steep face below the occupied station lip.
rocks=[]
bylabel={a.get_actor_label():a for a in actors}
def rock_actor(label,position):
 a=bylabel.get(label) or aa.spawn_actor_from_class(unreal.StaticMeshActor,position)
 a.set_actor_label(label);a.set_actor_location(position,False,True);a.set_folder_path('R12/Gorge/Rocks');return a
for i,x in enumerate(range(-27,18,6)):
 y=lip(x)+4+rng.uniform(-.7,.7);z=floor(x,y)
 mesh=unreal.load_asset('/Game/RockEnv_Pack/Meshes/Rocks/'+['SM_Rock_28','SM_Rock_20','SM_Rock_8'][i%3]);assert mesh
 bd=mesh.get_bounds();sx=800/(2*bd.box_extent.x);sy=600/(2*bd.box_extent.y);sz=1100/(2*bd.box_extent.z)
 top=min(-.65,z+3);anchor=top-(bd.origin.z+bd.box_extent.z)*sz/100
 a=rock_actor(f'Gorge_Foundation_Rock_{i:02}',wp(x,y,anchor));a.static_mesh_component.set_static_mesh(mesh);a.set_actor_scale3d(unreal.Vector(sx,sy,sz));a.static_mesh_component.set_collision_profile_name('BlockAll');rocks.append(a.get_actor_label())
for i,y in enumerate([-11,-6,-1,4]):
 mesh=unreal.load_asset('/Game/RockEnv_Pack/Meshes/Rocks/'+['SM_Rock_20','SM_Rock_28'][i%2]);bd=mesh.get_bounds();sc=unreal.Vector(330/(2*bd.box_extent.x),520/(2*bd.box_extent.y),420/(2*bd.box_extent.z));z=3.25-(bd.origin.z+bd.box_extent.z)*sc.z/100
 a=rock_actor(f'Gorge_Shoulder_Rock_{i:02}',wp(-25,y,z));a.static_mesh_component.set_static_mesh(mesh);a.set_actor_scale3d(sc);a.static_mesh_component.set_collision_profile_name('BlockAll');rocks.append(a.get_actor_label())
assert ls.save_current_level();RESULT={'saved':True,'existing_actors_grounded':moved,'new_trees':sum(counts),'rocks':rocks}
(out/'dressing.json').write_text(json.dumps({'result':RESULT,'tree_ground_positions':positions},indent=2))

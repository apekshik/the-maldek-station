"""Isolated R11 forest approach study; never modifies source meshes or source map."""
import unreal,json,math,random
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'forest_test';out.mkdir(exist_ok=True)
root='/Game/MaldekRefinement/ForestTest';map_path=root+'/Forest_Approach_Test'
lib=unreal.EditorAssetLibrary;aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);at=unreal.AssetToolsHelpers.get_asset_tools();ml=unreal.MaterialEditingLibrary
assert not levels.is_in_play_in_editor()
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
if world.get_name()!='Forest_Approach_Test':
 assert not lib.does_asset_exist(map_path),'Test already exists; open it instead of overwriting'
 assert levels.new_level_from_template(map_path,'/Game/MaldekRefinement/R11/BlockOut_R11')
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert world.get_name()=='Forest_Approach_Test'
origin=json.loads((out.parent/'working_level_report.json').read_text())['station_origin']
path=json.loads((out.parent/'revision10/approach_path.json').read_text())['points']
grid=json.loads((out/'terrain_grid.json').read_text())
def wp(p):return unreal.Vector(origin[0]-100*p[0],origin[1]+100*p[1],origin[2]+100*p[2])
def ground(x,y):
 i=round(x-grid['xmin']);j=round(y-grid['ymin'])
 return grid['vertices'][j*grid['nx']+i][2] if 0<=i<grid['nx'] and 0<=j<len(grid['vertices'])//grid['nx'] else None
def dist(x,y):return min(math.hypot(x-p[0],y-p[1]) for p in path)
def mark(a,label):a.set_actor_label('FT_'+label);a.set_folder_path('ForestTest');return a
# Local material overrides, leaving all R11/R10 shared materials intact.
def material(name,color,emissive=False):
 m=lib.load_asset(root+'/Materials/'+name) or at.create_asset(name,root+'/Materials',unreal.Material,unreal.MaterialFactoryNew())
 ml.delete_all_material_expressions(m)
 c=ml.create_material_expression(m,unreal.MaterialExpressionConstant3Vector);c.constant=unreal.LinearColor(*color,1)
 ml.connect_material_property(c,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR if emissive else unreal.MaterialProperty.MP_BASE_COLOR)
 r=ml.create_material_expression(m,unreal.MaterialExpressionConstant);r.r=.93;ml.connect_material_property(r,'',unreal.MaterialProperty.MP_ROUGHNESS)
 ml.recompile_material(m);lib.save_loaded_asset(m);return m
metal=lib.load_asset('/Game/MaldekRefinement/Materials/M_R04_Painted_Charcoal')
lens=material('M_Path_Marker',(1.2,.65,.22),True)
# Reuse authored gravel shader on this actor only, preserving texture breakup.
approach=next(a for a in aa.get_all_level_actors() if a.get_actor_label()=='R10_Forest_Approach')
approach.static_mesh_component.set_material(0,lib.load_asset('/Game/MaldekRefinement/R05/Materials/M_R03_Wet_Gravel'))
# Replace only the immediate study corridor's placeholder pines, retaining the distant forest.
for old in aa.get_all_level_actors():
 if old.get_actor_label().startswith('FT_'):aa.destroy_actor(old)
removed=0
for a in aa.get_all_level_actors():
 for c in a.get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent):
  mesh=c.static_mesh
  if not mesh or not mesh.get_name().startswith('SM_R06_Pine_'):continue
  keep=[]
  for i in range(c.get_instance_count()):
   t=c.get_instance_transform(i,True);x=(origin[0]-t.translation.x)/100;y=(t.translation.y-origin[1])/100
   if dist(x,y)<13 and y<-21:removed+=1
   else:keep.append(t)
  ft=lib.load_asset('/Game/MaldekRefinement/R06/Foliage/FT_R06_Pine_'+mesh.get_name()[-1])
  unreal.InstancedFoliageActor.remove_all_instances(world,ft);unreal.InstancedFoliageActor.add_instances(world,ft,keep)
rng=random.Random(709);placed=[];assets={}
for species in ['European_Beech','Goat_Willow','European_Aspen']:
 for v in 'ABCD':assets[species,v]=lib.load_asset(f'/Game/Megaplant_Library/Tree_{species}/Tree_{species}_01/SK_{species}_01_{v}')
# Sample clusters to the sides, preserving the 2.5m walking strip and parking footprint.
for i in range(120):
 idx=rng.randrange(8,88);p=path[idx];q=path[idx+1];dx=q[0]-p[0];dy=q[1]-p[1];length=math.hypot(dx,dy);side=rng.choice([-1,1]);offset=rng.uniform(4.2,13)
 x=p[0]-dy/length*offset*side+rng.uniform(-1.8,1.8);y=p[1]+dx/length*offset*side+rng.uniform(-1.8,1.8)
 z=ground(x,y)
 if z is None or z<-5 or y>-21 or dist(x,y)<3.5 or (-42<x<-30 and -65<y<-55):continue
 if any(math.hypot(x-r['x'],y-r['y'])<2.5 for r in placed):continue
 species='Goat_Willow' if offset<6.5 else ('European_Aspen' if rng.random()<.23 else 'European_Beech')
 v=rng.choice('CD' if species=='Goat_Willow' else 'ABBCD');s=rng.uniform(.82,1.12)
 a=mark(aa.spawn_actor_from_class(unreal.SkeletalMeshActor,wp((x,y,z-.03)),unreal.Rotator(yaw=rng.uniform(0,360))),f'{species}_{len(placed):03d}')
 c=a.skeletal_mesh_component;c.set_skeletal_mesh_asset(assets[species,v]);c.set_collision_profile_name('NoCollision');a.set_actor_scale3d(unreal.Vector(s,s,s))
 placed.append({'x':x,'y':y,'z':z,'species':species,'variant':v,'scale':s})
 if len(placed)>=58:break
# Real scanned rock/soil patches tuck into the shoulders rather than cover the walking surface.
rockpaths=[p for p in lib.list_assets('/Game/Fab/Megascans/3D',True,False) if '/StaticMeshes/' in p and 'Ground_Patch_Rock' in p]
rocks=0
if rockpaths:
 rock=lib.load_asset(rockpaths[0])
 for i in range(28):
  p=path[rng.randrange(7,90)];x=p[0]+rng.uniform(-5,5);y=p[1]+rng.uniform(-5,5);z=ground(x,y)
  if z is None or not 1.8<dist(x,y)<5 or y>-21:continue
  a=mark(aa.spawn_actor_from_class(unreal.StaticMeshActor,wp((x,y,z-.025)),unreal.Rotator(yaw=rng.uniform(0,360))),f'RockPatch_{rocks:02d}');a.static_mesh_component.set_static_mesh(rock);a.static_mesh_component.set_collision_profile_name('NoCollision');s=rng.uniform(.6,1.1);a.set_actor_scale3d(unreal.Vector(s,s,s));rocks+=1
cube=lib.load_asset('/Engine/BasicShapes/Cube')
def box(name,p,s,mat):
 a=mark(aa.spawn_actor_from_class(unreal.StaticMeshActor,wp(p)),name);a.static_mesh_component.set_static_mesh(cube);a.static_mesh_component.set_material(0,mat);a.static_mesh_component.set_collision_profile_name('NoCollision');a.set_actor_scale3d(unreal.Vector(*s));return a
for n,idx in enumerate([3,22,42,61,80,99]):
 p=path[idx];q=path[idx+1];dx=q[0]-p[0];dy=q[1]-p[1];l=math.hypot(dx,dy);x=p[0]-dy/l*1.65;y=p[1]+dx/l*1.65;z=ground(x,y)
 box(f'Marker_{n}_Post',(x,y,z+.45),(.09,.09,.9),metal)
 box(f'Marker_{n}_Cap',(x,y,z+.91),(.17,.17,.06),metal)
 box(f'Marker_{n}_Lens',(x,y,z+.83),(.105,.105,.055),lens)
 a=mark(aa.spawn_actor_from_class(unreal.SpotLight,wp((x,y,z+.83)),unreal.MathLibrary.find_look_at_rotation(wp((x,y,z+.83)),wp((p[0],p[1],p[2])))),f'Marker_{n}_Light')
 c=a.light_component;c.set_intensity_units(unreal.LightUnits.LUMENS);c.set_intensity(.07);c.set_attenuation_radius(420);c.set_inner_cone_angle(25);c.set_outer_cone_angle(65);c.set_temperature(3200);c.set_editor_property('use_temperature',True);c.set_editor_property('volumetric_scattering_intensity',.01);c.set_editor_property('cast_shadows',False)
unreal.EditorLevelLibrary.set_level_viewport_camera_info(wp((-36,-58.8,.65)),unreal.MathLibrary.find_look_at_rotation(wp((-36,-58.8,.65)),wp((-29,-53,.5))))
assert levels.save_current_level()
(out/'build.json').write_text(json.dumps({'map':map_path,'trees':placed,'rocks':rocks,'markers':6,'placeholder_pines_removed':removed,'source_map_untouched':True},indent=2))



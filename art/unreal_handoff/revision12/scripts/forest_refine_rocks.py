"""Seat imported geology in bank clusters with explicit route clearance."""
import unreal,json,math,random
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'forest_refine';aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
o=json.loads((b.parent/'working_level_report.json').read_text())['station_origin'];grid={(x,y):z for x,y,z in json.loads((out/'terrain_grid.json').read_text())['vertices']};path=json.loads((b/'forest_arrival_alignment.json').read_text())['path']
def ground(x,y):
 i=math.floor(x);j=math.floor(y);u=x-i;v=y-j
 return (1-v)*((1-u)*grid[i,j]+u*grid[i+1,j])+v*((1-u)*grid[i,j+1]+u*grid[i+1,j+1])
def wp(x,y,z):return unreal.Vector(o[0]-100*x,o[1]+100*y,o[2]+100*z)
actors={a.get_actor_label():a for a in aa.get_all_level_actors()};rng=random.Random(1711);rows=[]
centres=[(-42,-45),(-39,-34),(-21,-42),(-20,-32),(-31,-14),(-32,-3),(-30,13),(-22,28),(16,-32),(43,-32),(54,-24),(60,8),(-43,-64),(-46,-57),(-44,-51),(-29,-65),(-28,-53)]
for k,(cx,cy) in enumerate(centres):
 for j in range(3 if k<12 else 2):
  width=rng.uniform(1.5,2.6) if j==0 else rng.uniform(.65,1.15);x=cx+(0 if j==0 else rng.uniform(-1.6,1.6));y=cy+(0 if j==0 else rng.uniform(-1.3,1.3));radius=width*.72
  if min(math.hypot(x-p[0],y-p[1]) for p in path)<2.0+radius:continue
  name=['SM_Rock_28','SM_Rock_20','SM_Rock_8','SM_Rock_12'][k%4] if j==0 else ['SM_Small_Rock_2','SM_Small_Rock_5'][j%2]
  folder='Small_Rocks' if 'Small' in name else 'Rocks';asset=f'/Game/RockEnv_Pack/Meshes/{folder}/{name}';mesh=unreal.load_asset(asset);assert mesh
  bd=mesh.get_bounds();scale=width*100/max(2*bd.box_extent.x,2*bd.box_extent.y);label=f'FR_Outcrop_{k:02}_{j}'
  a=actors.get(label) or aa.spawn_actor_from_class(unreal.StaticMeshActor,wp(x,y,0));a.set_actor_label(label);a.set_folder_path('R12/ForestRefine/Rocks');a.static_mesh_component.set_static_mesh(mesh);a.set_actor_scale3d(unreal.Vector(scale,scale,scale));a.set_actor_rotation(unreal.Rotator(yaw=rng.uniform(0,360)),False);a.set_actor_location(wp(x,y,0),False,True)
  bounds=a.get_actor_bounds(False);bottom=(bounds[0].z-bounds[1].z-a.get_actor_location().z)/100;h=2*bounds[1].z/100
  # Sample across the footprint and sink the base into its low side.
  g=min(ground(x+math.cos(t)*width*.34,y+math.sin(t)*width*.34) for t in [0,math.pi*.5,math.pi,math.pi*1.5]);z=g-bottom-h*.20
  a.set_actor_location(wp(x,y,z),False,True);a.static_mesh_component.set_collision_profile_name('BlockAll');a.static_mesh_component.set_editor_property('ld_max_draw_distance',18000.)
  rows.append({'label':label,'mesh':asset,'local':[x,y,z],'width_m':width,'scale':scale,'base_burial_m':h*.20})
assert len(rows)>=30
old=actors.get('VF10_Parking_Rock_Clusters')
if old:old.static_mesh_component.set_static_mesh(None);old.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
assert ls.save_current_level();RESULT={'rocks':len(rows),'saved':True,'retired_parking_study':bool(old)};(out/'rocks'/'placement.json').write_text(json.dumps({'summary':RESULT,'placements':rows},indent=2))

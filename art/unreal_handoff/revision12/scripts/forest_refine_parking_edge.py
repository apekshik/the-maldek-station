"""Close the exposed parking perimeter with grounded trees and understorey."""
import unreal,json,math,random
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'forest_refine';aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
o=json.loads((b.parent/'working_level_report.json').read_text())['station_origin'];g={(x,y):z for x,y,z in json.loads((out/'terrain_grid.json').read_text())['vertices']};actors={a.get_actor_label():a for a in aa.get_all_level_actors()};rng=random.Random(1713);rows=[]
def ground(x,y):
 i=math.floor(x);j=math.floor(y);u=x-i;v=y-j
 return (1-v)*((1-u)*g[i,j]+u*g[i+1,j])+v*((1-u)*g[i,j+1]+u*g[i+1,j+1])
centres=[(-47,-63),(-48,-57),(-47,-52),(-44,-68),(-39,-68.5),(-34,-68),(-29,-67),(-26,-63),(-26,-57),(-28,-51)]
for i,(x,y) in enumerate(centres):
 for j in range(3):
  px=x+(rng.uniform(-1.4,1.4) if j else 0);py=y+(rng.uniform(-1.3,1.3) if j else 0)
  species='Black_Alder' if j==0 and i%3 else 'European_Beech' if j==0 else 'Common_Hazel';variant='B' if j==0 else 'C';scale=rng.uniform(.95,1.25) if j==0 else rng.uniform(.9,1.3)
  asset=f'/Game/Megaplant_Library/Tree_{species}/Tree_{species}_01/SK_{species}_01_{variant}';mesh=unreal.load_asset(asset);assert mesh
  bd=mesh.get_bounds();bottom=(bd.origin.z-bd.box_extent.z)*scale;z=ground(px,py)-(bottom+22)/100;label=f'FR_Parking_Edge_{i:02}_{j}';p=unreal.Vector(o[0]-100*px,o[1]+100*py,o[2]+100*z)
  a=actors.get(label) or aa.spawn_actor_from_class(unreal.SkeletalMeshActor,p);a.set_actor_label(label);a.set_folder_path('R12/ForestRefine/ParkingEdge');a.set_actor_location(p,False,True);a.set_actor_rotation(unreal.Rotator(yaw=rng.uniform(0,360)),False);a.set_actor_scale3d(unreal.Vector(scale,scale,scale));c=a.skeletal_mesh_component;c.set_skeletal_mesh_asset(mesh);c.set_collision_profile_name('NoCollision');c.set_editor_property('ld_max_draw_distance',14000.)
  rows.append({'label':label,'mesh':asset,'local':[px,py,z],'base_burial_cm':22})
assert ls.save_current_level();RESULT={'trees':10,'shrubs':20,'saved':True};(out/'parking_edge.json').write_text(json.dumps({'summary':RESULT,'plants':rows},indent=2))

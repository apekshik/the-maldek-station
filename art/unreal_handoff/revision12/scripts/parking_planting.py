"""Deterministic grass clumps anchored to rock groups, with clear circulation."""
import unreal,json,random,math
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'parking'
ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);actors={a.get_actor_label():a for a in aa.get_all_level_actors()}
o=json.loads((b.parent/'working_level_report.json').read_text())['station_origin'];grid={(x,y):z for x,y,z in json.loads((out/'terrain_grid.json').read_text())['vertices']}
def ground(x,y):
 x0=math.floor(x);y0=math.floor(y);u=x-x0;v=y-y0
 return (1-v)*((1-u)*grid[x0,y0]+u*grid[x0+1,y0])+v*((1-u)*grid[x0,y0+1]+u*grid[x0+1,y0+1])
def wp(x,y,z):return unreal.Vector(o[0]-x*100,o[1]+y*100,o[2]+z*100)
meshes=[unreal.load_asset('/Game/MWLandscapeAutoMaterial/Meshes/Plants/SM_MWAM_Grass'+c) for c in 'ABCD'];assert all(meshes)
rng=random.Random(1010);rows=[]
for k,(cx,cy) in enumerate([(-46,-61),(-45.8,-55),(-41.5,-50.5),(-31,-65.1),(-28.5,-61.5)]):
 for j in range(14):
  angle=rng.uniform(0,math.tau);radius=rng.uniform(.55,1.75);x=cx+math.cos(angle)*radius;y=cy+math.sin(angle)*radius
  if -45.35<x<-29.15 and -64.85<y<-51.15:continue
  mesh=meshes[(k+j)%4];bounds=mesh.get_bounds();scale=rng.uniform(45,85)/max(bounds.box_extent.x,bounds.box_extent.y)
  z=ground(x,y)-(bounds.origin.z-bounds.box_extent.z)*scale/100-.025
  label=f'VF10_Parking_Grass_{k:02}_{j:02}';a=actors.get(label) or aa.spawn_actor_from_class(unreal.StaticMeshActor,wp(x,y,z),unreal.Rotator(yaw=rng.uniform(0,360)))
  a.set_actor_label(label);a.set_actor_location(wp(x,y,z),False,True);a.set_actor_scale3d(unreal.Vector(scale,scale,scale));a.set_folder_path('R12/Parking/Planting')
  c=a.static_mesh_component;c.set_static_mesh(mesh);c.set_collision_profile_name('NoCollision');c.set_editor_property('ld_max_draw_distance',8000.)
  rows.append({'actor':a.get_path_name(),'mesh':mesh.get_path_name(),'position':[x,y,z],'scale':scale})
moves=[]
# Exact audited conflicts, including the separate collision proxy for the old beech.
for label,x,y in [('FT_European_Beech_022',-46.8,-52.8),('FT_TrunkCollision_16',-46.8,-52.8),('FT_RockPatch_04',-33,-65.1)]+[(f'FT_Marker_0_{part}',-31.2,-59) for part in ['Post','Cap','Lens','Light']]:
 a=actors[label];before=a.get_actor_location();audit=next(r for r in json.loads((out/'live_before.json').read_text())['actors'] if r['label']==label)
 oldx,oldy=audit['source_xy'];oldz=(audit['location'][2]-o[2])/100
 baseline={(px,py):pz for px,py,pz in json.loads((b.parent/'revision13/terrain_grid.json').read_text())['vertices']}
 dz=oldz-baseline.get((round(oldx),round(oldy)),oldz)
 target=wp(x,y,ground(x,y)+dz);a.set_actor_location(target,False,True);moves.append({'label':label,'before':audit['location'],'after':[target.x,target.y,target.z]})
trees=[]
for i,(species,variant,x,y,scale) in enumerate([('Goat_Willow','C',-47,-57,.85),('Goat_Willow','D',-28,-63,.9),('European_Aspen','B',-43.5,-49.5,.85),('European_Beech','A',-47.8,-62,.85)]):
 p=f'/Game/Megaplant_Library/Tree_{species}/Tree_{species}_01/SK_{species}_01_{variant}';mesh=unreal.load_asset(p);assert mesh,p
 label=f'VF10_Parking_Tree_{i:02}';a=actors.get(label) or aa.spawn_actor_from_class(unreal.SkeletalMeshActor,wp(x,y,ground(x,y)-.03),unreal.Rotator(yaw=i*97))
 a.set_actor_label(label);a.set_actor_location(wp(x,y,ground(x,y)-.03),False,True);a.set_actor_scale3d(unreal.Vector(scale,scale,scale));a.set_folder_path('R12/Parking/Planting');c=a.skeletal_mesh_component;c.set_skeletal_mesh_asset(mesh);c.set_collision_profile_name('NoCollision')
 trees.append({'actor':a.get_path_name(),'mesh':p,'position':[x,y,ground(x,y)],'scale':scale})
assert ls.save_current_level();(out/'planting.json').write_text(json.dumps({'grass':rows,'trees':trees,'moves':moves,'seed':1010,'clearance_envelope':[-45.35,-29.15,-64.85,-51.15]},indent=2));RESULT={'grass_clumps':len(rows),'trees':len(trees),'saved':True}

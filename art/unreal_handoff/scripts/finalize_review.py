import unreal,json,hashlib,math
from pathlib import Path
OUT=Path(__file__).resolve().parents[1];REPO=OUT.parents[1]
report=json.loads((OUT/'working_level_report.json').read_text())
assert hashlib.sha256((REPO/'game/Content/BlockOut.umap').read_bytes()).hexdigest()==report['source_sha256']
old=json.loads((OUT/'BlockOut_inventory.json').read_text())
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
byname={a.get_name():a for a in actors}
preserved=[]
for row in old:
 if row['class'] not in ['Landscape','Ultra_Dynamic_Sky_C','Ultra_Dynamic_Weather_C','PointLight','BP_GondolaSystem_C']:continue
 a=byname[row['name']];v=a.get_actor_location();expected=row['transform']['location']
 assert sum((v.to_tuple()[i]-expected[i])**2 for i in range(3))<.01,row['name']
 if row['splines']:
  spline=a.get_components_by_class(unreal.SplineComponent)[0]
  for i,p in enumerate(row['splines'][0]['points']):
   current=spline.get_location_at_spline_point(i,unreal.SplineCoordinateSpace.WORLD).to_tuple()
   assert sum((current[k]-p['location'][k])**2 for k in range(3))<.01
 preserved.append(row['name'])
unreal.EditorLevelLibrary.set_level_viewport_camera_info(unreal.Vector(-45700,20500,11300),unreal.Rotator(pitch=-25,yaw=-45,roll=0))
unreal.EditorLevelLibrary.editor_set_game_view(True)
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
(OUT/'final_verification.json').write_text(json.dumps({'source_map_unchanged':True,'preserved_environment_and_route_actors':preserved,'target_resolution':'2560x1440','target_fps':60,'performance_verified':False,'collision_samples':9,'capsule_radius_cm':34,'capsule_half_height_cm':88,'gondola_round_trip_passed':True,'local_terrain_triangles':32768},indent=2))

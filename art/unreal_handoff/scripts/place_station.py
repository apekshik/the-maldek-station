import unreal,json,hashlib
from pathlib import Path
OUT=Path(__file__).resolve().parents[1];REPO=OUT.parents[1]
ROOT='/Game/MaldekRefinement';MAP=ROOT+'/Maps/BlockOut_R04'
source_file=REPO/'game/Content/BlockOut.umap';source_hash=hashlib.sha256(source_file.read_bytes()).hexdigest()
manifest=json.loads((OUT/'export_manifest.json').read_text())
assetlib=unreal.EditorAssetLibrary
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert levels.load_level(MAP)
unreal.log('R04_PHASE loaded')
original=list(actors.get_all_level_actors())
controller=next(a for a in original if a.get_class().get_name()=='BP_GondolaSystem_C')
spline=controller.get_components_by_class(unreal.SplineComponent)[0]
carrier=next(c for c in controller.get_components_by_class(unreal.StaticMeshComponent) if c.get_name()=='GondolaMesh')
start=spline.get_location_at_distance_along_spline(0,unreal.SplineCoordinateSpace.WORLD)
rotation=spline.get_rotation_at_distance_along_spline(0,unreal.SplineCoordinateSpace.WORLD)
# Blender (x,y,z) maps to UE (x,-y,z)*100; yaw 180 makes the outbound route +Y.
floor=10298.5
origin=unreal.Vector(start.x,start.y-805,floor-400)
yaw=unreal.Rotator(pitch=0,yaw=180,roll=0)
legacy=[a for a in original if a.get_class().get_name()=='StaticMeshActor']
assert len(legacy)==218 and not any(a.get_actor_label().startswith('R04_') for a in legacy),'Expected untouched duplicate of original BlockOut'
report={'map':MAP,'source_sha256':source_hash,'legacy_removed':[a.get_name() for a in legacy],'station_origin':[origin.x,origin.y,origin.z],'station_yaw':180,'spawned':[],'preserved':[{'name':a.get_name(),'class':a.get_class().get_name()} for a in original if a not in legacy]}
unreal.log('R04_PHASE destroying old actors')
for a in legacy:assert actors.destroy_actor(a)
unreal.log('R04_PHASE old actors removed')
carrier.set_visibility(False,False);carrier.set_hidden_in_game(True,False);carrier.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
carrier.set_world_scale3d(unreal.Vector(1,1,1));carrier.set_world_location_and_rotation(start,rotation,False,True)
for row in manifest['chunks']:
 mesh=assetlib.load_asset(ROOT+'/Meshes/'+row['name'])
 p=row['pivot'];loc=unreal.Vector(origin.x-p[0]*100,origin.y+p[1]*100,origin.z+p[2]*100)
 a=actors.spawn_actor_from_class(unreal.StaticMeshActor,loc,yaw)
 a.set_actor_label(row['name'].replace('SM_R04_','R04_'));a.set_folder_path('R04_Station')
 component=a.static_mesh_component
 component.set_mobility(unreal.ComponentMobility.MOVABLE if row['collection']=='12_Gondola' else unreal.ComponentMobility.STATIC)
 component.set_static_mesh(mesh);component.set_collision_profile_name('BlockAll')
 if row['collection']=='12_Gondola':
  assert a.attach_to_component(carrier,'',unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,False)
 report['spawned'].append({'label':a.get_actor_label(),'asset':mesh.get_path_name(),'location':[loc.x,loc.y,loc.z]})
player=next(a for a in original if a.get_class().get_name()=='PlayerStart')
player.set_actor_location_and_rotation(unreal.Vector(origin.x+650,origin.y+300,floor+100),unreal.Rotator(pitch=0,yaw=135,roll=0),False,True)
camera=next(a for a in original if a.get_class().get_name()=='CineCameraActor')
camera.set_actor_location_and_rotation(unreal.Vector(origin.x-2200,origin.y+2600,floor+1400),unreal.Rotator(pitch=-25,yaw=-45,roll=0),False,True)
# Viewport set during visual review.
assert levels.save_current_level()
assert hashlib.sha256(source_file.read_bytes()).hexdigest()==source_hash,'Source map changed unexpectedly'
(OUT/'working_level_report.json').write_text(json.dumps(report,indent=2))
unreal.log('R04_WORKING_LEVEL_COMPLETE '+MAP)



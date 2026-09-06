"""Build a reversible R04 integration map; never save the source BlockOut map."""
import unreal,json,hashlib
from pathlib import Path
unreal.EditorPythonScripting.set_keep_python_script_alive(True)
import runpy
runpy.run_path(str(Path(__file__).with_name('review_session.py')))
OUT=Path(__file__).resolve().parents[1];REPO=OUT.parents[1]
ROOT='/Game/MaldekRefinement';MAP=ROOT+'/Maps/BlockOut_R04'
assert not unreal.EditorAssetLibrary.does_asset_exist(MAP),'Working map exists; do not overwrite manual review edits.'
source_file=REPO/'game/Content/BlockOut.umap'
source_hash=hashlib.sha256(source_file.read_bytes()).hexdigest()
manifest=json.loads((OUT/'export_manifest.json').read_text())
assetlib=unreal.EditorAssetLibrary;at=unreal.AssetToolsHelpers.get_asset_tools();ml=unreal.MaterialEditingLibrary
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
materials={}
for name,row in manifest['materials'].items():
 path=ROOT+'/Materials/M_'+name
 mat=assetlib.load_asset(path) if assetlib.does_asset_exist(path) else at.create_asset('M_'+name,ROOT+'/Materials',unreal.Material,unreal.MaterialFactoryNew())
 ml.delete_all_material_expressions(mat)
 color=ml.create_material_expression(mat,unreal.MaterialExpressionConstant3Vector,-400,0)
 color.constant=unreal.LinearColor(*row['color'])
 ml.connect_material_property(color,'',unreal.MaterialProperty.MP_BASE_COLOR)
 for prop,val,y in [(unreal.MaterialProperty.MP_METALLIC,row['metallic'],180),(unreal.MaterialProperty.MP_ROUGHNESS,row['roughness'],280)]:
  node=ml.create_material_expression(mat,unreal.MaterialExpressionConstant,-400,y);node.r=val;ml.connect_material_property(node,'',prop)
 for tex in row['textures']:
  if '_diff_' not in tex['name']:continue
  f=REPO/'art/blender/revision_02/assets'/tex['name']
  if not f.exists():continue
  tp=ROOT+'/Textures/'+f.stem
  if not assetlib.does_asset_exist(tp):
   task=unreal.AssetImportTask();task.filename=str(f);task.destination_path=ROOT+'/Textures';task.automated=True;task.save=True;at.import_asset_tasks([task])
  node=ml.create_material_expression(mat,unreal.MaterialExpressionTextureSample,-650,-200);node.texture=assetlib.load_asset(tp)
  ml.connect_material_property(node,'RGB',unreal.MaterialProperty.MP_BASE_COLOR)
 if row['transmission']>.5:
  mat.set_editor_property('blend_mode',unreal.BlendMode.BLEND_TRANSLUCENT);mat.set_editor_property('two_sided',True)
  node=ml.create_material_expression(mat,unreal.MaterialExpressionConstant,-400,400);node.r=.18;ml.connect_material_property(node,'',unreal.MaterialProperty.MP_OPACITY)
 ml.recompile_material(mat);assetlib.save_loaded_asset(mat);materials[name]=mat

for row in manifest['chunks']:
 mesh=assetlib.load_asset(ROOT+'/Meshes/'+row['name'])
 assert mesh,'Missing '+row['name']
 for i,slot in enumerate(mesh.static_materials):
  name=str(slot.material_slot_name)
  assert name in materials,'Unmapped material '+name
  mesh.set_material(i,materials[name])
 assetlib.save_loaded_asset(mesh)

assert not assetlib.does_asset_exist(MAP),'Working map already exists; inspect before rebuilding.'
assert levels.new_level_from_template(MAP,'/Game/BlockOut'),'Could not duplicate source level'
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
report={'map':MAP,'source_sha256':source_hash,'legacy_removed':[a.get_name() for a in legacy],'station_origin':[origin.x,origin.y,origin.z],'station_yaw':180,'spawned':[],'preserved':[{'name':a.get_name(),'class':a.get_class().get_name()} for a in original if a not in legacy]}
for a in legacy:assert actors.destroy_actor(a)
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
unreal.EditorLevelLibrary.set_level_viewport_camera_info(camera.get_actor_location(),camera.get_actor_rotation())
assert levels.save_current_level()
assert hashlib.sha256(source_file.read_bytes()).hexdigest()==source_hash,'Source map changed unexpectedly'
(OUT/'working_level_report.json').write_text(json.dumps(report,indent=2))
unreal.log('R04_WORKING_LEVEL_COMPLETE '+MAP)


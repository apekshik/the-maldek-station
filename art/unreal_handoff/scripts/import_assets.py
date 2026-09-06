import unreal,json
from pathlib import Path
OUT=Path(__file__).resolve().parents[1]
ROOT='/Game/MaldekRefinement'
assets=unreal.AssetToolsHelpers.get_asset_tools()
unreal.SystemLibrary.execute_console_command(None,'Interchange.FeatureFlags.Import.FBX 0')
tasks=[]
for f in sorted((OUT/'fbx').glob('*.fbx')):
 task=unreal.AssetImportTask();task.filename=str(f);task.destination_path=ROOT+'/Meshes';task.destination_name=f.stem
 task.automated=True;task.save=True;task.replace_existing=True
 opt=unreal.FbxImportUI();opt.import_mesh=True;opt.import_textures=False;opt.import_materials=False;opt.import_as_skeletal=False
 opt.automated_import_should_detect_type=False;opt.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
 data=opt.static_mesh_import_data;data.combine_meshes=True;data.auto_generate_collision=False;data.one_convex_hull_per_ucx=True
 data.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS
 data.generate_lightmap_u_vs=False;data.convert_scene=True;data.convert_scene_unit=True
 task.options=opt;tasks.append(task)
assets.import_asset_tasks([t for t in tasks if t.destination_name=='SM_R04_13_Roofs' or not unreal.EditorAssetLibrary.does_asset_exist(ROOT+'/Meshes/'+t.destination_name)])
report=[]
sub=unreal.get_default_object(unreal.StaticMeshEditorSubsystem)
for t in tasks:
 for path in [ROOT+'/Meshes/'+t.destination_name]:
  mesh=unreal.load_asset(path)
  if not isinstance(mesh,unreal.StaticMesh):continue
  b=mesh.get_bounds()
  report.append({'path':path,'center':[b.origin.x,b.origin.y,b.origin.z],'extent':[b.box_extent.x,b.box_extent.y,b.box_extent.z],'materials':[str(s.material_slot_name) for s in mesh.static_materials],'collision_hulls':sub.get_convex_collision_count(mesh),'lods':mesh.get_num_lods()})
(OUT/'import_report.json').write_text(json.dumps(report,indent=2))
(OUT/'api_notes.txt').write_text('\n\n'.join(str(getattr(unreal.Actor,n).__doc__) for n in ['attach_to_component','set_actor_location_and_rotation'])+'\n'+str(unreal.SceneComponent.set_world_location_and_rotation.__doc__))
unreal.log('R04_IMPORT_COMPLETE '+str(len(report)))




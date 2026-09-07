import unreal,json
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'revision10';root='/Game/MaldekRefinement/R10';lib=unreal.EditorAssetLibrary;at=unreal.AssetToolsHelpers.get_asset_tools();aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert world.get_name()=='BlockOut_R10'
origin=json.loads((out.parent/'working_level_report.json').read_text())['station_origin']
unreal.SystemLibrary.execute_console_command(None,'Interchange.FeatureFlags.Import.FBX 0')
report=[]
for f in (out/'fbx').glob('*.fbx'):
 if 'OrientationProbe' in f.name:continue
 task=unreal.AssetImportTask();task.filename=str(f);task.destination_path=root+'/Meshes';task.automated=True;task.save=True;task.replace_existing=True
 opt=unreal.FbxImportUI();opt.import_mesh=True;opt.import_materials=False;opt.import_textures=False;opt.automated_import_should_detect_type=False;opt.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
 d=opt.static_mesh_import_data;d.combine_meshes=True;d.auto_generate_collision=False;d.convert_scene=True;d.convert_scene_unit=True;d.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS;task.options=opt;at.import_asset_tasks([task]);mesh=lib.load_asset(root+'/Meshes/'+f.stem);assert mesh
 for i,s in enumerate(mesh.static_materials):
  m=lib.load_asset('/Game/MaldekRefinement/Materials/M_'+str(s.material_slot_name))
  if not m:m=lib.load_asset('/Game/MaldekRefinement/R05/Materials/M_'+str(s.material_slot_name))
  if m:mesh.set_material(i,m)
 if f.stem.startswith('SM_R10_'):
  mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
  mesh.set_material(0,lib.load_asset('/Game/MaldekRefinement/R06/Materials/M_Snowy_Terrain'))
 lib.save_loaded_asset(mesh)
 label='R04_Local_Terrain' if 'Canyon_Terrain' in f.stem else f.stem.replace('SM_R04_','R04_').replace('SM_R10_','R10_')
 a=next((a for a in aa.get_all_level_actors() if a.get_actor_label()==label),None)
 if not a:a=aa.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(*origin),unreal.Rotator(yaw=180))
 a.set_actor_label(label);a.static_mesh_component.set_static_mesh(mesh);a.static_mesh_component.set_collision_profile_name('BlockAll');report.append(label)
world.get_world_settings().set_editor_property('kill_z',0.)
start=next(a for a in aa.get_all_level_actors() if isinstance(a,unreal.PlayerStart));start.set_actor_location(unreal.Vector(origin[0]+3600,origin[1]-6050,origin[2]+10),False,False);start.set_actor_rotation(unreal.Rotator(yaw=90),False)
assert levels.save_current_level();(out/'import_report.json').write_text(json.dumps(report,indent=2))

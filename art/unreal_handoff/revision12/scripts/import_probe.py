"""Strict, repeatable pilot import. JOB.dry_run verifies every file before mutation."""
import unreal,json,hashlib
from pathlib import Path
base=Path(__file__).resolve().parents[1];manifest=json.loads((base/'probe_manifest.json').read_text())
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert world.get_name()=='Station_R12'
assert (base/'level_established.json').exists()
for row in manifest['chunks']:
 f=base/row['file'];assert f.exists() and hashlib.sha256(f.read_bytes()).hexdigest()==row['sha256'],row['name']
 assert row['material_slots'] and row['sources'],row['name']
if JOB.get('dry_run'):
 RESULT={'dry_run':True,'valid_files':len(manifest['chunks'])}
else:
 lib=unreal.EditorAssetLibrary;assets=unreal.AssetToolsHelpers.get_asset_tools();aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
 meshes=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
 origin=json.loads((base.parent/'working_level_report.json').read_text())['station_origin']
 def wp(p):return unreal.Vector(origin[0]-100*p[0],origin[1]+100*p[1],origin[2]+100*p[2])
 def arr(v):return [v.x,v.y,v.z]
 unreal.SystemLibrary.execute_console_command(world,'Interchange.FeatureFlags.Import.FBX 0')
 locations=[(-35,-5,12),(-30,-5,12),(-27,-5,13.2),(-30,-2,12),(-30,-.4,12),(-27,-2,12)]
 report=[]
 for row,p in zip(manifest['chunks'],locations):
  task=unreal.AssetImportTask();task.filename=str(base/row['file']);task.destination_path='/Game/MaldekRefinement/R12/Probe/Meshes';task.automated=True;task.save=True;task.replace_existing=True
  opt=unreal.FbxImportUI();opt.import_mesh=True;opt.import_materials=False;opt.import_textures=False;opt.automated_import_should_detect_type=False;opt.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
  d=opt.static_mesh_import_data;d.combine_meshes=True;d.auto_generate_collision=False;d.convert_scene=True;d.convert_scene_unit=True;d.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS
  task.options=opt;assets.import_asset_tasks([task]);path=task.destination_path+'/'+row['name'];mesh=lib.load_asset(path);assert mesh,path
  b=mesh.get_bounds();actual=[arr(b.origin-b.box_extent),arr(b.origin+b.box_extent)];lo,hi=row['bounds']
  expected=[[lo[0]*100,-hi[1]*100,lo[2]*100],[hi[0]*100,-lo[1]*100,hi[2]*100]]
  error=max(abs(actual[j][i]-expected[j][i]) for j in range(2) for i in range(3));assert error<.2,(row['name'],actual,expected)
  slots=[str(s.material_slot_name) for s in mesh.static_materials];assert slots==row['material_slots'],(slots,row['material_slots'])
  hulls=meshes.get_convex_collision_count(mesh);assert hulls==row['collision_hulls'],(row['name'],hulls,row['collision_hulls'])
  label=row['name'].replace('SM_','');a=next((a for a in aa.get_all_level_actors() if a.get_actor_label()==label),None)
  if not a:a=aa.spawn_actor_from_class(unreal.StaticMeshActor,wp(p),unreal.Rotator(yaw=180))
  a.set_actor_label(label);a.set_actor_location(wp(p),False,True);a.set_actor_rotation(unreal.Rotator(yaw=180),False)
  c=a.static_mesh_component;c.set_static_mesh(mesh);c.set_editor_property('override_materials',[]);c.set_collision_profile_name('BlockAll' if hulls else 'NoCollision')
  c.set_phys_material_override(lib.load_asset('/Game/MaldekRefinement/ForestTest/Audio/Surfaces/PM_Metal'))
  a.set_folder_path('R12/Pilot inspection')
  report.append({'name':row['name'],'path':path,'actor':a.get_path_name(),'bounds_error_cm':error,'collision_hulls':hulls,'material_slots':slots,'inspection_location_m':p})
 assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
 RESULT={'success':True,'assets':report,'scale_and_axis_validated':True,'materials_validated':False}
 (base/'probe_import.json').write_text(json.dumps(RESULT,indent=2))

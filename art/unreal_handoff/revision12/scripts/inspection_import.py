"""Import the authored portable meter; only writes /Game/Inspection assets."""
import unreal,json
from pathlib import Path
root=Path(__file__).resolve().parents[4]
task=unreal.AssetImportTask()
task.filename=str(root/'art/blender/inspection_01/SM_InspectionMeter.fbx')
task.destination_path='/Game/Inspection';task.destination_name='SM_InspectionMeter'
task.automated=True;task.replace_existing=True;task.save=True
options=unreal.FbxImportUI();options.import_mesh=True;options.import_materials=True;options.import_textures=False
options.import_as_skeletal=False;options.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
options.static_mesh_import_data.combine_meshes=True
options.static_mesh_import_data.auto_generate_collision=True
options.static_mesh_import_data.generate_lightmap_u_vs=False
task.options=options
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
mesh=unreal.load_asset('/Game/Inspection/SM_InspectionMeter')
assert isinstance(mesh,unreal.StaticMesh),'Meter import failed'
# A convex body supports physics and visibility queries without complex-as-simple restrictions.
editor=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
editor.remove_collisions(mesh);editor.add_simple_collisions(mesh,unreal.ScriptingCollisionShapeType.BOX)
unreal.EditorAssetLibrary.save_loaded_asset(mesh)
RESULT={'assets':list(task.imported_object_paths),'bounds':str(mesh.get_bounds())}
(root/'art/blender/inspection_01/import_report.json').write_text(json.dumps(RESULT,indent=2))

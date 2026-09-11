"""Install separate cliff assets, retaining all current building and lighting work."""
raise RuntimeError('Retired full-heightmap import: source PNG was blank. Use gorge_native_probe.py and gorge_native_apply.py with a fresh checkpoint.')
import unreal,json,shutil
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'gorge';root='/Game/MaldekRefinement/R12/Gorge'
ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert w.get_name()=='Station_R12'
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);actors={a.get_actor_label():a for a in aa.get_all_level_actors()}
assert ls.save_current_level()
backup=out/'Station_R12_before_install.umap'
if not backup.exists():shutil.copy2(b.parents[2]/'game/Content/MaldekRefinement/R12/Station_R12.umap',backup)
(out/'preserve.json').write_text(json.dumps({k:str(a.get_actor_transform()) for k,a in actors.items()},indent=2))
unreal.SystemLibrary.execute_console_command(w,'Interchange.FeatureFlags.Import.FBX 0')
t=unreal.AssetImportTask();t.filename=str(out/'SM_Station_Gorge_Terrain.fbx');t.destination_path=root+'/Meshes';t.automated=True;t.save=True;t.replace_existing=True
opt=unreal.FbxImportUI();opt.import_mesh=True;opt.import_materials=False;opt.import_textures=False;opt.automated_import_should_detect_type=False;opt.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
d=opt.static_mesh_import_data;d.combine_meshes=True;d.auto_generate_collision=False;d.convert_scene=True;d.convert_scene_unit=True;d.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_COMPUTE_NORMALS;t.options=opt
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t])
mesh=unreal.load_asset(root+'/Meshes/SM_Station_Gorge_Terrain');assert mesh
mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
mesh.set_material(0,unreal.load_asset('/Game/MaldekRefinement/R12/ForestRefine/Materials/M_Woodland_Ground'));unreal.EditorAssetLibrary.save_loaded_asset(mesh)
c=actors['VF10_Parking_Terrain'].static_mesh_component;c.set_static_mesh(mesh);c.set_editor_property('override_materials',[]);c.set_collision_profile_name('BlockAll')
assert ls.save_current_level()
p=Path(__file__).resolve().parent/'forest_refine_apply_landscape.py'
source=p.read_text().replace("out=b/'forest_refine'","out=b/'gorge'").replace('/ForestRefine/HeightImport','/Gorge/HeightImport').replace('landscape_valley','landscape_gorge')
exec(compile(source,str(p),'exec'))

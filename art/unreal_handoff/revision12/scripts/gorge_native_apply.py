"""Apply the verified local CPU patch and the existing separate terrain mesh."""
import unreal,json,time,traceback
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'gorge';ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);actors={a.get_actor_label():a for a in aa.get_all_level_actors()};land=next(a for a in actors.values() if isinstance(a,unreal.Landscape))
r=json.loads((out/JOB.get('patch','native_probe.json')).read_text());assert r['source']=='native CPU height data'
result=unreal.StationMigrationLibrary.apply_r12_landscape_patch(land,*r['bounds'],r['layer'],r['base'],r['desired']);assert result.startswith('OK'),result
if JOB.get('reimport'):
 w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();unreal.SystemLibrary.execute_console_command(w,'Interchange.FeatureFlags.Import.FBX 0')
 t=unreal.AssetImportTask();t.filename=str(out/'SM_Station_Gorge_Terrain.fbx');t.destination_path='/Game/MaldekRefinement/R12/Gorge/Meshes';t.automated=True;t.save=True;t.replace_existing=True
 opt=unreal.FbxImportUI();opt.import_mesh=True;opt.import_materials=False;opt.import_textures=False;opt.automated_import_should_detect_type=False;opt.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
 d=opt.static_mesh_import_data;d.combine_meshes=True;d.auto_generate_collision=False;d.convert_scene=True;d.convert_scene_unit=True;d.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_COMPUTE_NORMALS;t.options=opt;unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t])
mesh=unreal.load_asset('/Game/MaldekRefinement/R12/Gorge/Meshes/SM_Station_Gorge_Terrain');assert mesh
mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
for i in range(len(mesh.get_editor_property('static_materials'))):mesh.set_material(i,unreal.load_asset('/Game/MaldekRefinement/R12/ForestRefine/Materials/M_Woodland_Ground'))
unreal.EditorAssetLibrary.save_loaded_asset(mesh)
actors['VF10_Parking_Terrain'].static_mesh_component.set_static_mesh(mesh)
state={'edit':result,'next':time.monotonic()+20}
def finish(dt):
 if time.monotonic()<state['next']:return
 unreal.unregister_slate_post_tick_callback(handle)
 try:
  actual=list(unreal.StationMigrationLibrary.read_r12_landscape_patch(land,*r['bounds'],r['layer']))
  assert actual==r['desired'],'Base layer readback mismatch'
  assert ls.save_current_level();state.update(saved=True,readback_passed=True)
 except Exception:state['error']=traceback.format_exc()
 (out/JOB.get('report','native_applied.json')).write_text(json.dumps(state))
handle=unreal.register_slate_post_tick_callback(finish);RESULT={'started':True,'edit':result}

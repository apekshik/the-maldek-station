import unreal,json
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'gondola_route';root='/Game/MaldekRefinement/R12/GondolaRoute';plan=json.loads((out/'plan.json').read_text())
ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);actors={a.get_actor_label():a for a in aa.get_all_level_actors()};lib=unreal.EditorAssetLibrary;at=unreal.AssetToolsHelpers.get_asset_tools()
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();unreal.SystemLibrary.execute_console_command(w,'Interchange.FeatureFlags.Import.FBX 0')
report=[]
for index,item in enumerate(json.loads((out/'terminal_exports.json').read_text())):
 name=item['name'];t=unreal.AssetImportTask();t.filename=str(out/'fbx'/(name+'.fbx'));t.destination_path=root+'/Meshes';t.automated=True;t.save=True;t.replace_existing=True
 opt=unreal.FbxImportUI();opt.import_mesh=True;opt.import_materials=False;opt.import_textures=False;opt.automated_import_should_detect_type=False;opt.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
 d=opt.static_mesh_import_data;d.combine_meshes=True;d.auto_generate_collision=False;d.convert_scene=True;d.convert_scene_unit=True;t.options=opt;at.import_asset_tasks([t])
 mesh=lib.load_asset(root+'/Meshes/'+name);assert mesh
 for i,slot in enumerate(mesh.get_editor_property('static_materials')):
  mat=lib.load_asset(root+'/Materials/M_'+str(slot.get_editor_property('imported_material_slot_name')));assert mat;mesh.set_material(i,mat)
 mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE);lib.save_loaded_asset(mesh)
 p=plan['rope_samples_m'][0 if index==0 else -1];label='R12_Route_Terminal_'+('Millford' if index==0 else 'Maldek');a=actors.get(label) or aa.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector())
 a.set_actor_label(label);a.set_actor_rotation(unreal.Rotator(pitch=0,yaw=180,roll=0),True);a.set_folder_path('R12/Gondola Route');a.set_actor_location(unreal.Vector(p[0]*100+25,p[1]*100,p[2]*100),False,True);a.static_mesh_component.set_static_mesh(mesh);a.static_mesh_component.set_collision_profile_name('BlockAll');report.append(label)
assert ls.save_current_level();RESULT={'saved':True,'terminals':report};(out/'terminals.json').write_text(json.dumps(RESULT,indent=2))

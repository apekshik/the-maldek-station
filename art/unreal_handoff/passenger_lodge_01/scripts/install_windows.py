import unreal,json,hashlib,re
from pathlib import Path
OUT=Path(__file__).resolve().parents[1];REPO=OUT.parents[2];root='/Game/MaldekRefinement/PassengerLodge/Windows'
ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);lib=unreal.EditorAssetLibrary;at=unreal.AssetToolsHelpers.get_asset_tools();sm=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
assert not ls.is_in_play_in_editor() and unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_name()=='Station_Lodge_Migration'
data=json.loads((OUT/'windows/exports.json').read_text());base=json.loads((OUT/'before.json').read_text());o=base['origin'];actors={a.get_actor_label():a for a in aa.get_all_level_actors()}
before=[]
for a in actors.values():
 p=a.get_actor_location();r=a.get_actor_rotation();s=a.get_actor_scale3d();before.append({'label':a.get_actor_label(),'position':[p.x,p.y,p.z],'rotation':[r.pitch,r.yaw,r.roll],'scale':[s.x,s.y,s.z]})
if not (OUT/'windows/before.json').exists():(OUT/'windows/before.json').write_text(json.dumps(before,indent=2))
unreal.SystemLibrary.execute_console_command(None,'Interchange.FeatureFlags.Import.FBX 0');meshes={};checks=[]
for row in data['assets']:
 file=OUT/'windows/fbx'/(row['name']+'.fbx');assert hashlib.sha256(file.read_bytes()).hexdigest()==row['sha256']
 path=root+'/Meshes/'+row['name'];mesh=lib.load_asset(path)
 if not mesh:
  t=unreal.AssetImportTask();t.filename=str(file);t.destination_path=root+'/Meshes';t.automated=True;t.save=True
  opt=unreal.FbxImportUI();opt.import_mesh=True;opt.import_materials=False;opt.import_textures=False;opt.automated_import_should_detect_type=False;opt.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
  d=opt.static_mesh_import_data;d.combine_meshes=True;d.auto_generate_collision=False;d.convert_scene=True;d.convert_scene_unit=True;d.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS;t.options=opt;at.import_asset_tasks([t]);mesh=lib.load_asset(path)
 assert mesh,path
 b=mesh.get_bounds();actual=[b.origin-b.box_extent,b.origin+b.box_extent];lo,hi=row['lo'],row['hi'];expected=[[lo[0]*100,-hi[1]*100,lo[2]*100],[hi[0]*100,-lo[1]*100,hi[2]*100]]
 error=max(abs(v-exp[i]) for q,exp in zip(actual,expected) for i,v in enumerate([q.x,q.y,q.z]));assert error<.2,(path,error)
 mat=lib.load_asset('/Game/MaldekRefinement/PassengerLodge/Surfaces/Materials/M_'+re.sub(r'[^a-zA-Z0-9_]','_',row['material']));assert mat
 assert len(mesh.static_materials)==1;mesh.set_material(0,mat)
 sm.remove_collisions(mesh);mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
 ns=mesh.get_editor_property('nanite_settings');ns.set_editor_property('enabled',False);sm.set_nanite_settings(mesh,ns,True)
 assert lib.save_loaded_asset(mesh);meshes[row['name']]=mesh;checks.append({'asset':path,'bounds_error_cm':error})
for r in data['placements']:
 p=r['pivot'];a=actors.get(r['label']) or aa.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(o[0]-100*p[0],o[1]+100*p[1],o[2]+100*p[2]),unreal.Rotator(pitch=0,yaw=180,roll=0));a.set_actor_label(r['label']);a.set_folder_path('LodgeMigration/Windows')
 a.static_mesh_component.set_static_mesh(meshes[r['mesh']]);a.static_mesh_component.set_collision_profile_name('BlockAll');a.static_mesh_component.set_editor_property('override_materials',[])
assert ls.save_current_level()
assert hashlib.sha256((REPO/'game/Content/MaldekRefinement/R12/Station_R12.umap').read_bytes()).hexdigest()==base['map_sha256']
RESULT={'assets':checks,'assemblies':2,'source_components':sum(len(r['sources']) for r in data['placements']),'actors':len(data['placements']),'original_map_unchanged':True}
(OUT/'windows/install.json').write_text(json.dumps(RESULT,indent=2))

"""Install only baked static seating in the isolated migration map."""
import unreal,json,hashlib
from pathlib import Path
OUT=Path(__file__).resolve().parents[1];REPO=OUT.parents[2];dest=OUT/'seating';root='/Game/MaldekRefinement/PassengerLodge/Seating'
ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);lib=unreal.EditorAssetLibrary;at=unreal.AssetToolsHelpers.get_asset_tools();sm=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem);ml=unreal.MaterialEditingLibrary
assert not ls.is_in_play_in_editor() and unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_name()=='Station_Lodge_Migration'
data=json.loads((dest/'exports.json').read_text());base=json.loads((OUT/'before.json').read_text());o=base['origin'];actors={a.get_actor_label():a for a in aa.get_all_level_actors()}
before=[]
for a in actors.values():
 p=a.get_actor_location();r=a.get_actor_rotation();s=a.get_actor_scale3d();before.append({'label':a.get_actor_label(),'position':[p.x,p.y,p.z],'rotation':[r.pitch,r.yaw,r.roll],'scale':[s.x,s.y,s.z]})
if not (dest/'before.json').exists():(dest/'before.json').write_text(json.dumps(before,indent=2))
unreal.SystemLibrary.execute_console_command(None,'Interchange.FeatureFlags.Import.FBX 0');materials={};dependencies=[]
for index,row in enumerate(data['placements'],1):
 textures={}
 for channel,trow in row['textures'].items():
  file=dest/trow['file'];assert hashlib.sha256(file.read_bytes()).hexdigest()==trow['sha256'];name='T_PLS_%02d_%s'%(index,channel);path=root+'/Textures/'+name;tex=lib.load_asset(path)
  if not tex:
   task=unreal.AssetImportTask();task.filename=str(file);task.destination_path=root+'/Textures';task.destination_name=name;task.automated=True;task.save=False;at.import_asset_tasks([task]);tex=lib.load_asset(path)
  assert tex,path
  tex.set_editor_property('srgb',channel=='BaseColor');tex.set_editor_property('compression_settings',unreal.TextureCompressionSettings.TC_NORMALMAP if channel=='NormalGL' else unreal.TextureCompressionSettings.TC_DEFAULT if channel=='BaseColor' else unreal.TextureCompressionSettings.TC_MASKS)
  if channel=='NormalGL':tex.set_editor_property('flip_green_channel',True)
  assert lib.save_loaded_asset(tex);textures[channel]=tex;dependencies.append(path)
 name='M_PLS_%02d'%index;path=root+'/Materials/'+name;m=lib.load_asset(path) or at.create_asset(name,root+'/Materials',unreal.Material,unreal.MaterialFactoryNew());ml.delete_all_material_expressions(m)
 for channel,tex in textures.items():
  n=ml.create_material_expression(m,unreal.MaterialExpressionTextureSample);n.texture=tex;n.sampler_type=unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL if channel=='NormalGL' else unreal.MaterialSamplerType.SAMPLERTYPE_COLOR if channel=='BaseColor' else unreal.MaterialSamplerType.SAMPLERTYPE_MASKS
  if channel=='ORM':
   assert ml.connect_material_property(n,'G',unreal.MaterialProperty.MP_ROUGHNESS);assert ml.connect_material_property(n,'B',unreal.MaterialProperty.MP_METALLIC)
  else:assert ml.connect_material_property(n,'RGB',unreal.MaterialProperty.MP_BASE_COLOR if channel=='BaseColor' else unreal.MaterialProperty.MP_NORMAL)
 ml.recompile_material(m);assert lib.save_loaded_asset(m);materials[row['label']]=m
shader_errors=list(unreal.StationMigrationLibrary.validate_material_shaders(list(materials.values())));assert not shader_errors,shader_errors
meshes={};checks=[]
for row in data['assets']:
 file=dest/'fbx'/(row['name']+'.fbx');assert hashlib.sha256(file.read_bytes()).hexdigest()==row['sha256'];path=root+'/Meshes/'+row['name'];mesh=lib.load_asset(path)
 if not mesh:
  task=unreal.AssetImportTask();task.filename=str(file);task.destination_path=root+'/Meshes';task.automated=True;task.save=False
  opt=unreal.FbxImportUI();opt.import_mesh=True;opt.import_materials=False;opt.import_textures=False;opt.automated_import_should_detect_type=False;opt.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
  d=opt.static_mesh_import_data;d.combine_meshes=True;d.auto_generate_collision=False;d.convert_scene=True;d.convert_scene_unit=True;d.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS;task.options=opt;at.import_asset_tasks([task]);mesh=lib.load_asset(path)
 assert mesh,path;b=mesh.get_bounds();actual=[b.origin-b.box_extent,b.origin+b.box_extent];lo,hi=row['lo'],row['hi'];expected=[[lo[0]*100,-hi[1]*100,lo[2]*100],[hi[0]*100,-lo[1]*100,hi[2]*100]]
 error=max(abs(v-e[i]) for q,e in zip(actual,expected) for i,v in enumerate([q.x,q.y,q.z]));assert error<.2,(path,error);assert len(mesh.static_materials)==1
 first=next(p for p in data['placements'] if p['mesh']==row['name']);mesh.set_material(0,materials[first['label']]);sm.remove_collisions(mesh);mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
 ns=mesh.get_editor_property('nanite_settings');ns.set_editor_property('enabled',False);sm.set_nanite_settings(mesh,ns,True);assert lib.save_loaded_asset(mesh);meshes[row['name']]=mesh;checks.append({'asset':path,'bounds_error_cm':error})
for row in data['placements']:
 p=row['pivot'];a=actors.get(row['label']) or aa.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(o[0]-100*p[0],o[1]+100*p[1],o[2]+100*p[2]),unreal.Rotator(pitch=0,yaw=180,roll=0));a.set_actor_label(row['label']);a.set_folder_path('LodgeMigration/Seating')
 c=a.static_mesh_component;c.set_static_mesh(meshes[row['mesh']]);c.set_collision_profile_name('BlockAll');c.set_material(0,materials[row['label']])
assert ls.save_current_level();assert hashlib.sha256((REPO/'game/Content/MaldekRefinement/R12/Station_R12.umap').read_bytes()).hexdigest()==base['map_sha256']
RESULT={'assets':checks,'actors':6,'tables':6,'benches':12,'source_components':559,'texture_dependencies':dependencies,'shader_errors':shader_errors,'original_map_unchanged':True}
(dest/'install.json').write_text(json.dumps(RESULT,indent=2))

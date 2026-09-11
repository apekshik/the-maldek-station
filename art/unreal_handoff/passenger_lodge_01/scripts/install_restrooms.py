"""Install PLR fixtures and five fitted doors in the isolated migration map."""
import unreal,json,hashlib,re
from pathlib import Path
OUT=Path(__file__).resolve().parents[1];REPO=OUT.parents[2];dest=OUT/'restrooms';root='/Game/MaldekRefinement/PassengerLodge/Restrooms'
ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);lib=unreal.EditorAssetLibrary;at=unreal.AssetToolsHelpers.get_asset_tools();sm=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem);ml=unreal.MaterialEditingLibrary
assert not ls.is_in_play_in_editor() and unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_name()=='Station_Lodge_Migration'
data=json.loads((dest/'exports.json').read_text());base=json.loads((OUT/'before.json').read_text());o=base['origin'];actors={a.get_actor_label():a for a in aa.get_all_level_actors()}
before=[]
for a in actors.values():
 p=a.get_actor_location();r=a.get_actor_rotation();s=a.get_actor_scale3d();before.append({'label':a.get_actor_label(),'position':[p.x,p.y,p.z],'rotation':[r.pitch,r.yaw,r.roll],'scale':[s.x,s.y,s.z]})
if not (dest/'before.json').exists():(dest/'before.json').write_text(json.dumps(before,indent=2))
unreal.SystemLibrary.execute_console_command(None,'Interchange.FeatureFlags.Import.FBX 0');materials={};deps=[]
for row in data['groups']:
 textures={};id=row['id']
 for channel,trow in row['textures'].items():
  file=dest/trow['file'];assert hashlib.sha256(file.read_bytes()).hexdigest()==trow['sha256'];name='T_PLR_'+id+'_'+channel;path=root+'/Textures/'+name;tex=lib.load_asset(path)
  if not tex:
   task=unreal.AssetImportTask();task.filename=str(file);task.destination_path=root+'/Textures';task.destination_name=name;task.automated=True;task.save=False;at.import_asset_tasks([task]);tex=lib.load_asset(path)
  assert tex;tex.set_editor_property('srgb',channel=='BaseColor');tex.set_editor_property('compression_settings',unreal.TextureCompressionSettings.TC_NORMALMAP if channel=='NormalGL' else unreal.TextureCompressionSettings.TC_DEFAULT if channel=='BaseColor' else unreal.TextureCompressionSettings.TC_MASKS)
  if channel=='NormalGL':tex.set_editor_property('flip_green_channel',True)
  assert lib.save_loaded_asset(tex);textures[channel]=tex;deps.append(path)
 name='M_PLR_'+id;path=root+'/Materials/'+name;m=lib.load_asset(path) or at.create_asset(name,root+'/Materials',unreal.Material,unreal.MaterialFactoryNew());ml.delete_all_material_expressions(m)
 for channel,tex in textures.items():
  n=ml.create_material_expression(m,unreal.MaterialExpressionTextureSample);n.texture=tex;n.sampler_type=unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL if channel=='NormalGL' else unreal.MaterialSamplerType.SAMPLERTYPE_COLOR if channel=='BaseColor' else unreal.MaterialSamplerType.SAMPLERTYPE_MASKS
  if channel=='ORM':
   assert ml.connect_material_property(n,'G',unreal.MaterialProperty.MP_ROUGHNESS);assert ml.connect_material_property(n,'B',unreal.MaterialProperty.MP_METALLIC)
  else:assert ml.connect_material_property(n,'RGB',unreal.MaterialProperty.MP_BASE_COLOR if channel=='BaseColor' else unreal.MaterialProperty.MP_NORMAL)
 ml.recompile_material(m);assert lib.save_loaded_asset(m);materials[id]=m
name='M_PLR_Privacy';path=root+'/Materials/'+name;indicator=lib.load_asset(path) or at.create_asset(name,root+'/Materials',unreal.Material,unreal.MaterialFactoryNew());ml.delete_all_material_expressions(indicator)
n=ml.create_material_expression(indicator,unreal.MaterialExpressionVectorParameter);n.set_editor_property('parameter_name','StateColor');n.set_editor_property('default_value',unreal.LinearColor(.025,.22,.08,1));assert ml.connect_material_property(n,'RGB',unreal.MaterialProperty.MP_BASE_COLOR)
r=ml.create_material_expression(indicator,unreal.MaterialExpressionConstant);r.set_editor_property('r',.45);assert ml.connect_material_property(r,'',unreal.MaterialProperty.MP_ROUGHNESS);ml.recompile_material(indicator);assert lib.save_loaded_asset(indicator)
shaders=list(unreal.StationMigrationLibrary.validate_material_shaders([*materials.values(),indicator]));assert not shaders,shaders
meshes={};checks=[]
for row in data['assets']:
 file=dest/'fbx'/(row['name']+'.fbx');assert hashlib.sha256(file.read_bytes()).hexdigest()==row['sha256'];path=root+'/Meshes/'+row['name'];mesh=lib.load_asset(path)
 if not mesh:
  task=unreal.AssetImportTask();task.filename=str(file);task.destination_path=root+'/Meshes';task.automated=True;task.save=False;opt=unreal.FbxImportUI();opt.import_mesh=True;opt.import_materials=False;opt.import_textures=False;opt.automated_import_should_detect_type=False;opt.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
  d=opt.static_mesh_import_data;d.combine_meshes=True;d.auto_generate_collision=False;d.convert_scene=True;d.convert_scene_unit=True;d.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS;task.options=opt;at.import_asset_tasks([task]);mesh=lib.load_asset(path)
 assert mesh;b=mesh.get_bounds();actual=[b.origin-b.box_extent,b.origin+b.box_extent];lo,hi=row['lo'],row['hi'];expected=[[lo[0]*100,-hi[1]*100,lo[2]*100],[hi[0]*100,-lo[1]*100,hi[2]*100]];err=max(abs(v-e[i]) for q,e in zip(actual,expected) for i,v in enumerate([q.x,q.y,q.z]));assert err<.2,(path,err)
 assert len(mesh.static_materials)==1;mesh.set_material(0,indicator if row['role']=='Indicator' else materials[row['group']]);sm.remove_collisions(mesh)
 if row['role'] in {'Static','FixedHardware'}:mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
 ns=mesh.get_editor_property('nanite_settings');ns.set_editor_property('enabled',False);sm.set_nanite_settings(mesh,ns,True);assert lib.save_loaded_asset(mesh);meshes[row['name']]=mesh;checks.append({'asset':path,'bounds_error_cm':err})

standard=actors['R12_Door_Control_side'];placed=[]
components={'Leaf':'leaf','FixedHardware':'fixed_hardware','FrontLever':'front_lever','BackLever':'back_lever','MovingLatch':'moving_latch','Indicator':'privacy_indicator'}
def vec(p):return unreal.Vector(100*p[0],-100*p[1],100*p[2])
def world(p):return unreal.Vector(o[0]-100*p[0],o[1]+100*p[1],o[2]+100*p[2])
for row in data['groups']:
 label='MIG_PLR_'+row['id'];H=row['matrix'];position=[H[j][3] for j in range(3)];loc=world(position);rot=unreal.Rotator(pitch=0,yaw=180,roll=0)
 if row['door']:
  a=actors.get(label) or aa.spawn_actor_from_class(unreal.StationDoor,loc,rot);a.set_actor_label(label);a.set_folder_path('LodgeMigration/Restrooms')
  for prop,value in {'use_authored_hardware':True,'has_keypad':False,'has_key_lock':False,'has_privacy_latch':not row['entry'],'locked':False,'relock_on_close':False,'interior_is_negative_y':False,'open_angle':row['open_angle'],'degrees_per_second':70.,'authored_lever_angle':-25. if row['entry'] else 25.}.items():a.set_editor_property(prop,value)
  if not row['entry']:a.set_editor_property('privacy_bolt_location',vec(row['bolt_focus_source']))
  for part in row['parts']:
   if part['role']=='Static':continue
   c=getattr(a,components[part['role']]);c.set_static_mesh(meshes[part['mesh']]);c.set_editor_property('override_materials',[]);c.set_visibility(True);c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
   c.set_relative_location(vec([part['local_matrix'][j][3] for j in range(3)]),False,False)
  a.fixed_hardware.set_collision_profile_name('BlockAll');box=row['leaf_collision_source'];a.leaf_collision.set_relative_location(vec(box['center']),False,False);a.leaf_collision.set_box_extent(unreal.Vector(*[v*100 for v in box['extent']]),False)
  for prop in ['unlatch_sound','movement_sound','closing_movement_sound','close_sound','unlock_sound','lock_sound','door_volume','movement_volume']:a.set_editor_property(prop,standard.get_editor_property(prop))
  for audio in a.get_components_by_class(unreal.AudioComponent):audio.set_relative_location(vec(box['center']),False,False)
  a.get_editor_property('KeypadDisplay').set_visibility(False);a.key_inspection_light.set_visibility(False);a.service_key.set_visibility(False)
 for part in row['parts']:
  if part['role']!='Static':continue
  name=label+'_Fixtures';a=actors.get(name) or aa.spawn_actor_from_class(unreal.StaticMeshActor,loc,rot);a.set_actor_label(name);a.set_folder_path('LodgeMigration/Restrooms');a.static_mesh_component.set_static_mesh(meshes[part['mesh']]);a.static_mesh_component.set_collision_profile_name('BlockAll')
 placed.append({'id':row['id'],'position':position,'door':row['door']})
assert ls.save_current_level();assert hashlib.sha256((REPO/'game/Content/MaldekRefinement/R12/Station_R12.umap').read_bytes()).hexdigest()==base['map_sha256']
RESULT={'assets':checks,'groups':placed,'textures':deps,'shader_errors':shaders,'original_map_unchanged':True};(dest/'install.json').write_text(json.dumps(RESULT,indent=2))

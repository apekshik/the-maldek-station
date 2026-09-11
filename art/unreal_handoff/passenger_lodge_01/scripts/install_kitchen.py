"""Install weathered kitchen and fifteen fitted storage mechanisms in the isolated migration map."""
import unreal,json,hashlib,re,math
from pathlib import Path
OUT=Path(__file__).resolve().parents[1];REPO=OUT.parents[2];dest=OUT/'kitchen';root='/Game/MaldekRefinement/PassengerLodge/Kitchen'
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
  file=dest/trow['file'];assert hashlib.sha256(file.read_bytes()).hexdigest()==trow['sha256'];name='T_PLK_'+id+'_'+channel;path=root+'/Textures/'+name;tex=lib.load_asset(path)
  if not tex:
   task=unreal.AssetImportTask();task.filename=str(file);task.destination_path=root+'/Textures';task.destination_name=name;task.automated=True;task.save=False;at.import_asset_tasks([task]);tex=lib.load_asset(path)
  assert tex;tex.set_editor_property('srgb',channel=='BaseColor');tex.set_editor_property('compression_settings',unreal.TextureCompressionSettings.TC_NORMALMAP if channel=='NormalGL' else unreal.TextureCompressionSettings.TC_DEFAULT if channel=='BaseColor' else unreal.TextureCompressionSettings.TC_MASKS)
  if channel=='NormalGL':tex.set_editor_property('flip_green_channel',True)
  assert lib.save_loaded_asset(tex);textures[channel]=tex;deps.append(path)
 name='M_PLK_'+id;path=root+'/Materials/'+name;m=lib.load_asset(path) or at.create_asset(name,root+'/Materials',unreal.Material,unreal.MaterialFactoryNew());ml.delete_all_material_expressions(m)
 for channel,tex in textures.items():
  n=ml.create_material_expression(m,unreal.MaterialExpressionTextureSample);n.texture=tex;n.sampler_type=unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL if channel=='NormalGL' else unreal.MaterialSamplerType.SAMPLERTYPE_COLOR if channel=='BaseColor' else unreal.MaterialSamplerType.SAMPLERTYPE_MASKS
  if channel=='ORM':
   assert ml.connect_material_property(n,'G',unreal.MaterialProperty.MP_ROUGHNESS);assert ml.connect_material_property(n,'B',unreal.MaterialProperty.MP_METALLIC)
  else:assert ml.connect_material_property(n,'RGB',unreal.MaterialProperty.MP_BASE_COLOR if channel=='BaseColor' else unreal.MaterialProperty.MP_NORMAL)
 ml.recompile_material(m);assert lib.save_loaded_asset(m);materials[id]=m
name='M_PLK_DisplayGlass';path=root+'/Materials/'+name;glass=lib.load_asset(path) or at.create_asset(name,root+'/Materials',unreal.Material,unreal.MaterialFactoryNew());ml.delete_all_material_expressions(glass)
glass.set_editor_property('blend_mode',unreal.BlendMode.BLEND_TRANSLUCENT);glass.set_editor_property('two_sided',True)
n=ml.create_material_expression(glass,unreal.MaterialExpressionConstant3Vector);n.set_editor_property('constant',unreal.LinearColor(.32,.39,.37,1));assert ml.connect_material_property(n,'',unreal.MaterialProperty.MP_BASE_COLOR)
for prop,value in [(unreal.MaterialProperty.MP_OPACITY,.14),(unreal.MaterialProperty.MP_ROUGHNESS,.22)]:
 n=ml.create_material_expression(glass,unreal.MaterialExpressionConstant);n.set_editor_property('r',value);assert ml.connect_material_property(n,'',prop)
ml.recompile_material(glass);assert lib.save_loaded_asset(glass)
shaders=list(unreal.StationMigrationLibrary.validate_material_shaders([*materials.values(),glass]));assert not shaders,shaders
meshes={};checks=[]
for row in data['assets']:
 file=dest/'fbx'/(row['name']+'.fbx');assert hashlib.sha256(file.read_bytes()).hexdigest()==row['sha256'];path=root+'/Meshes/'+row['name'];mesh=lib.load_asset(path)
 if not mesh:
  task=unreal.AssetImportTask();task.filename=str(file);task.destination_path=root+'/Meshes';task.automated=True;task.save=False;opt=unreal.FbxImportUI();opt.import_mesh=True;opt.import_materials=False;opt.import_textures=False;opt.automated_import_should_detect_type=False;opt.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
  d=opt.static_mesh_import_data;d.combine_meshes=True;d.auto_generate_collision=False;d.convert_scene=True;d.convert_scene_unit=True;d.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS;task.options=opt;at.import_asset_tasks([task]);mesh=lib.load_asset(path)
 assert mesh;b=mesh.get_bounds();actual=[b.origin-b.box_extent,b.origin+b.box_extent];lo,hi=row['lo'],row['hi'];expected=[[lo[0]*100,-hi[1]*100,lo[2]*100],[hi[0]*100,-lo[1]*100,hi[2]*100]];err=max(abs(v-e[i]) for q,e in zip(actual,expected) for i,v in enumerate([q.x,q.y,q.z]));assert err<.2,(path,err)
 assert len(mesh.static_materials)==1;mesh.set_material(0,glass if row['role']=='Glass' else materials[row['group']]);sm.remove_collisions(mesh)
 if True:mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
 ns=mesh.get_editor_property('nanite_settings');ns.set_editor_property('enabled',False);sm.set_nanite_settings(mesh,ns,True);assert lib.save_loaded_asset(mesh);meshes[row['name']]=mesh;checks.append({'asset':path,'bounds_error_cm':err})

standard=actors['R12_Door_Control_side'];placed=[]
def vec(p):return unreal.Vector(100*p[0],-100*p[1],100*p[2])
def world(p):return unreal.Vector(o[0]-100*p[0],o[1]+100*p[1],o[2]+100*p[2])
for row in data['groups']:
 for part in row['parts']:
  label='MIG_PLK_'+row['id']+'_'+part['role'];M=part['matrix'];loc=world([M[j][3] for j in range(3)]);rot=unreal.Rotator(pitch=0,yaw=180-math.degrees(math.atan2(M[1][0],M[0][0])),roll=0)
  control=part['control'];a=actors.get(label) or aa.spawn_actor_from_class(unreal.StationCabinet if control else unreal.StaticMeshActor,loc,rot);a.set_actor_label(label);a.set_folder_path('LodgeMigration/Kitchen')
  if control:
   a.moving_mesh.set_static_mesh(meshes[part['mesh']]);a.set_editor_property('sliding',control['motion']=='slide');a.set_editor_property('open_angle',-control.get('open_degrees',0));a.set_editor_property('open_offset',unreal.Vector(0,-100*control.get('open_metres',0),0))
   a.set_editor_property('collision_centers',[vec(c['center']) for c in part['collision']]);a.set_editor_property('collision_extents',[unreal.Vector(*[max(.05,v*100) for v in c['extent']]) for c in part['collision']]);a.rebuild_collision()
   # Aim at the exposed front, avoiding the empty interior of a drawer.
   front=next(c for c in part['collision'] if 'front' in c['source'].lower() or ('door' in c['source'].lower() and 'hinge' not in c['source'].lower()))
   a.set_editor_property('focus_location',vec(front['center']));a.set_editor_property('display_name','drawer' if control['motion']=='slide' else row['id'].lower() if row['id'] in {'Fridge','Microwave'} else 'cupboard')
   a.set_editor_property('movement_sound',standard.movement_sound);a.set_editor_property('closing_sound',standard.closing_movement_sound);a.motion_audio.set_relative_location(vec(front['center']),False,False)
  else:
   a.static_mesh_component.set_static_mesh(meshes[part['mesh']]);a.static_mesh_component.set_collision_profile_name('NoCollision' if part['role']=='Glass' else 'BlockAll')
  placed.append({'label':label,'mesh':part['mesh'],'moving':bool(control)})
assert ls.save_current_level();assert hashlib.sha256((REPO/'game/Content/MaldekRefinement/R12/Station_R12.umap').read_bytes()).hexdigest()==base['map_sha256']
RESULT={'assets':checks,'actors':placed,'textures':deps,'shader_errors':shaders,'original_map_unchanged':True};(dest/'install.json').write_text(json.dumps(RESULT,indent=2))

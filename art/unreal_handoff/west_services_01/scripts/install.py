"""Manifest-owned, idempotent delta import into the existing migration checkpoint."""
import unreal,json,hashlib,re,math
from pathlib import Path
P=Path(__file__).resolve().parents[1];R=P.parents[2];D=json.loads((P/'exports.json').read_text());B=json.loads((P/'baseline.json').read_text());o=B['origin'];root='/Game/MaldekRefinement/WestServices'
ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert w and w.get_name()=='Station_Lodge_Migration' and not ls.is_in_play_in_editor()
lib=unreal.EditorAssetLibrary;at=unreal.AssetToolsHelpers.get_asset_tools();ml=unreal.MaterialEditingLibrary;sm=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
assert hashlib.sha256(Path(D['source']).read_bytes()).hexdigest()==D['source_sha256']
unreal.SystemLibrary.execute_console_command(w,'Interchange.FeatureFlags.Import.FBX 0')
def safe(n):return re.sub('[^A-Za-z0-9_]','_',n)
materials={}
for n,q in D['materials'].items():
 path=root+'/Materials/M_'+safe(n);m=lib.load_asset(path)
 if not m or (JOB.get('reimport') and not JOB.get('only')):
  m=m or at.create_asset('M_'+safe(n),root+'/Materials',unreal.Material,unreal.MaterialFactoryNew());ml.delete_all_material_expressions(m)
  for key,prop in [('color',unreal.MaterialProperty.MP_BASE_COLOR),('roughness',unreal.MaterialProperty.MP_ROUGHNESS),('metallic',unreal.MaterialProperty.MP_METALLIC)]:
   node=ml.create_material_expression(m,unreal.MaterialExpressionConstant3Vector if key=='color' else unreal.MaterialExpressionConstant)
   if key=='color':node.set_editor_property('constant',unreal.LinearColor(*q[key]))
   else:node.set_editor_property('r',q[key])
   assert ml.connect_material_property(node,'',prop)
  for channel,file in D['textures'].get(n,{}).items():
   name='T_'+safe(n)+'_'+channel;tp=root+'/Textures/'+name;tex=lib.load_asset(tp)
   if not tex or JOB.get('reimport'):
    task=unreal.AssetImportTask();task.filename=str(P/'textures'/file);task.destination_path=root+'/Textures';task.destination_name=name;task.automated=True;task.save=False;task.replace_existing=True;at.import_asset_tasks([task]);tex=lib.load_asset(tp)
   assert tex;tex.set_editor_property('srgb',channel=='BaseColor');tex.set_editor_property('compression_settings',unreal.TextureCompressionSettings.TC_NORMALMAP if channel=='NormalGL' else unreal.TextureCompressionSettings.TC_DEFAULT)
   if channel=='NormalGL':tex.set_editor_property('flip_green_channel',True)
   assert lib.save_loaded_asset(tex);node=ml.create_material_expression(m,unreal.MaterialExpressionTextureSample);node.texture=tex;node.sampler_type=unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL if channel=='NormalGL' else unreal.MaterialSamplerType.SAMPLERTYPE_COLOR
   uv=ml.create_material_expression(m,unreal.MaterialExpressionTextureCoordinate);uv.coordinate_index=1;assert ml.connect_material_expressions(uv,'',node,'UVs');assert ml.connect_material_property(node,'RGB',unreal.MaterialProperty.MP_NORMAL if channel=='NormalGL' else unreal.MaterialProperty.MP_BASE_COLOR)
  if q['glass']:
   m.set_editor_property('blend_mode',unreal.BlendMode.BLEND_TRANSLUCENT);m.set_editor_property('two_sided',True);node=ml.create_material_expression(m,unreal.MaterialExpressionConstant);node.r=.16;assert ml.connect_material_property(node,'',unreal.MaterialProperty.MP_OPACITY)
  ml.recompile_material(m);assert lib.save_loaded_asset(m)
 materials[n]=m
assert not list(unreal.StationMigrationLibrary.validate_material_shaders(list(materials.values())))
actors={a.get_actor_label():a for a in aa.get_all_level_actors()};standard=actors['R12_Door_Control_side'];records=[]
def vec(v):return unreal.Vector(v[0]*100,-v[1]*100,v[2]*100)
def rot(M):return unreal.MathLibrary.make_rotation_from_axes(unreal.Vector(-M[0][0],M[1][0],M[2][0]),unreal.Vector(M[0][1],-M[1][1],-M[2][1]),unreal.Vector(-M[0][2],M[1][2],M[2][2]))
for r in D['assets']:
 if JOB.get('only') and r['key'] not in JOB['only']:continue
 shared=r['key'].startswith(('WS_','WS02_'))
 if JOB.get('shared_only') and not shared:continue
 path=root+'/Meshes/'+r['mesh'];mesh=lib.load_asset(path)
 if not mesh or JOB.get('reimport'):
  file=P/'fbx'/(r['mesh']+'.fbx');assert hashlib.sha256(file.read_bytes()).hexdigest()==r['sha256'];task=unreal.AssetImportTask();task.filename=str(file);task.destination_path=root+'/Meshes';task.automated=True;task.save=False;task.replace_existing=True;opt=unreal.FbxImportUI();opt.import_mesh=True;opt.import_materials=False;opt.import_textures=False;opt.automated_import_should_detect_type=False;opt.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH;data=opt.static_mesh_import_data;data.combine_meshes=True;data.auto_generate_collision=False;data.convert_scene=True;data.convert_scene_unit=True;data.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS;task.options=opt;at.import_asset_tasks([task]);mesh=lib.load_asset(path)
 assert mesh;bb=mesh.get_bounds();actual=[bb.origin-bb.box_extent,bb.origin+bb.box_extent];a,b=r['lo'],r['hi'];exp=[[100*a[0],-100*b[1],100*a[2]],[100*b[0],-100*a[1],100*b[2]]];err=max(abs(v-e[j]) for q,e in zip(actual,exp) for j,v in enumerate([q.x,q.y,q.z]));assert err<.2,(path,err)
 assert len(mesh.static_materials)==len(r['materials']),(path,'material slots')
 for i,n in enumerate(r['materials']):mesh.set_material(i,materials[n])
 sm.remove_collisions(mesh);mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE);ns=mesh.get_editor_property('nanite_settings');ns.set_editor_property('enabled',False);sm.set_nanite_settings(mesh,ns,True);assert lib.save_loaded_asset(mesh)
 M=r['matrix'];loc=unreal.Vector(o[0]-100*M[0][3],o[1]+100*M[1][3],o[2]+100*M[2][3]);rotation=rot(M);label='MIG_WS_'+safe(r['key']);control=r['control'];actor=actors.get(label) or aa.spawn_actor_from_class(unreal.StationCabinet if control else unreal.StaticMeshActor,loc,rotation);actor.set_actor_label(label);actor.set_folder_path('WestServices/'+('Mechanisms' if control else r['key'].split('_')[0]));actor.set_actor_location(loc,False,True);actor.set_actor_rotation(rotation,True)
 if control:
  actor.moving_mesh.set_static_mesh(mesh);actor.set_editor_property('sliding',control['slide']);actor.set_editor_property('open_angle',-control['angle']);actor.set_editor_property('open_offset',vec(control['offset']));cs=control['collisions'];assert cs,(label,'collision missing');actor.set_editor_property('collision_centers',[vec(c['center']) for c in cs]);actor.set_editor_property('collision_extents',[unreal.Vector(*[v*100 for v in c['extent']]) for c in cs]);actor.rebuild_collision();actor.set_editor_property('focus_location',vec(max(cs,key=lambda c:c['extent'][0]*c['extent'][1]*c['extent'][2])['center']));actor.set_editor_property('display_name','door' if 'Door' in r['key'] else 'drawer' if control['slide'] else 'service cover' if 'cover' in r['key'] or 'lid' in r['key'] else 'cabinet');actor.set_editor_property('movement_sound',standard.movement_sound);actor.set_editor_property('closing_sound',standard.closing_movement_sound)
 else:actor.static_mesh_component.set_static_mesh(mesh);actor.static_mesh_component.set_collision_profile_name('NoCollision' if r.get('nonblocking') else 'BlockAll')
 records.append({'actor':label,'mesh':path,'bounds_error_cm':err,'source_count':len(r['sources']),'control':bool(control)});(P/'import_progress.json').write_text(json.dumps(records,indent=2))
assert ls.save_current_level();(P/('patch_install.json' if JOB.get('only') else 'shared_install.json' if JOB.get('shared_only') else 'install.json')).write_text(json.dumps({'actors':records,'source_sha256':D['source_sha256'],'shader_errors':[]},indent=2));RESULT={'imported':len(records),'moving':sum(r['control'] for r in records)}

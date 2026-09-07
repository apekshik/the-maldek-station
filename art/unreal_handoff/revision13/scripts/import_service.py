"""Scoped VF08/VF09 import into the live R12 level; retain unrelated actors and components."""
import unreal,json,hashlib
from pathlib import Path
base=Path(__file__).resolve().parents[1];old=base.parent/'revision12';root='/Game/MaldekRefinement/R13'
manifest=json.loads((base/'handoff_manifest.json').read_text())
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);sm=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
lib=unreal.EditorAssetLibrary;at=unreal.AssetToolsHelpers.get_asset_tools();ml=unreal.MaterialEditingLibrary
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert world.get_name()=='Station_R12' and not levels.is_in_play_in_editor()
origin=json.loads((base.parent/'working_level_report.json').read_text())['station_origin']
def wp(p):return unreal.Vector(origin[0]-100*p[0],origin[1]+100*p[1],origin[2]+100*p[2])
def vec(v):return [v.x,v.y,v.z]
actors={a.get_actor_label():a for a in aa.get_all_level_actors()}
ledger_path=base/'integration_ledger.json';ledger=json.loads(ledger_path.read_text()) if ledger_path.exists() else {'assets':{},'retired':[]}
assert levels.save_current_level()
bindings={r['slot']:r['instance'] for r in json.loads((old/'material_bindings.json').read_text())['materials']}
baked=json.loads((base/'baked_materials.json').read_text());textures={}
for row in baked['sets'].values():
 for ch,f in row['textures'].items():
  path=root+'/Textures/'+Path(f).stem;tex=lib.load_asset(path)
  if not tex:
   task=unreal.AssetImportTask();task.filename=str(base/f);task.destination_path=root+'/Textures';task.automated=True;task.save=True;at.import_asset_tasks([task]);tex=lib.load_asset(path)
  assert tex;tex.set_editor_property('srgb',ch=='BaseColor');tex.set_editor_property('compression_settings',unreal.TextureCompressionSettings.TC_NORMALMAP if ch=='NormalDX' else unreal.TextureCompressionSettings.TC_MASKS if ch=='ORM' else unreal.TextureCompressionSettings.TC_DEFAULT);lib.save_loaded_asset(tex);textures[ch]=tex
for info in manifest['materials'].values():
 slot=info['slot']
 if slot in bindings:continue
 if 'Terrain' in slot:continue
 red=info['source_material']=='VF08_Oxide_Red'
 source='UE_VF06_Safety_ochre__Exterior' if red else slot.replace('__Indoor','__Exterior')
 assert source in bindings,(slot,source)
 path=root+'/Materials/MI_'+slot
 mi=lib.load_asset(path) or lib.duplicate_asset(bindings[source],path);assert mi
 if info['exposure']=='Indoor' and 'Lamp' not in slot:
  parent=mi.get_editor_property('parent').get_path_name().replace('_Exterior','_Interior');assert lib.does_asset_exist(parent),parent;ml.set_material_instance_parent(mi,lib.load_asset(parent))
 if red:
  for ch,tex in textures.items():ml.set_material_instance_texture_parameter_value(mi,ch,tex)
 ml.update_material_instance(mi);lib.save_loaded_asset(mi);bindings[slot]=mi.get_path_name()
(base/'material_bindings.json').write_text(json.dumps(bindings,indent=2))
unreal.SystemLibrary.execute_console_command(world,'Interchange.FeatureFlags.Import.FBX 0')
for r in manifest['chunks']:
 path=root+'/Meshes/'+r['name'];p=base/r['file'];assert hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256']
 mesh=lib.load_asset(path)
 if not mesh or ledger['assets'].get(r['name'],{}).get('sha256')!=r['sha256']:
  task=unreal.AssetImportTask();task.filename=str(p);task.destination_path=root+'/Meshes';task.automated=True;task.save=True;task.replace_existing=True
  opt=unreal.FbxImportUI();opt.import_mesh=True;opt.import_materials=False;opt.import_textures=False;opt.automated_import_should_detect_type=False;opt.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
  d=opt.static_mesh_import_data;d.combine_meshes=True;d.auto_generate_collision=False;d.convert_scene=True;d.convert_scene_unit=True;d.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS;task.options=opt;at.import_asset_tasks([task]);mesh=lib.load_asset(path)
 assert mesh,path
 b=mesh.get_bounds();actual=[vec(b.origin-b.box_extent),vec(b.origin+b.box_extent)];lo,hi=r['bounds'];wanted=[[100*lo[0],-100*hi[1],100*lo[2]],[100*hi[0],-100*lo[1],100*hi[2]]]
 error=max(abs(actual[j][i]-wanted[j][i]) for j in range(2) for i in range(3));assert error<.2,(r['name'],error)
 assert [str(s.material_slot_name) for s in mesh.static_materials]==r['material_slots'],r['name']
 count=sm.get_convex_collision_count(mesh)
 unique=set()
 for box in r['collision_boxes']:
  vs=box.get('vertices') or [[x,y,z] for x in [box['min'][0],box['max'][0]] for y in [box['min'][1],box['max'][1]] for z in [box['min'][2],box['max'][2]]]
  unique.add(tuple(sorted(tuple(round(v,4) for v in p) for p in vs)))
 assert len(unique)<=count<=r['collision_hulls'],(r['name'],count,len(unique),r['collision_hulls'])
 if r.get('complex_collision'):mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
 for i,s in enumerate(mesh.static_materials):mesh.set_material(i,lib.load_asset(r['preserve_material'][min(i,len(r['preserve_material'])-1)] if r.get('complex_collision') else bindings[str(s.material_slot_name)]))
 ns=mesh.get_editor_property('nanite_settings');ns.set_editor_property('enabled',r['nanite'])
 if r['nanite']:
  ns.set_editor_property('fallback_relative_error',0.0);ns.set_editor_property('fallback_percent_triangles',1.0);ns.set_editor_property('fallback_target',unreal.NaniteFallbackTarget.PERCENT_TRIANGLES)
 sm.set_nanite_settings(mesh,ns,True)
 if r['role'] in ['grating','thin']:
  reduction=unreal.StaticMeshReductionOptions(auto_compute_lod_screen_size=False,reduction_settings=[unreal.StaticMeshReductionSettings(percent_triangles=1,screen_size=1),unreal.StaticMeshReductionSettings(percent_triangles=.5,screen_size=.12),unreal.StaticMeshReductionSettings(percent_triangles=.22,screen_size=.04)]);assert sm.set_lods(mesh,reduction)==3
 lib.save_loaded_asset(mesh)
 label=r['name'].replace('SM_','');a=actors.get(label) or aa.spawn_actor_from_class(unreal.StaticMeshActor,wp(r['pivot']),unreal.Rotator(yaw=180));a.set_actor_label(label);a.set_actor_location(wp(r['pivot']),False,True);a.set_actor_rotation(unreal.Rotator(yaw=180),False);a.set_folder_path('R13/Service/'+r.get('collection','Terrain'))
 c=a.static_mesh_component;c.set_static_mesh(mesh);c.set_editor_property('override_materials',[]);c.set_collision_profile_name('BlockAll' if count or r.get('complex_collision') else 'NoCollision');c.set_phys_material_override(lib.load_asset('/Game/MaldekRefinement/ForestTest/Audio/Surfaces/PM_'+r['physical_surface']))
 ledger['assets'][r['name']]={'sha256':r['sha256'],'actor':a.get_path_name(),'asset':path,'hulls':count,'bounds_error_cm':error};ledger_path.write_text(json.dumps(ledger,indent=2))
for a in aa.get_all_level_actors():
 for c in a.get_components_by_class(unreal.StaticMeshComponent):
  mesh=c.static_mesh
  if mesh and mesh.get_name() in manifest['retire_assets']:
   ledger['retired'].append({'actor':a.get_path_name(),'component':c.get_name(),'mesh':mesh.get_path_name()});c.set_static_mesh(None);c.set_editor_property('override_materials',[]);c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
assert set(r['mesh'].split('.')[-1] for r in ledger['retired'])==set(manifest['retire_assets'])
assert levels.save_current_level();ledger['saved']=True;ledger_path.write_text(json.dumps(ledger,indent=2));RESULT={'assets':len(ledger['assets']),'retired':len(ledger['retired']),'saved':True}

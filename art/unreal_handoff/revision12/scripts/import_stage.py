"""Strict R12 handoff importer. Exact component boundaries, checkpoint ledger, repeatable reruns."""
import unreal,json,hashlib,re,time
from pathlib import Path
base=Path(__file__).resolve().parents[1];root='/Game/MaldekRefinement/R12'
manifest=json.loads((base/'handoff_manifest.json').read_text());inventory=json.loads((base/'replacement_inventory.json').read_text())
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);lib=unreal.EditorAssetLibrary;sm=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert world.get_name()=='Station_R12';assert not levels.is_in_play_in_editor()
assert json.loads((base/'checkpoint-verification.json').read_text())
stage=JOB.get('stage','Circulation');assert stage in ['Circulation','Architecture','Infrastructure']
chunks=[r for r in manifest['chunks'] if r['stage']==stage]
ledger_path=base/'integration_ledger.json';ledger=json.loads(ledger_path.read_text()) if ledger_path.exists() else {'assets':{},'retired':{},'stages':{}}
actors={a.get_path_name():a for a in aa.get_all_level_actors()};expected={r['r12_path']:r for r in inventory}
targets={}
for r in manifest['chunks']:
 for t in r['replacement_targets']:targets[t['actor']+'|'+t['component']]=t
for t in manifest['retire_components']:targets[t['actor']+'|'+t['component']]=t
for key,t in targets.items():
 assert t['actor'] in expected and t['actor'] in actors,('Missing explicit replacement actor',key)
 cs=[c for c in actors[t['actor']].get_components_by_class(unreal.StaticMeshComponent) if c.get_name()==t['component']];assert len(cs)==1,key
 actual=cs[0].static_mesh
 if key not in ledger['retired']:assert actual and actual.get_path_name()==t['old_mesh'],('Old mesh changed',key,str(actual),t['old_mesh'])
 else:assert actual is None,('Retired component unexpectedly rebound',key)
for r in manifest['chunks']:
 p=base/r['file'];assert p.exists() and hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256'],r['name']
 assert all(s in [m['slot'] for m in manifest['materials'].values()] for s in r['material_slots']),r['name']
assert json.loads((base/'bridge_source_preservation.json').read_text())['success']
if JOB.get('dry_run'):
 RESULT={'success':True,'dry_run':True,'stage':stage,'stage_assets':len(chunks),'total_assets':len(manifest['chunks']),'explicit_replacement_components':len(targets),'preserved_actors':len(inventory)-len({t['actor'] for t in targets.values()})}
 (base/(stage.lower()+'_dry_run.json')).write_text(json.dumps(RESULT,indent=2))
else:
 pilot=json.loads((base/'pilot/acceptance.json').read_text());assert pilot['accepted'],'Pilot material/geometry acceptance required'
 if stage!='Circulation':assert ledger['stages'].get('Circulation',{}).get('accepted'),'Accept circulation before architecture/infrastructure'
 if stage=='Infrastructure':assert ledger['stages'].get('Architecture',{}).get('accepted'),'Accept architecture first'
 bindings={r['slot']:r['instance'] for r in json.loads((base/'material_bindings.json').read_text())['materials']}
 for r in chunks:
  if r.get('complex_collision'):continue
  assert all(s in bindings and lib.does_asset_exist(bindings[s]) for s in r['material_slots']),r['name']
 origin=json.loads((base.parent/'working_level_report.json').read_text())['station_origin']
 def wp(p):return unreal.Vector(origin[0]-100*p[0],origin[1]+100*p[1],origin[2]+100*p[2])
 def vec(v):return [v.x,v.y,v.z]
 at=unreal.AssetToolsHelpers.get_asset_tools();unreal.SystemLibrary.execute_console_command(world,'Interchange.FeatureFlags.Import.FBX 0')
 progress=unreal.ScopedSlowTask(len(chunks),'Import approved VF07 '+stage);progress.make_dialog(False)
 for r in chunks:
  progress.enter_progress_frame(1,r['name']);path=root+'/Meshes/'+r['name'];previous=ledger['assets'].get(r['name']);mesh=lib.load_asset(path) if lib.does_asset_exist(path) else None
  if not mesh or not previous or previous['sha256']!=r['sha256']:
   task=unreal.AssetImportTask();task.filename=str(base/r['file']);task.destination_path=root+'/Meshes';task.automated=True;task.save=True;task.replace_existing=True
   opt=unreal.FbxImportUI();opt.import_mesh=True;opt.import_materials=False;opt.import_textures=False;opt.automated_import_should_detect_type=False;opt.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
   d=opt.static_mesh_import_data;d.combine_meshes=True;d.auto_generate_collision=False;d.convert_scene=True;d.convert_scene_unit=True;d.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS;task.options=opt
   at.import_asset_tasks([task]);mesh=lib.load_asset(path);assert mesh,path
  b=mesh.get_bounds();actual=[vec(b.origin-b.box_extent),vec(b.origin+b.box_extent)];lo,hi=r['bounds'];wanted=[[100*lo[0],-100*hi[1],100*lo[2]],[100*hi[0],-100*lo[1],100*hi[2]]]
  error=max(abs(actual[j][i]-wanted[j][i]) for j in range(2) for i in range(3));assert error<.2,(r['name'],error)
  assert [str(s.material_slot_name) for s in mesh.static_materials]==r['material_slots'],r['name']
  # FBX importer coalesces identical UCX hulls (two adjoining rails can share a post).
  # Account only for geometrically identical vertex sets, never arbitrary lost hulls.
  unique_hulls={}
  for box in r['collision_boxes']:
   vertices=box.get('vertices') or [[x,y,z] for x in [box['min'][0],box['max'][0]] for y in [box['min'][1],box['max'][1]] for z in [box['min'][2],box['max'][2]]]
   signature=tuple(sorted(tuple(round(v,4) for v in p) for p in vertices))
   unique_hulls.setdefault(signature,[]).append(box['source'])
  count=sm.get_convex_collision_count(mesh);assert len(unique_hulls)<=count<=r['collision_hulls'],(r['name'],count,len(unique_hulls),r['collision_hulls'])
  if r.get('complex_collision'):
   mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
   for i,s in enumerate(mesh.static_materials):mesh.set_material(i,lib.load_asset(r['preserve_material'][min(i,len(r['preserve_material'])-1)]))
  else:
   for i,s in enumerate(mesh.static_materials):mesh.set_material(i,lib.load_asset(r.get('material_bindings_override',{}).get(str(s.material_slot_name),bindings[str(s.material_slot_name)])))
  ns=mesh.get_editor_property('nanite_settings');ns.set_editor_property('enabled',r['nanite']);mesh.set_editor_property('nanite_settings',ns)
  if r['role'] in ['grating','thin'] and not previous:
   reduction=unreal.StaticMeshReductionOptions(auto_compute_lod_screen_size=False,reduction_settings=[unreal.StaticMeshReductionSettings(percent_triangles=1,screen_size=1),unreal.StaticMeshReductionSettings(percent_triangles=.5,screen_size=.12),unreal.StaticMeshReductionSettings(percent_triangles=.22,screen_size=.04)])
   assert sm.set_lods(mesh,reduction)==3,r['name']
  lib.save_loaded_asset(mesh)
  a=actors.get(previous['actor']) if previous else None
  if a:assert a.get_actor_label()==r['name'].replace('SM_',''),('Stored actor identity reused unexpectedly',a.get_path_name())
  if not a:
   a=aa.spawn_actor_from_class(unreal.StaticMeshActor,wp(r['pivot']),unreal.Rotator(yaw=180));assert a
  a.set_actor_label(r['name'].replace('SM_',''));a.set_actor_location(wp(r['pivot']),False,True);a.set_actor_rotation(unreal.Rotator(yaw=180),False);a.set_actor_scale3d(unreal.Vector(1,1,1))
  c=a.static_mesh_component;c.set_static_mesh(mesh);c.set_editor_property('override_materials',[]);c.set_collision_profile_name('BlockAll' if count or r.get('complex_collision') else 'NoCollision')
  pm=lib.load_asset('/Game/MaldekRefinement/ForestTest/Audio/Surfaces/PM_'+r['physical_surface']);assert pm;c.set_phys_material_override(pm)
  a.set_folder_path('R12/'+stage+'/'+r['collection'])
  if r['replacement_targets']:
   parent=actors[r['replacement_targets'][0]['actor']]
   a.attach_to_actor(parent,unreal.Name('None'),unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,False)
  ledger['assets'][r['name']]={'sha256':r['sha256'],'asset':path,'actor':a.get_path_name(),'stage':stage,'bounds_error_cm':error,'hulls':count,'coincident_hull_sources':[v for v in unique_hulls.values() if len(v)>1],'physical_surface':r['physical_surface'],'material_slots':r['material_slots']}
  ledger_path.write_text(json.dumps(ledger,indent=2))
 # Retire old combined components only after every replacement for this stage exists.
 stage_targets={t['actor']+'|'+t['component']:t for r in chunks for t in r['replacement_targets']}
 for t in manifest['retire_components']:
  target_stage=t.get('stage','Architecture' if 'Doors_' in t['actor'] else 'Circulation')
  if target_stage==stage:stage_targets[t['actor']+'|'+t['component']]=t
 for key,t in stage_targets.items():
  if key in ledger['retired']:continue
  c=next(c for c in actors[t['actor']].get_components_by_class(unreal.StaticMeshComponent) if c.get_name()==t['component'])
  c.set_static_mesh(None);c.set_editor_property('override_materials',[]);c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION);ledger['retired'][key]=t
 assert levels.save_current_level()
 ledger['stages'][stage]={'imported':True,'accepted':False,'assets':len(chunks),'saved':True};ledger_path.write_text(json.dumps(ledger,indent=2))
 RESULT=ledger['stages'][stage]

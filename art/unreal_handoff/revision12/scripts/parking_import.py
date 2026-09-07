"""Exact parking replacement. Run dry first; preserve car, player, audio and service port."""
import unreal,json,hashlib
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'parking';m=json.loads((out/'handoff.json').read_text())
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);sm=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem);lib=unreal.EditorAssetLibrary
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert w.get_name()=='Station_R12' and not ls.is_in_play_in_editor()
assert hashlib.sha256((b.parent/'revision13/terrain_grid.json').read_bytes()).hexdigest()==m['terrain_source_sha256'],'Service terrain changed: rebuild parking export'
actors={a.get_actor_label():a for a in aa.get_all_level_actors()}
targets={'R12_Retained_Parking':'SM_R12_Retained_Parking','R12_Forest_Approach_Aligned':'SM_R12_Forest_Approach_Aligned','R13_Terrain':'SM_R13_Terrain'}
ledgerpath=out/'integration.json';ledger=json.loads(ledgerpath.read_text()) if ledgerpath.exists() else {'assets':{},'retired':[]}
for label,name in targets.items():
 assert label in actors,label
 mesh=actors[label].static_mesh_component.static_mesh
 assert (mesh and mesh.get_name()==name) or (mesh is None and label in ledger['retired']),(label,str(mesh))
bindings={r['slot']:r['instance'] for r in json.loads((b/'material_bindings.json').read_text())['materials']}
gravel='/Game/MaldekRefinement/R12/Materials/Instances/MI_Dry_UE_VF07_Compacted_Gravel__Exterior'
terrainmat=next(r for r in json.loads((b/'handoff_manifest.json').read_text())['chunks'] if r['name']=='SM_R12_Terrain')['preserve_material'][0]
bindings.update({'UE_VF10_Compacted_Gravel__Exterior':gravel,'UE_Ground__Exterior':gravel,'UE_Ground_001__Exterior':gravel,'UE_VF10_Local_Stone__Exterior':terrainmat,'UE_VF07_Terrain_Study':terrainmat})
bindings['UE_Ground_001__Exterior']=next(r for r in json.loads((out/'live_before.json').read_text())['actors'] if r['label']=='R12_Forest_Approach_Aligned')['components'][0]['materials'][0]
for r in m['chunks']:
 assert hashlib.sha256((out/r['file']).read_bytes()).hexdigest()==r['sha256']
 for slot in r['material_slots']:assert slot in bindings and lib.does_asset_exist(bindings[slot]),slot
if JOB.get('dry_run',True):
 RESULT={'dry_run':True,'chunks':len(m['chunks']),'targets':targets};(out/'dry_run.json').write_text(json.dumps(RESULT,indent=2))
else:
 origin=json.loads((b.parent/'working_level_report.json').read_text())['station_origin']
 def wp(p):return unreal.Vector(origin[0]-100*p[0],origin[1]+100*p[1],origin[2]+100*p[2])
 unreal.SystemLibrary.execute_console_command(w,'Interchange.FeatureFlags.Import.FBX 0')
 for r in m['chunks']:
  task=unreal.AssetImportTask();task.filename=str(out/r['file']);task.destination_path='/Game/MaldekRefinement/R12/Parking/Meshes';task.automated=True;task.save=True;task.replace_existing=True
  opt=unreal.FbxImportUI();opt.import_mesh=True;opt.import_materials=False;opt.import_textures=False;opt.automated_import_should_detect_type=False;opt.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
  d=opt.static_mesh_import_data;d.combine_meshes=True;d.auto_generate_collision=False;d.convert_scene=True;d.convert_scene_unit=True;d.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS;task.options=opt
  unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task]);mesh=lib.load_asset(task.destination_path+'/'+r['name']);assert mesh
  bounds=mesh.get_bounds();lo,hi=r['bounds'];actual=[bounds.origin-bounds.box_extent,bounds.origin+bounds.box_extent];wanted=[[100*lo[0],-100*hi[1],100*lo[2]],[100*hi[0],-100*lo[1],100*hi[2]]]
  err=max(abs([actual[j].x,actual[j].y,actual[j].z][i]-wanted[j][i]) for j in range(2) for i in range(3));assert err<.2,(r['name'],err)
  for i,slot in enumerate(mesh.static_materials):mesh.set_material(i,lib.load_asset(bindings[str(slot.material_slot_name)]))
  count=sm.get_convex_collision_count(mesh)
  if r.get('complex_collision'):mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
  else:assert count==r['collision_hulls'],(r['name'],count,r['collision_hulls'])
  lib.save_loaded_asset(mesh)
  label=r['name'].replace('SM_','');a=actors.get(label) or aa.spawn_actor_from_class(unreal.StaticMeshActor,wp(r['pivot']),unreal.Rotator(yaw=180));a.set_actor_label(label);a.set_actor_location(wp(r['pivot']),False,True);a.set_actor_rotation(unreal.Rotator(yaw=180),False);a.set_folder_path('R12/Parking')
  c=a.static_mesh_component;c.set_static_mesh(mesh);c.set_editor_property('override_materials',[]);c.set_collision_profile_name('BlockAll' if count or r.get('complex_collision') else 'NoCollision');c.set_phys_material_override(lib.load_asset('/Game/MaldekRefinement/ForestTest/Audio/Surfaces/PM_'+r['physical_surface']))
  ledger['assets'][r['name']]={'actor':a.get_path_name(),'mesh':mesh.get_path_name(),'bounds_error_cm':err,'collision_hulls':count,'sha256':r['sha256']}
  ledgerpath.write_text(json.dumps(ledger,indent=2))
 for label in targets:
  c=actors[label].static_mesh_component;c.set_static_mesh(None);c.set_editor_property('override_materials',[]);c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
  if label not in ledger['retired']:ledger['retired'].append(label)
 assert ls.save_current_level();ledger['saved']=True;ledgerpath.write_text(json.dumps(ledger,indent=2));RESULT=ledger

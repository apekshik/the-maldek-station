"""Import the bounded shell pilot into the migration map only."""
import unreal,json,hashlib
from pathlib import Path
OUT=Path(__file__).resolve().parents[1];REPO=OUT.parents[2]
kind=JOB.get('kind','Shell');assert kind in ['Shell','Deck']
data=json.loads((OUT/(kind.lower()+'_exports.json')).read_text());baseline=json.loads((OUT/'before.json').read_text());o=baseline['origin']
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert w.get_name()=='Station_Lodge_Migration' and not ls.is_in_play_in_editor()
lib=unreal.EditorAssetLibrary;at=unreal.AssetToolsHelpers.get_asset_tools();ml=unreal.MaterialEditingLibrary
root='/Game/MaldekRefinement/PassengerLodge/'+kind+'Pilot';bindings={}
for i,(name,props) in enumerate(sorted(data['materials'].items())):
 path=root+'/Materials/M_Pilot_'+str(i);m=lib.load_asset(path)
 if not m:
  m=at.create_asset('M_Pilot_'+str(i),root+'/Materials',unreal.Material,unreal.MaterialFactoryNew())
  n=ml.create_material_expression(m,unreal.MaterialExpressionConstant3Vector,-300,0);n.constant=unreal.LinearColor(*props['color'])
  assert ml.connect_material_property(n,'',unreal.MaterialProperty.MP_BASE_COLOR)
  for j,(key,pin) in enumerate([('roughness',unreal.MaterialProperty.MP_ROUGHNESS),('metallic',unreal.MaterialProperty.MP_METALLIC)]):
   n=ml.create_material_expression(m,unreal.MaterialExpressionConstant,-300,150+j*150);n.r=props[key];assert ml.connect_material_property(n,'',pin)
  ml.recompile_material(m);lib.save_loaded_asset(m)
 bindings[name]=m
actors={a.get_actor_label():a for a in aa.get_all_level_actors()};rows=[]
unreal.SystemLibrary.execute_console_command(w,'Interchange.FeatureFlags.Import.FBX 0')
for r in data['assets']:
 path=root+'/Meshes/'+r['name'];mesh=lib.load_asset(path)
 if not mesh:
  task=unreal.AssetImportTask();task.filename=str(OUT/'fbx'/(r['name']+'.fbx'));task.destination_path=root+'/Meshes';task.automated=True;task.save=True
  opt=unreal.FbxImportUI();opt.import_mesh=True;opt.import_materials=False;opt.import_textures=False;opt.automated_import_should_detect_type=False;opt.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
  d=opt.static_mesh_import_data;d.combine_meshes=True;d.auto_generate_collision=False;d.convert_scene=True;d.convert_scene_unit=True;d.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS;task.options=opt
  at.import_asset_tasks([task]);mesh=lib.load_asset(path)
 assert mesh,path
 b=mesh.get_bounds();lo=b.origin-b.box_extent;hi=b.origin+b.box_extent;p=r['pivot']
 expected=[[100*(r['lo'][0]-p[0]),-100*(r['hi'][1]-p[1]),100*(r['lo'][2]-p[2])],[100*(r['hi'][0]-p[0]),-100*(r['lo'][1]-p[1]),100*(r['hi'][2]-p[2])]]
 error=max(abs(x-y) for vec,exp in zip([lo,hi],expected) for x,y in zip([vec.x,vec.y,vec.z],exp));assert error<.2,(path,error)
 for i,slot in enumerate(mesh.static_materials):
  # Slot order remains the source order; labels may be sanitized by FBX.
  mesh.set_material(i,bindings[r['materials'][i]])
 mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE);lib.save_loaded_asset(mesh)
 label=r['name'].replace('SM_','MIG_');a=actors.get(label)
 if not a:a=aa.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(o[0]-100*p[0],o[1]+100*p[1],o[2]+100*p[2]),unreal.Rotator(yaw=180));a.set_actor_label(label)
 a.static_mesh_component.set_static_mesh(mesh);a.static_mesh_component.set_collision_profile_name('BlockAll');a.set_folder_path('LodgeMigration/'+kind+'Pilot')
 rows.append({'asset':path,'actor':a.get_name(),'bounds_error_cm':error})
# Exact old hall components, verified against the baseline; retain actors for rollback.
retired=[]
targets=[f'R12_VF06_Waiting_Hall_{i:03d}_{k}' for i,k in enumerate(['solid','solid','glass','solid','floor','floor','solid','solid','floor','glass','solid','floor','solid','solid','solid'])] if kind=='Shell' else json.loads((OUT/'deck_replacements.json').read_text())
for row in baseline['actors']:
 if row['label'] not in targets:continue
 a=actors[row['label']]
 for c in a.get_components_by_class(unreal.StaticMeshComponent):
  previous=next(x for x in row['components'] if x['name']==c.get_name())
  assert c.static_mesh is None or c.static_mesh.get_path_name()==previous['mesh']
  c.set_static_mesh(None);c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
 retired.append(row['label'])
assert len(retired)==len(targets)
assert ls.save_current_level()
assert hashlib.sha256((REPO/'game/Content/MaldekRefinement/R12/Station_R12.umap').read_bytes()).hexdigest()==baseline['map_sha256']
RESULT={'assets':rows,'retired':retired,'original_unchanged':True,'stage':'shell geometry pilot; materials are provisional; deck and mechanisms pending'}
(OUT/(kind.lower()+'_install.json')).write_text(json.dumps(RESULT,indent=2))

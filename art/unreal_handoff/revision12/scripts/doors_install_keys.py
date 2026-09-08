"""Import keyed variants and enable drag locks on the seven standard doors only."""
import unreal,json,hashlib
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'doors/key_lock';manifest=json.loads((out/'manifest.json').read_text())
lib=unreal.EditorAssetLibrary;at=unreal.AssetToolsHelpers.get_asset_tools();ml=unreal.MaterialEditingLibrary;sm=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem);ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert not ls.is_in_play_in_editor();root='/Game/MaldekRefinement/R12/Doors';dest=root+'/KeyLock';mats={};created=[]
for part in ['Leaf','Fixed','Glass']:
 for slot in lib.load_asset(root+'/Meshes/SM_StationDoor_'+part).static_materials:mats[str(slot.material_slot_name)]=slot.material_interface
for name,info in manifest['materials'].items():
 slot=info['slot']
 if slot in mats:continue
 m=lib.load_asset(dest+'/Materials/M_'+slot) or at.create_asset('M_'+slot,dest+'/Materials',unreal.Material,unreal.MaterialFactoryNew());ml.delete_all_material_expressions(m)
 for val,prop in [(info['base_color'][:3],unreal.MaterialProperty.MP_BASE_COLOR),(info['metallic'],unreal.MaterialProperty.MP_METALLIC),(info['roughness'],unreal.MaterialProperty.MP_ROUGHNESS)]:
  vec=isinstance(val,list);n=ml.create_material_expression(m,unreal.MaterialExpressionConstant3Vector if vec else unreal.MaterialExpressionConstant);n.set_editor_property('constant' if vec else 'r',unreal.LinearColor(*val,1) if vec else val);assert ml.connect_material_property(n,'',prop)
 ml.recompile_material(m);lib.save_loaded_asset(m);mats[slot]=m;created.append(m)
assert not unreal.StationMigrationLibrary.validate_material_shaders(created)
unreal.SystemLibrary.execute_console_command(None,'Interchange.FeatureFlags.Import.FBX 0');meshes={};rows=[]
for row in manifest['chunks']:
 file=out/row['file'];assert hashlib.sha256(file.read_bytes()).hexdigest()==row['sha256'];t=unreal.AssetImportTask();t.filename=str(file);t.destination_path=dest+'/Meshes';t.automated=True;t.save=True;t.replace_existing=True
 opt=unreal.FbxImportUI();opt.import_materials=False;opt.import_textures=False;opt.automated_import_should_detect_type=False;opt.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH;d=opt.static_mesh_import_data;d.combine_meshes=True;d.auto_generate_collision=False;d.convert_scene=True;d.convert_scene_unit=True;d.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS;t.options=opt;at.import_asset_tasks([t]);mesh=lib.load_asset(dest+'/Meshes/'+row['name']);assert mesh
 for i,slot in enumerate(mesh.static_materials):mesh.set_material(i,mats[str(slot.material_slot_name)])
 box=mesh.get_bounding_box();actual=[box.min.to_tuple(),box.max.to_tuple()];lo,hi=row['bounds'];wanted=[[100*lo[0],-100*hi[1],100*lo[2]],[100*hi[0],-100*lo[1],100*hi[2]]];error=max(abs(actual[j][i]-wanted[j][i]) for j in range(2) for i in range(3));assert error<.02,(row['name'],error)
 sm.remove_collisions(mesh);ns=mesh.get_editor_property('nanite_settings');ns.set_editor_property('enabled',False);sm.set_nanite_settings(mesh,ns,True);assert lib.save_loaded_asset(mesh);meshes[row['name'].replace('SM_KeyLock_','')]=mesh;rows.append({'mesh':mesh.get_path_name(),'bounds_error_cm':error,'triangles':row['triangles']})
def assign(o,physical):
 o.set_editor_property('has_key_lock',physical);o.set_editor_property('key_available',True)
 for comp,name in [('key_housing','Housing'),('key_plug','Plug'),('interior_key_plug','Plug'),('service_key','Key')]:getattr(o,comp).set_static_mesh(meshes[name])
 if physical:o.set_editor_property('locked',True)
for name in ['Standard','Keypad']:
 bp=lib.load_asset(root+'/BP_StationDoor_'+name);cdo=unreal.get_default_object(bp.generated_class());assign(cdo,name=='Standard')
 if name=='Standard':cdo.leaf.set_static_mesh(meshes['ControlLeaf'])
 unreal.BlueprintEditorLibrary.compile_blueprint(bp);assert lib.save_loaded_asset(bp)
mapping={'R12_Door_Control_side':'Control','R12_Door_Quarters':'Quarters','R12_Door_Hall_north':'Hall','R12_Door_Hall_south':'Hall','R12_Door_Generator_south':'GeneratorInward','R12_Door_Generator_west':'Generator','R12_Door_Workshop_shared':'Workshop'}
before={a.get_actor_label():a.get_actor_transform() for a in aa.get_all_level_actors()};placed=[]
for a in aa.get_all_level_actors():
 if not isinstance(a,unreal.StationDoor):continue
 name=a.get_actor_label();physical=name in mapping;old_collision=a.leaf_collision.get_editor_property('relative_location');old_extent=a.leaf_collision.get_unscaled_box_extent();assign(a,physical)
 if physical:
  # Preserve indoor/exterior material overrides by slot rather than material index.
  prior={str(slot.material_slot_name):a.leaf.get_material(i) for i,slot in enumerate(a.leaf.static_mesh.static_materials)};a.leaf.set_static_mesh(meshes[mapping[name]+'Leaf'])
  for i,slot in enumerate(a.leaf.static_mesh.static_materials):
   if str(slot.material_slot_name) in prior:a.leaf.set_material(i,prior[str(slot.material_slot_name)])
 assert a.leaf_collision.get_editor_property('relative_location')==old_collision and a.leaf_collision.get_unscaled_box_extent()==old_extent
 a.key_lock_root.set_relative_location(unreal.Vector(114.6,old_collision.y,100),False,False);a.key_lock_root.set_world_scale3d(unreal.Vector(1,1,1))
 for comp in [a.key_housing,a.key_plug,a.interior_key_plug]:comp.set_visibility(physical)
 a.service_key.set_visibility(False);placed.append({'label':name,'key_lock':physical,'locked':a.is_locked(),'keypad':a.has_keypad})
for a in aa.get_all_level_actors():assert a.get_actor_transform()==before[a.get_actor_label()]
assert sum(r['key_lock'] for r in placed)==7 and sum(r['keypad'] for r in placed)==3;assert ls.save_current_level()
RESULT={'success':True,'meshes':rows,'doors':placed,'unchanged_actor_transforms':len(before),'walking_collision_unchanged':True};(out/'install.json').write_text(json.dumps(RESULT,indent=2))

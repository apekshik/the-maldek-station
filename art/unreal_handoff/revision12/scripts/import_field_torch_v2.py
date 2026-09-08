"""Import the reference-led torch and bind it to the existing R12 pawn only."""
import unreal,json
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'sensory_refine'/'torch_v2'
assert not unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).is_in_play_in_editor()
lib=unreal.EditorAssetLibrary;at=unreal.AssetToolsHelpers.get_asset_tools();ml=unreal.MaterialEditingLibrary
root='/Game/MaldekRefinement/R12/Player/TorchV2';mats={}
specs=[('Anodized',(.018,.023,.028),.85,.29),('Grip',(.015,.019,.023),.75,.42),
 ('Machined',(.32,.36,.4),1,.23),('Reflector',(.74,.77,.8),1,.12),
 ('Lens',(.075,.11,.13),0,.06),('Switch',(.012,.014,.017),.03,.70),('Markings',(.34,.36,.33),.15,.56)]
for name,color,metal,rough in specs:
 path=root+'/M_TorchV2_'+name;m=lib.load_asset(path)
 if not m:m=at.create_asset('M_TorchV2_'+name,root,unreal.Material,unreal.MaterialFactoryNew())
 ml.delete_all_material_expressions(m)
 for val,prop in [(color,unreal.MaterialProperty.MP_BASE_COLOR),(metal,unreal.MaterialProperty.MP_METALLIC),(rough,unreal.MaterialProperty.MP_ROUGHNESS)]:
  vec=isinstance(val,tuple);n=ml.create_material_expression(m,unreal.MaterialExpressionConstant3Vector if vec else unreal.MaterialExpressionConstant)
  n.set_editor_property('constant' if vec else 'r',unreal.LinearColor(*val,1) if vec else val);ml.connect_material_property(n,'',prop)
 if name=='Lens':
  m.set_editor_property('blend_mode',unreal.BlendMode.BLEND_TRANSLUCENT)
  n=ml.create_material_expression(m,unreal.MaterialExpressionConstant);n.set_editor_property('r',.12);ml.connect_material_property(n,'',unreal.MaterialProperty.MP_OPACITY)
 ml.recompile_material(m);assert lib.save_loaded_asset(m);mats[name]=m
unreal.SystemLibrary.execute_console_command(None,'Interchange.FeatureFlags.Import.FBX 0')
t=unreal.AssetImportTask();t.filename=str(out/'SM_Torch_Field_V2.fbx');t.destination_path=root;t.automated=True;t.save=True;t.replace_existing=True
opt=unreal.FbxImportUI();opt.import_materials=False;opt.import_textures=False;opt.automated_import_should_detect_type=False;opt.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
opt.static_mesh_import_data.combine_meshes=True;opt.static_mesh_import_data.auto_generate_collision=False
opt.static_mesh_import_data.convert_scene=True;opt.static_mesh_import_data.convert_scene_unit=True
opt.static_mesh_import_data.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS;t.options=opt
at.import_asset_tasks([t]);mesh=lib.load_asset(root+'/SM_Torch_Field_V2');assert mesh
for i,slot in enumerate(mesh.static_materials):mesh.set_material(i,mats[str(slot.material_slot_name)])
unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem).remove_collisions(mesh);assert lib.save_loaded_asset(mesh)
box=mesh.get_bounding_box();size=box.max-box.min
assert abs(size.x-23.18)<.1 and abs(size.y-5.715)<.1,(size.x,size.y,size.z)
bp=lib.load_asset('/Game/MaldekRefinement/R12/Player/BP_StationWalker_Polished')
p=unreal.get_default_object(bp.generated_class());c=p.get_component_by_class(unreal.StationPlayerPresentationComponent)
c.set_editor_property('detailed_torch_mesh',mesh);c.set_editor_property('held_motion_scale',.15)
beam=p.get_component_by_class(unreal.SpotLightComponent);beam.set_editor_property('relative_location',unreal.Vector(40,17.5,-11))
unreal.BlueprintEditorLibrary.compile_blueprint(bp);assert lib.save_loaded_asset(bp,False)
assert abs(p.get_component_by_class(unreal.SurfaceFootstepComponent).volume-3.5)<.01
assert abs(c.idle_sway_scale-5)<.01
errors=list(unreal.StationMigrationLibrary.validate_material_shaders(list(mats.values())));assert not errors,errors
RESULT={'success':True,'mesh':mesh.get_path_name(),'dimensions_cm':list(size.to_tuple()),'materials':len(mats),'held_motion_scale':c.held_motion_scale,'foot_volume':3.5,'idle_sway_scale':5,'map_modified':False}
(out/'import.json').write_text(json.dumps(RESULT,indent=2))

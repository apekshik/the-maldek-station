import unreal,json
from pathlib import Path
out=Path(__file__).resolve().parents[1];rev=out/'revision06';root='/Game/MaldekRefinement/R06';lib=unreal.EditorAssetLibrary;ml=unreal.MaterialEditingLibrary;at=unreal.AssetToolsHelpers.get_asset_tools()
unreal.SystemLibrary.execute_console_command(None,'Interchange.FeatureFlags.Import.FBX 0')
textures=out.parents[1]/'art/blender/revision_03/assets/textures'
for f in textures.glob('*.png'):
 if not any(s in f.name for s in ['diff','alpha']):continue
 t=unreal.AssetImportTask();t.filename=str(f);t.destination_path=root+'/Textures';t.automated=True;t.save=True;t.replace_existing=True;at.import_asset_tasks([t])
def material(name):
 path=root+'/Materials/M_'+name
 
 m=lib.load_asset(path) or at.create_asset('M_'+name,root+'/Materials',unreal.Material,unreal.MaterialFactoryNew());ml.delete_all_material_expressions(m);twig='twig' in name
 texname=name if any(s in name for s in ['trunk','twig']) else 'pine_tree_01_bark'
 tx=ml.create_material_expression(m,unreal.MaterialExpressionTextureSample);tx.texture=lib.load_asset(root+'/Textures/'+texname+'_diff_1k');assert tx.texture,texname
 if twig:
  m.set_editor_property('blend_mode',unreal.BlendMode.BLEND_MASKED);m.set_editor_property('two_sided',True)
  alpha=ml.create_material_expression(m,unreal.MaterialExpressionTextureSample);alpha.texture=lib.load_asset(root+'/Textures/pine_tree_01_twig_alpha_1k');assert ml.connect_material_property(alpha,'R',unreal.MaterialProperty.MP_OPACITY_MASK)
 n=ml.create_material_expression(m,unreal.MaterialExpressionVertexNormalWS);mask=ml.create_material_expression(m,unreal.MaterialExpressionComponentMask);mask.set_editor_property('r',False);mask.set_editor_property('g',False);mask.set_editor_property('b',True);assert ml.connect_material_expressions(n,'',mask,'')
 clamp=ml.create_material_expression(m,unreal.MaterialExpressionClamp);assert ml.connect_material_expressions(mask,'',clamp,'')
 snow=ml.create_material_expression(m,unreal.MaterialExpressionConstant3Vector);snow.set_editor_property('constant',unreal.LinearColor(.32,.37,.42,1))
 lerp=ml.create_material_expression(m,unreal.MaterialExpressionLinearInterpolate);assert ml.connect_material_expressions(tx,'RGB',lerp,'A');assert ml.connect_material_expressions(snow,'',lerp,'B');assert ml.connect_material_expressions(clamp,'',lerp,'Alpha');assert ml.connect_material_property(lerp,'',unreal.MaterialProperty.MP_BASE_COLOR)
 rough=ml.create_material_expression(m,unreal.MaterialExpressionConstant);rough.r=.85;ml.connect_material_property(rough,'',unreal.MaterialProperty.MP_ROUGHNESS);ml.recompile_material(m);lib.save_loaded_asset(m);return m
for file in (rev/'fbx').glob('*.fbx'):
 task=unreal.AssetImportTask();task.filename=str(file);task.destination_path=root+'/Meshes';task.automated=True;task.save=True;task.replace_existing=True
 opt=unreal.FbxImportUI();opt.import_mesh=True;opt.import_materials=False;opt.import_textures=False;opt.automated_import_should_detect_type=False;opt.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
 d=opt.static_mesh_import_data;d.combine_meshes=True;d.auto_generate_collision=False;d.convert_scene=True;d.convert_scene_unit=True;d.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS;task.options=opt;at.import_asset_tasks([task]);mesh=lib.load_asset(root+'/Meshes/'+file.stem);assert mesh
 if 'Pine' in file.stem:
  for i,s in enumerate(mesh.static_materials):mesh.set_material(i,material(str(s.material_slot_name)))
 else:
  mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
 lib.save_loaded_asset(mesh)
(rev/'asset_import.json').write_text(json.dumps({'complete':True}))



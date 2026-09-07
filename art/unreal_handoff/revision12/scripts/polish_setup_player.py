"""R12-owned player assets, focusable optics and a detailed held torch."""
import unreal,json
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'polish';root='/Game/MaldekRefinement/R12/Player';lib=unreal.EditorAssetLibrary;ml=unreal.MaterialEditingLibrary;at=unreal.AssetToolsHelpers.get_asset_tools()
ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
def asset(name,folder,cls,factory):return lib.load_asset(folder+'/'+name) if lib.does_asset_exist(folder+'/'+name) else at.create_asset(name,folder,cls,factory)
materials={}
for name,color,metal,rough in [('Anodized',(.032,.041,.049),.9,.32),('Grip',(.021,.025,.028),.12,.72),('Machined',(.29,.32,.34),1,.24),('Reflector',(.63,.67,.7),1,.17),('Lens',(.10,.16,.19),.25,.14),('Switch',(.12,.14,.13),.15,.65)]:
 m=asset('M_Torch_'+name,root+'/Materials',unreal.Material,unreal.MaterialFactoryNew());ml.delete_all_material_expressions(m)
 v=ml.create_material_expression(m,unreal.MaterialExpressionConstant3Vector);v.set_editor_property('constant',unreal.LinearColor(*color,1));ml.connect_material_property(v,'',unreal.MaterialProperty.MP_BASE_COLOR)
 for value,prop in [(metal,unreal.MaterialProperty.MP_METALLIC),(rough,unreal.MaterialProperty.MP_ROUGHNESS)]:
  v=ml.create_material_expression(m,unreal.MaterialExpressionConstant);v.set_editor_property('r',value);ml.connect_material_property(v,'',prop)
 ml.recompile_material(m);lib.save_loaded_asset(m);materials[name]=m
unreal.SystemLibrary.execute_console_command(None,'Interchange.FeatureFlags.Import.FBX 0')
path=root+'/Meshes/SM_Torch_Field';mesh=lib.load_asset(path)
if not mesh:
 task=unreal.AssetImportTask();task.filename=str(out/'torch'/'SM_Torch_Field.fbx');task.destination_path=root+'/Meshes';task.automated=True;task.save=True
 opt=unreal.FbxImportUI();opt.import_materials=False;opt.import_textures=False;opt.import_mesh=True;opt.automated_import_should_detect_type=False;opt.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
 opt.static_mesh_import_data.combine_meshes=True;opt.static_mesh_import_data.auto_generate_collision=False;opt.static_mesh_import_data.convert_scene=True;opt.static_mesh_import_data.convert_scene_unit=True;opt.static_mesh_import_data.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS;task.options=opt;at.import_asset_tasks([task]);mesh=lib.load_asset(path)
assert mesh
for i,slot in enumerate(mesh.static_materials):
 name=str(slot.material_slot_name);assert name in materials,name;mesh.set_material(i,materials[name])
lib.save_loaded_asset(mesh)
box=mesh.get_bounding_box();size=box.max-box.min;assert abs(size.x-25)<.2 and size.y<8 and size.z<8,('Torch axis/scale',size)
m=asset('M_Torch_Optics',root+'/Materials',unreal.Material,unreal.MaterialFactoryNew());ml.delete_all_material_expressions(m);m.set_editor_property('material_domain',unreal.MaterialDomain.MD_LIGHT_FUNCTION)
uv=ml.create_material_expression(m,unreal.MaterialExpressionTextureCoordinate)
focus=ml.create_material_expression(m,unreal.MaterialExpressionScalarParameter);focus.set_editor_property('parameter_name','Focus');focus.set_editor_property('default_value',.35)
f=ml.create_material_expression(m,unreal.MaterialExpressionCustom);f.set_editor_property('output_type',unreal.CustomMaterialOutputType.CMOT_FLOAT1)
inputs=[]
for name in ['UV','Focus']:
 ci=unreal.CustomInput();ci.set_editor_property('input_name',name);inputs.append(ci)
f.set_editor_property('inputs',inputs)
code='''float2 p=(UV-0.5)*2.0;
p=p*float2(1.012,0.988)+float2(0.006,-0.004);
float r=length(p); float a=atan2(p.y,p.x); float focus=saturate(Focus);
float radialWarp=max(0.0,r+0.004*sin(a*5.0+0.7)+0.003*sin(a*9.0-0.8));
float coreWidth=lerp(0.38,0.24,focus);
float core=0.80*exp(-pow(radialWarp/coreWidth,3.2));
float spill=0.22*exp(-pow(r/0.66,2.0));
float corona=0.065*exp(-pow((radialWarp-lerp(0.69,0.49,focus))/0.027,2.0));
float innerRing=0.028*exp(-pow((radialWarp-lerp(0.43,0.32,focus))/0.045,2.0));
float reflector=1.0+0.024*sin(a*7.0+r*21.0)+0.015*sin(a*13.0-r*15.0);
float centralDip=1.0-0.085*focus*exp(-pow(r/0.055,2.0));
return saturate((core*centralDip+spill+corona+innerRing)*reflector*(1.0-smoothstep(0.84,1.0,r)));'''
f.set_editor_property('code',code);ml.connect_material_expressions(uv,'',f,'UV');ml.connect_material_expressions(focus,'',f,'Focus');ml.connect_material_property(f,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR);ml.recompile_material(m);lib.save_loaded_asset(m)
(out/'torch'/'optics.hlsl').write_text(code)
bp=lib.load_asset(root+'/BP_StationWalker_Polished') or lib.duplicate_asset('/Game/MaldekRefinement/ForestTest/BP_ForestWalker',root+'/BP_StationWalker_Polished');unreal.BlueprintEditorLibrary.compile_blueprint(bp)
cdo=unreal.get_default_object(bp.generated_class());cdo.set_editor_property('unlimited_sprint',True)
presentation=cdo.get_components_by_class(unreal.StationPlayerPresentationComponent)[0];presentation.set_editor_property('detailed_torch_mesh',mesh)
light=cdo.get_components_by_class(unreal.SpotLightComponent)[0];light.set_light_function_material(m);light.set_light_function_scale(unreal.Vector(1,1,1));light.set_editor_property('light_function_fade_distance',100000.);light.set_editor_property('disabled_brightness',.16)
light.set_editor_property('use_temperature',True);light.set_temperature(4900);light.set_editor_property('source_radius',.6);light.set_editor_property('soft_source_radius',.4);light.set_editor_property('volumetric_scattering_intensity',.035)
light.set_editor_property('relative_location',unreal.Vector(42,17.5,-11));light.set_editor_property('relative_rotation',unreal.Rotator(pitch=0,yaw=-1.5,roll=0));lib.save_loaded_asset(bp,False)
gm=lib.load_asset(root+'/BP_StationGameMode_Polished') or lib.duplicate_asset('/Game/MaldekRefinement/ForestTest/BP_ForestGameMode',root+'/BP_StationGameMode_Polished');unreal.get_default_object(gm.generated_class()).set_editor_property('default_pawn_class',bp.generated_class());lib.save_loaded_asset(gm,False)
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert w.get_name()=='Station_R12';w.get_world_settings().set_editor_property('default_game_mode',gm.generated_class());assert ls.save_current_level()
report={'success':True,'pawn':bp.get_path_name(),'game_mode':gm.get_path_name(),'torch_bounds_cm':list(size.to_tuple()),'optics':m.get_path_name(),'controls':'F toggle; wheel up focus/far throw, wheel down wide spill; hold Shift for unlimited sprint.','material_count':7,'shared_forest_assets_modified':False}
(out/'player_setup.json').write_text(json.dumps(report,indent=2));RESULT=report

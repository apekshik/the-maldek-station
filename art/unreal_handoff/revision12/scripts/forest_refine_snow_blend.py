"""Fade the station snow mask spatially, inside local component overrides."""
import unreal,json
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'forest_refine';ml=unreal.MaterialEditingLibrary;lib=unreal.EditorAssetLibrary
root='/Game/MaldekRefinement/R12/ForestRefine/Materials';srcroot='/Game/MWLandscapeAutoMaterial/Materials/MASTER'
fp=root+'/Functions/MF_Woodland_SnowMask_Final';f=unreal.load_asset(fp) if lib.does_asset_exist(fp) else lib.duplicate_asset(srcroot+'/Func/MF_MWAM_SnowMask',fp)
dst=root+'/M_Woodland_Landscape_Final';m=unreal.load_asset(dst) if lib.does_asset_exist(dst) else lib.duplicate_asset(srcroot+'/MTL_MWAM_AutoMaterial_MASTER',dst)
nodes=[n for n in unreal.ObjectIterator(unreal.MaterialExpression) if n.get_outer() in [f,m]]
byname={n.get_name():n for n in nodes if n.get_outer()==m};call=byname['MaterialExpressionMaterialFunctionCall_16'];call.set_material_function(f)
assert ml.connect_material_expressions(byname['MaterialExpressionMultiply_7'],'',call,'Mask')
def node(cls):return ml.create_material_expression_in_function(f,cls)
def wire(a,b,pin,output=''):
 ok=ml.connect_material_expressions(a,output,b,pin)
 if not ok and len(ml.get_material_expression_input_names(b))==1:ok=ml.connect_material_expressions(a,output,b,'')
 assert ok,(b.get_class().get_name(),pin,list(ml.get_material_expression_input_names(b)))
def scalar(v):
 n=node(unreal.MaterialExpressionConstant);n.set_editor_property('r',v);return n
def vec(v):
 n=node(unreal.MaterialExpressionConstant3Vector);n.set_editor_property('constant',unreal.LinearColor(*v,1));return n
if not (out/'snow_blend_final.json').exists():
 outputs=[n for n in nodes if n.get_outer()==f and isinstance(n,unreal.MaterialExpressionFunctionOutput)]
 o=json.loads((b.parent/'working_level_report.json').read_text())['station_origin'];world=node(unreal.MaterialExpressionWorldPosition)
 delta=node(unreal.MaterialExpressionSubtract);wire(world,delta,'A');wire(vec([o[0],o[1]+4000,0]),delta,'B')
 scaled=node(unreal.MaterialExpressionMultiply);wire(delta,scaled,'A');wire(vec([.0001,1/15500,0]),scaled,'B')
 dot=node(unreal.MaterialExpressionDotProduct);wire(scaled,dot,'A');wire(scaled,dot,'B');length=node(unreal.MaterialExpressionSquareRoot);wire(dot,length,'Input')
 sub=node(unreal.MaterialExpressionSubtract);wire(length,sub,'A');wire(scalar(.5),sub,'B');twice=node(unreal.MaterialExpressionMultiply);wire(sub,twice,'A');wire(scalar(2),twice,'B');mask=node(unreal.MaterialExpressionSaturate);wire(twice,mask,'Input')
 # Smooth the fade without introducing a geometric or material tile boundary.
 sq=node(unreal.MaterialExpressionMultiply);wire(mask,sq,'A');wire(mask,sq,'B');neg=node(unreal.MaterialExpressionMultiply);wire(mask,neg,'A');wire(scalar(-2),neg,'B');three=node(unreal.MaterialExpressionAdd);wire(neg,three,'A');wire(scalar(3),three,'B');smooth=node(unreal.MaterialExpressionMultiply);wire(sq,smooth,'A');wire(three,smooth,'B')
 for output in outputs:
  inputs=list(ml.get_inputs_for_material_expression(m,output));old=inputs[0];assert old
  mul=node(unreal.MaterialExpressionMultiply);wire(old,mul,'A');wire(smooth,mul,'B');wire(mul,output,list(ml.get_material_expression_input_names(output))[0])
 assert len(outputs)==2
ml.update_material_function(f);lib.save_loaded_asset(f)
ml.recompile_material(m);lib.save_loaded_asset(m)
mi=unreal.load_asset(root+'/MI_Woodland_Landscape');ml.set_material_instance_parent(mi,m)
ml.set_material_instance_scalar_parameter_value(mi,'MW_SnowMaskMultiplier',1.4);ml.set_material_instance_scalar_parameter_value(mi,'MW_SnowWorldPosition',-1500.)
for n,v in [('MW_GrassColorCorrection',(.5,.38,.28)),('MW_DirtColorCorrection',(.65,.65,.65)),('MW_RockColorCorrection',(.55,.55,.55))]:ml.set_material_instance_vector_parameter_value(mi,n,unreal.LinearColor(*v,1))
ml.update_material_instance(mi);lib.save_loaded_asset(mi)
saved=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level();assert saved
RESULT={'saved':saved,'functions':1,'material':m.get_path_name(),'ellipse_center_local':[0,40],'ellipse_radius_m':[100,155],'full_clear_fraction':.5};(out/'snow_blend_final.json').write_text(json.dumps(RESULT,indent=2))

"""Blend toward the snow-free side of the library's snow masks."""
import unreal,json
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'forest_refine';ml=unreal.MaterialEditingLibrary;lib=unreal.EditorAssetLibrary;root='/Game/MaldekRefinement/R12/ForestRefine/Materials';m=unreal.load_asset(root+'/M_Woodland_Landscape_Final');f=unreal.load_asset(root+'/Functions/MF_Woodland_SnowMask_Final')
outputs=[n for n in unreal.ObjectIterator(unreal.MaterialExpressionFunctionOutput) if n.get_outer()==f]
for output in outputs:
 oldmul=list(ml.get_inputs_for_material_expression(m,output))[0]
 inputs=list(ml.get_inputs_for_material_expression(m,oldmul))
 old,alpha=inputs[1:] if isinstance(oldmul,unreal.MaterialExpressionLinearInterpolate) else inputs
 if JOB.get('clear_mask',1)==0:
  mul=ml.create_material_expression_in_function(f,unreal.MaterialExpressionMultiply);assert ml.connect_material_expressions(old,'',mul,'A');assert ml.connect_material_expressions(alpha,'',mul,'B');assert ml.connect_material_expressions(mul,'',output,'');continue
 one=ml.create_material_expression_in_function(f,unreal.MaterialExpressionConstant);one.set_editor_property('r',1.)
 lerp=ml.create_material_expression_in_function(f,unreal.MaterialExpressionLinearInterpolate)
 for n,pin in [(one,'A'),(old,'B'),(alpha,'Alpha')]:assert ml.connect_material_expressions(n,'',lerp,pin)
 assert ml.connect_material_expressions(lerp,'',output,'')
ml.update_material_function(f);lib.save_loaded_asset(f);ml.recompile_material(m);lib.save_loaded_asset(m);assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
RESULT={'saved':True,'clear_mask':JOB.get('clear_mask',1),'outputs':2};(out/'snow_polarity.json').write_text(json.dumps(RESULT))

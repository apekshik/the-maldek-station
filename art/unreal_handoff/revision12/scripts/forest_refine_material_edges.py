import unreal,json
from pathlib import Path
b=Path(__file__).resolve().parents[1];ml=unreal.MaterialEditingLibrary;m=unreal.load_asset('/Game/MWLandscapeAutoMaterial/Materials/MASTER/MTL_MWAM_AutoMaterial_MASTER');seen=set();edges=[]
def walk(n):
 if not n or n.get_path_name() in seen:return
 seen.add(n.get_path_name());names=list(ml.get_material_expression_input_names(n));ins=list(ml.get_inputs_for_material_expression(m,n))
 for i,c in enumerate(ins):
  if not c:continue
  if isinstance(c,unreal.MaterialExpressionScalarParameter) and 'Snow' in str(c.get_editor_property('parameter_name')):edges.append({'consumer':n.get_name(),'pin':names[i],'parameter':str(c.get_editor_property('parameter_name'))})
  walk(c)
walk(ml.get_material_property_input_node(m,unreal.MaterialProperty.MP_MATERIAL_ATTRIBUTES))
mi=unreal.load_asset('/Game/MaldekRefinement/R12/ForestRefine/Materials/MI_Woodland_Landscape')
RESULT={'edges':edges,'vectors':{str(n):str(ml.get_material_instance_vector_parameter_value(mi,n)) for n in ml.get_vector_parameter_names(mi)}};(b/'forest_refine'/'material_edges.json').write_text(json.dumps(RESULT,indent=2))

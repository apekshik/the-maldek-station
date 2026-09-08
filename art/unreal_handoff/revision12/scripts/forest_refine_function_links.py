import unreal,json
from pathlib import Path
ml=unreal.MaterialEditingLibrary;rows=[]
for n in unreal.ObjectIterator(unreal.MaterialExpressionMaterialFunctionCall):
 if not n.get_outer().get_path_name().startswith('/Game/MWLandscapeAutoMaterial/Materials/MASTER'):continue
 f=n.get_editor_property('material_function')
 if f and 'SnowMask' in f.get_name():
  owner=n.get_outer();m=unreal.load_asset('/Game/MWLandscapeAutoMaterial/Materials/MASTER/MTL_MWAM_AutoMaterial_MASTER')
  ins=list(ml.get_inputs_for_material_expression(m,n));names=list(ml.get_material_expression_input_names(n))
  rows.append({'owner':owner.get_path_name(),'node':n.get_name(),'inputs':[{'pin':names[i],'node':c.get_name() if c else None,'output':str(ml.get_input_node_output_name_for_material_expression(n,c)) if c else None} for i,c in enumerate(ins)]})
RESULT=rows;(Path(__file__).resolve().parents[1]/'forest_refine/function_links.json').write_text(json.dumps(rows,indent=2))

import unreal,json
from pathlib import Path
ml=unreal.MaterialEditingLibrary;rows=[];m=unreal.load_asset('/Game/MWLandscapeAutoMaterial/Materials/MASTER/MTL_MWAM_AutoMaterial_MASTER')
for n in unreal.ObjectIterator(unreal.MaterialExpressionFunctionOutput):
 if 'SnowMask' in n.get_outer().get_name():
  def tree(x,depth):
   return {'node':x.get_name(),'inputs':[tree(c,depth-1) for c in ml.get_inputs_for_material_expression(m,x) if c]} if depth else x.get_name()
  rows.append({'function':n.get_outer().get_path_name(),'node':n.get_name(),'name':str(n.get_editor_property('output_name')),'tree':tree(n,3)})
RESULT=rows;(Path(__file__).resolve().parents[1]/'forest_refine/output_audit.json').write_text(json.dumps(rows,indent=2))

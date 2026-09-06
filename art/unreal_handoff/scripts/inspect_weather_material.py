import unreal,json
from pathlib import Path
ml=unreal.MaterialEditingLibrary
m=unreal.Material()
f=unreal.load_asset('/Game/UltraDynamicSky/Materials/Weather/Surface_Weather_Effects')
n=ml.create_material_expression(m,unreal.MaterialExpressionMaterialFunctionCall)
n.set_material_function(f)
out={'function':f.get_class().get_name(),'inputs':list(ml.get_material_expression_input_names(n))}
for prop in ['function_inputs','function_outputs','outputs']:
 try:out[prop]=str(n.get_editor_property(prop))
 except Exception as e:out[prop]=str(e)
(Path(__file__).resolve().parents[1]/'weather_material_api.json').write_text(json.dumps(out,indent=2))

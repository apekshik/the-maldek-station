import unreal,json
from pathlib import Path
m=unreal.load_asset('/Game/MWLandscapeAutoMaterial/Materials/MASTER/MTL_MWAM_AutoMaterial_MASTER')
ml=unreal.MaterialEditingLibrary
n=ml.get_material_property_input_node(m,unreal.MaterialProperty.MP_MATERIAL_ATTRIBUTES)
out={'input_names':list(ml.get_material_expression_input_names(n)),'properties':{},'connected':[]}
for p in ['base_color','emissive_color','normal','roughness','metallic','shading_model']:
 try:out['properties'][p]=str(n.get_editor_property(p))
 except Exception as e:out['properties'][p]=str(e)
for idx,node in enumerate(ml.get_inputs_for_material_expression(m,n)):
 if node is None:continue
 row={'input_index':idx,'name':node.get_name(),'class':node.get_class().get_name()}
 for p in ['parameter_name','default_value','r','constant','material_function']:
  try:row[p]=str(node.get_editor_property(p))
  except Exception:pass
 out['connected'].append(row)
out['scalar_parameters']={str(p):ml.get_material_default_scalar_parameter_value(m,p) for p in ml.get_scalar_parameter_names(m)}
(Path(__file__).resolve().parents[1]/'landscape_graph_audit.json').write_text(json.dumps(out,indent=2))


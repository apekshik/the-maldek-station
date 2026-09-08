"""Weather local copies of vehicle body materials while retaining original maps."""
import unreal,json
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'forest_refine'/'vehicles';out.mkdir(parents=True,exist_ok=True)
ml=unreal.MaterialEditingLibrary;lib=unreal.EditorAssetLibrary;rows=[]
for vehicle in ['Hatchback','Pickup']:
 src=f'/Game/VehicleVarietyPack/Materials/{vehicle}/M_{vehicle}_Body'
 dst=f'/Game/MaldekRefinement/R12/ForestRefine/Materials/M_Weathered_{vehicle}'
 if lib.does_asset_exist(dst):
  rows.append({'source':src,'material':dst,'existing':True});continue
 mat=lib.duplicate_asset(src,dst);assert isinstance(mat,unreal.Material)
 base=ml.get_material_property_input_node(mat,unreal.MaterialProperty.MP_BASE_COLOR);assert base
 baseout=ml.get_material_property_input_node_output_name(mat,unreal.MaterialProperty.MP_BASE_COLOR)
 def node(cls):return ml.create_material_expression(mat,cls)
 def wire(a,b,pin,output=''):assert ml.connect_material_expressions(a,output,b,pin)
 def scalar(value):
  n=node(unreal.MaterialExpressionConstant);n.set_editor_property('r',value);return n
 noise=node(unreal.MaterialExpressionNoise);noise.set_editor_property('scale',.018);noise.set_editor_property('levels',2);noise.set_editor_property('output_min',0.);noise.set_editor_property('output_max',1.)
 amount=node(unreal.MaterialExpressionMultiply);amount.set_editor_property('const_b',.23);wire(noise,amount,'A')
 dust=node(unreal.MaterialExpressionAdd);dust.set_editor_property('const_b',.10);wire(amount,dust,'A')
 color=node(unreal.MaterialExpressionConstant3Vector);color.set_editor_property('constant',unreal.LinearColor(.105,.085,.061,1))
 mix=node(unreal.MaterialExpressionLinearInterpolate);wire(base,mix,'A',baseout);wire(color,mix,'B');wire(dust,mix,'Alpha');assert ml.connect_material_property(mix,'',unreal.MaterialProperty.MP_BASE_COLOR)
 rough=ml.get_material_property_input_node(mat,unreal.MaterialProperty.MP_ROUGHNESS)
 roughout=ml.get_material_property_input_node_output_name(mat,unreal.MaterialProperty.MP_ROUGHNESS)
 maximum=node(unreal.MaterialExpressionMax);wire(rough or scalar(.5),maximum,'A',roughout if rough else '');wire(scalar(.68),maximum,'B');assert ml.connect_material_property(maximum,'',unreal.MaterialProperty.MP_ROUGHNESS)
 ml.layout_material_expressions(mat);ml.recompile_material(mat);lib.save_loaded_asset(mat);rows.append({'source':src,'material':dst,'dust_fraction':[.10,.33],'minimum_roughness':.68})
(out/'materials.json').write_text(json.dumps(rows,indent=2));RESULT=rows

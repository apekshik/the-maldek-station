"""Preserve brass UI colors when a world widget is rendered in a dark exposure."""
import unreal, json
from pathlib import Path
lib=unreal.MaterialEditingLibrary
path='/Game/MaldekRefinement/R12/Doors/M_DoorInteractionPrompt'
asset=unreal.EditorAssetLibrary.load_asset(path)
if asset and not isinstance(asset,unreal.Material):
    assert unreal.EditorAssetLibrary.delete_asset(path)
    asset=None
if not asset:
    template=unreal.EditorAssetLibrary.load_asset('/Engine/EngineMaterials/Widget3DPassThrough_Translucent')
    while isinstance(template,unreal.MaterialInstanceConstant):template=template.get_editor_property('parent')
    asset=unreal.EditorAssetLibrary.duplicate_asset(template.get_path_name(),path)
    assert asset,'widget material template missing'
    asset.set_editor_property('blend_mode',unreal.BlendMode.BLEND_TRANSLUCENT)
    asset.set_editor_property('two_sided',True)
    emissive=lib.get_material_property_input_node(asset,unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    output=lib.get_material_property_input_node_output_name(asset,unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    inverse=lib.create_material_expression(asset,unreal.MaterialExpressionEyeAdaptationInverse,500,0)
    inputs=lib.get_material_expression_input_names(inverse)
    assert lib.connect_material_expressions(emissive,output,inverse,str(inputs[0]))
    alpha=lib.create_material_expression(asset,unreal.MaterialExpressionConstant,300,200)
    alpha.set_editor_property('r',1.0)
    assert lib.connect_material_expressions(alpha,'',inverse,str(inputs[1]))
    assert lib.connect_material_property(inverse,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    lib.recompile_material(asset)
    assert unreal.EditorAssetLibrary.save_loaded_asset(asset)
RESULT={'success':True,'material':path}
out=Path(__file__).resolve().parents[1]/'doors'/'prompt_egress';out.mkdir(exist_ok=True)
(out/'material.json').write_text(json.dumps(RESULT,indent=2))

import unreal,json
from pathlib import Path
m=unreal.EditorAssetLibrary.load_asset('/Game/MaldekRefinement/R12/GondolaRoute/Materials/M_Pylon_Faded_Grey_Green')
n=unreal.MaterialEditingLibrary.create_material_expression(m,unreal.MaterialExpressionNoise)
RESULT={'noise_inputs':unreal.MaterialEditingLibrary.get_material_expression_input_names(n),'local_fog':str(unreal.LocalFogVolume),'gondola_properties':[x for x in dir(unreal.GondolaSystem) if any(s in x for s in ['arrival','cabin','route'])]}
(Path(__file__).resolve().parents[1]/'gondola_route/api.json').write_text(json.dumps(RESULT,indent=2,default=str))

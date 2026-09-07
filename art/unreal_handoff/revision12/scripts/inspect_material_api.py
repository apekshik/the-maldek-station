import unreal,json
from pathlib import Path
ml=unreal.MaterialEditingLibrary
mat=unreal.load_asset('/Game/MaldekRefinement/R12/Materials/Masters/M_R12_PaintedMetal_Exterior')
RESULT={'texture_names':[str(n) for n in ml.get_texture_parameter_names(mat)],'scalar_names':[str(n) for n in ml.get_scalar_parameter_names(mat)],'set_doc':str(ml.set_material_instance_texture_parameter_value.__doc__)}

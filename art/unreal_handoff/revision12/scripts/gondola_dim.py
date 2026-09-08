"""Local cabin lighting revision; shared station lamps remain independent."""
import unreal,json
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'gondola_route'
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert not ls.is_in_play_in_editor()
src='/Game/MaldekRefinement/R12/Materials/Instances/MI_UE_VF06_Lamp__Exterior'
dst='/Game/MaldekRefinement/R12/GondolaRoute/Materials/MI_Gondola_Lamp_Dim'
mat=unreal.load_asset(dst) or unreal.EditorAssetLibrary.duplicate_asset(src,dst)
unreal.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(mat,'EmissionStrength',.6)
unreal.MaterialEditingLibrary.update_material_instance(mat)
changed=[]
for a in aa.get_all_level_actors():
 label=a.get_actor_label()
 if label.startswith('R12_Gondola_Interior_Light_'):
  a.point_light_component.set_intensity(12)
  a.point_light_component.set_volumetric_scattering_intensity(.025)
 if label.startswith('R12_VF06_Gondola_Details_'):
  for c in a.get_components_by_class(unreal.StaticMeshComponent):
   for i in range(c.get_num_materials()):
    old=c.get_material(i)
    if old and old.get_path_name().split('.')[0] in (src,dst):c.set_material(i,mat);changed.append(label)
assert len(changed)==2
unreal.EditorAssetLibrary.save_loaded_asset(mat)
assert ls.save_current_level()
RESULT={'saved':True,'interior_lumens_each':12,'emission_strength':.6,'previous_emission':3,'lamp_actors':changed}
(out/'dimming.json').write_text(json.dumps(RESULT,indent=2))

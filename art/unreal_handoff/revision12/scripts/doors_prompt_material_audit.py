import unreal,json
from pathlib import Path
lib=unreal.MaterialEditingLibrary
m=unreal.EditorAssetLibrary.load_asset('/Game/MaldekRefinement/R12/Doors/M_DoorInteractionPrompt')
node=lib.get_material_property_input_node(m,unreal.MaterialProperty.MP_EMISSIVE_COLOR)
RESULT={'node':node.get_class().get_name(),'inputs':[str(n) for n in lib.get_material_expression_input_names(node)],'connections':[x.get_class().get_name() if x else None for x in lib.get_inputs_for_material_expression(m,node)]}
w=unreal.EditorLevelLibrary.get_game_world()
if w:
    RESULT['runtime']=[]
    for d in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.StationDoor):
        c=d.get_editor_property('InteractionPrompt');mi=c.get_material_instance()
        RESULT['runtime'].append({'door':d.get_actor_label(),'material':c.get_material(0).get_path_name(),'parent':mi.get_editor_property('parent').get_path_name() if mi else None})
(Path(__file__).resolve().parents[1]/'doors'/'prompt_egress'/'material_audit.json').write_text(json.dumps(RESULT,indent=2))

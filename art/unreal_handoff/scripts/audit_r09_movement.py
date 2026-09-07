import unreal,json
from pathlib import Path
w=unreal.EditorLevelLibrary.get_game_world();p=unreal.GameplayStatics.get_player_pawn(w,0)
r={'class':p.get_class().get_name(),'walk_property':p.get_editor_property('walk_speed'),'max_walk':p.get_components_by_class(unreal.CharacterMovementComponent)[0].get_editor_property('max_walk_speed'),'controller':str(p.get_controller()),'movement_mode':str(p.get_components_by_class(unreal.CharacterMovementComponent)[0].get_editor_property('movement_mode'))}
r['cdo_walk']=unreal.get_default_object(p.get_class()).get_editor_property('walk_speed')
(Path(__file__).resolve().parents[1]/'revision09/movement_audit.json').write_text(json.dumps(r,indent=2))


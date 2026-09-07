import unreal,json
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'trim2';out.mkdir(exist_ok=True)
w=unreal.EditorLevelLibrary.get_game_world();r={}
if w:
 p=unreal.GameplayStatics.get_player_pawn(w,0);pc=unreal.GameplayStatics.get_player_controller(w,0);cam=p.get_component_by_class(unreal.CameraComponent)
 r={'camera':list(cam.get_world_location().to_tuple()),'rotation':list(pc.get_control_rotation().to_tuple()),'pawn':list(p.get_actor_location().to_tuple())}
(out/'user_view.json').write_text(json.dumps(r,indent=2));unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play();RESULT=r

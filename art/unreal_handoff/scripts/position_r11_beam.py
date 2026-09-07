import unreal,time
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'revision11';world=unreal.EditorLevelLibrary.get_game_world();pawn=unreal.GameplayStatics.get_player_pawn(world,0);pc=unreal.GameplayStatics.get_player_controller(world,0)
pawn.set_actor_location(unreal.Vector(-43312,18700,10395),False,True);pc.set_control_rotation(unreal.Rotator(pitch=-4,yaw=-90))
state={'next':time.monotonic()+4}
def tick(dt):
 if time.monotonic()<state['next']:return
 unreal.AutomationLibrary.take_high_res_screenshot(1920,1080,str(out/'beam_hotspot.png'));unreal.unregister_slate_post_tick_callback(handle)
handle=unreal.register_slate_post_tick_callback(tick)

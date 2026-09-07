import unreal,json,time
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'revision11';state={'start':time.monotonic(),'changes':[],'last':None}
def tick(dt):
 world=unreal.EditorLevelLibrary.get_game_world()
 if not world:return
 pawn=unreal.GameplayStatics.get_player_pawn(world,0)
 if not pawn:return
 light=pawn.get_components_by_class(unreal.SpotLightComponent)[0];v=light.is_visible()
 if v!=state['last']:
  state['last']=v;state['changes'].append({'visible':v,'elapsed':time.monotonic()-state['start']});(out/'flashlight_toggle.json').write_text(json.dumps(state,indent=2))
  if not v:unreal.AutomationLibrary.take_high_res_screenshot(1920,1080,str(out/'flashlight_off.png'))
 if len(state['changes'])>=3 or time.monotonic()-state['start']>120:unreal.unregister_slate_post_tick_callback(handle)
handle=unreal.register_slate_post_tick_callback(tick)

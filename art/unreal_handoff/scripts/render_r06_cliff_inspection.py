import unreal,time,json
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'revision06/final_renders';actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for pitch,yaw,intensity in [(-45,-40,2),(-35,150,1)]:
 a=actors.spawn_actor_from_class(unreal.DirectionalLight,unreal.Vector(),unreal.Rotator(pitch=pitch,yaw=yaw,roll=0));a.set_actor_label('TEMP_Cliff_Inspection');a.light_component.set_intensity(intensity);a.light_component.set_editor_property('cast_shadows',False)
loc=unreal.Vector(-44900,22000,11300);target=unreal.Vector(-44300,18800,9350);unreal.EditorLevelLibrary.set_level_viewport_camera_info(loc,unreal.MathLibrary.find_look_at_rotation(loc,target))
state={'stage':0,'when':time.monotonic()+12}
def tick(delta):
 if time.monotonic()<state['when']:return
 if state['stage']==0:
  unreal.AutomationLibrary.take_high_res_screenshot(2560,1440,str(out/'10_cliff_inspection.png'),delay=1.0,force_game_view=True);state.update(stage=1,when=time.monotonic()+6)
 elif (out/'10_cliff_inspection.png').exists():
  for a in actors.get_all_level_actors():
   if a.get_actor_label()=='TEMP_Cliff_Inspection':actors.destroy_actor(a)
  (out/'inspection_note.json').write_text(json.dumps({'temporary_fill_lighting':True,'saved_to_level':False,'purpose':'show cliff geometry in otherwise dark night scene'}));unreal.unregister_slate_post_tick_callback(handle)
handle=unreal.register_slate_post_tick_callback(tick)

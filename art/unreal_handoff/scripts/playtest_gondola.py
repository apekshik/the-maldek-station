import unreal,time,json,traceback
from pathlib import Path
test_out=Path(__file__).resolve().parents[1]
test_state={'phase':'starting','samples':[],'started':time.monotonic()}
def test_vec(v):return [v.x,v.y,v.z]
def test_tick(delta):
 try:
  now=time.monotonic()
  if now-test_state['started']>90:raise RuntimeError('PIE verification timed out')
  world=unreal.EditorLevelLibrary.get_game_world()
  if not world:return
  if test_state['phase']=='starting':
   aa=unreal.GameplayStatics.get_all_actors_of_class(world,unreal.Actor)
   controller=next((a for a in aa if a.get_class().get_name()=='BP_GondolaSystem_C'),None)
   cabin=next((a for a in aa if a.get_actor_label()=='R04_12_Gondola'),None)
   if not controller or not cabin:return
   test_state['controller']=controller;test_state['cabin']=cabin
   test_state['start']=test_vec(cabin.get_actor_location())
   controller.set_editor_property('travel_time',3.0)
   controller.set_editor_property('wait_time_at_maldek',1.0)
   controller.send_gondola();test_state['phase']='moving';test_state['sent']=now
  elif test_state['phase']=='moving':
   c=test_state['controller'];a=test_state['cabin']
   test_state['samples'].append({'time':now-test_state['sent'],'location':test_vec(a.get_actor_location()),'alpha':c.get_editor_property('current_alpha'),'moving':c.is_moving(),'docked':c.is_docked()})
   if now-test_state['sent']>8 and c.is_docked() and not c.is_moving():
    result={k:v for k,v in test_state.items() if k not in ['controller','cabin']}
    result['end']=test_vec(a.get_actor_location());result['success']=max(s['alpha'] for s in result['samples'])>.99 and sum((result['end'][i]-result['start'][i])**2 for i in range(3))<1
    (test_out/'gondola_playtest.json').write_text(json.dumps(result,indent=2))
    unreal.unregister_slate_post_tick_callback(test_handle)
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
 except Exception:
  (test_out/'gondola_playtest.json').write_text(json.dumps({'success':False,'error':traceback.format_exc()}))
  unreal.unregister_slate_post_tick_callback(test_handle)
test_handle=unreal.register_slate_post_tick_callback(test_tick)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_play_simulate()

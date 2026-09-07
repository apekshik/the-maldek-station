"""Capture saved lighting, plus clearly marked temporary geometry inspection views."""
import unreal,time,json,traceback
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'revision11'/'renders';out.mkdir(exist_ok=True)
origin=json.loads((out.parent.parent/'working_level_report.json').read_text())['station_origin']
def p(v):return unreal.Vector(origin[0]-v[0]*100,origin[1]+v[1]*100,origin[2]+v[2]*100)
shots=[('01_bridge_night',(11,9,5.65),(19,34,5),False),('02_service_night',(23,-14,.65),(27,-15,0),False),('03_bridge_structure',(32,42,20),(15,20,4),True),('04_maintenance_layout',(14,-32,15),(29,-16,0),True),('05_canyon_moon',(-2.9,10.5,5.65),(0,250,45),False)]
state={'i':0,'stage':0,'next':time.monotonic()+3,'fills':[],'busy':False}
def tick(dt):
 if state['busy'] or time.monotonic()<state['next']:return
 state['busy']=True
 try:
  aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
  if state['i']>=len(shots):
   for a in state['fills']:aa.destroy_actor(a)
   (out/'complete.json').write_text(json.dumps(shots));unreal.unregister_slate_post_tick_callback(handle);return
  name,loc,target,inspection=shots[state['i']]
  if state['stage']==0:
   for a in state['fills']:aa.destroy_actor(a)
   state['fills']=[]
   if inspection:
    a=aa.spawn_actor_from_class(unreal.DirectionalLight,unreal.Vector(),unreal.Rotator(pitch=-45,yaw=-30));a.set_actor_label('TEMP_R11_Inspection');a.light_component.set_intensity(2);a.light_component.set_editor_property('cast_shadows',False);state['fills']=[a]
   unreal.EditorLevelLibrary.set_level_viewport_camera_info(p(loc),unreal.MathLibrary.find_look_at_rotation(p(loc),p(target)));state.update(stage=1,next=time.monotonic()+7)
  elif state['stage']==1:
   unreal.AutomationLibrary.take_high_res_screenshot(1920,1080,str(out/(name+'.png')),force_game_view=True);state.update(stage=2,next=time.monotonic()+6)
  else:
   if not (out/(name+'.png')).exists():state.update(stage=1,next=time.monotonic()+2)
   else:state.update(stage=0,i=state['i']+1,next=time.monotonic()+2)
 except Exception:
  (out/'error.txt').write_text(traceback.format_exc());unreal.unregister_slate_post_tick_callback(handle)
 finally:state['busy']=False
handle=unreal.register_slate_post_tick_callback(tick)

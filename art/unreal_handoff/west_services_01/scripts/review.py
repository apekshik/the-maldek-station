"""Temporary neutral lighting; all review actors are removed before saving."""
import unreal,json,time,traceback
from pathlib import Path
OUT=Path(__file__).resolve().parents[1];seating=globals().get('JOB',{}).get('seating',False);doors=globals().get('JOB',{}).get('doors',False);dest=OUT/('previews/night' if JOB.get('night') else 'previews/day');dest.mkdir(parents=True,exist_ok=True);o=json.loads((OUT/'baseline.json').read_text())['origin']
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert not ls.is_in_play_in_editor() and unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_name()=='Station_Lodge_Migration'
def wp(p):return unreal.Vector(o[0]-p[0]*100,o[1]+p[1]*100,o[2]+p[2]*100)
for previous in aa.get_all_level_actors():
 if previous.get_actor_label().startswith('Lodge_Surface_Review_Temporary'):aa.destroy_actor(previous)
unreal.SystemLibrary.execute_console_command(unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world(),'viewmode lit')
temps=[]
for x,y in []:
 a=aa.spawn_actor_from_class(unreal.RectLight,wp([x,y,6.8]),unreal.Rotator(pitch=-75,yaw=0,roll=0));a.set_actor_label('Lodge_Surface_Review_Temporary');temps.append(a)
 c=a.get_component_by_class(unreal.RectLightComponent);c.set_mobility(unreal.ComponentMobility.MOVABLE);c.set_intensity_units(unreal.LightUnits.LUMENS);c.set_intensity(500);c.set_attenuation_radius(1600);c.set_light_color(unreal.LinearColor(1,.95,.88,1));c.set_volumetric_scattering_intensity(0);c.set_editor_property('source_width',250);c.set_editor_property('source_height',250)
sun=aa.spawn_actor_from_class(unreal.DirectionalLight,wp([-20,2,20]),unreal.Rotator(pitch=-40,yaw=30,roll=0));sun.set_actor_label('Lodge_Surface_Review_Temporary');temps.append(sun);sun.get_component_by_class(unreal.DirectionalLightComponent).set_mobility(unreal.ComponentMobility.MOVABLE);sun.get_component_by_class(unreal.DirectionalLightComponent).set_intensity(0 if JOB.get('night') else 3)
settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'));throttle=settings.get_editor_property('bThrottleCPUWhenNotForeground');settings.set_editor_property('bThrottleCPUWhenNotForeground',False)
views=[('compound',[-27,13,10],[-35,0,4]),('west_outward',[-39.6,0,2.85],[-52,0,-3]),('south_outward',[-37,-6.7,2.85],[-43,-22,-5]),('north_outward',[-38.7,9.8,2.85],[-48,21,-3]),('lower_east',[-30,-6,2.85],[-30,7,1.7]),('porch_outward',[-30.4,4.2,6.25],[-49,15,1]) ]
views=[v for v in views if not JOB.get('only') or v[0] in JOB['only']]
state={'index':0,'phase':'set','next':time.monotonic()+5,'deadline':time.monotonic()+240};rows=[]
def finish(error=None):
 for a in temps:aa.destroy_actor(a)
 settings.set_editor_property('bThrottleCPUWhenNotForeground',throttle);unreal.unregister_slate_post_tick_callback(handle)
 (OUT/('review_night.json' if JOB.get('night') else ('review_day_final.json' if JOB.get('only') else 'review_day.json'))).write_text(json.dumps({'views':rows,'error':error,'temporary_lights_removed':True,'mode':'Lit, temporary neutral review lights; live weather retained'},indent=2))
def tick(dt):
 if time.monotonic()<state['next']:return
 try:
  assert time.monotonic()<state['deadline']
  if state['index']==len(views):finish();return
  name,p,target=views[state['index']];path=dest/(name+'.png')
  if state['phase']=='set':
   unreal.EditorLevelLibrary.set_level_viewport_camera_info(wp(p),unreal.MathLibrary.find_look_at_rotation(wp(p),wp(target)));state.update(phase='capture',next=time.monotonic()+5)
  elif state['phase']=='capture':
   unreal.AutomationLibrary.take_high_res_screenshot(1600,1000,str(path));state.update(phase='wait',next=time.monotonic()+3)
  else:
   assert path.exists() and path.stat().st_size>10000;rows.append({'name':name,'position':p,'target':target,'path':str(path)});state.update(index=state['index']+1,phase='set',next=0)
 except Exception:finish(traceback.format_exc())
handle=unreal.register_slate_post_tick_callback(tick);RESULT={'started':True}

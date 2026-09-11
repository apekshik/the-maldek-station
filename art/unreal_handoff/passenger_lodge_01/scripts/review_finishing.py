"""Temporary neutral lighting; all review actors are removed before saving."""
import unreal,json,time,traceback
from pathlib import Path
OUT=Path(__file__).resolve().parents[1];dest=OUT/'previews/finishing';dest.mkdir(exist_ok=True);o=json.loads((OUT/'before.json').read_text())['origin']

aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert not ls.is_in_play_in_editor() and unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_name()=='Station_Lodge_Migration'
def wp(p):return unreal.Vector(o[0]-p[0]*100,o[1]+p[1]*100,o[2]+p[2]*100)
for previous in aa.get_all_level_actors():
 if previous.get_actor_label().startswith('Lodge_Surface_Review_Temporary'):aa.destroy_actor(previous)
temps=[]
for x,y in [(-22,-8),(-20,-10),(-22,-5),(-20,-1),(-17,2),(-12,0),(-13,-5),(-17,-5),(-22,2)]:
 a=aa.spawn_actor_from_class(unreal.RectLight,wp([x,y,6.8]),unreal.Rotator(pitch=-75,yaw=0,roll=0));a.set_actor_label('Lodge_Surface_Review_Temporary');temps.append(a)
 c=a.get_component_by_class(unreal.RectLightComponent);c.set_mobility(unreal.ComponentMobility.MOVABLE);c.set_intensity_units(unreal.LightUnits.LUMENS);c.set_intensity(200);c.set_attenuation_radius(1600);c.set_light_color(unreal.LinearColor(1,.95,.88,1));c.set_volumetric_scattering_intensity(0);c.set_editor_property('source_width',250);c.set_editor_property('source_height',250)
sun=aa.spawn_actor_from_class(unreal.DirectionalLight,wp([-20,2,20]),unreal.Rotator(pitch=-40,yaw=30,roll=0));sun.set_actor_label('Lodge_Surface_Review_Temporary');temps.append(sun);sun.get_component_by_class(unreal.DirectionalLightComponent).set_mobility(unreal.ComponentMobility.MOVABLE);sun.get_component_by_class(unreal.DirectionalLightComponent).set_intensity(3)
settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'));throttle=settings.get_editor_property('bThrottleCPUWhenNotForeground');settings.set_editor_property('bThrottleCPUWhenNotForeground',False)
views=[('01_Hall',(-21.8,1.8,5.65),(-16.5,-6.7,5.8)),('02_Lockers_closed',(-14.8,-4.4,5.65),(-12.4,-6.6,5.0)),('03_Lockers_open',(-14.8,-4.4,5.65),(-12.4,-6.6,5.0)),('04_Locker_detail',(-12.9,-5.8,5.4),(-12.5,-6.8,5.0)),('05_Posters',(-21.7,-.575,5.65),(-23.90,-.575,5.85)),('06_Timetable',(-18.3,2.15,5.65),(-18.3,3.77,5.65)),('07_Map',(-12.4,.4,5.68),(-10.33,.4,5.68)),('08_Community',(-22,-4.8,5.66),(-23.87,-4.8,5.66)),('09_Restroom_hall',(-16.4,-4.8,5.65),(-14.95,-7.1,6)),('10_Menu',(-21.6,-4.6,6.1),(-21.6,-6.96,6.53)),('11_Cubby',(-19.63,-5.7,5.22),(-19.63,-6.596,5.156)),('12_Case_angle',(-17.15,2.3,5.75),(-18.3,3.7,5.65)),('13_Poster_angle',(-22.4,2.8,5.65),(-23.87,1.425,5.675))]
lockers=[a for a in aa.get_all_level_actors() if a.get_actor_label().startswith('MIG_PLL_') and isinstance(a,unreal.StationCabinet)]
def pose(opened):
 for a in lockers:
  active=opened and a.get_actor_label() in ['MIG_PLL_05','MIG_PLL_06','MIG_PLL_07']
  a.pivot.set_relative_rotation(unreal.Rotator(yaw=-100 if active else 0),False,True)
  a.cam.set_relative_rotation(unreal.Rotator(pitch=-90 if active else 0),False,True)
aa.set_selected_level_actors([])
state={'index':0,'phase':'set','next':time.monotonic()+5,'deadline':time.monotonic()+600};rows=[]
def finish(error=None):
 pose(False)
 for a in temps:aa.destroy_actor(a)
 settings.set_editor_property('bThrottleCPUWhenNotForeground',throttle);unreal.unregister_slate_post_tick_callback(handle)
 (OUT/'finishing/review.json').write_text(json.dumps({'views':rows,'error':error,'temporary_lights_removed':True,'mode':'Lit neutral, roof visible; closed default; lockers 05-07 temporarily open in views 03-04'},indent=2))

def tick(dt):
 if time.monotonic()<state['next']:return
 try:
  assert time.monotonic()<state['deadline']
  if state['index']==len(views):finish();return
  name,p,target=views[state['index']];path=dest/(name+'.png')
  if state['phase']=='set':
   pose(name in ['03_Lockers_open','04_Locker_detail']);unreal.EditorLevelLibrary.set_level_viewport_camera_info(wp(p),unreal.MathLibrary.find_look_at_rotation(wp(p),wp(target)));state.update(phase='capture',next=time.monotonic()+5)
  elif state['phase']=='capture':
   unreal.AutomationLibrary.take_high_res_screenshot(1600,1000,str(path));state.update(phase='wait',next=time.monotonic()+3)
  else:
   assert path.exists() and path.stat().st_size>10000;rows.append({'name':name,'position':p,'target':target,'path':str(path)});state.update(index=state['index']+1,phase='set',next=0)
 except Exception:finish(traceback.format_exc())
handle=unreal.register_slate_post_tick_callback(tick);RESULT={'started':True}

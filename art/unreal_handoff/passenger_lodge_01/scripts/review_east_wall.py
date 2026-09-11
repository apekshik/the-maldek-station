"""Temporary neutral lighting; all review actors are removed before saving."""
import unreal,json,time,traceback
from pathlib import Path
OUT=Path(__file__).resolve().parents[1];dest=OUT/'previews/east_wall';dest.mkdir(exist_ok=True);o=json.loads((OUT/'before.json').read_text())['origin']

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
views=[('01_Hall',(-22.7,2.4,5.65),(-12.5,-3.2,5.55)),('02_East_wall',(-15,-2.7,5.7),(-10.3,-2.7,5.65)),('03_Oblique',(-12.3,.2,5.65),(-10.4,-3.3,5.6)),('04_Leaflets',(-11.65,-3.1,5.5),(-10.37,-3.23,5.22)),('05_Gauge',(-11.6,-4.03,5.95),(-10.35,-4.03,5.91)),('06_FirstAid',(-11.8,-5.15,5.75),(-10.43,-5.02,5.61)),('07_FirstAid_open',(-11.8,-5.15,5.75),(-10.43,-5.02,5.61)),('08_Archive',(-11.8,-2.2,5.8),(-10.34,-2.2,5.8)),('09_Safety',(-11.8,-1.12,5.8),(-10.34,-1.12,5.78))]
cabinet=next(a for a in aa.get_all_level_actors() if a.get_actor_label()=='MIG_PLG2_FirstAid')
def pose(opened):cabinet.pivot.set_relative_rotation(unreal.Rotator(yaw=95 if opened else 0),False,False)
aa.set_selected_level_actors([])
state={'index':0,'phase':'set','next':time.monotonic()+5,'deadline':time.monotonic()+600};rows=[]
def finish(error=None):
 pose(False)
 for a in temps:aa.destroy_actor(a)
 settings.set_editor_property('bThrottleCPUWhenNotForeground',throttle);unreal.unregister_slate_post_tick_callback(handle)
 (OUT/'east_wall/review.json').write_text(json.dumps({'views':rows,'error':error,'temporary_lights_removed':True,'mode':'Lit neutral, roof visible; first-aid open only in view 07'},indent=2))

def tick(dt):
 if time.monotonic()<state['next']:return
 try:
  assert time.monotonic()<state['deadline']
  if state['index']==len(views):finish();return
  name,p,target=views[state['index']];path=dest/(name+'.png')
  if state['phase']=='set':
   pose(name=='07_FirstAid_open');unreal.EditorLevelLibrary.set_level_viewport_camera_info(wp(p),unreal.MathLibrary.find_look_at_rotation(wp(p),wp(target)));state.update(phase='capture',next=time.monotonic()+5)
  elif state['phase']=='capture':
   unreal.AutomationLibrary.take_high_res_screenshot(1600,1000,str(path));state.update(phase='wait',next=time.monotonic()+3)
  else:
   assert path.exists() and path.stat().st_size>10000;rows.append({'name':name,'position':p,'target':target,'path':str(path)});state.update(index=state['index']+1,phase='set',next=0)
 except Exception:finish(traceback.format_exc())
handle=unreal.register_slate_post_tick_callback(tick);RESULT={'started':True}

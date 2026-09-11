"""Temporary neutral lighting; all review actors are removed before saving."""
import unreal,json,time,traceback
from pathlib import Path
OUT=Path(__file__).resolve().parents[1];dest=OUT/'previews/restrooms';dest.mkdir(exist_ok=True);o=json.loads((OUT/'before.json').read_text())['origin']

aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert not ls.is_in_play_in_editor() and unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_name()=='Station_Lodge_Migration'
def wp(p):return unreal.Vector(o[0]-p[0]*100,o[1]+p[1]*100,o[2]+p[2]*100)
for previous in aa.get_all_level_actors():
 if previous.get_actor_label().startswith('Lodge_Surface_Review_Temporary'):aa.destroy_actor(previous)
temps=[]
for x,y in [(-15,-9),(-13,-9),(-15,-11),(-11.5,-11),(-15,-12.5),(-11.5,-12.5)]:
 a=aa.spawn_actor_from_class(unreal.RectLight,wp([x,y,6.8]),unreal.Rotator(pitch=-75,yaw=0,roll=0));a.set_actor_label('Lodge_Surface_Review_Temporary');temps.append(a)
 c=a.get_component_by_class(unreal.RectLightComponent);c.set_mobility(unreal.ComponentMobility.MOVABLE);c.set_intensity_units(unreal.LightUnits.LUMENS);c.set_intensity(260);c.set_attenuation_radius(1600);c.set_light_color(unreal.LinearColor(1,.95,.88,1));c.set_volumetric_scattering_intensity(0);c.set_editor_property('source_width',250);c.set_editor_property('source_height',250)
sun=aa.spawn_actor_from_class(unreal.DirectionalLight,wp([-20,2,20]),unreal.Rotator(pitch=-40,yaw=30,roll=0));sun.set_actor_label('Lodge_Surface_Review_Temporary');temps.append(sun);sun.get_component_by_class(unreal.DirectionalLightComponent).set_mobility(unreal.ComponentMobility.MOVABLE);sun.get_component_by_class(unreal.DirectionalLightComponent).set_intensity(3)
settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'));throttle=settings.get_editor_property('bThrottleCPUWhenNotForeground');settings.set_editor_property('bThrottleCPUWhenNotForeground',False)
views=[]
for r in json.loads((OUT.parents[2]/'art/blender/passenger_lodge_restrooms_01/previews/views_all.json').read_text()):
 if r['name']=='09_all_swings':continue
 def convert(p):return [p[0]-24.1,4-p[1],4+p[2]]
 views.append((r['name'],convert(r['camera_local']),convert(r['target_local'])))
for room,x in [('Women',10.45),('Men',12.45)]:
 for side in [-1,1]:
  for i in range(3):views.append((room+'_header_'+str(side)+'_'+str(i),[x-24.1-.2+i*.04,4-13.11+side*.7,6.12],[x-24.1,4-13.11,6.21]))
state={'index':0,'phase':'set','next':time.monotonic()+5,'deadline':time.monotonic()+360};rows=[]
def finish(error=None):
 for a in temps:aa.destroy_actor(a)
 settings.set_editor_property('bThrottleCPUWhenNotForeground',throttle);unreal.unregister_slate_post_tick_callback(handle)
 (OUT/'restrooms/review.json').write_text(json.dumps({'views':rows,'error':error,'temporary_lights_removed':True,'mode':'Lit neutral, roof visible; restroom doors closed'},indent=2))

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

"""Imported pilot material/geometry checks and two lighting review captures."""
import unreal,json,time,traceback
from pathlib import Path
base=Path(__file__).resolve().parents[1];out=base/'pilot';out.mkdir(exist_ok=True)
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert world.get_name()=='Station_R12'
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);lib=unreal.EditorAssetLibrary
origin=json.loads((base.parent/'working_level_report.json').read_text())['station_origin']
def wp(p):return unreal.Vector(origin[0]-100*p[0],origin[1]+100*p[1],origin[2]+100*p[2])
def capsule(a,b):
 return unreal.SystemLibrary.capsule_trace_single(world,wp(a),wp(b),34,96,unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,False,[],unreal.DrawDebugTrace.NONE,True)
checks=[]
for name,x,blocked in [('door_center',-30,False),('left_jamb',-30.65,True),('right_jamb',-29.35,True)]:
 hit=capsule((x,-6,13),(x,-4,13));actual=bool(hit and hit.to_tuple()[0]);checks.append({'name':name,'expected_block':blocked,'actual_block':actual});assert actual==blocked,(name,str(hit))
for row in json.loads((base/'probe_import.json').read_text())['assets']:
 mesh=lib.load_asset(row['path']);assert mesh
 assert all(s.material_interface and '/R12/' in s.material_interface.get_path_name() for s in mesh.static_materials),row['name']
unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).set_level_viewport_camera_info(wp((-33,3,16)),unreal.MathLibrary.find_look_at_rotation(wp((-33,3,16)),wp((-30,-4,13))))
state={'stage':0,'next':time.monotonic()+12,'lights':[],'checks':checks}
def tick(dt):
 if time.monotonic()<state['next']:return
 try:
  if state['stage']==0:
   unreal.AutomationLibrary.take_high_res_screenshot(2560,1440,str(out/'night.png'))
   light=aa.spawn_actor_from_class(unreal.RectLight,wp((-30,1,16)),unreal.MathLibrary.find_look_at_rotation(wp((-30,1,16)),wp((-30,-4,13))))
   light.set_actor_label('R12_Temporary_Pilot_Inspection_Light');c=light.get_component_by_class(unreal.RectLightComponent);c.set_intensity(16000);c.set_editor_property('attenuation_radius',2500);c.set_editor_property('source_width',700);c.set_editor_property('source_height',500);state['lights'].append(light)
   state.update(stage=1,next=time.monotonic()+12);return
  if state['stage']==1:
   unreal.AutomationLibrary.take_high_res_screenshot(2560,1440,str(out/'neutral.png'));state.update(stage=2,next=time.monotonic()+4);return
  for a in state['lights']:aa.destroy_actor(a)
  unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
  (out/'validation.json').write_text(json.dumps({'success':True,'capsule_radius_cm':34,'capsule_half_height_cm':96,'collision_checks':checks,'visual_review':'pending human/model image inspection','inspection_lights_removed':True},indent=2));unreal.unregister_slate_post_tick_callback(handle)
 except Exception:
  for a in state['lights']:
   if a:aa.destroy_actor(a)
  (out/'validation.json').write_text(json.dumps({'success':False,'error':traceback.format_exc()},indent=2));unreal.unregister_slate_post_tick_callback(handle)
handle=unreal.register_slate_post_tick_callback(tick)
RESULT={'started':True,'collision_checks':checks}

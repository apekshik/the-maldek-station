"""PIE door movement, privacy bolt/indicator and player routes to every fixture."""
import unreal,json,time,traceback
from pathlib import Path
OUT=Path(__file__).resolve().parents[1];dest=OUT/'restrooms';shots=OUT/'previews/restrooms_night';shots.mkdir(exist_ok=True);ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
assert unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_name()=='Station_Lodge_Migration'
settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'));throttle=settings.get_editor_property('bThrottleCPUWhenNotForeground');settings.set_editor_property('bThrottleCPUWhenNotForeground',False)
o=json.loads((OUT/'before.json').read_text())['origin'];data=json.loads((dest/'exports.json').read_text());specs=[r for r in data['groups'] if r['door']];routes=json.loads((OUT.parents[2]/'art/blender/passenger_lodge_restrooms_01/verification.json').read_text())['routes']
s={'phase':0,'index':0,'next':time.monotonic()+12,'deadline':time.monotonic()+480,'checks':{},'images':[],'routes':[],'busy':False}
def advance(n,wait=.2):s.update(phase=n,next=time.monotonic()+wait)
def check(n,v):s['checks'][n]=bool(v);assert v,n
def key(down):unreal.StationMigrationLibrary.send_pie_key('E',down)
def world(v):return unreal.MathLibrary.transform_location(d.get_actor_transform(),unreal.Vector(*v))
def put(side,distance=140,bolt=False):
 p.character_movement.set_movement_mode(unreal.MovementMode.MOVE_FLYING);p.character_movement.stop_movement_immediately();p.set_actor_location(world([cx,side*distance,99-offset]),False,True);aim(bolt)
def aim(bolt=False):
 target=world([r['bolt_focus_source'][0]*100,-r['bolt_focus_source'][1]*100,r['bolt_focus_source'][2]*100]) if bolt else world([cx,0,150-offset]);pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(p.get_actor_location()+unreal.Vector(0,0,64),target))
def shot(name):
 file=shots/(name+'.png');unreal.AutomationLibrary.take_high_res_screenshot(1600,1000,str(file));s['images'].append(str(file))
def finish(error=None):
 key(False);settings.set_editor_property('bThrottleCPUWhenNotForeground',throttle);unreal.StationMigrationLibrary.set_pie_render_size(0,0);s.update(success=error is None,error=error);(dest/'runtime.json').write_text(json.dumps({k:v for k,v in s.items() if k!='busy'},indent=2));unreal.unregister_slate_post_tick_callback(handle);ls.editor_request_end_play()
def localpoint(v):return unreal.Vector(o[0]-100*(v[0]-24.1),o[1]+100*(4-v[1]),o[2]+499)
def tick(dt):
 global d,p,pc,r,cx,offset,doors,target,route
 if s['busy']:return
 s['busy']=True
 try:
  now=time.monotonic()
  if now<s['next']:return
  assert now<s['deadline'],'timeout';w=unreal.EditorLevelLibrary.get_game_world()
  if not w:return
  p=unreal.GameplayStatics.get_player_pawn(w,0);pc=unreal.GameplayStatics.get_player_controller(w,0)
  if not p:return
  phase=s['phase']
  if phase==0:
   unreal.StationMigrationLibrary.set_pie_render_size(1600,1000);doors={a.get_actor_label():a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.StationDoor)}
   for c in p.get_components_by_class(unreal.ActorComponent):
    if c.get_class().get_name()=='StationOpeningComponent':c.destroy_component(p)
   if not p.get_components_by_class(unreal.SpotLightComponent)[0].is_visible():p.toggle_flashlight()
   advance(1);return
  if phase==1:
   if s['index']==len(specs):advance(40);return
   r=specs[s['index']];d=doors['MIG_PLR_'+r['id']];cx=r['leaf_collision_source']['center'][0]*100;offset=(r['matrix'][2][3]-4)*100;check(r['id']+'_initial_vacant',not d.is_locked() and abs(d.get_open_angle())<.01);put(-1);advance(2,.7);return
  if phase==2:key(True);advance(3,.15);return
  if phase==3:key(False);advance(4,.5);return
  if phase==4:check(r['id']+'_lever_motion',abs(d.front_lever.get_relative_transform().rotation.rotator().pitch)>1 and abs(d.back_lever.get_relative_transform().rotation.rotator().pitch)>1);check(r['id']+'_movement_audio',d.get_editor_property('MotionAudio').is_playing());advance(5,1.8);return
  if phase==5:check(r['id']+'_full_swing',abs(d.get_open_angle()-r['open_angle'])<.1);shot(r['id']+'_open');advance(5.5,1);return
  if phase==5.5:put(1,120 if r['entry'] else 45);advance(6,.7);return
  if phase==6:d.try_interact();advance(7,2);return
  if phase==7:
   check(r['id']+'_close_from_inside',abs(d.get_open_angle())<.01 and not d.is_locked())
   if r['entry']:s['index']+=1;advance(1);return
   aim(True);advance(8,.5);return
  if phase==8:key(True);advance(9,.15);return
  if phase==9:key(False);advance(10,.4);return
  if phase==10:
   check(r['id']+'_bolt_locks',d.is_locked());check(r['id']+'_bolt_extended',abs(d.moving_latch.get_relative_transform().translation.x-2)<.01);color=d.privacy_indicator.get_material(0).get_vector_parameter_value('StateColor');check(r['id']+'_red_indicator',color.r>color.g);shot(r['id']+'_locked_inside');advance(11,1);return
  if phase==11:key(True);advance(12,.15);return
  if phase==12:key(False);advance(13,.4);return
  if phase==13:
   check(r['id']+'_bolt_unlocks_without_opening',not d.is_locked() and abs(d.get_open_angle())<.01);color=d.privacy_indicator.get_material(0).get_vector_parameter_value('StateColor');check(r['id']+'_green_indicator',color.g>color.r);key(True);advance(14,.15);return
  if phase==14:key(False);advance(15,.4);return
  if phase==15:check(r['id']+'_relock',d.is_locked());put(-1,90);advance(16,.6);return
  if phase==16:key(True);advance(17,.15);return
  if phase==17:key(False);advance(18,.5);return
  if phase==18:check(r['id']+'_outside_blocked',d.is_locked() and abs(d.get_open_angle())<.01);check(r['id']+'_outside_prompt',d.interaction_prompt.is_visible());shot(r['id']+'_occupied');advance(18.5,1);return
  if phase==18.5:put(1,45);advance(19,.6);return
  if phase==19:key(True);advance(20,.15);return
  if phase==20:key(False);advance(21,2);return
  if phase==21:check(r['id']+'_inside_egress',not d.is_locked() and abs(d.get_open_angle()-r['open_angle'])<.1);put(-1);d.try_interact();advance(22,2);return
  if phase==22:check(r['id']+'_ends_vacant',not d.is_locked() and abs(d.get_open_angle())<.01);s['index']+=1;advance(1);return
  if phase==40:
   p.set_actor_location(localpoint([9,10.5]),False,True)
   for row in specs:
    a=doors['MIG_PLR_'+row['id']];a.unlock();a.try_interact()
   s['route_index']=0;advance(41,2.5);return
  if phase==41:
   if s['route_index']==len(routes):finish();return
   route=routes[s['route_index']];p.character_movement.set_movement_mode(unreal.MovementMode.MOVE_WALKING);p.character_movement.max_walk_speed=135;p.character_movement.stop_movement_immediately();p.set_actor_location(localpoint(route['path_local'][0]),False,True);s['waypoint']=1;s['walk_started']=now;s['max_floor_error']=0;advance(42,.5);return
  if phase==42:
   target=localpoint(route['path_local'][s['waypoint']]);delta=target-p.get_actor_location();delta.z=0
   if delta.length()>5:
    assert now-s['walk_started']<35,route['name']+' stalled';p.add_movement_input(delta/delta.length(),min(1,max(.12,delta.length()/60)),True);pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(p.get_actor_location(),target));s['max_floor_error']=max(s['max_floor_error'],abs(p.get_actor_location().z-p.capsule_component.get_scaled_capsule_half_height()-(o[2]+400)));return
   s['waypoint']+=1
   if s['waypoint']<len(route['path_local']):return
   p.character_movement.stop_movement_immediately();check(route['name']+'_walking',s['max_floor_error']<8);s['routes'].append({'name':route['name'],'max_floor_error_cm':s['max_floor_error']});shot(route['name']);s['route_index']+=1;advance(41,1);return
 except Exception:finish(traceback.format_exc())
 finally:s['busy']=False
handle=unreal.register_slate_post_tick_callback(tick);ls.editor_request_begin_play();RESULT={'started':True}

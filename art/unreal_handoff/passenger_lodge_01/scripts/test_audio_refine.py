"""Actual movement, no-repeat sample selection, and sheltered storm transition checks."""
import unreal,time,json,traceback
from pathlib import Path
O=Path(__file__).resolve().parents[1];D=O/'audio_refine';ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);assert not ls.is_in_play_in_editor()
o=json.loads((O/'before.json').read_text())['origin']
def pt(x,d,z=4.99):return unreal.Vector(o[0]+2410-x*100,o[1]+400-d*100,o[2]+z*100)
pad=aa.spawn_actor_from_class(unreal.StaticMeshActor,pt(100,100,100));pad.set_actor_label('TEMP_Audio_Concrete');pad.static_mesh_component.set_static_mesh(unreal.EditorAssetLibrary.load_asset('/Engine/BasicShapes/Cube'));pad.set_actor_scale3d(unreal.Vector(20,4,.2));pad.static_mesh_component.set_phys_material_override(unreal.EditorAssetLibrary.load_asset('/Game/MaldekRefinement/ForestTest/Audio/Surfaces/PM_Concrete'))
s={'phase':0,'next':time.monotonic()+12,'deadline':time.monotonic()+300,'checks':{},'routes':[],'takes':{},'busy':False}
settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'));throttle=settings.get_editor_property('bThrottleCPUWhenNotForeground');settings.set_editor_property('bThrottleCPUWhenNotForeground',False)
def advance(n,t=.2):s.update(phase=n,next=time.monotonic()+t)
def check(k,v):s['checks'][k]=bool(v);assert v,k
def finish(error=None):
 s.update(success=error is None,error=error);(D/'runtime.json').write_text(json.dumps({k:v for k,v in s.items() if k!='busy'},indent=2));ls.editor_request_end_play();s['phase']=99

def tick(dt):
 global p,pc,storm,foot,selected,d
 if s['busy']:return
 s['busy']=True
 try:
  now=time.monotonic()
  if s['phase']==99:
   if not ls.is_in_play_in_editor():aa.destroy_actor(pad);settings.set_editor_property('bThrottleCPUWhenNotForeground',throttle);unreal.unregister_slate_post_tick_callback(handle)
   return
  if now<s['next']:return
  assert now<s['deadline'],'timeout';w=unreal.EditorLevelLibrary.get_game_world()
  if not w:return
  p=unreal.GameplayStatics.get_player_pawn(w,0);pc=unreal.GameplayStatics.get_player_controller(w,0)
  if not p:return
  phase=s['phase']
  if phase==0:
   for c in p.get_components_by_class(unreal.ActorComponent):
    if c.get_class().get_name()=='StationOpeningComponent':c.destroy_component(p)
   foot=p.get_components_by_class(unreal.SurfaceFootstepComponent)[0];check('separate_boot_banks',len(foot.tile_steps)==6 and len(foot.concrete_steps)==6 and set(foot.tile_steps).isdisjoint(foot.concrete_steps))
   storm=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.StationLodgeAcoustics)[0];p.character_movement.set_movement_mode(unreal.MovementMode.MOVE_FLYING);p.set_actor_location(pt(7,5),False,True);advance(1,3);return
  if phase==1:
   check('storm_inside',storm.interior_blend>.99 and storm.wind_audio.is_playing());check('court_excluded',storm.weight_at(pt(6.5,14))==0);check('roof_excluded',storm.weight_at(pt(7,5,9))==0);check('restrooms_included',storm.weight_at(pt(12,15))==1);check('coffee_included',storm.weight_at(pt(2.5,14))==1);unreal.AudioMixerLibrary.start_recording_output(w,8);advance(2,6);return
  if phase==2:
   unreal.AudioMixerLibrary.stop_recording_output(w,unreal.AudioRecordingExportType.WAV_FILE,'Sheltered_storm_game',str(D));p.set_actor_location(pt(6.5,14),False,True);advance(3,.4);return
  if phase==3:check('smooth_fade',0<storm.interior_blend<1);advance(4,2);return
  if phase==4:
   check('no_indoor_layer_outside',storm.interior_blend==0);p.set_actor_location(pt(7,5),False,True);storm.storm_intensity=0;advance(5,2);return
  if phase==5:
   check('calm_weather_silent',storm.interior_blend==0);storm.storm_intensity=1
   # Test a representative of every recording family with three complete cycles.
   actors=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.StationCabinet);selected=[]
   for prefix in ['MIG_PLL_','MIG_PLK_Serving_','MIG_PLK_Hot_base_','MIG_PLK_Fridge_']:
    selected.append(next(a for a in actors if a.get_actor_label().startswith(prefix)))
   s.update(index=0,cycle=0);advance(6);return
  if phase==6:
   if s['index']==len(selected):s['route_index']=0;advance(10);return
   d=selected[s['index']];p.set_actor_location(pt(7,5),False,True);d.try_interact();s.setdefault('current',{})['open']=d.motion_audio.sound.get_path_name();advance(7,1.5);return
  if phase==7:
   check(d.get_actor_label()+'_open',d.get_open_fraction()==1);d.try_interact();s['current']['close']=d.motion_audio.sound.get_path_name();advance(8,1.5);return
  if phase==8:
   label=d.get_actor_label();check(label+'_closed',d.get_open_fraction()==0);history=s['takes'].setdefault(label,[])
   if history:check(label+'_no_repeat_'+str(s['cycle']),all(history[-1][k]!=s['current'][k] for k in ['open','close']))
   history.append(s.pop('current'));s['cycle']+=1
   if s['cycle']==3:s['index']+=1;s['cycle']=0
   advance(6);return
  if phase==10:
   if s['route_index']==2:finish();return
   ri=s['route_index'];p.character_movement.stop_movement_immediately();p.set_actor_location(pt(7,9.5) if ri==0 else pt(104,100,101.1),False,True);p.character_movement.set_movement_mode(unreal.MovementMode.MOVE_WALKING);p.character_movement.max_walk_speed=220;s.update(count=foot.footstep_count,steps=[],last=foot.footstep_count,start=now);unreal.AudioMixerLibrary.start_recording_output(w,15);advance(11,.7);return
  if phase==11:
   ri=s['route_index'];target=pt(7,.8) if ri==0 else pt(96,100,101.1);delta=target-p.get_actor_location();delta.z=0
   if foot.footstep_count!=s['last']:s['steps'].append(foot.last_surface);s['last']=foot.footstep_count
   assert now-s['start']<18,'walking blocked'
   if delta.length()>12:p.add_movement_input(delta/delta.length(),min(1,delta.length()/70),True);advance(11,.01);return
   p.character_movement.stop_movement_immediately();check('tile' if ri==0 else 'concrete',len(s['steps'])>=3 and set(s['steps'])=={6 if ri==0 else 4});unreal.AudioMixerLibrary.stop_recording_output(w,unreal.AudioRecordingExportType.WAV_FILE,'Tile_steps_game' if ri==0 else 'Concrete_steps_game',str(D));s['routes'].append({'surface':6 if ri==0 else 4,'steps':s['steps']});s['route_index']+=1;advance(10,1);return
 except Exception:finish(traceback.format_exc())
 finally:s['busy']=False
handle=unreal.register_slate_post_tick_callback(tick);ls.editor_request_begin_play();RESULT={'started':True}

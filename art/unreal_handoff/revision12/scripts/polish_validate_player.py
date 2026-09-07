"""Real PIE input and movement checks for the polished player; no saved test actors."""
import unreal,json,time,traceback,math
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/JOB.get('output','polish');out.mkdir(parents=True,exist_ok=True);ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
o=json.loads((b.parent/'working_level_report.json').read_text())['station_origin']
settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'));throttle=settings.get_editor_property('bThrottleCPUWhenNotForeground');settings.set_editor_property('bThrottleCPUWhenNotForeground',False)
s={'phase':'start','next':time.monotonic()+8,'checks':{},'samples':{'walk':[],'run':[]},'busy':False,'deadline':time.monotonic()+180}
def key(k):
 unreal.StationMigrationLibrary.send_pie_key(k,True)
 unreal.StationMigrationLibrary.send_pie_key(k,False)
def finish():
 for k in ['LeftShift','F','MouseScrollUp','MouseScrollDown']:unreal.StationMigrationLibrary.send_pie_key(k,False)
 settings.set_editor_property('bThrottleCPUWhenNotForeground',throttle)
 s['success']='error' not in s and all(s['checks'].values());s['phase']='finished';(out/'player_validation.json').write_text(json.dumps(s,indent=2));ls.editor_request_end_play();unreal.unregister_slate_post_tick_callback(handle)
def tick(dt):
 if s['busy'] or time.monotonic()<s['next']:return
 s['busy']=True
 try:
  now=time.monotonic();assert now<s['deadline'],'timeout'
  w=unreal.EditorLevelLibrary.get_game_world()
  if not w:return
  p=unreal.GameplayStatics.get_player_pawn(w,0)
  if not p:return
  c=p.get_component_by_class(unreal.StationPlayerPresentationComponent);beam=p.get_component_by_class(unreal.SpotLightComponent);m=p.character_movement;foot=p.get_component_by_class(unreal.SurfaceFootstepComponent)
  if s['phase']=='start':
   s['pawn']=p.get_class().get_path_name();s['checks']['polished_pawn']='Polished' in s['pawn'];s['checks']['unlimited_enabled']=p.get_editor_property('unlimited_sprint')
   s['checks']['detailed_torch']=any(x.get_name()=='HeldTorchDetailed' and x.static_mesh for x in p.get_components_by_class(unreal.StaticMeshComponent))
   s['stamina_verification']='Native HorrorUI.SetupCharacter collapses the unlimited-sprint widget; also inspect captured viewport.'
   s['initial_focus']=c.get_target_focus();key('MouseScrollUp');s.update(phase='scroll',next=now+.7);return
  if s['phase']=='scroll':
   s['checks']['wheel_focus']=abs(c.get_target_focus()-s['initial_focus']-.1)<.001
   for i in range(20):key('MouseScrollUp')
   s.update(phase='narrow',next=now+1);return
  if s['phase']=='narrow':
   s['narrow']={'focus':c.get_focus(),'angle':beam.outer_cone_angle,'range':beam.attenuation_radius,'intensity':beam.intensity};s['checks']['narrow_clamped']=c.get_target_focus()==1 and abs(beam.outer_cone_angle-11)<.01
   if JOB.get('focused_intensity') is not None:s['checks']['focused_intensity']=abs(beam.intensity-JOB['focused_intensity'])<.01
   for i in range(20):key('MouseScrollDown')
   s.update(phase='wide',next=now+1);return
  if s['phase']=='wide':
   s['wide']={'focus':c.get_focus(),'angle':beam.outer_cone_angle,'range':beam.attenuation_radius};s['checks']['wide_clamped']=c.get_target_focus()==0 and abs(beam.outer_cone_angle-34)<.01
   s['checks']['focus_extends_range']=s['narrow']['range']>s['wide']['range']*3
   s['initial_visible']=beam.is_visible();key('F');s.update(phase='off',next=now+.3);return
  if s['phase']=='off':
   s['checks']['toggle_off']=beam.is_visible()!=s['initial_visible'];key('F');s.update(phase='on',next=now+.3);return
  if s['phase']=='on':
   s['checks']['toggle_on']=beam.is_visible()==s['initial_visible'];s['checks']['focus_retained']=c.get_target_focus()==0;c.set_focus(.35)
   p.set_actor_location(unreal.Vector(o[0]+2050,o[1],o[2]+500),False,True);m.stop_movement_immediately();s.update(phase='settle',next=now+2);return
  if s['phase']=='settle':
   assert not m.is_falling();s['idle_count']=foot.footstep_count;s.update(phase='idle',next=now+2);return
  if s['phase']=='idle':
   s['checks']['idle_silent']=foot.footstep_count==s['idle_count'];s['checks']['idle_camera_settles']=c.get_view_offset().length()<.01
   s.update(phase='walk',started=now,next=now,direction=1);return
  if s['phase'] in ['walk','run']:
   phase=s['phase'];pos=p.get_actor_location();y=(pos.y-o[1])/100
   if y>5:s['direction']=-1
   if y<-6:s['direction']=1
   p.add_movement_input(unreal.Vector(0,s['direction'],0),1,False)
   s['samples'][phase].append([round(now-s['started'],3),round(p.get_velocity().length(),2),round(c.get_view_offset().z,4),m.is_falling()])
   if now-s['started']>(9 if phase=='walk' else 35):
    if phase=='walk':
     unreal.StationMigrationLibrary.send_pie_key('LeftShift',True);s.update(phase='run',started=now);return
    s['checks']['sustained_run']=m.max_walk_speed>=599 and max(r[1] for r in s['samples']['run'][-100:])>590
    unreal.StationMigrationLibrary.send_pie_key('LeftShift',False);m.stop_movement_immediately();s.update(phase='stop',next=now+2);return
   return
  if s['phase']=='stop':
   s['checks']['release_walk_speed']=abs(m.max_walk_speed-350)<1;s['checks']['camera_settles_after_run']=c.get_view_offset().length()<.01
   for name,rows in s['samples'].items():
    s['checks'][name+'_grounded']=all(not r[3] for r in rows);s['checks'][name+'_bob_bounded']=max(abs(r[2]) for r in rows)<2
   def hz(rows):
    rows=[r for r in rows if r[0]>1];return sum(a[2]<0<=z[2] for a,z in zip(rows,rows[1:]))/(rows[-1][0]-rows[0][0])
   s['cadence_hz']={n:hz(r) for n,r in s['samples'].items()};s['checks']['run_bob_faster']=s['cadence_hz']['run']>s['cadence_hz']['walk']*1.25
   s['checks']['moving_footsteps']=foot.footstep_count>s['idle_count'];s['footsteps']=foot.footstep_count-s['idle_count'];finish()
 except Exception:s['error']=traceback.format_exc();finish()
 finally:s['busy']=False
handle=unreal.register_slate_post_tick_callback(tick);ls.editor_request_begin_play();RESULT={'started':True}

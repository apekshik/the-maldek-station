import unreal,json,time,traceback,statistics
from pathlib import Path
P=Path(__file__).resolve().parents[1];ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor();o=json.loads((P/'baseline.json').read_text())['origin'];settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'));old=settings.get_editor_property('bThrottleCPUWhenNotForeground');settings.set_editor_property('bThrottleCPUWhenNotForeground',False)
views=[('compound',[-27,13,10],[-35,0,4]),('west_outward',[-39.6,0,2.85],[-48,0,-1]),('rescue',[-32.8,3.8,6.25],[-36,2.5,5.6])];s={'phase':0,'index':0,'next':time.monotonic()+10,'deadline':time.monotonic()+240,'samples':[],'results':[],'busy':False}
def wp(q):return unreal.Vector(o[0]-100*q[0],o[1]+100*q[1],o[2]+100*q[2])
def finish(error=None):
 settings.set_editor_property('bThrottleCPUWhenNotForeground',old);unreal.StationMigrationLibrary.set_pie_render_size(0,0);(P/'performance.json').write_text(json.dumps({'error':error,'method':'PIE paired 1600x1000, same camera/settings, 60 samples per state. Reference hides only new WestServices actors; terrain and relocated native foliage remain identical. This isolates added render/actor cost, not a whole-map historical benchmark.','results':s['results']},indent=2));unreal.unregister_slate_post_tick_callback(handle);ls.editor_request_end_play()
def tick(dt):
 global p,pc,actors,w
 if s['busy'] or time.monotonic()<s['next']:return
 s['busy']=True
 try:
  assert time.monotonic()<s['deadline'];w=unreal.EditorLevelLibrary.get_game_world()
  if not w:return
  p=unreal.GameplayStatics.get_player_pawn(w,0);pc=unreal.GameplayStatics.get_player_controller(w,0)
  if not p:return
  if s['phase']==0:
   actors=[a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.Actor) if a.get_actor_label().startswith('MIG_WS_')]
   for c in p.get_components_by_class(unreal.ActorComponent):
    if c.get_class().get_name()=='StationOpeningComponent':c.destroy_component(p)
   p.character_movement.set_movement_mode(unreal.MovementMode.MOVE_FLYING);p.set_actor_enable_collision(False);unreal.StationMigrationLibrary.set_pie_render_size(1600,1000);unreal.SystemLibrary.execute_console_command(w,'stat unit');s['phase']=1
  if s['index']==6:finish();return
  name,pos,target=views[s['index']//2];added=s['index']%2==1
  if s['phase']==1:
   for a in actors:a.set_actor_hidden_in_game(not added)
   p.set_actor_location(wp(pos)-unreal.Vector(0,0,64),False,True);pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(wp(pos),wp(target)));s.update(phase=2,next=time.monotonic()+5,samples=[])
  else:
   s['samples'].append(dict(unreal.StationMigrationLibrary.capture_pie_frame_stats()));s['next']=time.monotonic()+.05
   if len(s['samples'])>=60:
    s['results'].append({'view':name,'new_actors_visible':added,'median':{k:statistics.median(x[k] for x in s['samples']) for k in s['samples'][0]},'samples':s['samples']});s.update(index=s['index']+1,phase=1)
 except Exception:finish(traceback.format_exc())
 finally:s['busy']=False
handle=unreal.register_slate_post_tick_callback(tick);ls.editor_request_begin_play();RESULT={'started':True}

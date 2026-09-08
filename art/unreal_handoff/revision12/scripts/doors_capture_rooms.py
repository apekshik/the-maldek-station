"""Small sequential PIE captures with temporary inspection light; never saves test actors."""
import unreal,json,time,traceback
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'doors'/'room_previews';out.mkdir(exist_ok=True)
ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'));throttle=settings.get_editor_property('bThrottleCPUWhenNotForeground');settings.set_editor_property('bThrottleCPUWhenNotForeground',False)
s={'phase':0,'index':0,'next':time.monotonic()+8,'deadline':time.monotonic()+240,'files':[]};shots=[]
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
editor_lamp=aa.spawn_actor_from_class(unreal.RectLight,unreal.Vector(0,0,-10000));editor_lamp.set_actor_label('D03_Transient_InspectionLight')
def finish(error=None):
 settings.set_editor_property('bThrottleCPUWhenNotForeground',throttle);unreal.StationMigrationLibrary.set_pie_render_size(0,0);s['success']=error is None;s['error']=error;(out/'capture.json').write_text(json.dumps(s,indent=2));unreal.unregister_slate_post_tick_callback(handle);ls.editor_request_end_play()
 def cleanup(dt):
  if ls.is_in_play_in_editor():return
  s['temporary_light_removed']=aa.destroy_actor(editor_lamp);(out/'capture.json').write_text(json.dumps(s,indent=2));unreal.unregister_slate_post_tick_callback(clean_handle)
 clean_handle=unreal.register_slate_post_tick_callback(cleanup)
def tick(dt):
 global front,side,lamp
 if time.monotonic()<s['next']:return
 try:
  now=time.monotonic();assert now<s['deadline'],'timeout';w=unreal.EditorLevelLibrary.get_game_world()
  if not w:return
  p=unreal.GameplayStatics.get_player_pawn(w,0);pc=unreal.GameplayStatics.get_player_controller(w,0)
  if not p:return
  if s['phase']==0:
   unreal.StationMigrationLibrary.set_pie_render_size(1280,720);p.character_movement.set_movement_mode(unreal.MovementMode.MOVE_FLYING)
   doors={a.get_actor_label():a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.StationDoor)};targets=[(doors[r['label']],r['label']) for r in json.loads((out.parent/'rooms_install.json').read_text())['new_doors']]
   for d,n in targets:
    for mode in ['night','neutral']:
     for i in range(3):shots.append((d,n+'_'+mode+'_'+str(i),mode,unreal.Vector(75+i*2,220,120)))
   for d,n in targets:
    if d.open_angle<0:
     for mode in ['night','neutral']:
      for i in range(3):shots.append((d,n+'_inside_'+mode+'_'+str(i),mode,unreal.Vector(75+i*2,-220,120)))
   lamp=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RectLight) if a.get_actor_label()=='D03_Transient_InspectionLight')
   c=lamp.get_component_by_class(unreal.RectLightComponent);c.set_mobility(unreal.ComponentMobility.MOVABLE);c.set_intensity(20);c.set_editor_property('attenuation_radius',600);c.set_editor_property('source_width',160);c.set_editor_property('source_height',160);lamp.set_actor_hidden_in_game(True)
   s['phase']=1
  if s['phase']==1:
   if s['index']>=len(shots):finish();return
   door,name,mode,offset=shots[s['index']];t=door.get_actor_transform();pos=unreal.MathLibrary.transform_location(t,offset);target=unreal.MathLibrary.transform_location(t,unreal.Vector(64,0,125))
   # Pawn origin includes eye height; aim using the actual player camera after settling.
   p.set_actor_location(pos,False,True);p.character_movement.stop_movement_immediately();pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(pos+unreal.Vector(0,0,60),target))
   lamp.set_actor_hidden_in_game(mode!='neutral');lp=unreal.MathLibrary.transform_location(t,unreal.Vector(-30,180 if offset.y>0 else -180,240));lamp.set_actor_location(lp,False,True);lamp.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(lp,target),False)
   for beam in p.get_components_by_class(unreal.SpotLightComponent):beam.set_visibility(mode=='night')
   s.update(phase=2,next=now+(5 if s['index']%3==0 else .3));return
  if s['phase']==2:
   name=shots[s['index']][1];file=out/(name+'.png');file.unlink(missing_ok=True);unreal.AutomationLibrary.take_high_res_screenshot(1280,720,str(file));s['awaiting']=str(file);s.update(phase=3,next=now+.3);return
  if s['phase']==3:
   file=Path(s['awaiting'])
   if not file.exists() or file.stat().st_size<1000:return
   s['files'].append(str(file));s['index']+=1;s['phase']=1;s['next']=now+.2
 except Exception:finish(traceback.format_exc())
handle=unreal.register_slate_post_tick_callback(tick);ls.editor_request_begin_play();RESULT={'started':True}

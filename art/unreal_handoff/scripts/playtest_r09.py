"""Exercise the saved review pawn and prove the cabin cannot inherit route movement."""
import unreal,time,json,traceback
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'revision09'
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert levels.save_current_level();assert levels.load_level('/Game/MaldekRefinement/R09/BlockOut_R09')
editoractors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
cab=next(a for a in editoractors if a.get_actor_label()=='R04_12_Gondola')
assert cab.get_attach_parent_actor() is None
assert cab.static_mesh_component.get_editor_property('mobility')==unreal.ComponentMobility.STATIC
p=cab.get_actor_location();q=cab.get_actor_transform().rotation
state={'start':time.monotonic(),'ready':False,'location':[p.x,p.y,p.z],'rotation':[q.x,q.y,q.z,q.w],'max_delta_cm':0.,'max_rotation_delta':0.}
def tick(dt):
 try:
  now=time.monotonic()
  if now-state['start']>45:raise RuntimeError('PIE verification timeout')
  world=unreal.EditorLevelLibrary.get_game_world()
  if not world:return
  aa=unreal.GameplayStatics.get_all_actors_of_class(world,unreal.Actor)
  cabin=next((a for a in aa if a.get_actor_label()=='R04_12_Gondola'),None)
  pawn=unreal.GameplayStatics.get_player_pawn(world,0)
  if not cabin or not pawn:return
  if not state['ready']:
   assert pawn.get_class().get_name()=='BP_StationWalker_C',pawn.get_class().get_name()
   light=pawn.get_components_by_class(unreal.SpotLightComponent)[0]
   state['flashlight_lumens']=light.get_editor_property('intensity');assert abs(state['flashlight_lumens']-.2)<.001
   state['held_mesh_count']=len(pawn.get_components_by_class(unreal.StaticMeshComponent));assert state['held_mesh_count']>=11
   state['walk_speed']=pawn.get_components_by_class(unreal.CharacterMovementComponent)[0].get_editor_property('max_walk_speed');assert abs(state['walk_speed']-350)<.1
   state['walk_start']=[pawn.get_actor_location().x,pawn.get_actor_location().y,pawn.get_actor_location().z];state['pawn']=pawn.get_class().get_name();state['ready']=True;state['ready_time']=now
   ctrl=next(a for a in aa if a.get_class().get_name()=='BP_GondolaSystem_C');ctrl.set_editor_property('travel_time',1.);ctrl.set_editor_property('wait_time_at_maldek',.5);ctrl.set_actor_tick_enabled(True);ctrl.send_gondola()
  if now-state['ready_time']<.6:pawn.add_movement_input(unreal.Vector(-1,0,0),1.,False)
  p=cabin.get_actor_location();q=cabin.get_actor_transform().rotation
  state['max_delta_cm']=max(state['max_delta_cm'],sum((v-o)**2 for v,o in zip([p.x,p.y,p.z],state['location']))**.5)
  state['max_rotation_delta']=max(state['max_rotation_delta'],max(abs(v-o) for v,o in zip([q.x,q.y,q.z,q.w],state['rotation'])))
  if now-state['ready_time']>9:
   assert state['max_delta_cm']<.01 and state['max_rotation_delta']<.00001
   v=pawn.get_actor_location();state['walk_displacement_cm']=sum((v0-v1)**2 for v0,v1 in zip([v.x,v.y,v.z],state['walk_start']))**.5;assert state['walk_displacement_cm']>15
   state['success']=True
   (out/'play_verification.json').write_text(json.dumps(state,indent=2))
   unreal.unregister_slate_post_tick_callback(handle)
 except Exception:
  (out/'play_verification.json').write_text(json.dumps({'success':False,'error':traceback.format_exc()},indent=2));unreal.unregister_slate_post_tick_callback(handle)
handle=unreal.register_slate_post_tick_callback(tick)
levels.editor_request_begin_play()

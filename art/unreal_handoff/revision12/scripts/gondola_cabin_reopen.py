"""Reload the saved level and verify the installed cabin, collision and sound assignments."""
import unreal,json,time,traceback
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'gondola_cabin';ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);assert not ls.is_in_play_in_editor()
assert not any(a.get_actor_label()=='Cabin_Inspection_Temporary' for a in aa.get_all_level_actors())
assert ls.save_current_level();assert ls.load_level('/Game/MaldekRefinement/R12/Station_R12');start=time.monotonic()
def check(dt):
 if time.monotonic()-start<8:return
 unreal.unregister_slate_post_tick_callback(handle)
 try:
  actors={a.get_actor_label():a for a in aa.get_all_level_actors()};g=actors['BP_GondolaSystem'];report={'passed':True,'reopened':True,'checks':[]}
  assert not any(k.startswith(('R12_12_Gondola_','R12_VF06_Gondola_Details_')) for k in actors)
  assert len(g.door_rollers)==8 and all(c.static_mesh for c in g.door_rollers)
  assert g.door_left.static_mesh and g.door_right.static_mesh and g.door_pinion.static_mesh
  assert g.door_open_sound and g.door_close_sound
  assert g.door_open_sound.get_editor_property('duration')>3.4 and g.door_close_sound.get_editor_property('duration')>1.7
  shell=actors['R12_Gondola_CabinShell'].static_mesh_component
  assert unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem).get_convex_collision_count(shell.static_mesh)==10
  assert str(shell.get_collision_profile_name())=='BlockAll'
  assert all(a.get_actor_label()!='R12_Gondola_Mechanism' for a in g.cabin_parts)
  assert all(a.get_actor_label() in actors for a in g.cabin_parts)
  for i in range(2):assert actors['R12_Gondola_Interior_Light_%d'%i].point_light_component.intensity==12
  assert g.stage_first_arrival and abs(g.first_arrival_distance-3048)<.01 and g.far_boarding_bridge
  assert abs(g.get_editor_property('wait_time_at_maldek')-180)<.01,'Test dwell leaked into saved level'
  report['checks']=['Old cabin chunks replaced','Independent door and drive meshes saved','Both recorded sounds assigned','Ten shaped cabin collision hulls saved','Station mechanism stays independent of moving cabin','Existing 12-lumen lamps preserved','Staged arrival and far gangway preserved']
  report['cabin_parts']=[a.get_actor_label() for a in g.cabin_parts]
 except Exception:report={'passed':False,'error':traceback.format_exc()}
 (out/'reopen.json').write_text(json.dumps(report,indent=2))
handle=unreal.register_slate_post_tick_callback(check);RESULT={'started':True}

"""Read the live pawn and nearby practicals before the sensory tuning pass."""
import json, unreal
from pathlib import Path
b=Path(__file__).resolve().parents[1]; out=b/'sensory_refine'; out.mkdir(exist_ok=True)
ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert w.get_name()=='Station_R12' and not ls.is_in_play_in_editor()
pawn=unreal.get_default_object(w.get_world_settings().default_game_mode).default_pawn_class
cdo=unreal.get_default_object(pawn)
foot=cdo.get_component_by_class(unreal.SurfaceFootstepComponent)
camera=cdo.get_component_by_class(unreal.StationPlayerPresentationComponent)
report={'pawn':pawn.get_path_name(),'foot_volume':foot.volume,
 'camera':{k:camera.get_editor_property(k) for k in ['head_bob_scale','idle_sway_scale','walk_sway_cm','run_sway_cm']},
 'samples':{k:[{'path':v.get_path_name(),'volume':v.get_editor_property('volume')} for v in foot.get_editor_property(k+'_steps')] for k in ['soil','gravel','metal','concrete','wood']},'lights':[]}
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
 if any(k in a.get_actor_label().lower() for k in ['practical','ceiling','marker_spill']):
  report['lights'].append({'label':a.get_actor_label(),'position':a.get_actor_location().to_tuple()})
(out/'before.json').write_text(json.dumps(report,indent=2)); RESULT=report

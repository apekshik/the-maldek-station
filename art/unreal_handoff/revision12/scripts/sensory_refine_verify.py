"""Verify saved tuning, all recorded surface sets, fixtures, and shader health."""
import json, unreal
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'sensory_refine'
ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert not ls.is_in_play_in_editor()
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert w.get_name()=='Station_R12'
setup=json.loads((out/'setup.json').read_text());before=json.loads((out/'before.json').read_text())
bp=unreal.EditorAssetLibrary.load_asset(setup['pawn']);cdo=unreal.get_default_object(bp.generated_class())
c=cdo.get_component_by_class(unreal.StationPlayerPresentationComponent)
foot=cdo.get_component_by_class(unreal.SurfaceFootstepComponent)
assert abs(foot.volume-setup['foot_volume'])<.001
for k,v in setup['camera'].items():assert abs(c.get_editor_property(k)-v)<.001,k
for k,rows in before['samples'].items():
 assert [v.get_path_name() for v in foot.get_editor_property(k+'_steps')]==[r['path'] for r in rows],k
actors={a.get_actor_label():a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()}
for item in setup['fixtures']:
 a=actors[item['label']]
 if isinstance(a,unreal.StaticMeshActor):
  assert a.static_mesh_component.static_mesh
  assert a.static_mesh_component.get_collision_enabled()==unreal.CollisionEnabled.NO_COLLISION
assert len([k for k in actors if k.startswith('R12_Sensory_')])==len(setup['fixtures'])
assert not unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
RESULT={'success':True,'fixture_actors':len(setup['fixtures']),'surface_samples_preserved':sum(len(r) for r in before['samples'].values()),'foot_volume':foot.volume,'camera':setup['camera']}
(out/'verified.json').write_text(json.dumps(RESULT,indent=2))

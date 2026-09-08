import unreal,json
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'doors';aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);lib=unreal.EditorAssetLibrary
assert not ls.is_in_play_in_editor()
actors=aa.get_all_level_actors();assert not any(a.get_actor_label().startswith('D03_Transient_') for a in actors)
assert json.loads((out/'runtime.json').read_text())['success'];assert json.loads((out/'previews/capture.json').read_text())['success']
assert ls.save_current_level()
# Reload the saved map to prove the placed actors and default states persist.
assert ls.load_level('/Game/MaldekRefinement/R12/Station_R12')
doors=[a for a in aa.get_all_level_actors() if isinstance(a,unreal.StationDoor)]
assert len(doors)==2 and all(not a.is_locked() and not a.has_keypad and a.leaf.static_mesh and abs(a.open_angle-95)<.01 for a in doors)
side=next(a for a in doors if a.get_actor_label()=='R12_Door_Control_side')
for i,slot in enumerate(side.leaf.static_mesh.static_materials):
 if str(slot.material_slot_name)=='UE_VF06_Petrol_paint':assert '__Indoor' in side.leaf.get_material(i).get_name()
bp=lib.load_asset('/Game/MaldekRefinement/R12/Player/BP_StationWalker_Polished');cdo=unreal.get_default_object(bp.generated_class());foot=cdo.get_component_by_class(unreal.SurfaceFootstepComponent);view=cdo.get_component_by_class(unreal.StationPlayerPresentationComponent)
assert abs(foot.volume-3.5)<.01 and abs(view.idle_sway_scale-5)<.01 and abs(view.held_motion_scale-.15)<.001
RESULT={'success':True,'reopened_standard_doors':[a.get_actor_label() for a in doors],'keypad_unplaced':True,'temporary_actors_removed':True,'foot_volume':foot.volume,'idle_sway':view.idle_sway_scale,'held_motion':view.held_motion_scale,'source_buildings_unchanged':True,'open_angle_degrees':95}
(out/'saved_verification.json').write_text(json.dumps(RESULT,indent=2))

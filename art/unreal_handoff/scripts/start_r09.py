import unreal,json,runpy
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'revision09'
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert world.get_name() in ['BlockOut_R08','BlockOut_R09']
if world.get_name()=='BlockOut_R08':
 assert levels.save_current_level()
 assert levels.new_level_from_template('/Game/MaldekRefinement/R09/BlockOut_R09','/Game/MaldekRefinement/R08/BlockOut_R08')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
cabin=next(a for a in actors.get_all_level_actors() if a.get_actor_label()=='R04_12_Gondola')
controller=next(a for a in actors.get_all_level_actors() if a.get_class().get_name()=='BP_GondolaSystem_C')
report={'cabin_before':str(cabin.get_actor_transform()),'parent_before':str(cabin.get_attach_parent_actor())}
cabin.detach_from_actor(unreal.DetachmentRule.KEEP_WORLD,unreal.DetachmentRule.KEEP_WORLD,unreal.DetachmentRule.KEEP_WORLD)
cabin.static_mesh_component.set_mobility(unreal.ComponentMobility.STATIC)
controller.set_actor_tick_enabled(False)
for c in controller.get_components_by_class(unreal.StaticMeshComponent):
 c.set_visibility(False,False);c.set_hidden_in_game(True,False);c.set_collision_profile_name('NoCollision')
report['cabin_after']=str(cabin.get_actor_transform())
report['parent_after']=str(cabin.get_attach_parent_actor())
report['game_mode']=str(unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_world_settings().get_editor_property('default_game_mode'))
report['remaining_lights']=[a.get_actor_label() for a in actors.get_all_level_actors() if isinstance(a,unreal.Light)]
pawn_class=unreal.EditorAssetLibrary.load_blueprint_class('/Game/Variant_Horror/Blueprints/BP_HorrorCharacter')
pawn=actors.spawn_actor_from_class(pawn_class,unreal.Vector(0,0,-100000))
report['horror_components']=[]
for c in pawn.get_components_by_class(unreal.ActorComponent):
 d={'name':c.get_name(),'class':c.get_class().get_name()}
 if isinstance(c,unreal.StaticMeshComponent):d['mesh']=str(c.get_editor_property('static_mesh'))
 if isinstance(c,unreal.SkeletalMeshComponent):d['mesh']=str(c.get_editor_property('skeletal_mesh_asset'))
 if isinstance(c,unreal.PointLightComponent):d.update({'intensity':c.get_editor_property('intensity'),'units':str(c.get_editor_property('intensity_units'))})
 report['horror_components'].append(d)
actors.destroy_actor(pawn)
assert levels.save_current_level()
(out/'initial_review.json').write_text(json.dumps(report,indent=2))
runpy.run_path(str(Path(__file__).with_name('review_session.py')))

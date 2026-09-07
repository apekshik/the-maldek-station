import unreal
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
for a in actors:
 if a.get_actor_label().startswith('R07_') and isinstance(a,unreal.LocalFogVolume):
  c=a.get_components_by_class(unreal.LocalFogVolumeComponent)[0];c.set_editor_property('radial_fog_extinction',.025 if 'Station' in a.get_actor_label() else .018);c.set_editor_property('height_fog_extinction',0.)
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()

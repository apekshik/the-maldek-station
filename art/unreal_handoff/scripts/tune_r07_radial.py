import unreal
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
 if isinstance(a,unreal.LocalFogVolume) and a.get_actor_label().startswith('R07_'):
  c=a.get_components_by_class(unreal.LocalFogVolumeComponent)[0];c.set_editor_property('radial_fog_extinction',1.6 if 'Station' in a.get_actor_label() else 1.0);c.set_editor_property('height_fog_extinction',0.)
 for c in a.get_components_by_class(unreal.PointLightComponent):c.set_editor_property('volumetric_scattering_intensity',2.0)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()

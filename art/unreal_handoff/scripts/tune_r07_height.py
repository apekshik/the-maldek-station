import unreal
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in actors.get_all_level_actors():
 if isinstance(a,unreal.LocalFogVolume) and a.get_actor_label().startswith('R07_'):
  scale=7.2 if 'Station' in a.get_actor_label() else 5.6
  a.set_actor_scale3d(unreal.Vector(scale,scale,scale))
  c=a.get_components_by_class(unreal.LocalFogVolumeComponent)[0]
  c.set_radial_fog_extinction(.6)
  c.set_height_fog_extinction(.05)
  c.set_height_fog_falloff(2.)
  c.set_height_fog_offset(0.)
  c.set_fog_albedo(unreal.LinearColor(.7,.75,.8,1))
  c.set_fog_emissive(unreal.LinearColor(0,0,0,1))
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()


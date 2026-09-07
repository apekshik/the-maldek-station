import unreal,json
from pathlib import Path
r={'cvars':{},'actors':[]}
for v in ['r.SupportLocalFogVolumes','r.LocalFogVolume','r.LocalFogVolume.RenderIntoVolumetricFog','r.VolumetricFog','r.Fog','r.LocalFogVolume.GlobalStartDistance']:r['cvars'][v]=unreal.SystemLibrary.get_console_variable_int_value(v)
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
 if isinstance(a,unreal.LocalFogVolume):
  c=a.get_components_by_class(unreal.LocalFogVolumeComponent)[0];r['actors'].append({'name':a.get_actor_label(),'actor_scale':str(a.get_actor_scale3d()),'component_scale':str(c.get_world_scale()),'component_location':str(c.get_world_location()),'visible':c.get_editor_property('visible')})
(Path(__file__).resolve().parents[1]/'revision07/runtime_fog_flags.json').write_text(json.dumps(r,indent=2))

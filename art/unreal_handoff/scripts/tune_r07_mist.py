import unreal,json
from pathlib import Path
r={'lights':[]};actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
for a in actors:
 if a.get_actor_label().startswith('R07_') and isinstance(a,unreal.LocalFogVolume):
  c=a.get_components_by_class(unreal.LocalFogVolumeComponent)[0];c.set_editor_property('radial_fog_extinction',.14 if 'Station' in a.get_actor_label() else .10);c.set_editor_property('height_fog_extinction',0.);c.set_editor_property('fog_albedo',unreal.LinearColor(.55,.6,.65,1))
 for c in a.get_components_by_class(unreal.LightComponent):
  d={'actor':a.get_actor_label(),'name':c.get_name()}
  for p in ['mobility','intensity','volumetric_scattering_intensity']:
   try:d[p]=str(c.get_editor_property(p))
   except:pass
  r['lights'].append(d)
 if a.get_actor_label()=='Ultra_Dynamic_Sky':
  c=a.get_components_by_class(unreal.ExponentialHeightFogComponent)[0]
  for p in ['enable_volumetric_fog','volumetric_fog','volumetric_fog_extinction_scale']:
   try:r[p]=str(c.get_editor_property(p))
   except:pass
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level();(Path(__file__).resolve().parents[1]/'revision07/light_fog_audit.json').write_text(json.dumps(r,indent=2))

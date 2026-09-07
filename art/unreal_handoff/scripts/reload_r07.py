"""Reload and verify the saved R07 atmosphere before capturing it."""
import json
from pathlib import Path
import unreal
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert levels.save_current_level()
assert levels.load_level('/Game/MaldekRefinement/R07/BlockOut_R07')
report = {'map': '/Game/MaldekRefinement/R07/BlockOut_R07', 'volumes': [], 'study_lights': [], 'local_start_cm': unreal.SystemLibrary.get_console_variable_int_value('r.LocalFogVolume.GlobalStartDistance')}
assert report['local_start_cm'] == 100
for actor in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
    if actor.get_actor_label().startswith('R07_TestLight_'):
        light = actor.get_components_by_class(unreal.SpotLightComponent)[0]
        assert light.get_editor_property('intensity') > 0
        report['study_lights'].append({'name': actor.get_actor_label(), 'intensity_lumens': light.get_editor_property('intensity'), 'cast_shadows': light.get_editor_property('cast_shadows')})
    if isinstance(actor, unreal.LocalFogVolume) and actor.get_actor_label().startswith('R07_'):
        component = actor.get_components_by_class(unreal.LocalFogVolumeComponent)[0]
        scale = actor.get_actor_scale3d()
        density = component.get_editor_property('height_fog_extinction')
        assert abs(density - .05) < .00001
        assert abs(component.get_editor_property('height_fog_falloff') - 2.) < .001
        assert abs(scale.x - (7.2 if 'Station' in actor.get_actor_label() else 5.6)) < .001
        report['volumes'].append({'label': actor.get_actor_label(), 'center': str(actor.get_actor_location()), 'radius_cm': scale.x * 500., 'radial_density': component.get_editor_property('radial_fog_extinction'), 'height_density': density, 'height_falloff': component.get_editor_property('height_fog_falloff'), 'albedo': str(component.get_editor_property('fog_albedo')), 'emissive': str(component.get_editor_property('fog_emissive'))})
    if actor.get_actor_label() == 'Ultra_Dynamic_Sky':
        report['volumetric_enabled'] = actor.get_components_by_class(unreal.ExponentialHeightFogComponent)[0].get_editor_property('enable_volumetric_fog')
        report['moon_intensity'] = actor.get_editor_property('Moon Light Intensity')
        report['sky_light_intensity'] = actor.get_editor_property('Sky Light Intensity')
assert report['volumetric_enabled']
assert len(report['volumes']) == 2
assert len(report['study_lights']) == 6
assert abs(report['moon_intensity'] - .15) < .00001
assert abs(report['sky_light_intensity'] - 1.) < .00001
(Path(__file__).resolve().parents[1] / 'revision07/reload_verification.json').write_text(json.dumps(report, indent=2))

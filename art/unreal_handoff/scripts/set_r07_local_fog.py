"""Apply the R07 atmosphere to the open R07 map; preserves geometry and weather."""
import json
from pathlib import Path
import unreal

OUT = Path(__file__).resolve().parents[1] / 'revision07'
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert world.get_name() == 'BlockOut_R07', 'Open BlockOut_R07 before applying this pass.'
sky = next(a for a in actors.get_all_level_actors() if a.get_actor_label() == 'Ultra_Dynamic_Sky')
settings = {
    'Use Volumetric Fog': True,
    'Scale Fog Density': .35,
    'Fog Color Intensity Scale': .2,
    'Max Fog Start Distance': 100.,
    'Min Fog Start Distance': 0.,
    'Volumetric Fog Distance': 8000.,
    'Volumetric Fog Extinction': 1.,
    'All Fog Colors Multiplier': unreal.LinearColor(.35, .4, .48, 1),
    'Volumetric Fog Albedo (Night)': unreal.LinearColor(.45, .48, .52, 1),
}
for name, value in settings.items():
    sky.set_editor_property(name, value)
unreal.SystemLibrary.execute_console_command(world, 'r.LocalFogVolume.GlobalStartDistance 100')
report = {'sky': {k: str(v) for k, v in settings.items()}, 'volumes': []}
for label, location, radius in [
    ('R07_Local_Station_Mist', [-44150, 18750, 10200], 3600),
    ('R07_Relay_Approach_Mist', [-47600, 19700, 10200], 2800),
]:
    actor = next((a for a in actors.get_all_level_actors() if a.get_actor_label() == label), None)
    if actor is None:
        actor = actors.spawn_actor_from_class(unreal.LocalFogVolume, unreal.Vector(*location))
    actor.set_actor_label(label)
    actor.set_actor_location(unreal.Vector(*location), False, False)
    actor.set_folder_path('R07_Atmosphere')
    # Native ULocalFogVolumeComponent::GetBaseVolumeSize() is 500 cm.
    # Actor bounds report the editor icon and cannot determine the fog radius.
    scale = radius / 500.
    actor.set_actor_scale3d(unreal.Vector(scale, scale, scale))
    component = actor.get_components_by_class(unreal.LocalFogVolumeComponent)[0]
    # Both terms must be nonzero for UE5.7's volumetric injection coverage product.
    component.set_radial_fog_extinction(.6)
    component.set_height_fog_extinction(.05)
    component.set_height_fog_falloff(2.)
    component.set_height_fog_offset(0.)
    component.set_fog_albedo(unreal.LinearColor(.7, .75, .8, 1))
    component.set_fog_emissive(unreal.LinearColor(0, 0, 0, 1))
    component.set_fog_phase_g(.15)
    report['volumes'].append({'name': label, 'location_cm': location, 'radius_cm': radius, 'scale': scale, 'radial_extinction': .6, 'height_extinction': .05, 'height_falloff': 2.})
for actor in actors.get_all_level_actors():
    for component in actor.get_components_by_class(unreal.PointLightComponent):
        component.set_editor_property('volumetric_scattering_intensity', 2.)
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
(OUT / 'fog_changes.json').write_text(json.dumps(report, indent=2))

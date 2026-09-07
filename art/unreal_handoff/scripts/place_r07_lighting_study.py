"""Place provisional architectural spotlights for an in-engine lighting study."""
import json
from pathlib import Path
import unreal
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert world.get_name()=='BlockOut_R07'
sky=next(a for a in actors.get_all_level_actors() if a.get_actor_label()=='Ultra_Dynamic_Sky')
sky.set_editor_property('Moon Light Intensity',.15)
sky.set_editor_property('Sky Light Intensity',1.)
lights=[
 ('Main_Platform_West',[-44830,18560,10565],[-44900,19120,10298],13,4700,1000,52),
 ('Main_Platform_East',[-43600,18540,10565],[-43700,19050,10298],10,4700,950,48),
 ('Lower_Deck_Machine',[-44750,18700,10225],[-44500,19250,9898],9,3200,900,50),
 ('Lower_Deck_Exit',[-44100,18850,10210],[-44300,19550,9898],7,3800,1000,45),
 ('Relay_Path_Bend',[-47580,20680,10650],[-47350,20300,10340],10,3600,1100,48),
 ('Relay_Door',[-49050,20050,10480],[-48580,20200,10198],9,4000,1000,48),
]
report=[]
for name,loc,target,lumens,temp,radius,cone in lights:
 label='R07_TestLight_'+name
 a=next((a for a in actors.get_all_level_actors() if a.get_actor_label()==label),None)
 if a is None:a=actors.spawn_actor_from_class(unreal.SpotLight,unreal.Vector(*loc))
 a.set_actor_label(label);a.set_folder_path('R07_Lighting_Study')
 a.set_actor_location(unreal.Vector(*loc),False,False)
 a.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(unreal.Vector(*loc),unreal.Vector(*target)),False)
 c=a.get_components_by_class(unreal.SpotLightComponent)[0]
 c.set_mobility(unreal.ComponentMobility.MOVABLE)
 c.set_editor_property('intensity_units',unreal.LightUnits.LUMENS)
 c.set_intensity(lumens);c.set_attenuation_radius(radius)
 c.set_inner_cone_angle(cone*.5);c.set_outer_cone_angle(cone)
 c.set_editor_property('use_temperature',True);c.set_temperature(temp)
 c.set_editor_property('volumetric_scattering_intensity',.35)
 c.set_editor_property('cast_shadows',True)
 c.set_editor_property('cast_volumetric_shadow',True)
 c.set_editor_property('source_radius',4.)
 report.append({'name':label,'location_cm':loc,'target_cm':target,'lumens':lumens,'kelvin':temp,'attenuation_radius_cm':radius,'outer_cone_degrees':cone,'provisional':True})
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
(Path(__file__).resolve().parents[1]/'revision07/lighting_study.json').write_text(json.dumps(report,indent=2))

"""Bind practical illumination to the approved fixtures without changing sky, exposure or weather."""
import unreal,json,re
from pathlib import Path
b=Path(__file__).resolve().parents[1];aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert not ls.is_in_play_in_editor()
assert unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_name()=='Station_R12'
assert json.loads((b/'integration_ledger.json').read_text())['stages']['Infrastructure']['saved']
o=json.loads((b.parent/'working_level_report.json').read_text())['station_origin']
def wp(p):return unreal.Vector(o[0]-100*p[0],o[1]+100*p[1],o[2]+100*p[2])
actors={a.get_actor_label():a for a in aa.get_all_level_actors()}
adjustments=json.loads((b/'actor_adjustments.json').read_text());report={'relocated':[],'created':[],'global_environment_changed':False}
for label,p in [('R08_WallLight_Control_Entry',[-3.3,.32,6.535]),('R08_WallLight_Waiting_Hall_Entry',[-10.25,.32,6.585]),('R09_Light_Cabin_Ceiling',[0,6.4,6.23])]:
 a=actors[label];key=a.get_path_name();old=str(a.get_actor_transform());a.set_actor_location(wp(p),False,True)
 adjustments.setdefault(key,{'original_transform':old,'reason':'Align retained functional entrance light with approved bulkhead diffuser.'})
 adjustments[key]['new_transform']=str(a.get_actor_transform());report['relocated'].append({'label':label,'actor':key,'position_m':p})
specs=[
 ('R12_Control_Ceiling_Practical',[-5.2,-2.7,6.93],[-5.2,-2.7,4],1.0,550,100,23),
 ('R12_Quarters_Ceiling_Practical',[-4.5,-2.4,10.15],[-4.5,-2.4,7.65],.8,500,100,23),
 ('R12_Generator_North_Practical',[30,-10.72,1.59],[30,-9.2,-1],.22,450,20,18),
 ('R12_Cabin_Rear_Practical',[0,9.6,6.23],[0,9.6,4],.16,300,80,18)]
for label,p,q,power,radius,width,height in specs:
 a=actors.get(label)
 if not a:a=aa.spawn_actor_from_class(unreal.RectLight,wp(p),unreal.MathLibrary.find_look_at_rotation(wp(p),wp(q)))
 assert isinstance(a,unreal.RectLight);a.set_actor_label(label);a.set_folder_path('R12/Infrastructure/PracticalLights')
 a.set_actor_location(wp(p),False,True);a.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(wp(p),wp(q)),False)
 c=a.get_component_by_class(unreal.RectLightComponent);c.set_mobility(unreal.ComponentMobility.MOVABLE)
 c.set_editor_property('intensity_units',unreal.LightUnits.LUMENS);c.set_intensity(power);c.set_editor_property('attenuation_radius',radius)
 c.set_editor_property('source_width',width);c.set_editor_property('source_height',height);c.set_editor_property('use_temperature',True);c.set_temperature(3500)
 c.set_editor_property('cast_shadows',True);c.set_editor_property('volumetric_scattering_intensity',.035)
 report['created'].append({'label':label,'actor':a.get_path_name(),'position_m':p,'lumens':power,'radius_cm':radius})
# The inherited unshaded yard point now sits beside a reflective tank. Its former
# volumetric multiplier created a white fog orb; calibrate this affected local light.
light_changes=b/'light_component_adjustments.json';changes=json.loads(light_changes.read_text()) if light_changes.exists() else {}
a=actors['PointLight7'];c=a.get_component_by_class(unreal.PointLightComponent);key=c.get_path_name()
changes.setdefault(key,{'label':'PointLight7','old_intensity':c.intensity,'old_volumetric_scattering_intensity':c.volumetric_scattering_intensity,'units':str(c.intensity_units),'reason':'Calibrate retained yard light beside the newly added reflective water tower; preserve position, color and radius.'})
c.set_intensity(.15);c.set_editor_property('volumetric_scattering_intensity',.035)
changes[key].update(new_intensity=.15,new_volumetric_scattering_intensity=.035);light_changes.write_text(json.dumps(changes,indent=2))
assert ls.save_current_level()
(b/'actor_adjustments.json').write_text(json.dumps(adjustments,indent=2));(b/'practical_lights.json').write_text(json.dumps(report,indent=2));RESULT=report

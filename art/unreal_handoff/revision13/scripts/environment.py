import unreal,json
from pathlib import Path
b=Path(__file__).resolve().parents[1];aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert not ls.is_in_play_in_editor();assert json.loads((b/'integration_ledger.json').read_text())['saved']
o=json.loads((b.parent/'working_level_report.json').read_text())['station_origin']
def wp(p):return unreal.Vector(o[0]-100*p[0],o[1]+100*p[1],o[2]+100*p[2])
def local(p):return [(o[0]-p.x)/100,(p.y-o[1])/100,(p.z-o[2])/100]
actors={a.get_actor_label():a for a in aa.get_all_level_actors()};report={'disabled_legacy_lights':[],'fixtures':[],'foliage':[]}
for name in ['R11_Generator_Entrance_Light','R11_Generator_Ceiling_Light','R11_Workshop_Ceiling_Light','R11_Fuel_Yard_Exit_Light','R12_Generator_North_Practical']:
 a=actors.get(name)
 if a:
  for c in a.get_components_by_class(unreal.LightComponent):c.set_visibility(False);c.set_intensity(0)
  report['disabled_legacy_lights'].append(name)
for name,p,q,power,w,h in [('Ceiling_A',(28.25,-17,3.04),(28.25,-17,-1),.30,17,107),('Ceiling_B',(28.25,-12,3.04),(28.25,-12,-1),.30,17,107),('Ceiling_C',(34.8,-17,3.04),(34.8,-17,-1),.30,17,107),('Ceiling_D',(34.8,-12,3.04),(34.8,-12,-1),.30,17,107),('South_Bulkhead',(30.65,-19.32,1.47),(30.65,-22,-1),.16,14,32)]:
 label='R13_Generator_'+name;a=actors.get(label) or aa.spawn_actor_from_class(unreal.RectLight,wp(p),unreal.MathLibrary.find_look_at_rotation(wp(p),wp(q)));a.set_actor_label(label);a.set_folder_path('R13/Service/PracticalLights');a.set_actor_location(wp(p),False,True);a.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(wp(p),wp(q)),False)
 c=a.get_component_by_class(unreal.RectLightComponent);c.set_mobility(unreal.ComponentMobility.MOVABLE);c.set_editor_property('intensity_units',unreal.LightUnits.LUMENS);c.set_intensity(power);c.set_editor_property('attenuation_radius',550);c.set_editor_property('source_width',w);c.set_editor_property('source_height',h);c.set_editor_property('use_temperature',True);c.set_temperature(3500);c.set_editor_property('cast_shadows',True);c.set_editor_property('volumetric_scattering_intensity',.035);report['fixtures'].append({'label':label,'local':p,'lumens':power})
if 'R12_Audio_Generator' in actors:
 a=actors['R12_Audio_Generator'];report['audio']={'actor':a.get_path_name(),'before':local(a.get_actor_location()),'after':[32,-13.6,2.2]};a.set_actor_location(wp((32,-13.6,2.2)),False,True)
for a in aa.get_all_level_actors():
 if isinstance(a,unreal.InstancedFoliageActor):
  rows=unreal.StationMigrationLibrary.get_foliage_instance_transforms(a)
  report['foliage'] += [{'actor':a.get_path_name(),'key':str(k),'local':local(v.translation),'world':[v.translation.x,v.translation.y,v.translation.z]} for k,v in rows.items()]
assert ls.save_current_level();(b/'environment.json').write_text(json.dumps(report,indent=2));RESULT={'saved':True,'lights':len(report['fixtures']),'foliage':len(report['foliage'])}

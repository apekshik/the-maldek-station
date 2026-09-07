import unreal,json
from pathlib import Path
b=Path(__file__).resolve().parents[1];repo=b.parents[2];out=b/'machinery_audio';out.mkdir(exist_ok=True)
ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert not ls.is_in_play_in_editor()
assert unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_name()=='Station_R12'
lib=unreal.EditorAssetLibrary;root='/Game/MaldekRefinement/Audio/Machinery';tasks=[]
for f in (repo/'art/audio/machinery/wav').glob('*.wav'):
 t=unreal.AssetImportTask();t.filename=str(f);t.destination_path=root;t.automated=True;t.save=True;t.replace_existing=True;tasks.append(t)
assert len(tasks)==4;unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
origin=json.loads((b.parent/'working_level_report.json').read_text())['station_origin']
manifest=json.loads((b/'handoff_manifest.json').read_text())
def source_center(name):
 boxes=[c for r in manifest['chunks'] for c in r.get('collision_boxes',[]) if c['source']==name]
 assert len(boxes)==1,(name,len(boxes))
 return [(lo+hi)/2 for lo,hi in zip(boxes[0]['min'],boxes[0]['max'])]
generator=source_center('Generator');generator[2]=.8 # above housing to avoid self-occlusion
# The approved service-room port replaces the old generator housing.
if lib.does_asset_exist('/Game/MaldekRefinement/R13/Meshes/SM_R13_VF08_04_Diesel_Generator_solid_Indoor'):
 generator=[32,-13.6,2.2]
wheel=source_center('R04_Bearing_Pedestal');wheel[0]-=.6 # beside the bearing, outside the solid hub
rows=[];actors={a.get_actor_label():a for a in aa.get_all_level_actors()}
for name,pos,volume,inner,falloff in [('Generator',generator,.65,250,2200),('Flywheel',wheel,.4,150,1400),('Ventilation',[-5.2,-2.7,6.65],.3,120,700)]:
 sound=lib.load_asset(root+'/'+name+'_Loop');assert sound
 sound.set_editor_property('looping',True);sound.set_editor_property('virtualization_mode',unreal.VirtualizationMode.PLAY_WHEN_SILENT)
 sound.set_editor_property('sound_asset_compression_type',unreal.SoundAssetCompressionType.BINK_AUDIO);lib.save_loaded_asset(sound)
 label='R12_Audio_'+name;location=unreal.Vector(origin[0]-pos[0]*100,origin[1]+pos[1]*100,origin[2]+pos[2]*100)
 actor=actors.get(label) or aa.spawn_actor_from_class(unreal.AmbientSound,location);actor.set_actor_label(label);actor.set_folder_path('R12/Audio/Machinery');actor.set_actor_location(location,False,True)
 c=actor.get_component_by_class(unreal.AudioComponent);c.set_sound(sound);c.set_volume_multiplier(volume);c.set_editor_property('auto_activate',True)
 settings=unreal.SoundAttenuationSettings()
 for prop,value in dict(attenuate=True,spatialize=True,distance_algorithm=unreal.AttenuationDistanceModel.LINEAR,attenuation_shape=unreal.AttenuationShape.SPHERE,attenuation_shape_extents=unreal.Vector(inner,0,0),falloff_distance=float(falloff),enable_occlusion=True,occlusion_volume_attenuation=.35,occlusion_low_pass_filter_frequency=1800.,occlusion_interpolation_time=.4,use_complex_collision_for_occlusion=True).items():settings.set_editor_property(prop,value)
 c.set_editor_property('override_attenuation',True);c.set_editor_property('attenuation_overrides',settings);c.set_editor_property('occlusion_check_interval',.25)
 rows.append(dict(name=name,label=label,station_local=pos,location=list(location.to_tuple()),volume=volume,inner_radius_cm=inner,falloff_cm=falloff,sound=sound.get_path_name()))
sound=lib.load_asset(root+'/Cable_Loop');assert sound
sound.set_editor_property('looping',True);sound.set_editor_property('virtualization_mode',unreal.VirtualizationMode.PLAY_WHEN_SILENT);lib.save_loaded_asset(sound)
targets=[a for a in aa.get_all_level_actors() if isinstance(a,unreal.GondolaSystem)]
if not targets:
 targets=[a for a in aa.get_all_level_actors() if a.get_actor_label().startswith('R12_12_Gondola') and a.get_actor_label().endswith('_solid')]
assert targets,'No visible gondola target found'
target=max(targets,key=lambda a:sum(v*v for v in a.get_actor_bounds(False)[1].to_tuple()))
label='R12_Audio_GondolaCable';actor=actors.get(label) or aa.spawn_actor_from_class(unreal.StationCableAudio,target.get_actor_location());actor.set_actor_label(label);actor.set_folder_path('R12/Audio/Machinery')
actor.set_editor_property('gondola_target',target);actor.set_editor_property('cable_loop',sound)
rows.append(dict(name='Cable',label=label,target=target.get_actor_label(),sound=sound.get_path_name(),motion_driven=True))
assert ls.save_current_level()
(out/'installation.json').write_text(json.dumps(rows,indent=2));RESULT={'installed':len(rows),'sources':rows}

import unreal,json
from pathlib import Path
b=Path(__file__).resolve().parents[1];repo=b.parents[2];out=b/'gondola_mechanism';root='/Game/MaldekRefinement/R12/GondolaMechanism/Audio';lib=unreal.EditorAssetLibrary;at=unreal.AssetToolsHelpers.get_asset_tools();aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
actors={a.get_actor_label():a for a in aa.get_all_level_actors()};g=actors['R12_Gondola_Mechanism'];bank=json.loads((repo/'art/audio/gondola_drive/sources.json').read_text());sounds={}
for row in bank['assets']:
 name=row['asset'];t=unreal.AssetImportTask();t.filename=str(repo/'art/audio/gondola_drive/wav'/(name+'.wav'));t.destination_path=root;t.automated=True;t.save=True;t.replace_existing=True;at.import_asset_tasks([t]);s=lib.load_asset(root+'/'+name);assert s;s.set_editor_property('looping',row['loop']);s.set_editor_property('virtualization_mode',unreal.VirtualizationMode.PLAY_WHEN_SILENT);lib.save_loaded_asset(s);sounds[name]=s
def attenuation(inner,falloff):
 s=unreal.SoundAttenuationSettings()
 for k,v in dict(attenuate=True,spatialize=True,distance_algorithm=unreal.AttenuationDistanceModel.LINEAR,attenuation_shape_extents=unreal.Vector(inner,0,0),falloff_distance=falloff,enable_occlusion=True,occlusion_volume_attenuation=.5,occlusion_low_pass_filter_frequency=2200.,occlusion_interpolation_time=.2,use_complex_collision_for_occlusion=True,attenuate_with_lpf=True,lpf_radius_min=800.,lpf_radius_max=falloff,lpf_frequency_at_min=16000.,lpf_frequency_at_max=1400.).items():s.set_editor_property(k,v)
 return s
origins=json.loads((out/'install.json').read_text())['terminal_origins'];sources=[];report=[]
def sound(name,pos,asset,volume,inner,falloff,minpitch=.72,maxpitch=1):
 a=actors.get(name) or aa.spawn_actor_from_class(unreal.AmbientSound,unreal.Vector(*pos));a.set_actor_label(name);a.set_actor_location(unreal.Vector(*pos),False,True);a.set_folder_path('R12/Gondola Mechanism/Audio');c=a.get_component_by_class(unreal.AudioComponent);c.set_sound(sounds[asset]);c.set_editor_property('auto_activate',False);c.set_editor_property('override_attenuation',True);c.set_editor_property('attenuation_overrides',attenuation(inner,falloff));c.set_editor_property('occlusion_check_interval',.2)
 s=unreal.GondolaMachineSound();s.actor=a;s.running_volume=volume;s.idle_volume=0;s.minimum_pitch=minpitch;s.maximum_pitch=maxpitch;sources.append(s);report.append({'label':name,'position':pos,'asset':asset,'volume':volume,'inner_cm':inner,'falloff_cm':falloff})
o=origins[0];motor=[o[0]-2,o[1]-555,o[2]-817.7];sound('R12_GM_Audio_Motor',motor,'Motor_Load_Loop',2.,350.,12000.)
sound('R12_GM_Audio_Gearbox',[o[0]+230,o[1]-550,o[2]-817.7],'Gearbox_Loop',1.,200.,5000.)
for i,o in enumerate(origins):sound('R12_GM_Audio_Bullwheel_%d'%i,[o[0]+117.5,o[1]+(-560 if i==0 else 440),o[2]+80],'Bullwheel_Roll_Loop',3.,500.,16000.)
for i in range(1,6):
 a=actors['R12_Route_Pylon_%02d'%i];p=a.get_actor_location();n=json.loads((b/'gondola_route/plan.json').read_text())['nodes'][i];sound('R12_GM_Audio_Rollers_%d'%i,[p.x,p.y,n['contact_z']*100-65],'Pylon_Roller_Loop',.85,250.,6000.)
g.sound_sources=sources;g.brake_release_sound=sounds['Brake_Release'];g.brake_set_sound=sounds['Brake_Set'];g.brake_location=unreal.Vector(*motor)
att=lib.load_asset(root+'/ATT_Brake') or at.create_asset('ATT_Brake',root,unreal.SoundAttenuation,unreal.SoundAttenuationFactory());att.set_editor_property('attenuation',attenuation(250.,7000.));lib.save_loaded_asset(att);g.brake_attenuation=att
cable=actors['R12_Audio_GondolaCable'];cable.cable_loop=sounds['Pylon_Roller_Loop'];cable.cable_volume=.85
assert ls.save_current_level();RESULT={'saved':True,'sources':report,'brake_cues':True,'cabin_cable_volume':.85};(out/'audio_install.json').write_text(json.dumps(RESULT,indent=2))

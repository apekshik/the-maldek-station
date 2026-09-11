import unreal,json
from pathlib import Path
b=Path(__file__).resolve().parents[1];repo=b.parents[2];out=b/'police_tape';ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);lib=unreal.EditorAssetLibrary;at=unreal.AssetToolsHelpers.get_asset_tools();assert not ls.is_in_play_in_editor();root='/Game/MaldekRefinement/R12/PoliceTape/Audio';tasks=[]
for f in sorted((repo/'art/audio/police_tape/wav').glob('*.wav')):
 t=unreal.AssetImportTask();t.filename=str(f);t.destination_path=root;t.automated=True;t.save=True;t.replace_existing=True;tasks.append(t)
at.import_asset_tasks(tasks);sounds=[lib.load_asset(root+f'/Tape_Tear_{i:02}') for i in range(1,4)];assert all(sounds)
for sound in sounds:sound.set_editor_property('looping',False);lib.save_loaded_asset(sound)
atten=lib.load_asset(root+'/ATT_TapeTear') or at.create_asset('ATT_TapeTear',root,unreal.SoundAttenuation,unreal.SoundAttenuationFactory());settings=unreal.SoundAttenuationSettings()
for k,v in dict(attenuate=True,spatialize=True,distance_algorithm=unreal.AttenuationDistanceModel.LINEAR,attenuation_shape=unreal.AttenuationShape.SPHERE,attenuation_shape_extents=unreal.Vector(200,0,0),falloff_distance=1200.,enable_occlusion=False).items():settings.set_editor_property(k,v)
atten.set_editor_property('attenuation',settings);lib.save_loaded_asset(atten)
a=next(a for a in aa.get_all_level_actors() if a.get_actor_label()=='PoliceTape_MainCrossing');a.set_editor_property('tear_sounds',sounds);a.set_editor_property('tear_attenuation',atten);a.set_editor_property('tear_volume',1.3);assert ls.save_current_level();RESULT={'saved':True,'sounds':[s.get_path_name() for s in sounds],'volume':a.tear_volume};(out/'audio_installation.json').write_text(json.dumps(RESULT,indent=2))

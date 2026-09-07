import unreal,json
from pathlib import Path
repo=Path(__file__).resolve().parents[4];out=Path(__file__).resolve().parents[1]
assert not unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).is_in_play_in_editor()
lib=unreal.EditorAssetLibrary;root='/Game/MaldekRefinement/Audio/Opening';tasks=[]
for f in (repo/'art/audio/opening/wav').glob('*.wav'):
 t=unreal.AssetImportTask();t.filename=str(f);t.destination_path=root;t.automated=True;t.save=True;t.replace_existing=True;tasks.append(t)
assert len(tasks)==3;unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
bp=lib.load_asset('/Game/MaldekRefinement/R12/Player/BP_StationWalker_Polished')
unreal.BlueprintEditorLibrary.compile_blueprint(bp)
c=unreal.get_default_object(bp.generated_class()).get_components_by_class(unreal.StationOpeningComponent)[0]
for prop,name in [('switch_on','Flashlight_On'),('switch_off','Flashlight_Off'),('opening_atmosphere','Opening_Atmosphere')]:
 s=lib.load_asset(root+'/'+name);assert s;s.set_editor_property('looping',False);s.set_editor_property('sound_asset_compression_type',unreal.SoundAssetCompressionType.PCM);lib.save_loaded_asset(s);c.set_editor_property(prop,s)
c.set_editor_property('enable_opening',True)
lib.save_loaded_asset(bp,False)
RESULT={'installed':True,'pawn':bp.get_path_name(),'opening_enabled':c.get_editor_property('enable_opening'),'sounds':3}
(out/'opening_install.json').write_text(json.dumps(RESULT))

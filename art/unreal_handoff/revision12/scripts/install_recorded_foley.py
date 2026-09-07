"""Install recorded foley into the current R12 pawn without editing the level."""
import unreal,json
from pathlib import Path
repo=Path(__file__).resolve().parents[4]
src=repo/'art/audio/recorded_foley';out=Path(__file__).resolve().parents[1]
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert not levels.is_in_play_in_editor(),'Wait for the existing PIE session to finish'
lib=unreal.EditorAssetLibrary
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert world.get_name()=='Station_R12'
gm=world.get_world_settings().get_editor_property('default_game_mode')
pawn=unreal.get_default_object(gm).get_editor_property('default_pawn_class')
bp=lib.load_asset(pawn.get_path_name().split('.')[0])
root='/Game/MaldekRefinement/Audio/RecordedFoley'
tasks=[]
for f in sorted((src/'wav').glob('*.wav')):
 t=unreal.AssetImportTask();t.filename=str(f);t.destination_path=root;t.automated=True;t.save=True;t.replace_existing=True;tasks.append(t)
assert len(tasks)==62
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
c=unreal.get_default_object(pawn).get_components_by_class(unreal.SurfaceFootstepComponent)[0]
previous={};counts={}
for kind in ['soil','gravel','metal','concrete','wood']:
 prop=kind+'_steps';previous[prop]=[v.get_path_name() for v in c.get_editor_property(prop)]
 waves=[lib.load_asset(root+'/'+f.stem) for f in sorted((src/'wav').glob('Recorded_'+kind+'_*.wav'))]
 assert all(waves)
 for wave in waves:
  wave.set_editor_property('looping',False);wave.set_editor_property('volume',1.0);wave.set_editor_property('sound_asset_compression_type',unreal.SoundAssetCompressionType.PCM);lib.save_loaded_asset(wave)
 c.set_editor_property(prop,waves);counts[kind]=len(waves)
c.set_editor_property('volume',.8)
unreal.BlueprintEditorLibrary.compile_blueprint(bp)
lib.save_loaded_asset(bp,False)
actual=unreal.get_default_object(bp.generated_class()).get_components_by_class(unreal.SurfaceFootstepComponent)[0]
for kind,count in counts.items():assert len(actual.get_editor_property(kind+'_steps'))==count
RESULT={'pawn':bp.get_path_name(),'counts':counts,'volume':actual.volume,'previous':previous,'imported':len(tasks)}
(out/'recorded_foley_install.json').write_text(json.dumps(RESULT,indent=2))

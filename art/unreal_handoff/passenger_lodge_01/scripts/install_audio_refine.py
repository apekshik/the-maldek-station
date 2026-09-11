import unreal,json,hashlib
from pathlib import Path
O=Path(__file__).resolve().parents[1];R=O.parents[2];D=O/'audio_refine';S=R/'art/audio/lodge_refine_01';root='/Game/MaldekRefinement/PassengerLodge/AudioRefine';lib=unreal.EditorAssetLibrary;at=unreal.AssetToolsHelpers.get_asset_tools();ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert not ls.is_in_play_in_editor();assert ls.load_level('/Game/MaldekRefinement/PassengerLodge/Station_Lodge_Migration')
rows=json.loads((S/'edits.json').read_text());tasks=[]
for r in rows:
 f=S/'wav'/(r['asset']+'.wav');assert hashlib.sha256(f.read_bytes()).hexdigest()==r['sha256'];t=unreal.AssetImportTask();t.filename=str(f);t.destination_path=root;t.destination_name=r['asset'];t.automated=True;t.replace_existing=True;t.save=False;tasks.append(t)
at.import_asset_tasks(tasks);waves={}
for r in rows:
 w=lib.load_asset(root+'/'+r['asset']);assert w;w.set_editor_property('looping',r['loop']);w.set_editor_property('sound_asset_compression_type',unreal.SoundAssetCompressionType.PCM);w.set_editor_property('virtualization_mode',unreal.VirtualizationMode.PLAY_WHEN_SILENT);assert lib.save_loaded_asset(w);waves[r['asset']]=w

def bank(prefix):return [w for k,w in sorted(waves.items()) if k.startswith(prefix+'_')]
actors={a.get_actor_label():a for a in aa.get_all_level_actors()};changes=[]
for label,a in actors.items():
 if isinstance(a,unreal.StationCabinet) and label.startswith(('MIG_PLL_','MIG_PLK_')):
  kind='Locker' if label.startswith('MIG_PLL_') else 'Fridge' if 'Fridge' in label else 'Drawer' if a.sliding else 'Cupboard'
  a.set_editor_property('opening_takes',bank(kind+'Open'));a.set_editor_property('closing_takes',bank(kind+'Close'));a.movement_sound=bank(kind+'Open')[0];a.closing_sound=bank(kind+'Close')[0];changes.append({'actor':label,'bank':kind})
 if isinstance(a,unreal.StationDoor):
  # Full-size steel access doors and lighter restroom/stall leaves use different recordings.
  kind='Room' if label.startswith('MIG_PLR_') else 'Steel'
  a.set_editor_property('opening_takes',bank(kind+'Open'));a.set_editor_property('closing_takes',bank('RoomTravelClose' if kind=='Room' else kind+'Close'))
  if kind=='Room':a.set_editor_property('close_impact_takes',bank('RoomClose'));a.set_editor_property('unlatch_sound',bank('CupboardOpen')[0])
  changes.append({'actor':label,'bank':kind})
a=actors['MIG_PLD_GONDOLA'];a.key_camera_offset=unreal.Vector(-18,35,14)
pm=lib.load_asset(root+'/PM_Tile') or at.create_asset('PM_Tile',root,unreal.PhysicalMaterial,unreal.PhysicalMaterialFactoryNew());pm.set_editor_property('surface_type',unreal.PhysicalSurface.SURFACE_TYPE6);assert lib.save_loaded_asset(pm)
m=lib.load_asset('/Game/MaldekRefinement/PassengerLodge/Surfaces/Materials/M_PLSH_Quarry_Floor');m.set_editor_property('phys_material',pm);assert lib.save_loaded_asset(m)
bp=lib.load_asset('/Game/MaldekRefinement/R12/Player/BP_StationWalker_Polished');c=unreal.get_default_object(bp.generated_class()).get_components_by_class(unreal.SurfaceFootstepComponent)[0];c.concrete_steps=bank('StepConcrete');c.tile_steps=bank('StepTile');unreal.BlueprintEditorLibrary.compile_blueprint(bp);assert lib.save_loaded_asset(bp,False)
o=json.loads((O/'before.json').read_text())['origin'];a=actors.get('MIG_Lodge_Sheltered_Storm') or aa.spawn_actor_from_class(unreal.StationLodgeAcoustics,unreal.Vector(o[0]+2410,o[1]+400,o[2]+400),unreal.Rotator());a.set_actor_label('MIG_Lodge_Sheltered_Storm');a.set_folder_path('LodgeMigration/Audio');a.wind_loop=waves['ShelteredStorm'];a.volume=.8;a.weather_actor=actors['Ultra_Dynamic_Weather'];a.room_centers=[unreal.Vector(-700,-560,160),unreal.Vector(-250,-1370,160),unreal.Vector(-1100,-1420,160)];a.room_extents=[unreal.Vector(682,542,155),unreal.Vector(232,232,155),unreal.Vector(282,282,155)]
assert ls.save_current_level();RESULT={'waves':len(waves),'assignments':changes,'key_camera':[-18,35,14],'footsteps':{'tile':6,'concrete':6},'storm':a.get_actor_label()};(D/'install.json').write_text(json.dumps(RESULT,indent=2))

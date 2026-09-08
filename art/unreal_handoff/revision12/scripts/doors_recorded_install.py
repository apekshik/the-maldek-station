"""Install the recorded bank, update all door defaults/instances, preserve geometry."""
import unreal,json
from pathlib import Path
b=Path(__file__).resolve().parents[1];repo=b.parents[2]
out=b/'doors'/'recorded_audio';out.mkdir(parents=True,exist_ok=True)
lib=unreal.EditorAssetLibrary;ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);assert not ls.is_in_play_in_editor()
before={a.get_actor_label():a.get_actor_transform() for a in aa.get_all_level_actors()}
root='/Game/MaldekRefinement/R12/Doors';at=unreal.AssetToolsHelpers.get_asset_tools()
mapping={'button_sound':'KeyPress','clear_sound':'KeyClear','confirm_sound':'KeyConfirm','reject_sound':'KeyReject',
 'unlatch_sound':'DoorUnlatch','movement_sound':'DoorMovement','closing_movement_sound':'DoorClosingMovement',
 'close_sound':'DoorClose','unlock_sound':'DoorUnlock','lock_sound':'DoorLock'}
sounds={}
for prop,name in mapping.items():
 t=unreal.AssetImportTask();t.filename=str(repo/'art/audio/doors/wav'/(name+'.wav'))
 t.destination_path=root+'/Audio';t.automated=True;t.save=True;t.replace_existing=True
 at.import_asset_tasks([t]);s=lib.load_asset(root+'/Audio/'+name);assert s
 s.set_editor_property('looping',name in ['DoorMovement','DoorClosingMovement'])
 s.set_editor_property('volume',1.0);s.set_editor_property('compression_quality',100)
 lib.save_loaded_asset(s);sounds[prop]=s

def assign(obj):
 for prop,sound in sounds.items():obj.set_editor_property(prop,sound)
 for prop,value in {'keypad_volume':1.6,'door_volume':1.3,'movement_volume':1.2,'relock_on_close':True}.items():obj.set_editor_property(prop,value)
 # Serialized component defaults can override native constructor attenuation.
 for comp in obj.get_components_by_class(unreal.AudioComponent):
  if comp.get_name() not in ['DoorEventAudio','DoorMotionAudio','DoorKeypadAudio','DoorLockAudio']:continue
  settings=comp.get_editor_property('attenuation_overrides')
  settings.set_editor_property('attenuation_shape_extents',unreal.Vector(150,0,0))
  settings.set_editor_property('falloff_distance',1350.0)
  settings.set_editor_property('distance_algorithm',unreal.AttenuationDistanceModel.LINEAR)
  comp.set_editor_property('attenuation_overrides',settings)
for name in ['Standard','Keypad']:
 bp=lib.load_asset(root+'/BP_StationDoor_'+name);assign(unreal.get_default_object(bp.generated_class()))
 unreal.BlueprintEditorLibrary.compile_blueprint(bp);assert lib.save_loaded_asset(bp)
rows=[]
for a in aa.get_all_level_actors():
 if isinstance(a,unreal.StationDoor):
  assign(a);rows.append({'label':a.get_actor_label(),'keypad':a.get_editor_property('has_keypad'),
   'relock_on_close':a.get_editor_property('relock_on_close')})
for a in aa.get_all_level_actors():assert a.get_actor_transform()==before[a.get_actor_label()]
assert len(rows)==10;assert ls.save_current_level()
RESULT={'success':True,'doors':rows,'preserved_transforms':len(before),'sounds':{k:s.get_path_name() for k,s in sounds.items()}}
(out/'install.json').write_text(json.dumps(RESULT,indent=2))

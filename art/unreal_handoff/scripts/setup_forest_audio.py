"""Configure surface-aware footsteps and stronger ambience in the ForestTest map only."""
import unreal,json,hashlib
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'forest_test';root='/Game/MaldekRefinement/ForestTest/Audio';lib=unreal.EditorAssetLibrary;at=unreal.AssetToolsHelpers.get_asset_tools();aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert world.get_name()=='Forest_Approach_Test'
wav_dir=out.parents[1]/'audio/footsteps/wav';tasks=[]
for f in sorted(wav_dir.glob('*.wav')):
 t=unreal.AssetImportTask();t.filename=str(f);t.destination_path=root+'/Steps';t.automated=True;t.save=True;t.replace_existing=True;tasks.append(t)
assert len(tasks)==25;at.import_asset_tasks(tasks)
surfaces=['Soil','Gravel','Metal','Concrete','Wood'];pms={}
for i,name in enumerate(surfaces,1):
 pm=lib.load_asset(root+'/Surfaces/PM_'+name) or at.create_asset('PM_'+name,root+'/Surfaces',unreal.PhysicalMaterial,unreal.PhysicalMaterialFactoryNew());pm.set_editor_property('surface_type',getattr(unreal.PhysicalSurface,'SURFACE_TYPE'+str(i)));lib.save_loaded_asset(pm);pms[name]=pm
bp=lib.load_asset('/Game/MaldekRefinement/ForestTest/BP_ForestWalker');unreal.BlueprintEditorLibrary.compile_blueprint(bp)
c=unreal.get_default_object(bp.generated_class()).get_components_by_class(unreal.SurfaceFootstepComponent)[0]
for name in surfaces:
 waves=[lib.load_asset(root+f'/Steps/Step_{name.lower()}_{i:02}') for i in range(5)];assert all(waves);c.set_editor_property(name.lower()+'_steps',waves)
c.set_editor_property('volume',.65);lib.save_loaded_asset(bp,False)
def surface(name):
 n=name.lower()
 if any(s in n for s in ['gravel','m_ground']):return 'Gravel'
 if any(s in n for s in ['soil','terrain','grass','snowy']):return 'Soil'
 if any(s in n for s in ['concrete','safety_paint','stone']):return 'Concrete'
 if any(s in n for s in ['timber','wood']):return 'Wood'
 if any(s in n for s in ['steel','grating','galvanized','metal','charcoal']):return 'Metal'
 return None
mapped={};rows=[]
for a in aa.get_all_level_actors():
 if not isinstance(a,unreal.StaticMeshActor) or a.get_actor_label().startswith('FT_'):continue
 comp=a.static_mesh_component;types=[]
 for i,m in enumerate(comp.get_materials()):
  if not m:continue
  kind=surface(m.get_name())
  if not kind:continue
  key=m.get_path_name();mi_name='MI_Foot_'+kind+'_'+hashlib.sha1(key.encode()).hexdigest()[:10]
  mi=lib.load_asset(root+'/SurfaceMaterials/'+mi_name)
  if not mi:
   mi=at.create_asset(mi_name,root+'/SurfaceMaterials',unreal.MaterialInstanceConstant,unreal.MaterialInstanceConstantFactoryNew());unreal.MaterialEditingLibrary.set_material_instance_parent(mi,m)
  mi.set_editor_property('phys_material',pms[kind]);lib.save_loaded_asset(mi);comp.set_material(i,mi);mapped[key]=kind;types.append(kind);rows.append({'actor':a.get_actor_label(),'slot':i,'surface':kind})
 if types and len(types)==comp.get_num_materials() and len(set(types))==1:comp.set_phys_material_override(pms[types[0]])
 if a.get_actor_label()=='R04_20_Lookout_Bridge':comp.set_phys_material_override(pms['Metal'])
wind=next(a for a in aa.get_all_level_actors() if a.get_actor_label()=='R10_Forest_Wind');wind.audio_component.set_volume_multiplier(.35)
weather=next(a for a in aa.get_all_level_actors() if a.get_actor_label()=='Ultra_Dynamic_Weather');weather.set_editor_property('Weather Sounds Master Volume',.6);weather.set_editor_property('Wind Volume',.85)
insects=lib.load_asset(root+'/NightInsects_Loop') or lib.duplicate_asset('/Game/UltraDynamicSky/Sound/Environment/Forest_Example/Waves/Insects/NightInsects',root+'/NightInsects_Loop');insects.set_editor_property('looping',True);lib.save_loaded_asset(insects)
a=next((a for a in aa.get_all_level_actors() if a.get_actor_label()=='FT_Night_Insects'),None) or aa.spawn_actor_from_class(unreal.AmbientSound,wind.get_actor_location());a.set_actor_label('FT_Night_Insects');a.set_folder_path('ForestTest/Audio');a.audio_component.set_sound(insects);a.audio_component.set_volume_multiplier(.10);a.audio_component.set_editor_property('auto_activate',True)
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
(out/'audio_setup.json').write_text(json.dumps({'sound_variants':25,'wind_volume':.35,'weather_master':.6,'insects_volume':.1,'footstep_volume':.65,'material_mapping':mapped,'actors':rows},indent=2))

"""Disable inherited procedural snow for this woodland map only."""
import unreal,json
from pathlib import Path
b=Path(__file__).resolve().parents[1]; out=b/'forest_refine'
ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert not ls.is_in_play_in_editor()
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
limit_name='grass.GrassMap.MaxComponentsForBlockingUpdate'
previous_limit=unreal.SystemLibrary.get_console_variable_int_value(limit_name)
unreal.SystemLibrary.execute_console_command(w,limit_name+' 1')
land=next(a for a in aa.get_all_level_actors() if isinstance(a,unreal.Landscape))
lib=unreal.EditorAssetLibrary; ml=unreal.MaterialEditingLibrary
src=land.get_editor_property('landscape_material')
dst='/Game/MaldekRefinement/R12/ForestRefine/Materials/MI_Woodland_Landscape'
mi=unreal.load_asset(dst) if lib.does_asset_exist(dst) else lib.duplicate_asset(src.get_path_name(),dst)
before={n:ml.get_material_instance_scalar_parameter_value(mi,n) for n in ['MW_SnowMaskMultiplier','MW_SnowWorldPosition']}
ml.set_material_instance_scalar_parameter_value(mi,'MW_SnowMaskMultiplier',0.0)
ml.set_material_instance_scalar_parameter_value(mi,'MW_SnowWorldPosition',1000000.0)
ml.update_material_instance(mi)
o=json.loads((b.parent/'working_level_report.json').read_text())['station_origin']
changed=[]
for c in land.get_components_by_class(unreal.LandscapeComponent):
 p,ext,_=unreal.SystemLibrary.get_component_bounds(c);x=(o[0]-p.x)/100;y=(p.y-o[1])/100;ex=ext.x/100;ey=ext.y/100
 # Only the station-side valley needs this override; preserve the far mountains.
 if x+ex>=-100 and x-ex<=100 and y-ey<=230 and y+ey>=-70:
  c.set_editor_property('override_material',mi);changed.append({'component':c.get_path_name(),'local_center':[x,y],'size_m':2*ex})
assert changed and len(changed)<40
lib.save_loaded_asset(mi)
saved=ls.save_current_level()
unreal.SystemLibrary.execute_console_command(w,limit_name+' '+str(previous_limit))
RESULT={'source':src.get_path_name(),'material':mi.get_path_name(),'before':before,'snow_mask_multiplier':0,'snow_height':1000000,'saved':saved,'components':changed,'blocking_grass_batch':1,'original_batch_restored':previous_limit}
(out/'cover.json').write_text(json.dumps(RESULT,indent=2))

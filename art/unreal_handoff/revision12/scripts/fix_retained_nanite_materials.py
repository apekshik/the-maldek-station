"""Persist Nanite usage for retained rock patches in R12-owned material copies."""
import unreal,json,hashlib
from pathlib import Path
b=Path(__file__).resolve().parents[1];lib=unreal.EditorAssetLibrary;ml=unreal.MaterialEditingLibrary;ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert not ls.is_in_play_in_editor()
rows=json.loads((b/'retained_material_audit.json').read_text());actors={a.get_path_name():a for a in aa.get_all_level_actors()};root='/Game/MaldekRefinement/R12/Materials/Retained';lib.make_directory(root)
source='/Fab/Materials/Standard/M_MS_Base.M_MS_Base';dest=root+'/M_R12_Retained_Megascan'
master=lib.load_asset(dest) if lib.does_asset_exist(dest) else lib.duplicate_asset(source,dest);assert master
ml.set_material_usage(master,unreal.MaterialUsage.MATUSAGE_NANITE);ml.recompile_material(master);lib.save_loaded_asset(master)
bindings=[];copies={}
for r in rows:
 if not r['nanite'] or r['chain'][-1]!=source:continue
 assert len(r['chain'])==2,'Unexpected material inheritance; audit before rebinding'
 original=r['chain'][0];path=root+'/MI_R12_Retained_'+hashlib.sha256(original.encode()).hexdigest()[:10]
 mi=lib.load_asset(path) if lib.does_asset_exist(path) else lib.duplicate_asset(original,path);assert mi
 ml.set_material_instance_parent(mi,master);ml.update_material_instance(mi);lib.save_loaded_asset(mi);copies[original]=mi
 a=actors[r['actor']];c=next(c for c in a.get_components_by_class(unreal.StaticMeshComponent) if c.get_name()==r['component'])
 assert c.get_material(r['slot']).get_path_name() in [original,mi.get_path_name()];c.set_material(r['slot'],mi)
 bindings.append(dict(r,new_material=mi.get_path_name()))
errors=list(unreal.StationMigrationLibrary.validate_material_shaders([master]+list(copies.values())));assert not errors,errors
assert ls.save_current_level();report={'success':True,'bindings':bindings,'original_shared_materials_saved':False,'reason':'Existing Fab master auto-enables Nanite in editor but lacks the serialized usage flag. R12 copies retain all textures/parameters and explicitly persist that usage for packaging.'}
(b/'retained_material_bindings.json').write_text(json.dumps(report,indent=2));RESULT={'success':True,'slots':len(bindings),'instances':len(copies)}

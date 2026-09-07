"""Create an isolated opaque-terrain rendering candidate; full fallback collision retained."""
import unreal,json
from pathlib import Path
b=Path(__file__).resolve().parents[1];lib=unreal.EditorAssetLibrary;ml=unreal.MaterialEditingLibrary
assert not unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).is_in_play_in_editor()
root='/Game/MaldekRefinement/R12/Diagnostics';lib.make_directory(root)
def copy(source,name):
 path=root+'/'+name
 return lib.load_asset(path) if lib.does_asset_exist(path) else lib.duplicate_asset(source,path)
master=copy('/Game/MaldekRefinement/ForestTest/Materials/M_Forest_Soil','M_TerrainNaniteProbe')
ml.set_material_usage(master,unreal.MaterialUsage.MATUSAGE_NANITE);ml.recompile_material(master);lib.save_loaded_asset(master)
mi=copy('/Game/MaldekRefinement/ForestTest/Audio/SurfaceMaterials/MI_Foot_Soil_4af055d463','MI_TerrainNaniteProbe')
ml.set_material_instance_parent(mi,master);ml.update_material_instance(mi);lib.save_loaded_asset(mi)
mesh=copy('/Game/MaldekRefinement/R12/Meshes/SM_R12_Terrain','SM_TerrainNaniteProbe');ns=mesh.get_editor_property('nanite_settings')
ns.set_editor_property('enabled',True);ns.set_editor_property('fallback_relative_error',0);ns.set_editor_property('fallback_percent_triangles',1)
mesh.set_editor_property('nanite_settings',ns);mesh.set_material(0,mi);lib.save_loaded_asset(mesh)
assert not unreal.StationMigrationLibrary.validate_material_shaders([master,mi])
RESULT={'candidate':mesh.get_path_name(),'saved_level_changed':False,'fallback_relative_error':0,'fallback_percent_triangles':1}
(b/'terrain_nanite_candidate.json').write_text(json.dumps(RESULT,indent=2))

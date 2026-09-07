import unreal,json
from pathlib import Path
base=Path(__file__).resolve().parents[1];lib=unreal.EditorAssetLibrary;ml=unreal.MaterialEditingLibrary
paths=lib.list_assets('/Game/MaldekRefinement/R12/Materials',True,False)
materials=[lib.load_asset(p) for p in paths if isinstance(lib.load_asset(p),unreal.MaterialInterface)]
for m in materials:
 if isinstance(m,unreal.Material) and m.get_editor_property('blend_mode')==unreal.BlendMode.BLEND_OPAQUE:
  ml.set_material_usage(m,unreal.MaterialUsage.MATUSAGE_NANITE);ml.recompile_material(m);lib.save_loaded_asset(m)
errors=list(unreal.StationMigrationLibrary.validate_material_shaders(materials));rows=[]
for m in materials:
 stats=ml.get_statistics(m)
 rows.append({'material':m.get_path_name(),'pixel_instructions':stats.num_pixel_shader_instructions,'vertex_instructions':stats.num_vertex_shader_instructions,'samplers':stats.num_samplers})
report={'success':not errors,'errors':errors,'materials':rows}
(base/'shader_validation.json').write_text(json.dumps(report,indent=2));assert not errors,errors
RESULT={'success':True,'checked_materials':len(materials)}

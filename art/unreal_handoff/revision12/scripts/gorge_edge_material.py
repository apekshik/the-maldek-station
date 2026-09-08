"""Feather the overlay's material into the underlying landscape at its boundary."""
import unreal,json
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'gorge';ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
lib=unreal.EditorAssetLibrary;ml=unreal.MaterialEditingLibrary;o=json.loads((b.parent/'working_level_report.json').read_text())['station_origin']
path='/Game/MaldekRefinement/R12/Gorge/Materials/M_Gorge_Ground'
m=unreal.load_asset(path) or lib.duplicate_asset('/Game/MaldekRefinement/R12/ForestRefine/Materials/M_Woodland_Ground',path)
m.set_editor_property('blend_mode',unreal.BlendMode.BLEND_MASKED)
pos=ml.create_material_expression(m,unreal.MaterialExpressionWorldPosition)
edge=ml.create_material_expression(m,unreal.MaterialExpressionCustom);edge.set_editor_property('output_type',unreal.CustomMaterialOutputType.CMOT_FLOAT1)
ci=unreal.CustomInput();ci.set_editor_property('input_name','Position');edge.set_editor_property('inputs',[ci])
edge.set_editor_property('code',f'float x=({o[0]:.9f}-Position.x)*0.01; float y=(Position.y-{o[1]:.9f})*0.01; float d=min(min(x+96.0,112.0-x),min(y+80.0,170.0-y)); return smoothstep(0.15,3.0,d);')
assert ml.connect_material_expressions(pos,'',edge,'Position')
dither=ml.create_material_expression(m,unreal.MaterialExpressionMaterialFunctionCall)
dither.set_material_function(unreal.load_asset('/Engine/Functions/Engine_MaterialFunctions02/Utility/DitherTemporalAA'))
assert ml.connect_material_expressions(edge,'',dither,'Alpha Threshold')
assert ml.connect_material_property(dither,'Result',unreal.MaterialProperty.MP_OPACITY_MASK)
ml.recompile_material(m);errors=list(unreal.StationMigrationLibrary.validate_material_shaders([m]));assert not errors,errors
lib.save_loaded_asset(m)
a=next(a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors() if a.get_actor_label()=='VF10_Parking_Terrain');mesh=a.static_mesh_component.static_mesh
for i in range(len(mesh.get_editor_property('static_materials'))):mesh.set_material(i,m);a.static_mesh_component.set_material(i,m)
lib.save_loaded_asset(mesh);assert ls.save_current_level();RESULT={'material':m.get_path_name(),'edge_fade_m':3,'shader_errors':errors};(out/'edge_material.json').write_text(json.dumps(RESULT))

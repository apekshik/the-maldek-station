import unreal,json
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'gorge';ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
a=next(a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors() if a.get_actor_label()=='VF10_Parking_Terrain');c=a.static_mesh_component;mesh=c.static_mesh;material=unreal.load_asset('/Game/MaldekRefinement/R12/ForestRefine/Materials/M_Woodland_Ground')
before=[str(s) for s in mesh.get_editor_property('static_materials')]
for i in range(len(before)):
 mesh.set_material(i,material);c.set_material(i,material)
errors=list(unreal.StationMigrationLibrary.validate_material_shaders([material]));assert not errors,errors
unreal.EditorAssetLibrary.save_loaded_asset(mesh);assert ls.save_current_level()
RESULT={'before':before,'material_slots':len(before),'material_errors':errors};(out/'material_audit.json').write_text(json.dumps(RESULT))

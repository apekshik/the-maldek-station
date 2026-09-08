"""Persist rock retirement and avoid shadow cost for small ground cover."""
import unreal,json,runpy
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'forest_refine';aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert not unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).is_in_play_in_editor()
labels=set(json.loads((out/'install.json').read_text())['retired_rock_patches'])
for a in aa.get_all_level_actors():
 if a.get_actor_label() in labels:a.static_mesh_component.set_static_mesh(None)
for letter in 'ABCD':
 ft=unreal.load_asset('/Game/MaldekRefinement/R12/ForestRefine/Foliage/FT_Woodland_Grass_'+letter);ft.set_editor_property('cast_shadow',False);unreal.EditorAssetLibrary.save_loaded_asset(ft)
for a in aa.get_all_level_actors():
 if not isinstance(a,unreal.InstancedFoliageActor):continue
 for c in a.get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent):
  if c.static_mesh and c.static_mesh.get_name().startswith('SM_MWAM_Grass'):c.set_cast_shadow(False)
RESULT=runpy.run_path(str(b/'scripts/forest_refine_verify.py'))['RESULT']

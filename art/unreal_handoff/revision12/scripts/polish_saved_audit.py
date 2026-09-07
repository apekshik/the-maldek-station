"""Verify persisted player defaults and repaired fallback data after reopening Unreal."""
import unreal,json
from pathlib import Path
b=Path(__file__).resolve().parents[1];lib=unreal.EditorAssetLibrary
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert w.get_name()=='Station_R12'
gm=w.get_world_settings().get_editor_property('default_game_mode');assert 'Polished' in gm.get_name()
pawn=unreal.get_default_object(unreal.get_default_object(gm).default_pawn_class)
c=pawn.get_component_by_class(unreal.StationPlayerPresentationComponent);beam=pawn.get_component_by_class(unreal.SpotLightComponent)
assert pawn.get_editor_property('unlimited_sprint')
assert c.get_editor_property('detailed_torch_mesh').get_name()=='SM_Torch_Field'
assert beam.get_editor_property('light_function_material').get_name()=='M_Torch_Optics'
rows=[]
rebuilt={r['mesh']:r['after']['triangles'] for r in json.loads((b/'polish/trim_fallback_repair.json').read_text())['meshes']}
for x in json.loads((b/'handoff_manifest.json').read_text())['chunks']:
 if 'nanite_fallback_target' not in x:continue
 m=lib.load_asset('/Game/MaldekRefinement/R12/Meshes/'+x['name']);ns=m.get_editor_property('nanite_settings')
 assert ns.fallback_target==unreal.NaniteFallbackTarget.PERCENT_TRIANGLES
 assert m.get_num_triangles(0)==rebuilt[x['name']],x['name']
 rows.append(x['name'])
assert len(rows)==17
report={'success':True,'reopened_editor':True,'map':w.get_path_name(),'game_mode':gm.get_path_name(),'pawn':pawn.get_class().get_path_name(),'torch':c.get_editor_property('detailed_torch_mesh').get_path_name(),'optics':beam.get_editor_property('light_function_material').get_path_name(),'repaired_meshes':rows}
(b/'polish/saved_audit.json').write_text(json.dumps(report,indent=2));RESULT=report

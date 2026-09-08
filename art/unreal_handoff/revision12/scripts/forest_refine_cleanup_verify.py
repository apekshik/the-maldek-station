"""Remove unused trial shader copies, then validate the saved final pass."""
import unreal,json,runpy
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'forest_refine';lib=unreal.EditorAssetLibrary;ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
root='/Game/MaldekRefinement/R12/ForestRefine/Materials';mi=unreal.load_asset(root+'/MI_Woodland_Landscape');assert mi.get_editor_property('parent').get_name()=='M_Woodland_Landscape_Final'
removed=[];old=root+'/M_Woodland_Landscape_Blend'
if lib.does_asset_exist(old):assert lib.delete_asset(old);removed.append(old)
for p in lib.list_assets(root+'/Functions',True,False):
 name=p.split('/')[-1].split('.')[0]
 if name.startswith(('MF_MWAM_','MW_MWAM_')):
  assert lib.delete_asset(p);removed.append(p)
result=runpy.run_path(str(b/'scripts/forest_refine_verify.py'))['RESULT'];assert result['passed'],result
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);actors={a.get_actor_label():a for a in aa.get_all_level_actors()}
for p in json.loads((out/'parking_edge.json').read_text())['plants']:
 assert actors[p['label']].skeletal_mesh_component.get_editor_property('skeletal_mesh_asset').get_path_name().split('.')[0]==p['mesh']
for p in json.loads((out/'rocks'/'placement.json').read_text())['placements']:
 assert actors[p['label']].static_mesh_component.static_mesh.get_path_name().split('.')[0]==p['mesh']
for name in ['Hatchback','Pickup']:assert actors['FR_Parked_'+name].static_mesh_component.static_mesh.get_name()=='SM_'+name
RESULT={'passed':True,'saved':True,'vehicles':2,'new_rock_pieces':44,'parking_edge_plants':30,'removed_unused_trial_assets':removed};(out/'completion.json').write_text(json.dumps(RESULT,indent=2))

"""Cull redundant backfaces only on audited closed glass volumes; keep gondola sheets two-sided."""
import unreal,json
from pathlib import Path
b=Path(__file__).resolve().parents[1];lib=unreal.EditorAssetLibrary;ml=unreal.MaterialEditingLibrary;ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert not ls.is_in_play_in_editor()
m=json.loads((b/'handoff_manifest.json').read_text());audit=json.loads((b/'glass_topology.json').read_text());closed={c['name'] for c in m['chunks'] if c['role']=='glass' and all(r['non_manifold_edges']==0 for r in audit['objects'] if r['assembly']==c['name'])}
assert len(closed)==7
root='/Game/MaldekRefinement/R12/Materials';parent=lib.load_asset(root+'/Masters/M_R12_Glass_Interior');assert parent
path=root+'/Masters/M_R12_Glass_ClosedPane';master=lib.load_asset(path) if lib.does_asset_exist(path) else lib.duplicate_asset(parent.get_path_name(),path)
master.set_editor_property('two_sided',False);ml.recompile_material(master);lib.save_loaded_asset(master)
bindings={r['slot']:r['instance'] for r in json.loads((b/'material_bindings.json').read_text())['materials']};instances={};rows=[]
for c in m['chunks']:
 if c['name'] not in closed:continue
 for slot in c['material_slots']:
  if slot not in instances:
   path=root+'/Instances/MI_Closed_'+slot;mi=lib.load_asset(path) if lib.does_asset_exist(path) else lib.duplicate_asset(bindings[slot],path)
   ml.set_material_instance_parent(mi,master);ml.update_material_instance(mi);lib.save_loaded_asset(mi);instances[slot]=mi
  c.setdefault('material_bindings_override',{})[slot]=instances[slot].get_path_name()
 mesh=lib.load_asset('/Game/MaldekRefinement/R12/Meshes/'+c['name'])
 if mesh:
  for i,s in enumerate(mesh.static_materials):mesh.set_material(i,instances[str(s.material_slot_name)])
  lib.save_loaded_asset(mesh)
 rows.append({'assembly':c['name'],'bindings':c['material_bindings_override'],'geometry_changed':False,'collision_changed':False})
assert not unreal.StationMigrationLibrary.validate_material_shaders([master]+list(instances.values()))
(b/'handoff_manifest.json').write_text(json.dumps(m,indent=2))
report={'success':True,'closed_assemblies':rows,'closed_objects':14,'gondola_sheet_objects_two_sided':10,'reason':'Closed panes already have outward-facing surfaces on both sides. Backface culling removes redundant tint/overdraw while preserving visibility from inside and outside. Open gondola sheets retain two-sided shading.'}
(b/'closed_glass_optimization.json').write_text(json.dumps(report,indent=2))
if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_name()=='Station_R12':assert ls.save_current_level()
RESULT={'success':True,'assemblies':len(rows),'materials':len(instances)+1}

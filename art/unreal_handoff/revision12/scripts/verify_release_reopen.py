"""Read-only final editor startup and saved material-binding verification."""
import unreal,json
from pathlib import Path
b=Path(__file__).resolve().parents[1]
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert w.get_path_name()=='/Game/MaldekRefinement/R12/Station_R12.Station_R12',w.get_path_name()
m=json.loads((b/'handoff_manifest.json').read_text());checked=[]
for c in m['chunks']:
 overrides=c.get('material_bindings_override',{})
 if not overrides:continue
 mesh=unreal.load_asset('/Game/MaldekRefinement/R12/Meshes/'+c['name'])
 for slot in mesh.static_materials:
  expected=overrides.get(str(slot.material_slot_name))
  if expected:
   assert slot.material_interface.get_path_name().split('.')[0]==expected.split('.')[0],c['name']
   checked.append({'mesh':c['name'],'slot':str(slot.material_slot_name),'material':expected})
assert checked
(b/'editor_release_reopen.json').write_text(json.dumps({'success':True,'world':w.get_path_name(),'saved_material_overrides':checked,'operation':'Read-only default-map startup; no asset saves.'},indent=2))

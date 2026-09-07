"""Audit selective window repair without changing prior review evidence."""
import unreal,json,runpy,hashlib
from pathlib import Path
b=Path(__file__).resolve().parents[1]
runpy.run_path(str(b/'scripts/audit_stage.py'),init_globals={'JOB':{'stage':'Architecture','checkpoint_transforms':'trim2/checkpoint_transforms.json'}})
repair=json.loads((b/'window_fix/core_recess.json').read_text());assert repair['collision_unchanged']
manifest=json.loads((b/'handoff_manifest.json').read_text())
checks=[]
for r in manifest['chunks']:
 if r['name'] not in repair['changed_assets']:continue
 mesh=unreal.EditorAssetLibrary.load_asset('/Game/MaldekRefinement/R12/Meshes/'+r['name']);assert mesh
 assert hashlib.sha256((b/r['file']).read_bytes()).hexdigest()==r['sha256']
 assert mesh.get_num_triangles(0)>0
 checks.append({'mesh':r['name'],'triangles':mesh.get_num_triangles(0),'collision_boxes':len(r['collision_boxes'])})
assert len(checks)==7
(b/'window_fix/verification.json').write_text(json.dumps({'success':True,'meshes':checks,'collision_unchanged':True,'retained_actor_audit':'audit_architecture.json'},indent=2))
RESULT={'success':True,'meshes':len(checks)}

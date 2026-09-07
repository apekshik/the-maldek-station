"""Compare shared Content against the immutable pre-migration commit, including working edits."""
import subprocess,json,hashlib
from pathlib import Path
b=Path(__file__).resolve().parents[1];repo=b.parents[2]
changed=subprocess.check_output(['git','diff','--name-only','pre-vf07-unreal-migration','--','game/Content'],cwd=repo,text=True).splitlines()
outside=[p for p in changed if not p.startswith('game/Content/MaldekRefinement/R12/')];assert not outside,outside
source=repo/'art/blender/visual_fidelity_07/Maldek_Station_Cleanup.blend'
expected=json.loads((b/'handoff_manifest.json').read_text())['source_sha256'];assert hashlib.sha256(source.read_bytes()).hexdigest()==expected
level=repo/'game/Content/MaldekRefinement/ForestTest/Forest_Approach_Test.umap'
checkpoint=json.loads((b/'checkpoint-verification.json').read_text());prior=next(r['sha256'].lower() for r in checkpoint['critical_hashes'] if r['file'].endswith('Forest_Approach_Test.umap'))
assert hashlib.sha256(level.read_bytes()).hexdigest()==prior
report={'success':True,'baseline':'pre-vf07-unreal-migration','shared_content_changed':outside,'approved_blender_unchanged':True,'forest_source_level_unchanged':True,'scope':'Git comparison of all shared Content plus byte hashes of approved VF07 and saved forest source level. R12-owned replacements are the only changed Content paths.'}
(b/'preservation_verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))

"""Verify portable source/FBX/texture hashes and complete imported asset coverage."""
import hashlib,json,sys
from pathlib import Path
repo=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parents[4]
b=repo/'art/unreal_handoff/revision12'
m=json.loads((b/'handoff_manifest.json').read_text());bakes=json.loads((b/'baked_materials.json').read_text());ledger=json.loads((b/'integration_ledger.json').read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
source=repo/'art/blender/visual_fidelity_07/Maldek_Station_Cleanup.blend'
assert sha(source)==m['source_sha256']
assert len(m['chunks'])==328 and len(ledger['assets'])==328
for chunk in m['chunks']:
 assert sha(b/chunk['file'])==chunk['sha256'],chunk['file']
 row=ledger['assets'][chunk['name']];assert row['sha256']==chunk['sha256']
 assert (repo/'game/Content'/Path(row['asset'].removeprefix('/Game/')).with_suffix('.uasset')).is_file(),row['asset']
for texture_set in bakes['sets'].values():
 for kind,path in texture_set['textures'].items():assert sha(b/path)==texture_set['files'][kind]['sha256'],path
assert (repo/'game/Content/MaldekRefinement/R12/Station_R12.umap').is_file()
report={'success':True,'repository':str(repo),'source_sha256':m['source_sha256'],'assemblies':328,'texture_sets':len(bakes['sets']),'textures':sum(len(s['textures']) for s in bakes['sets'].values()),'export_triangles':sum(c['triangles'] for c in m['chunks']),'checks':'Source, FBX and texture SHA-256; imported ledger hash coverage; all 328 Unreal meshes and level exist.'}
print(json.dumps(report,indent=2))
if len(sys.argv)>2:Path(sys.argv[2]).write_text(json.dumps(report,indent=2))

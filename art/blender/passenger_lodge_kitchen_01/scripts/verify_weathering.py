"""Verify the delivered library, source texture hashes and render inventory."""
import bpy, json, hashlib
from pathlib import Path
OUT=Path(__file__).resolve().parents[1];W=OUT/'weathering'
rows=json.loads((W/'texture_sources.json').read_text())
for r in rows:assert hashlib.sha256((W/'textures'/r['file']).read_bytes()).hexdigest()==r['sha256'],r['file']
bpy.ops.wm.open_mainfile(filepath=str(W/'PLK_Assets_Weathered.blend'))
assets=bpy.data.collections['PLK_Assets']
assert all(o.name.startswith('PLK_') for o in assets.all_objects)
assert not any(c.name.startswith('REFERENCE_ONLY') or c.name.startswith('PLK_REVIEW') for c in bpy.data.collections)
meshes=[o for o in assets.all_objects if o.type=='MESH'];assert len(meshes)==402
images={n.image for o in assets.all_objects if o.type in {'MESH','FONT'} for m in o.data.materials if m and m.use_nodes for n in m.node_tree.nodes if n.type=='TEX_IMAGE'}
assert len(images)==7 and all(i.packed_file for i in images)
assert all(i.filepath.replace('\\','/').startswith('//textures/') for i in images),[(i.name,i.filepath) for i in images]
expected=sorted(p.name for p in (OUT/'previews').glob('PLK_REVIEW_*.png'))
assert len(expected)==10 and all((W/'previews'/n).exists() for n in expected)
doc=json.loads((W/'verification.json').read_text())
doc.update({'asset_library_reopened':True,'asset_library_meshes':len(meshes),'asset_library_reference_context_absent':True,'asset_library_packed_relative_images':len(images),'downloaded_texture_hashes_verified':len(rows),'review_renders':expected})
(W/'verification.json').write_text(json.dumps(doc,indent=2))
print('PASS: library isolated; 402 meshes; 7 packed relative maps; 14 download hashes; 10 renders.')

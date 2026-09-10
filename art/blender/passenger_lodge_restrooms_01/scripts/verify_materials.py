"""Verify packed map persistence, hash identity, and basin attributes after reopening."""
import bpy,json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(P/'Maldek_Passenger_Lodge_Restrooms.blend'))
records=json.loads((P/'textures/provenance.json').read_text(encoding='utf-8-sig'))
for r in records:
    im=bpy.data.images[r['file']]
    assert im.packed_file and list(im.size)==[2048,2048]
    assert hashlib.md5(im.packed_file.data).hexdigest()==r['md5']
    assert hashlib.sha256(im.packed_file.data).hexdigest().lower()==r['sha256'].lower()
meshes=[o for o in bpy.data.collections['PLR_Assets'].objects if o.type=='MESH']
assert all(o.data.uv_layers.get('PLR_Metric_2m') for o in meshes)
for n in ['Women','Men']:
    o=bpy.data.objects['PLR_'+n+'_Basin_bowl']
    assert o.data.attributes.get('PLR_Deposit')
    assert bpy.data.objects.get('PLR_'+n+'_Tap_deck') is None
    assert abs(o.dimensions.x-.510)<.0001 and abs(o.dimensions.y-.620)<.0001
r=json.loads((P/'material_verification.json').read_text());r.update(saved_reopened=True,packed_hashes_verified=True,rounded_basin_envelopes_verified=True,uv_mesh_count=len(meshes))
(P/'material_verification.json').write_text(json.dumps(r,indent=2))
print('PLR MATERIAL REOPEN PASS')

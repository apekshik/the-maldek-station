import bpy,bmesh,json,hashlib
from pathlib import Path
OUT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(OUT/'Maldek_Passenger_Lodge_Layout.blend'))
s=bpy.data.scenes['01_Lodge_Layout'];dg=bpy.context.evaluated_depsgraph_get();bad=[]
for o in s.objects:
 if o.type!='MESH':continue
 eo=o.evaluated_get(dg);me=eo.to_mesh();bm=bmesh.new();bm.from_mesh(me)
 if any(not e.is_manifold for e in bm.edges):bad.append(o.name)
 bm.free();eo.to_mesh_clear()
r=json.loads((OUT/'layout_report.json').read_text())
assert not bad,bad
assert all(not c['blocked_by'] for c in r['routes']),r['routes']
assert len([o for o in s.objects if o.name.startswith('Table_') and o.name.endswith('_Top')])==6
assert len([o for o in s.objects if o.name.startswith('Bench_') and o.name.endswith('_Seat')])==12
assert len([o for o in s.objects if o.name.startswith('Locker_') and o.name.endswith('_Door')])==12
assert bpy.data.collections['PL01_Roof_Envelope'].hide_render
assert '02_Protected_Site_Study' in bpy.data.scenes
previews=sorted((OUT/'previews').glob('*.png'));assert len(previews)==5
result={'passed':True,'saved_reopened':True,'evaluated_nonmanifold_meshes':bad,'sampled_clearance_radius_m':.34,'routes':len(r['routes']),'preview_count':len(previews),'blend_sha256':hashlib.sha256((OUT/'Maldek_Passenger_Lodge_Layout.blend').read_bytes()).hexdigest(),'limitations':'Axis-aligned blockout clearance samples; not Unreal collision or continuous capsule testing. Site placement uncommitted. Roof and props are layout proxies.'}
(OUT/'verification.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))

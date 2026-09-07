import bpy,json,hashlib,numpy as np
from pathlib import Path
base=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(base.parent/'revision10/station_patched.blend'),load_ui=False);deps=bpy.context.evaluated_depsgraph_get()
approved=json.loads((base.parents[1]/'checkpoints/pre_vf07/approved_source_inventory.json').read_text());current={o['name']:o for o in approved['objects']};rows=[]
for name in ['Parking','Parked_Car']:
 o=bpy.data.objects[name];ev=o.evaluated_get(deps);me=ev.to_mesh(preserve_all_data_layers=True,depsgraph=deps);me.transform(o.matrix_world);me.calc_loop_triangles()
 vs=np.empty(len(me.vertices)*3,dtype=np.float32);me.vertices.foreach_get('co',vs);ts=np.empty(len(me.loop_triangles)*3,dtype=np.int32);me.loop_triangles.foreach_get('vertices',ts)
 sha=hashlib.sha256(vs.tobytes()+ts.tobytes()).hexdigest();ev.to_mesh_clear();assert sha==current[name]['geometry_sha256'],name
 rows.append({'name':name,'unchanged':True,'geometry_sha256':sha})
(base/'parking_source_preservation.json').write_text(json.dumps({'success':True,'objects':rows},indent=2));print('PARKING_SOURCE_PRESERVED',flush=True)

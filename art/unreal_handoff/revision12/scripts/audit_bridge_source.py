import bpy,json,hashlib,numpy as np
from pathlib import Path
base=Path(__file__).resolve().parents[1]
old=base.parent/'revision11/station_layout.blend'
bpy.ops.wm.open_mainfile(filepath=str(old),load_ui=False);deps=bpy.context.evaluated_depsgraph_get()
approved=json.loads((base.parents[1]/'checkpoints/pre_vf07/approved_source_inventory.json').read_text())
current={o['name']:o for o in approved['objects'] if '20_Lookout_Bridge' in o['collections']}
rows=[];removed=[];changed=[]
for o in bpy.data.collections['20_Lookout_Bridge'].all_objects:
 if o.type not in {'MESH','CURVE','FONT'}:continue
 ev=o.evaluated_get(deps);me=ev.to_mesh(preserve_all_data_layers=True,depsgraph=deps)
 if not me:continue
 me.transform(o.matrix_world);me.calc_loop_triangles();vs=np.empty(len(me.vertices)*3,dtype=np.float32);me.vertices.foreach_get('co',vs);ts=np.empty(len(me.loop_triangles)*3,dtype=np.int32);me.loop_triangles.foreach_get('vertices',ts)
 sha=hashlib.sha256(vs.tobytes()+ts.tobytes()).hexdigest();v=vs.reshape(-1,3);bounds=[v.min(0).tolist(),v.max(0).tolist()];ev.to_mesh_clear()
 if o.name not in current:
  removed.append({'source':o.name,'bounds':bounds});continue
 same=sha==current[o.name]['geometry_sha256'];rows.append({'source':o.name,'unchanged':same,'r11_geometry_sha256':sha,'vf07_geometry_sha256':current[o.name]['geometry_sha256'],'collision_guide':bool(o.get('collision',False)),'r11_bounds':bounds,'vf07_bounds':current[o.name]['bounds']})
 if not same:changed.append(o.name)
assert set(changed)<= {'Tower_Footing','Tower_Footing.001'},changed
assert all(r['bounds'][1][1]<8.6 for r in removed),removed
report={'success':True,'r11_source':str(old),'r11_file_sha256':hashlib.sha256(old.read_bytes()).hexdigest(),'retained_geometry':rows,'affected_supports':changed,'removed_junction_only':removed}
(base/'bridge_source_preservation.json').write_text(json.dumps(report,indent=2));print('BRIDGE_PRESERVATION',sum(r['unchanged'] for r in rows),'unchanged;',len(changed),'affected supports;',len(removed),'junction objects removed',flush=True)

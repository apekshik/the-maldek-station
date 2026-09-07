"""Read-only approved VF07 geometry/material inventory for exact replacement mapping."""
import bpy,json,hashlib,numpy as np
from pathlib import Path
from mathutils import Vector
out=Path(__file__).resolve().parent
source=out.parents[1]/'blender/visual_fidelity_07/Maldek_Station_Cleanup.blend'
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
deps=bpy.context.evaluated_depsgraph_get()
report={'source':str(source),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'objects':[],'materials':{}}
for o in bpy.context.scene.objects:
 row={'name':o.name,'type':o.type,'collections':[c.name for c in o.users_collection],'hide_render':o.hide_render,'export_geometry':bool(o.get('export_geometry',True)),'collision_guide':bool(o.get('collision',False)),'assembly':o.get('assembly'),'parent':o.parent.name if o.parent else None,'matrix_world':[list(r) for r in o.matrix_world]}
 if o.type in {'MESH','FONT','CURVE'}:
  ev=o.evaluated_get(deps); me=ev.to_mesh(preserve_all_data_layers=True,depsgraph=deps)
  if me:
   me.transform(o.matrix_world);me.calc_loop_triangles()
   vs=np.empty(len(me.vertices)*3,dtype=np.float32);me.vertices.foreach_get('co',vs)
   ts=np.empty(len(me.loop_triangles)*3,dtype=np.int32);me.loop_triangles.foreach_get('vertices',ts)
   row.update(vertices=len(me.vertices),triangles=len(me.loop_triangles),geometry_sha256=hashlib.sha256(vs.tobytes()+ts.tobytes()).hexdigest(),materials=[m.name if m else None for m in me.materials])
   if len(vs):row['bounds']=[vs.reshape(-1,3).min(axis=0).tolist(),vs.reshape(-1,3).max(axis=0).tolist()]
   ev.to_mesh_clear()
 report['objects'].append(row)
for m in bpy.data.materials:
 if not m.use_nodes:report['materials'][m.name]={'diffuse':list(m.diffuse_color)};continue
 p=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
 row={'diffuse':list(m.diffuse_color),'nodes':[n.bl_idname for n in m.node_tree.nodes],'inputs':{}}
 if p:
  for name in ['Base Color','Metallic','Roughness','Normal','Transmission Weight','Emission Color','Emission Strength']:
   inp=p.inputs[name];v=inp.default_value
   row['inputs'][name]={'value':float(v) if isinstance(v,(float,int)) else list(v),'linked':inp.is_linked}
 report['materials'][m.name]=row
(out/'approved_source_inventory.json').write_text(json.dumps(report,indent=2))
print('APPROVED_SOURCE_INVENTORY',len(report['objects']),flush=True)


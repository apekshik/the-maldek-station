import bpy,json,hashlib
from pathlib import Path
OUT=Path(__file__).resolve().parents[1];REPO=OUT.parents[2]
source=REPO/'art/blender/passenger_lodge_04/Maldek_Passenger_Lodge_Integrated.blend'
bpy.ops.wm.open_mainfile(filepath=str(source));bpy.context.scene.frame_set(1)
names=set()
for kind in ['shell','deck']:names.update(json.loads((OUT/(kind+'_exports.json')).read_text())['materials'])
for ob in bpy.data.collections['PLW_Assets'].all_objects:
 if ob.type=='MESH':names.update(m.name for m in ob.data.materials if m)
def val(v):
 try:return list(v)
 except:return v
data={}
for name in sorted(names):
 m=bpy.data.materials[name];ns=[]
 for n in m.node_tree.nodes:
  d={'name':n.name,'type':n.type,'inputs':{s.name:val(s.default_value) for s in n.inputs if hasattr(s,'default_value') and s.enabled}}
  for p in ['operation','blend_type','noise_dimensions','normalize']:
   if hasattr(n,p):d[p]=getattr(n,p)
  if n.type=='VALTORGB':d['ramp']=[{'position':e.position,'color':list(e.color)} for e in n.color_ramp.elements]
  if n.type=='TEX_IMAGE' and n.image:d['image']=n.image.filepath
  ns.append(d)
 data[name]={'nodes':ns,'links':[[l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name] for l in m.node_tree.links]}
(OUT/'material_audit.json').write_text(json.dumps(data,indent=2))
objs=[]
for ob in bpy.data.collections['PLW_Assets'].all_objects:
 objs.append({'name':ob.name,'type':ob.type,'parent':ob.parent.name if ob.parent else None,'uv':len(ob.data.uv_layers) if ob.type=='MESH' else None,'location':list(ob.matrix_world.translation)})
(OUT/'window_source_audit.json').write_text(json.dumps(objs,indent=2))
print('MATERIAL_AUDIT',len(data),flush=True)

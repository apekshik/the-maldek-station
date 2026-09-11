import bpy,json
from pathlib import Path
OUT=Path(__file__).resolve().parents[1];REPO=OUT.parents[2];d=OUT/'finishing';d.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(REPO/'art/blender/passenger_lodge_04/Maldek_Passenger_Lodge_Integrated.blend'));bpy.context.scene.frame_set(1)
obs=list(bpy.data.collections['PLL_Lockers'].all_objects)+list(bpy.data.collections['PLG_Wall_Details'].all_objects)
rows=[{'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,'matrix':[list(r) for r in o.matrix_world],'properties':dict(o.items()),'materials':[m.name for m in o.data.materials] if o.type in {'MESH','FONT','CURVE'} else []} for o in obs]
(d/'source_survey.json').write_text(json.dumps(rows,indent=2,default=str))
(d/'materials.json').write_text(json.dumps({m.name:[{'type':n.type,'name':n.name,'image':n.image.filepath if n.type=='TEX_IMAGE' and n.image else None} for n in m.node_tree.nodes] for m in bpy.data.materials if m.use_nodes and any(m in list(o.data.materials) for o in obs if o.type in {'MESH','CURVE','FONT'})},indent=2))
print('FINISHING',len(rows),[(o.name,dict(o.items())) for o in obs if o.type=='EMPTY'],flush=True)

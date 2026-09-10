"""Record editable delivery hierarchies before engine conversion."""
import bpy,json
from pathlib import Path
OUT=Path(__file__).resolve().parents[1];REPO=OUT.parents[2]
bpy.ops.wm.open_mainfile(filepath=str(REPO/'art/blender/passenger_lodge_04/Maldek_Passenger_Lodge_Integrated.blend'));bpy.context.scene.frame_set(1)
collections=['PLW_Assets','PLD_ASSETS','PLR_Assets','PLK_Assets','PLS_Seating_Kit','PLL_Lockers','PLG_Wall_Details'];rows=[];materials={}
for cn in collections:
 c=bpy.data.collections.get(cn);assert c,cn
 for ob in c.all_objects:
  action=ob.animation_data.action if ob.animation_data else None
  rows.append({'package':cn,'name':ob.name,'type':ob.type,'data':ob.data.name if ob.data else None,'parent':ob.parent.name if ob.parent else None,'world_matrix':[list(r) for r in ob.matrix_world],'local_matrix':[list(r) for r in ob.matrix_local],'action':action.name if action else None,'action_range':list(action.frame_range) if action else None,'hidden':ob.hide_render,'materials':[m.name if m else None for m in ob.data.materials] if ob.type in ['MESH','CURVE','FONT'] else []})
  if ob.type not in ['MESH','CURVE','FONT']:continue
  for m in ob.data.materials:
   if not m or m.name in materials:continue
   materials[m.name]={'nodes':[{'name':n.name,'type':n.type,'image':n.image.name if n.type=='TEX_IMAGE' and n.image else None,'path':n.image.filepath if n.type=='TEX_IMAGE' and n.image else None} for n in m.node_tree.nodes] if m.use_nodes else []}
(OUT/'delivery_inventory.json').write_text(json.dumps({'objects':rows,'materials':materials},indent=2))
print('DELIVERY_INVENTORY',len(rows),len(materials),flush=True)

"""Reopen the editable study and check evaluated geometry and animation stages."""
import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
OUT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(OUT/'Maldek_Keyed_Door.blend'));s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update()
checks={};details={}
def bounds(o):
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();pts=[e.matrix_world@v.co for v in m.vertices];e.to_mesh_clear();return [[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]]
checks['old_cylinder_removed']=not any(o.name.startswith(('Lock_cylinder','Key_slot')) for o in s.objects)
checks['pear_shaped_bow']='Pear_shaped_key_bow' in bpy.data.objects
checks['glass_preserved']=bpy.data.objects['Vision_glass'].data.materials[0].name=='D01_Frosted_glass'
checks['all_key_parts_parented']=all(o.parent==bpy.data.objects['D04_KEY_INSERT_AND_TURN'] for o in bpy.data.collections['09_Cut_service_key'].objects)
bad=[]
for name in ['07_Key_cylinder_housings','08_Rotating_plugs','09_Cut_service_key']:
 for o in bpy.data.collections[name].objects:
  if o.type!='MESH':continue
  e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=e.to_mesh();bm=bmesh.new();bm.from_mesh(me)
  if any(not edge.is_manifold for edge in bm.edges):bad.append(o.name)
  bm.free();e.to_mesh_clear()
checks['evaluated_parts_closed']=not bad;details['nonmanifold_parts']=bad
# Through-hole exists through both opaque door layers at the cylinder axis.
for n in ['Leaf_slab','Interior_enamel']+[o.name for o in bpy.data.collections['01_Moving_leaf'].objects if o.name.startswith('Lock_escutcheon')]:
 o=bpy.data.objects[n];tree=BVHTree.FromObject(o,bpy.context.evaluated_depsgraph_get());inv=o.matrix_world.inverted();a=inv@Vector((1.15,-.1,1));b=inv@Vector((1.15,.1,1));hit=tree.ray_cast(a,(b-a).normalized(),(b-a).length)[0];checks[n+'_through_hole']=hit is None
rows=[]
for frame in [1,30,48,70,88,120]:
 s.frame_set(frame);bpy.context.view_layer.update();key=bpy.data.objects['D04_KEY_INSERT_AND_TURN'];plug=bpy.data.objects['D04_PLUG_FRONT'];hinge=bpy.data.objects['D01_HINGE_PIVOT']
 rows.append({'frame':frame,'key_turn':math.degrees(key.rotation_euler.y),'plug_turn':math.degrees(plug.rotation_euler.y),'door_angle':math.degrees(hinge.rotation_euler.z),'blade_bounds':bounds(bpy.data.objects['Five_cut_brass_blade'])})
checks['key_and_plug_turn_together']=all(abs(r['key_turn']-r['plug_turn'])<.01 for r in rows)
checks['door_stays_closed_until_key_withdrawn']=all(abs(r['door_angle'])<.01 for r in rows[:-1])
checks['opens_95_degrees']=abs(rows[-1]['door_angle']+95)<.01
checks['key_inserted_80mm']=abs(rows[1]['blade_bounds'][1][1]-rows[0]['blade_bounds'][1][1]-.08)<.0001
checks['key_returned_before_withdrawal']=abs(rows[3]['key_turn'])<.01
report={'success':all(checks.values()),'checks':checks,'details':details,'animation':rows,'scope':'Blender design validation, not Unreal runtime validation'}
(OUT/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));assert report['success']

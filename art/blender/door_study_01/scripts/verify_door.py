import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
OUT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(OUT/'Maldek_Control_Door_Study.blend'))
s=bpy.context.scene
def tree(objects):
 verts=[];faces=[];dg=bpy.context.evaluated_depsgraph_get()
 for o in objects:
  if o.type!='MESH':continue
  e=o.evaluated_get(dg);m=e.to_mesh();base=len(verts)
  verts.extend(e.matrix_world@v.co for v in m.vertices)
  faces.extend([base+i for i in p.vertices] for p in m.polygons);e.to_mesh_clear()
 return BVHTree.FromPolygons(verts,faces)
def cast(t,p,d,dist):return t.ray_cast(Vector(p),Vector(d),dist)[0] is not None
s.frame_set(1);bpy.context.view_layer.update()
slab=tree([bpy.data.objects['Leaf_slab'],bpy.data.objects['Interior_enamel']])
checks={'vision_cut_through_both_skins':not cast(slab,(.85,-.2,1.65),(0,1,0),.4),'solid_skin_beside_vision':cast(slab,(.07,-.2,1.65),(0,1,0),.4),'closed_leaf_blocks_route':cast(slab,(.65,-.2,1.0),(0,1,0),.4)}
body=bpy.data.objects['Leaf_slab'];v=[body.matrix_world@Vector(p) for p in body.bound_box]
checks['bottom_above_existing_threshold']=min(p.z for p in v)>.024
checks['leaf_inside_measured_reveal']=min(p.x for p in v)>0 and max(p.x for p in v)<1.3 and max(p.z for p in v)<2.4
s.frame_set(90);bpy.context.view_layer.update()
objects=list(bpy.data.collections['01_Moving_leaf'].objects)+list(bpy.data.collections['02_Stationary_hardware'].objects)+list(bpy.data.collections['03_Review_frame'].objects)
t=tree(objects);blocked=[]
for ix in range(29):
 x=.1+ix*1.1/28
 for z in [.15,.5,1.0,1.5,2.1]:
  if cast(t,(x,-.4,z),(0,1,0),.8):blocked.append([x,z])
checks['open_105_degree_sampled_1_1m_route']=not blocked
checks['hinge_pivot_persisted']=abs(bpy.data.objects['D01_HINGE_PIVOT'].location.x-.004)<1e-6
triangles=0
for o in objects:
 if o.type=='MESH':
  e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();m.calc_loop_triangles();triangles+=len(m.loop_triangles);e.to_mesh_clear()
report={'checks':checks,'sampled_open_route_rays':145,'blocked':blocked,'evaluated_review_triangles':triangles,'scope':'Saved/reopened Blender geometry. Includes study frame and moving leaf. Does not prove building swing clearance or Unreal capsule/collision behavior.'}
(OUT/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));assert all(checks.values())

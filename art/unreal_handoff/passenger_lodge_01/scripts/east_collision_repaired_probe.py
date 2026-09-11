import bpy,json,math
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
O=Path(__file__).resolve().parents[1];R=O.parents[2]
bpy.ops.wm.open_mainfile(filepath=str(R/'art/blender/passenger_lodge_wall_details_02/Maldek_East_Wall_Details.blend'));bpy.context.scene.frame_set(1);dg=bpy.context.evaluated_depsgraph_get();data=json.loads((O/'east_wall/exports.json').read_text());part=next(p for p in data['groups'][0]['parts'] if p['role']=='Leaf');H=Matrix(part['matrix']);c=Vector(part['collision'][0]['center']);e=Vector(part['collision'][0]['extent'])-Vector((.0005,)*3)
c.y-=.0035;e.y-=.0035
faces=[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)];hits=[]
for angle in [0,-1.8,-5,-45,-95]:
 M=H@Matrix.Rotation(math.radians(angle),4,'Z');pts=[M@(c+Vector((x*e.x,y*e.y,z*e.z))) for x in [-1,1] for y in [-1,1] for z in [-1,1]];bv=BVHTree.FromPolygons(pts,faces)
 for n in next(p for p in data['groups'][0]['parts'] if p['role']=='Static')['sources']:
  ob=bpy.data.objects[n];ev=ob.evaluated_get(dg);me=ev.to_mesh();vv=[ev.matrix_world@v.co for v in me.vertices];bb=BVHTree.FromPolygons(vv,[list(p.vertices) for p in me.polygons]);ov=bv.overlap(bb)
  if ov:hits.append({'angle':angle,'object':n,'overlap_faces':len(ov)})
  ev.to_mesh_clear()
(O/'east_wall/collision_repaired_probe.json').write_text(json.dumps(hits,indent=2));print(hits)

import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
OUT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(OUT/'Maldek_Integrated_Station.blend'))
bpy.context.view_layer.update()
terrain=bpy.data.objects['R11_Current_Terrain'];m=terrain.data
bvh=BVHTree.FromPolygons([terrain.matrix_world@v.co for v in m.vertices],[p.vertices[:] for p in m.polygons])
def ground(x,y):
 hit=bvh.ray_cast(Vector((x,y,50)),Vector((0,0,-1)))
 return hit[0].z if hit[0] else None
report={'terrain_samples':[], 'stairs':[], 'collections':{c.name:len(c.objects) for c in bpy.data.collections}}
for x,y in [(-24.5,-7),(-24.5,6.7),(-18.4,6.7),(-8.6,6.7),(-16.7,-14.5),(-10.7,-14.5),(-7.2,-11.9),(-1.9,-11.9),(18.2,-20.8),(23.8,-15.4),(21,-18),(22,-12)]:report['terrain_samples'].append([x,y,ground(x,y)])
for o in bpy.data.collections['VF06_Quarters_Rear_Stair'].objects:
 if o.name.startswith(('Grate_perimeter','Stair_nosing','Landing_support')):
  pts=[o.matrix_world@Vector(v) for v in o.bound_box];report['stairs'].append([o.name,[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]])
(OUT/'inspection.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report['terrain_samples']))

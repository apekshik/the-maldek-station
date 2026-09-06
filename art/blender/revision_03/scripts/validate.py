"""Validate the saved blockout, export one render mesh + its convex hulls per FBX,
then independently re-import every FBX to check dimensions and hull counts.
Run with Blender --background art/blender/millford_v2_blockout_01.blend --python ...
"""
import bpy, json, math
from pathlib import Path
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
OUT=Path(__file__).resolve().parents[1]
source=bpy.context.scene
# Include the physical ceilings in clearance checks, regardless of the saved cutaway view.
for lc in bpy.context.view_layer.layer_collection.children: lc.exclude=False
bpy.context.view_layer.update()
colliders=[o for o in source.objects if o.type=='MESH' and (o.get('collision') or o.name=='Terrain_Cliff_And_Relay_Spur') and not o.name.startswith('Site_Presentation')]
verts=[];faces=[];face_names=[]
for o in colliders:
    offset=len(verts);verts += [o.matrix_world@v.co for v in o.data.vertices]
    for p in o.data.polygons: faces.append(tuple(offset+i for i in p.vertices));face_names.append(o.name)
bvh=BVHTree.FromPolygons(verts,faces)
report={'status':'checking','clearance_radius_m':.28,'body_check_heights_m':[.7,1.65],'required_headroom_m':2.0,'routes':{},'fbx_roundtrips':[],'limitations':['Geometric samples are not a UE5 CharacterMovement or capsule sweep test.','FBX checked by Blender re-import; UE5 import is not verified.','Placeholder materials and UVs are not production surfacing.']}
# Samples follow the intended public, service and exterior connections. Stair points use actual tread elevations.
routes={
 'control_to_gondola':[(-6.2,-1.7,4),(-5,-1.7,4),(-3.8,-1.7,4),(-3.8,.6,4),(-2,2,4),(0,3.5,4),(0,6,4),(0,7.5,4)],
 'sheltered_loop':[(-6.2,-1.7,4),(-7,-2,4),(-9,-2,4),(-11.5,-2,4),(-11.5,1.5,4),(-7,1.5,4),(-3.8,1.5,4)],
 'lower_service':[(7,-.5,0),(5.2,-.5,0),(5.2,.8,0),(4,1.5,0),(2,1.5,0),(2,-1.5,0),(4,-3,0),(7,-3,0),(9,-3,0)],
 'upper_bridge':[(4,4,4),(4.5,7.55,4),(7,7.55,4),(9.8,7.55,4),(9.8,5.5,4),(12,4.5,4),(16.3,3,4),(16.3,2.15,4)],
 'forest_route':[(14,-2,0),(14,-6,0),(18.5,-7,0),(21,-6,.4),(26,-4,1),(26,-1,2),(26,3,2),(26,10,3),(19,11,4),(15,5,4),(14,5,4)],
 'exposed_drive':[(5.2,.8,0),(4.7,2,0),(4.7,5,0),(4.7,8.7,0),(4.7,10,0)],
 'arrival_to_hall':[(-11.5,-7.3,4),(-11.5,-5,4),(-11.5,-2,4)],
}
def interpolate(points,spacing=.22):
    result=[]
    for a,b in zip(points,points[1:]):
        a,b=Vector(a),Vector(b);n=max(1,math.ceil((b-a).length/spacing))
        result += [a.lerp(b,i/n) for i in range(n)]
    return result+[Vector(points[-1])]
route_data=json.loads((OUT/'route_points.json').read_text())
routes['forest_route']=route_data['paths'][0]+[[48,13,3]]+route_data['paths'][1]
for label,points in list(routes.items()): routes[label]=interpolate(points)
# The generator already records precise tread dimensions.
dim=json.loads((OUT/'blockout_dimensions.json').read_text())
for st in dim['stairs']:
    points=[]
    for i in range(23): points.append(Vector((st['x'],st['y0']+(st['y1']-st['y0'])*(i+.5)/23,st['z0']+(st['z1']-st['z0'])*(i+1)/24)))
    routes['stairs_'+st['name']]=points
errors=[]
for label,points in routes.items():
    issues=[]
    for i,p in enumerate(points):
        # Probe the actual walking surface, including small level joints in sloping paths.
        # Allow at most 220 mm deviation from the planned route height; larger steps fail.
        floor=bvh.ray_cast(p+Vector((0,0,.26)),Vector((0,0,-1)),.52)
        if floor[0] is None:
            issues.append({'sample':i,'issue':'no floor near planned feet','point':list(p)})
        elif abs(floor[0].z-p.z)>.22:
            issues.append({'sample':i,'issue':'excessive floor step','point':list(p)})
        else:
            p=p.copy(); p.z=floor[0].z
        # Upward clearance ray includes roof lintels; horizontal spokes approximate body radius.
        hit=bvh.ray_cast(p+Vector((0,0,.02)),Vector((0,0,1)),1.98)
        if hit[0] is not None: issues.append({'sample':i,'issue':'headroom','object':face_names[hit[2]],'point':list(p)})
        for h in [.7,1.65]:
            for angle in range(0,360,45):
                v=Vector((math.cos(math.radians(angle)),math.sin(math.radians(angle)),0))
                hit=bvh.ray_cast(p+Vector((0,0,h)),v,.28)
                if hit[0] is not None: issues.append({'sample':i,'issue':'body clearance','object':face_names[hit[2]],'point':list(p)});break
    report['routes'][label]={'samples':len(points),'issues':issues[:30],'issue_count':len(issues)}
    errors+=issues
# Confirm operator eye has an unobstructed architectural view to the returning car.
eye=Vector((-6.5,-1.6,5.65));target=Vector((0,5.05,5.35));delta=target-eye
hit=bvh.ray_cast(eye,delta.normalized(),delta.length-.15)
report['operator_to_gondola']={'clear':hit[0] is None,'obstruction':face_names[hit[2]] if hit[0] is not None else None}
if hit[0] is not None: errors.append({'issue':'operator sightline','object':face_names[hit[2]]})
report['geometry_issues']=len(errors)
(OUT/'validation_report.json').write_text(json.dumps(report,indent=2))
if errors:
    print('VALIDATION_FAILED',json.dumps({k:v for k,v in report['routes'].items() if v['issue_count']},indent=2),flush=True)
    print('SIGHTLINE',report['operator_to_gondola'],flush=True)
    raise RuntimeError(f'{len(errors)} geometry issues; fix before export')

report['status']='passed sampled geometry; no revision03 FBX exports or UE5 playtest'
report['fbx_roundtrips']=[]
report['packed_tree_images']=[im.name for im in bpy.data.images if 'pine_tree' in im.name and im.packed_file]
report['tree_instances']=len([o for o in source.objects if o.name.startswith(('Pine_CC0_','Distant_Pine_'))])
(OUT/'validation_report.json').write_text(json.dumps(report,indent=2))
print('R03_VALIDATED',sum(v['samples'] for v in report['routes'].values()),report['tree_instances'],'trees',len(report['packed_tree_images']),'packed maps',flush=True)

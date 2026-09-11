"""Replace the parking hairpin with a north-facing trailhead; retain later path sections."""
import bpy,json,math,sys,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
b=Path(__file__).resolve().parents[1];out=b/'parking_navigation';root=b.parents[2]
sys.path.insert(0,str(b/'scripts'));import mesh_handoff as mh
source=root/'art/blender/visual_fidelity_10/Maldek_Parking_Arrival.blend'
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
furniture=list(bpy.data.collections['VF10_02_Parking_Furniture'].objects)
signs=[o for o in furniture if any(k in o.name for k in ['Sign_post','Arrival_sign','Sign_face','Sign_text'])]
turn=Matrix.Translation(Vector((-35.3,-52.25,0)))@Matrix.Rotation(math.pi,4,'Z')@Matrix.Translation(Vector((33,61.5,0)))
for o in signs:
 o.matrix_world=turn@o.matrix_world
 if o.type=='FONT' and 'FOOTPATH' in o.data.body:o.data.body='FOOTPATH  >'
for o in furniture:
 if 'East_curb' in o.name:o.location.y=-58;o.dimensions.y=12
 if 'North_curb' in o.name:o.location.x=-39.15;o.dimensions.x=10.7
 if any(k in o.name for k in ['Bench_seat','Sign_post','Edge_curb','Rear_curb','East_curb','North_curb']):o['collision']=True
for name,pos,size in [('Sign_lamp_stem',(-35.3,-52.25,1.23),(.035,.035,.16)),('Sign_lamp_arm',(-35.3,-52.43,1.31),(.035,.40,.035)),('Sign_lamp_hood',(-35.3,-52.61,1.36),(.34,.18,.07))]:
 bpy.ops.mesh.primitive_cube_add(size=1,location=pos);ob=bpy.context.object;ob.name=name;ob.dimensions=size;ob.data.materials.append(bpy.data.materials['VF06_Structural_steel']);furniture.append(ob)
old=json.loads((out/'source_audit.json').read_text())[0]['vertices']
join=16;end=(Vector(old[join*2])+Vector(old[join*2+1]))/2
pts=[];centres=[]
for i in range(17):
 t=i/16;s=t*t*(3-2*t);cx=-32+(end.x+32)*s;cy=-52+(end.y+52)*t;cz=-1+(end.z+1)*s+.28*math.sin(math.pi*t)**2
 half=1.6+(.0+1.25-1.6)*s
 pts.extend([(cx+half,cy,cz),(cx-half,cy,cz)]);centres.append([cx,cy,cz])
# Join with the exact old edge pair, preserving every subsequent vertex and face.
pts[-2:]=old[join*2:join*2+2];pts+=old[(join+1)*2:]
faces=[(2*i-2,2*i,2*i+1,2*i-1) for i in range(1,len(pts)//2)]
# Concealed gravel shoulders close the exposed ribbon edges into the earth.
for side in [0,1]:
 start=len(pts)
 for i in range(17):
  p=pts[i*2+side];pts.append((p[0]+(.22 if side==0 else -.22),p[1],p[2]-.65))
 for i in range(16):
  face=(i*2+side,start+i,start+i+1,(i+1)*2+side)
  faces.append(face if side==0 else tuple(reversed(face)))
me=bpy.data.meshes.new('Parking_North_Trailhead');me.from_pydata(pts,[],faces);me.update()
assert all(p.normal.z>.98 for p in me.polygons[:16])
mat=bpy.data.materials.new('Parking_Navigation_Gravel');mat.diffuse_color=(.19,.18,.145,1);me.materials.append(mat)
path=bpy.data.objects.new('Parking_North_Trailhead',me);bpy.context.scene.collection.objects.link(path)
bpy.context.view_layer.update();mh.OUT=out;mh.SOURCE=source;mh.EXPECTED=hashlib.sha256(source.read_bytes()).hexdigest()
h=mh.Handoff(bpy.context.scene,bpy.context.evaluated_depsgraph_get(),'fbx')
kind=mh.collision_kind;mh.collision_kind=lambda ob:'surface_prisms' if ob==path else kind(ob)
h.chunk('SM_Parking_Navigation_Furniture',furniture,pivot=(-37,-58,-1),surface='Concrete',role='solid',exposure='Exterior')
h.chunk('SM_Parking_Navigation_Path',[path],surface='Gravel',role='floor',exposure='Exterior')
h.save('handoff')
(out/'plan.json').write_text(json.dumps({'opening':[[-33.6,-52,-1],[-30.4,-52,-1]],'centreline':centres,'preserved_old_cross_section':join,'preserved_remaining_vertices':len(old)-(join+1)*2,'sign_centre':[-35.3,-52.25,.78],'sign_front':[0,-1,0],'arrow_direction':[1,0,0],'reason':'Direct north exit visible from spawn, arrow right toward opening, existing forest path preserved after join.'},indent=2))
print('PARKING_NAVIGATION_BUILD_COMPLETE',flush=True)

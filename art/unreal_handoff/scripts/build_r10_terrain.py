import bpy,json,math
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'revision10';base=json.loads((out.parent/'revision06/terrain_grid.json').read_text())
points=[(-36,-57,-1),(-29,-53,-.9),(-32,-44,-.7),(-25,-35,-.5),(-28,-27,-.3),(-20,-23,-.15),(-12.9,-19,0),(-12.9,-17.3,0)]
path=[]
for i in range(len(points)-1):
 p0=points[max(0,i-1)];p1=points[i];p2=points[i+1];p3=points[min(len(points)-1,i+2)]
 for j in range(16):
  t=j/16;path.append([.5*((2*p1[k])+(-p0[k]+p2[k])*t+(2*p0[k]-5*p1[k]+4*p2[k]-p3[k])*t*t+(-p0[k]+3*p1[k]-3*p2[k]+p3[k])*t*t*t) for k in range(3)])
path.append(list(points[-1]))
def smooth(v):
 t=max(0,min(1,v));return t*t*(3-2*t)
verts=[]
for x,y,z in base['vertices']:
 p=min(path,key=lambda p:(p[0]-x)**2+(p[1]-y)**2);d=math.hypot(x-p[0],y-p[1]);w=1-smooth((d-1.6)/6)
 z=z*(1-w)+(p[2]-.12)*w
 pd=math.hypot(max(-41-x,0,x+31),max(-64-y,0,y+56));w=1-smooth(pd/7);z=z*(1-w)+(-1.14)*w
 # Abrupt lip beyond the occupied decks; preserve the relay shoulder on the right.
 lip=7 if x<20 else 29
 cliff=smooth((y-lip)/10)
 if x>20:cliff*=smooth((y-27)/7)
 z=z*(1-cliff)+(-145+9*math.sin(x*.07)*math.cos(y*.08))*cliff
 verts.append((x,y,z))
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def export(name,vs,fs):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o)
 uv=me.uv_layers.new(name='UVMap')
 for poly in me.polygons:
  poly.use_smooth='Terrain' in name
  for li in poly.loop_indices:
   v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v.x/4,v.y/4)
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
 bpy.ops.export_scene.fbx(filepath=str(out/'fbx'/(name+'.fbx')),use_selection=True,axis_forward='-Y',axis_up='Z',apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',bake_anim=False)
 return o
nx=base['nx'];ny=len(verts)//nx;faces=[]
for j in range(ny-1):
 for i in range(nx-1):
  a=j*nx+i;faces.append((a,a+1,a+nx+1,a+nx))
export('SM_R10_Canyon_Terrain',verts,faces)
rv=[];rf=[]
for i,p in enumerate(path):
 q=path[max(0,i-1)];r=path[min(len(path)-1,i+1)];dx=r[0]-q[0];dy=r[1]-q[1];l=math.hypot(dx,dy)
 for s in [-1,1]:rv.append((p[0]-s*dy/l*1.25,p[1]+s*dx/l*1.25,p[2]))
 if i:rf.append((2*i-2,2*i,2*i+1,2*i-1))
export('SM_R10_Forest_Approach',rv,rf)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'canyon_approach.blend'))
base['vertices']=verts;(out/'terrain_grid.json').write_text(json.dumps(base));(out/'approach_path.json').write_text(json.dumps({'points':path,'width_m':2.5,'length_m':sum(math.dist(a,b) for a,b in zip(path,path[1:]))},indent=2))

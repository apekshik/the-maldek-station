import bpy,json,math
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'revision11';grid=json.loads((out.parent/'revision10/terrain_grid.json').read_text());route=json.loads((out/'layout.json').read_text())['service_route']
def smooth(v):
 t=max(0,min(1,v));return t*t*(3-2*t)
def nearest(x,y):
 best=(1e9,0)
 for a,b in zip(route,route[1:]):
  dx,dy=b[0]-a[0],b[1]-a[1];t=max(0,min(1,((x-a[0])*dx+(y-a[1])*dy)/(dx*dx+dy*dy)));d=math.hypot(x-a[0]-t*dx,y-a[1]-t*dy)
  if d<best[0]:best=(d,a[2]+t*(b[2]-a[2]))
 return best
v=[]
for x,y,z in grid['vertices']:
 dist=math.hypot(max(26-x,0,x-37),max(-26-y,0,y+10));w=1-smooth(dist/5);z=z*(1-w)-1.28*w
 # A rock shoulder interrupts the direct station-to-maintenance sightline.
 bump=7*math.exp(-((x-19)/5)**4-((y+6)/4.5)**4);z=max(z,bump-.2) if bump>.05 else z
 d,r=nearest(x,y);w=1-smooth((d-1.35)/2.2);z=z*(1-w)+(r-.14)*w
 v.append((x,y,z))
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
nx=grid['nx'];ny=len(v)//nx;faces=[]
for j in range(ny-1):
 for i in range(nx-1):
  a=j*nx+i;faces.append((a,a+1,a+nx+1,a+nx))
me=bpy.data.meshes.new('R11_Terrain');me.from_pydata(v,[],faces);me.update();o=bpy.data.objects.new('SM_R11_Terrain',me);bpy.context.collection.objects.link(o)
uv=me.uv_layers.new(name='UVMap')
for poly in me.polygons:
 poly.use_smooth=True
 for li in poly.loop_indices:
  p=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(p.x/4,p.y/4)
o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.wm.save_as_mainfile(filepath=str(out/'terrain.blend'))
bpy.ops.export_scene.fbx(filepath=str(out/'fbx/SM_R11_Terrain.fbx'),use_selection=True,axis_forward='-Y',axis_up='Z',apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',bake_anim=False)
grid['vertices']=v;(out/'terrain_grid.json').write_text(json.dumps(grid))

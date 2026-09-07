import bpy,json,math
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'forest_test';grid=json.loads((out.parent/'revision11/terrain_grid.json').read_text());path=json.loads((out.parent/'revision10/approach_path.json').read_text())['points']
def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)
verts=[]
for x,y,z in grid['vertices']:
 p=min(path,key=lambda p:(x-p[0])**2+(y-p[1])**2);d=math.hypot(x-p[0],y-p[1]);w=(1-smooth((d-11)/9))*(1-smooth((y+24)/5))
 # A continuous forest floor around the route, with shallow asymmetric hummocks.
 target=p[2]-.14+(1-math.exp(-max(0,d-1.5)**2/10))*(.55+.7*math.sin(x*.31)*math.cos(y*.22))
 z=max(z,z*(1-w)+target*w)
 # Retain the parking apron elevation and its join to the footpath.
 pd=math.hypot(max(-41-x,0,x+31),max(-64-y,0,y+56));pw=1-smooth(pd/3);z=z*(1-pw)+(-1.14)*pw
 verts.append((x,y,z))
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
nx=grid['nx'];ny=len(verts)//nx;faces=[]
for j in range(ny-1):
 for i in range(nx-1):
  a=j*nx+i;faces.append((a,a+1,a+nx+1,a+nx))
me=bpy.data.meshes.new('ForestTerrain');me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new('SM_ForestTerrain',me);bpy.context.collection.objects.link(o)
uv=me.uv_layers.new(name='UVMap')
for poly in me.polygons:
 poly.use_smooth=True
 for li in poly.loop_indices:
  p=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(p.x/4,p.y/4)
o.select_set(True);bpy.context.view_layer.objects.active=o
bpy.ops.export_scene.fbx(filepath=str(out/'SM_ForestTerrain.fbx'),use_selection=True,axis_forward='-Y',axis_up='Z',apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',bake_anim=False)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'forest_terrain.blend'));grid['vertices']=verts;(out/'terrain_grid.json').write_text(json.dumps(grid))

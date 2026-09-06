import bpy,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'revision05'
s=json.loads((OUT/'terrain_samples.json').read_text());h=s['heights']
paths=json.loads((ROOT.parents[1]/'art/blender/revision_03/route_points.json').read_text())['paths']
route=[p for path in paths for p in path[::3]]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
xmin,xmax,ymin,ymax=[s[k] for k in ['xmin','xmax','ymin','ymax']];nx=xmax-xmin+1;ny=ymax-ymin+1
def blend(d,width):
 t=min(1,max(0,d/width));return 1-t*t*(3-2*t)
def base(x,y):
 u=(x-xmin)/2;v=(y-ymin)/2;i=min(len(h[0])-2,int(u));j=min(len(h)-2,int(v));a=u-i;b=v-j
 return h[j][i]*(1-a)*(1-b)+h[j][i+1]*a*(1-b)+h[j+1][i]*(1-a)*b+h[j+1][i+1]*a*b
verts=[];faces=[]
for y in range(ymin,ymax+1):
 for x in range(xmin,xmax+1):
  ground=base(x,y)
  d=math.hypot(max(-24-x,0,x-20),max(-21-y,0,y-12));w=blend(d,28)
  z=ground+(-.145-ground)*w
  p=min(route,key=lambda p:(p[0]-x)**2+(p[1]-y)**2);pd=math.hypot(p[0]-x,p[1]-y)
  # A broad wooded shoulder supports the relay loop, not a thin elevated strip.
  sd=math.hypot(max(21-x,0,x-53),max(-8-y,0,y-27));sw=blend(sd,42)
  sw*=min(1,max(0,(x-18)/5))
  target=p[2]-.18 + .22*math.sin(x*.19)*math.cos(y*.15)*min(1,pd/8)
  shoulder=ground+(target-ground)*sw
  z=max(z,shoulder,ground-.18)
  z=max(z,z+(p[2]-.12-z)*blend(max(0,pd-1.7),6))
  if 45.5<=x<=50.5 and 10.5<=y<=15.5:z=2.65
  verts.append((x,y,z))
for j in range(ny-1):
 for i in range(nx-1):
  a=j*nx+i;faces.append((a,a+1,a+nx+1,a+nx))
me=bpy.data.meshes.new('Complete_Route_Terrain');me.from_pydata(verts,[],faces);me.update()
o=bpy.data.objects.new('SM_R05_Local_Terrain',me);bpy.context.collection.objects.link(o)
uv=me.uv_layers.new(name='UVMap')
for poly in me.polygons:
 poly.use_smooth=True
 for li in poly.loop_indices:
  v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v.x/4,v.y/4)
o.select_set(True);bpy.context.view_layer.objects.active=o
bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'complete_route_terrain.blend'))
bpy.ops.export_scene.fbx(filepath=str(OUT/'fbx/SM_R05_Local_Terrain.fbx'),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',bake_anim=False,mesh_smooth_type='FACE')
(OUT/'terrain_build.json').write_text(json.dumps({'vertices':len(verts),'triangles':len(faces)*2,'bounds':[xmin,xmax,ymin,ymax],'route_samples':len(route)},indent=2))


"""Blender: extend the valley mesh and join its visible perimeter to native ground."""
import bpy,json,math,sys
from pathlib import Path
from mathutils import Matrix
sys.path.insert(0,str(Path(__file__).resolve().parent))
from gorge_shape import height,smooth
b=Path(__file__).resolve().parents[1];out=b/'gorge';o=json.loads((b.parent/'working_level_report.json').read_text())['station_origin']
edge=json.loads((out/'edge_probe.json').read_text());bb=edge['bounds'];stride=bb[2]-bb[0]+1
baseline={(x,y):edge['current'][(y-bb[1])*stride+x-bb[0]] for y in range(bb[1],bb[3]+1) for x in range(bb[0],bb[2]+1)}
original=json.loads((out/'native_probe.json').read_text());r=original['bounds'];rw=r[2]-r[0]+1
for y in range(r[1],r[3]+1):
 for x in range(r[0],r[2]+1):baseline[x,y]=original['merged'][(y-r[1])*rw+x-r[0]]
def gaia(x,y):
 u=(o[0]+105812)/100-x;v=(o[1]+138209)/100+y;i=math.floor(u);j=math.floor(v);a=u-i;c=v-j
 raw=(1-c)*((1-a)*baseline[i,j]+a*baseline[i+1,j])+c*((1-a)*baseline[i,j+1]+a*baseline[i+1,j+1])
 return (23763+(raw-32768)*100/128-o[2])/100
def joined(old,x,y):
 z=height(old,x,y)
 side=1-smooth(min(x+96,112-x)/18)
 front=smooth((y-142)/28)
 rear=1-smooth((y+80)/10)
 blend=max(side,front,rear)
 return z+(gaia(x,y)-z)*blend
old=json.loads((b/'forest_refine/terrain_grid.json').read_text())['vertices']
lookup={(round(x,3),round(y,3)):joined(z,x,y) for x,y,z in old}
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=str(b/'forest_refine/SM_Forest_Refined_Terrain.fbx'))
obj=next(v for v in bpy.context.scene.objects if v.type=='MESH')
vs=[]
for v in obj.data.vertices:
 p=obj.matrix_world@v.co;vs.append((p.x,p.y,lookup[round(p.x,3),round(p.y,3)]))
faces=[tuple(p.vertices) for p in obj.data.polygons];idx={(round(x,3),round(y,3)):i for i,(x,y,z) in enumerate(vs)}
for y in range(97,171):
 for x in range(-96,113):
  idx[x,y]=len(vs);vs.append((x,y,joined(gaia(x,y),x,y)))
 for x in range(-96,112):faces.extend([(idx[x,y-1],idx[x+1,y-1],idx[x+1,y]),(idx[x,y-1],idx[x+1,y],idx[x,y])])
me=bpy.data.meshes.new('StationGorgeJoined');me.from_pydata(vs,[],faces);me.update();obj.data=me;obj.matrix_world=Matrix.Identity(4);obj.name='SM_Station_Gorge_Terrain'
me.materials.append(bpy.data.materials.new('Gorge_Surface'))
uv=me.uv_layers.new(name='UVMap')
for p in me.polygons:
 p.use_smooth=True
 for li in p.loop_indices:
  v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v.x/4,v.y/4)
bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
bpy.ops.export_scene.fbx(filepath=str(out/'SM_Station_Gorge_Terrain.fbx'),use_selection=True,axis_forward='-Y',axis_up='Z',apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',bake_anim=False)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'station_gorge.blend'))
(out/'terrain_grid.json').write_text(json.dumps({'vertices':vs}))
errors=[abs(z-gaia(x,y)) for x,y,z in vs if x in [-96,112] or y in [-80,170]]
assert max(errors)<.0001
(out/'edge_blend.json').write_text(json.dumps({'vertices':len(vs),'front_extension_m':74,'perimeter_samples':len(errors),'max_perimeter_error_m':max(errors)},indent=2));print('JOINED',len(vs),max(errors))

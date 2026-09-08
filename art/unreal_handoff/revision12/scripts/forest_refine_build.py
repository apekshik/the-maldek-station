"""Blender: broaden the old ten-metre canyon cut; preserve occupied ground."""
import bpy,json,math,hashlib,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from forest_refine_shape import height
b=Path(__file__).resolve().parents[1];out=b/'forest_refine';out.mkdir(exist_ok=True)
src=b/'parking/terrain_grid.json';data=json.loads(src.read_text());old=data['vertices']
path=json.loads((b.parent/'revision10/approach_path.json').read_text())['points']
def smooth(t):
 t=max(0,min(1,t));return t*t*(3-2*t)
vs=[];changes=[]
for x,y,z in old:
 nz=height(z,x,y)
 if -53<y<-21 and not (-48<x<-26 and -68<y<-48):
  p=min(path,key=lambda p:(x-p[0])**2+(y-p[1])**2);d=math.hypot(x-p[0],y-p[1])
  w=smooth((d-1.85)/2.6)*(1-smooth((d-7)/7))*smooth((y+53)/5)*(1-smooth((y+26)/5))
  hummock=.8+1.4*(.5+.5*math.sin(x*.31+y*.19)*math.cos(y*.27-x*.12))
  nz+=min(2.3,max(0,p[2]+hummock-nz))*w
 delta=nz-z
 vs.append((x,y,nz))
 if delta>.001:changes.append([x,y,z,nz])
# The original grid contains a finer rectangular station patch, so reconstruct
# its original topology from the actual exported parking terrain, not nx*ny.
fbx=b/'parking/fbx/SM_VF10_Parking_Terrain.fbx'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=str(fbx))
objects=[o for o in bpy.context.scene.objects if o.type=='MESH' and not o.name.startswith('UCX_')]
assert len(objects)==1,[o.name for o in objects]
o=objects[0];o.name='SM_Forest_Refined_Terrain'
# FBX round trip retains station local metres and triangle topology.
lookup={(round(x,3),round(y,3)):z for x,y,z in vs}
maxerr=0
for v in o.data.vertices:
 p=o.matrix_world@v.co;key=(round(p.x,3),round(p.y,3));assert key in lookup,(tuple(p),key)
 p.z=lookup[key];v.co=o.matrix_world.inverted()@p
for p in o.data.polygons:p.use_smooth=True
uv=o.data.uv_layers.active or o.data.uv_layers.new(name='UVMap')
for p in o.data.polygons:
 for li in p.loop_indices:
  v=o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(v.x/4,v.y/4)
bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
bpy.ops.export_scene.fbx(filepath=str(out/'SM_Forest_Refined_Terrain.fbx'),use_selection=True,axis_forward='-Y',axis_up='Z',apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',bake_anim=False)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'forest_refined.blend'))
(out/'terrain_grid.json').write_text(json.dumps({'vertices':vs}))
(out/'build.json').write_text(json.dumps({'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'changed_vertices':len(changes),'maximum_raise_m':max(r[3]-r[2] for r in changes),'no_lowering':True,'path_clear_strip_half_width_m':1.85,'bank_max_raise_m':2.3,'changes':changes},indent=2))
print('FOREST_TERRAIN_BUILT',len(changes),flush=True)

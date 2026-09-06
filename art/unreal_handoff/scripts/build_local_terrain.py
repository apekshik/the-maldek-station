"""Supplemental terrain apron fitted to sampled UE landscape, without editing Gaea."""
import bpy,json,math
from pathlib import Path
OUT=Path(__file__).resolve().parents[1]
samples=json.loads((OUT/'terrain_samples.json').read_text());heights=samples['heights']
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def base(x,y):
 u=(x+64)/2;v=(y+64)/2;i=min(63,int(u));j=min(63,int(v));a=u-i;b=v-j
 return heights[j][i]*(1-a)*(1-b)+heights[j][i+1]*a*(1-b)+heights[j+1][i]*(1-a)*b+heights[j+1][i+1]*a*b
verts=[];faces=[];weights=[]
for y in range(-64,65):
 for x in range(-64,65):
  dx=max(-24-x,0,x-20);dy=max(-21-y,0,y-12);d=math.sqrt(dx*dx+dy*dy)
  # Broad shoulders support tree planting; a shorter north falloff opens the cable departure.
  falloff=19 if y>12 else 28
  t=min(1,d/falloff);influence=1-t*t*(3-2*t)
  ground=base(x,y)
  irregular=.6*math.sin(x*.21)*math.cos(y*.19)+.25*math.sin((x+y)*.41)
  target=-.12+irregular*(1-influence)
  z=max(ground-.15,ground+(target-ground)*influence)-.025
  verts.append((x,y,z));weights.append(influence)
for j in range(128):
 for i in range(128):
  a=j*129+i;faces.append((a,a+1,a+130,a+129))
me=bpy.data.meshes.new('Station_Local_Terrain');me.from_pydata(verts,[],faces);me.update()
o=bpy.data.objects.new('SM_R04_Local_Terrain',me);bpy.context.collection.objects.link(o)
uv=me.uv_layers.new(name='UVMap')
for p in me.polygons:
 p.use_smooth=True
 for li in p.loop_indices:
  v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v.x/4,v.y/4)
mat=bpy.data.materials.new('R04_Local_Terrain');mat.diffuse_color=(.33,.35,.34,1);me.materials.append(mat)
o.select_set(True);bpy.context.view_layer.objects.active=o
bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'station_local_terrain.blend'))
bpy.ops.export_scene.fbx(filepath=str(OUT/'fbx/SM_R04_Local_Terrain.fbx'),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',bake_anim=False,mesh_smooth_type='FACE')
(OUT/'local_terrain_report.json').write_text(json.dumps({'size_m':128,'vertices':len(verts),'triangles':len(faces)*2,'ground_target_m':-.145,'origin':samples['origin'],'landscape_samples':4225,'source_landscape_modified':False},indent=2))

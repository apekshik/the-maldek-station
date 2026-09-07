"""Parking-only FBX handoff. No station, car, or terrain replacement is exported."""
import bpy,sys,json,hashlib,math
from pathlib import Path
OUT=Path(__file__).resolve().parents[1];ROOT=OUT.parents[2]
sys.path.insert(0,str(ROOT/'art/unreal_handoff/revision12/scripts'))
import mesh_handoff as mh
source=OUT/'Maldek_Parking_Arrival.blend'
bpy.ops.wm.open_mainfile(filepath=str(source));bpy.context.view_layer.update()
mh.OUT=ROOT/'art/unreal_handoff/revision12/parking';mh.SOURCE=source;mh.EXPECTED=hashlib.sha256(source.read_bytes()).hexdigest()
h=mh.Handoff(bpy.context.scene,bpy.context.evaluated_depsgraph_get(),'fbx')
for cn,name,surface,role in [('VF10_01_Parking_Ground','Ground','Gravel','floor'),('VF10_02_Parking_Furniture','Furniture','Concrete','solid'),('VF10_03_Rock_Clusters','Rock_Clusters','Soil','solid')]:
 objects=list(bpy.data.collections[cn].objects)
 # Gravel provides walk collision. Detail hardware stays passable.
 if name=='Furniture':
  for o in objects:
   if any(t in o.name for t in ['Bench_seat','Sign_post','Edge_curb','Rear_curb','East_curb','North_curb']):o['collision']=True
 h.chunk('SM_VF10_Parking_'+name,objects,pivot=(-37,-58,-1),surface=surface,role=role,exposure='Exterior')
# Merge local parking earthworks onto the service task's current combined terrain.
terrain=bpy.data.objects['R11_Current_Terrain']
gridpath=ROOT/'art/unreal_handoff/revision13/terrain_grid.json'
assert gridpath.exists(),'Finish service terrain export before parking handoff'
base=json.loads(gridpath.read_text())['vertices'];vs=[];changed=[]
for x,y,z in base:
 d=math.hypot(max(-44.6-x,0,x+29.9),max(-64.1-y,0,y+51.9))
 value=z+(-1.34-z)*max(0,1-d/2) if d<2 else z
 vs.append((x,y,value))
 if abs(value-z)>1e-6:changed.append([x,y,z,value])
me=bpy.data.meshes.new('VF10_Terrain');me.from_pydata(vs,[],[tuple(p.vertices) for p in terrain.data.polygons]);me.materials.append(terrain.data.materials[0])
o=bpy.data.objects.new('VF10_Terrain',me);h.source.collection.objects.link(o)
# Replace only the beginning of the approach ribbon swallowed by the expanded lot.
with bpy.data.libraries.load(str(ROOT/'art/unreal_handoff/revision12/forest_arrival_export.blend'),link=False) as (src,dst):
 assert 'R12_Forest_Approach_Aligned' in src.objects;dst.objects=['R12_Forest_Approach_Aligned']
old=dst.objects[0];pts=[tuple(v.co) for v in old.data.vertices][32:]
# Keep the connector wholly east of the lot until it clears the north edge.
pts=[(max(x,-30),y,z) if y<-52 else (x,y,z) for x,y,z in pts]
pts=[(-30,-55.8,-1),(-30,-52.8,-1)]+pts
me2=bpy.data.meshes.new('VF10_Path');me2.from_pydata(pts,[],[(2*i-2,2*i,2*i+1,2*i-1) for i in range(1,len(pts)//2)]);me2.materials.append(old.data.materials[0])
path=bpy.data.objects.new('VF10_Forest_Connector',me2);h.source.collection.objects.link(path)
kind=mh.collision_kind;mh.collision_kind=lambda ob:'surface_prisms' if ob==path else kind(ob)
bpy.context.view_layer.update();h.deps=bpy.context.evaluated_depsgraph_get()
h.chunk('SM_VF10_Parking_Forest_Connector',[path],role='floor',surface='Gravel',exposure='Exterior')
r=h.chunk('SM_VF10_Parking_Terrain',[o],role='terrain',surface='Soil');r['complex_collision']=True
m=h.save('handoff');m['terrain_source_sha256']=hashlib.sha256(gridpath.read_bytes()).hexdigest();m['terrain_changes']=changed;m['preserved_path_from_cross_section']=16
(mh.OUT/'handoff.json').write_text(json.dumps(m,indent=2));(mh.OUT/'terrain_grid.json').write_text(json.dumps({'vertices':vs}))

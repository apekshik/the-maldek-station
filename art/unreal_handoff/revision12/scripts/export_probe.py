"""Export actual VF07 entry, grating, plate, tread and glass, plus an asymmetric metre probe."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mesh_handoff import *
source,deps=load_source();handoff=Handoff(source,deps,'probe_fbx')
# A one-metre cube plus an offset marker exposes incorrect scale, handedness and axes.
probe_objects=[]
for name,p,d in [('MetreCube',(0,0,0),(1,1,1)),('AxisMarker',(2,3,5),(.5,.5,.5))]:
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.name=name;o.scale=d;o['collision']=True
 mat=bpy.data.materials.get('VF06_Safety_ochre');o.data.materials.append(mat);probe_objects.append(o)
deps=bpy.context.evaluated_depsgraph_get();handoff.deps=deps
handoff.chunk('SM_R12_OrientationProbe',probe_objects,role='probe')
control=bpy.data.collections['VF06_Control']
door=[]
for o in control.objects:
 if o.type!='MESH' or o.hide_render:continue
 a,b=bounds(o)
 if a[1]<.2 and b[1]>-.2 and a[0]>-4.5 and b[0]<-2.15 and not o.name.startswith('Clear_glazing'):door.append(o)
handoff.chunk('SM_R12_Probe_Door',door,pivot=(-3.3,0,4),role='solid')
glass=next(o for o in control.objects if o.name=='Clear_glazing')
a,b=bounds(glass);handoff.chunk('SM_R12_Probe_Glass',[glass],pivot=[(a[i]+b[i])/2 for i in range(3)],role='glass')
deck=bpy.data.collections['VF07_Public_Deck']
for name,prefix,role in [('Grating','Open_grating_tile','grating'),('Plate','Flush_steel_plate','floor')]:
 o=next(o for o in deck.objects if o.name.startswith(prefix));a,b=bounds(o)
 handoff.chunk('SM_R12_Probe_'+name,[o],pivot=[(a[0]+b[0])/2,(a[1]+b[1])/2,b[2]],role=role)
o=next(o for o in bpy.data.collections['VF07_Sideways_Arrival'].objects if o.name.startswith('Open_grating_tile'))
a,b=bounds(o);handoff.chunk('SM_R12_Probe_Tread',[o],pivot=[(a[0]+b[0])/2,(a[1]+b[1])/2,b[2]],role='grating')
handoff.save('probe_manifest')

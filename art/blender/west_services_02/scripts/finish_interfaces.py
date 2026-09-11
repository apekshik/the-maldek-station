import bpy,math,json
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1];F=OUT/'Maldek_Station_West_Integrated.blend'
bpy.ops.wm.open_mainfile(filepath=str(F));s=bpy.context.scene;c=bpy.data.collections['WS_SHARED_ROOF']
# Exhaust package is immutable. Resolve the common roof interface in this integration copy.
roof=bpy.data.objects['WS_RoofPanel']
bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=.13,depth=1.3,location=(-35.2,-5.3,8.1));cut=bpy.context.object
bpy.context.view_layer.objects.active=roof;mod=roof.modifiers.new('Exhaust roof bore','BOOLEAN');mod.solver='EXACT';mod.operation='DIFFERENCE';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
# Replace only the seam intersecting riser/clamp with two terminated runs.
ob=bpy.data.objects['WS02_RoofSeam'];bpy.data.objects.remove(ob,do_unlink=True)
def rod(n,a,b,r=.018):
 a=Vector(a);b=Vector(b);v=(b-a).normalized();u=v.cross(Vector((0,1,0))).normalized();w=v.cross(u);vs=[p+r*(math.cos(i*math.tau/12)*u+math.sin(i*math.tau/12)*w) for p in [a,b] for i in range(12)];fs=[tuple(reversed(range(12))),tuple(range(12,24))]+[(i,(i+1)%12,(i+1)%12+12,i+12) for i in range(12)];me=bpy.data.meshes.new(n);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(n,me);c.objects.link(o);me.materials.append(bpy.data.materials['WS02_Petrol_Paint'])
def z(x):return 7.38+(x+37.85)*(.77/3.4)+.16
for a,b in [(-37.85,-35.46),(-34.94,-34.45)]:rod('WS02_Seam_terminated',(a,-5.37,z(a)+.01),(b,-5.37,z(b)+.01))
# Closed annular tapered roof flashing: open central bore, not a solid cylinder.
vs=[];N=48
for radius,top in [(.145,False),(.13,True),(.115,True),(.13,False)]:
 for i in range(N):
  x=-35.2+radius*math.cos(i*math.tau/N);y=-5.3+radius*math.sin(i*math.tau/N);vs.append((x,y,8.18 if top else z(x)+.002))
fs=[]
for j in range(4):
 for i in range(N):fs.append((j*N+i,j*N+(i+1)%N,((j+1)%4)*N+(i+1)%N,((j+1)%4)*N+i))
me=bpy.data.meshes.new('WS02_ExhaustRoofFlashing');me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(me.name,me);c.objects.link(o);me.materials.append(bpy.data.materials['WS02_Galvanized'])
# Top standoff has a small roof-mounted socket instead of terminating in open air.
rod('WS02_StandoffRoofSocket',(-35.2,-4.98,z(-35.2)+.01),(-35.2,-4.98,8.23),.05)
# Guard the full low-headroom portion from the lower platform; preserve stair access above.
for ob in list(bpy.data.collections['WS02_WRAP_PLATFORM'].objects):
 if ob.name.startswith('WS02_UnderStair') and ob.type=='MESH':
  # Stretch the endpoint side only, including the existing end post/foot, along the underflight edge.
  for v in ob.data.vertices:
   if v.co.x>-35.1:v.co.x+=1.8
bpy.ops.wm.save_as_mainfile(filepath=str(F))
(OUT/'roof_patch.json').write_text(json.dumps({'roof_object':'WS_RoofPanel','bore_center':[-35.2,-5.3,8.1],'bore_radius':.13,'retired_seam':'WS02_RoofSeam','new_flashing':'WS02_ExhaustRoofFlashing','package_geometry_modified':False,'intentional_contacts':['WSE_Riser_standoff.003 embeds into the gable as a wall fixing.','WSE_Riser_standoff.004 seats in WS02_StandoffRoofSocket.'],'underflight_guard':'Extended eastern endpoint 1.8m; lower walking route runs around north perimeter.'},indent=2))



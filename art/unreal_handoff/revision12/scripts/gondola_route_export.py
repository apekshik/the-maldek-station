"""Blender: approved tower geometry adapted to the surveyed feet and cable grade."""
import bpy,json,math,bisect
from pathlib import Path
from mathutils import Vector,Matrix
b=Path(__file__).resolve().parents[1];out=b/'gondola_route';fbx=out/'fbx';fbx.mkdir(exist_ok=True)
repo=b.parents[2];plan=json.loads((out/'plan.json').read_text());survey=json.loads((out/'survey.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(repo/'art/blender/pylon_study_03/Maldek_Tapered_Central_Pylon.blend'))
source=list(bpy.data.collections['PYLON | export geometry'].objects);deps=bpy.context.evaluated_depsgraph_get()
points=plan['rope_samples_m'];ys=[p[1] for p in points]
def rope(y):
 i=max(0,min(len(points)-2,bisect.bisect_right(ys,y)-1));a,c=points[i:i+2];t=(y-a[1])/(c[1]-a[1]);return a[2]+t*(c[2]-a[2])
def slope(y):return (rope(y+.05)-rope(y-.05))/.1
col=bpy.data.collections.new('ROUTE | installed variants');bpy.context.scene.collection.children.link(col)
exported=[]
def export(objects,name):
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.select_set(True)
 bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();o=bpy.context.object;o.name=name
 bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
 bpy.ops.export_scene.fbx(filepath=str(fbx/(name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,add_leaf_bones=False,bake_anim=False)
 exported.append({'name':name,'vertices':len(o.data.vertices),'materials':[m.name for m in o.data.materials],'bounds':[list(o.matrix_world@Vector(v)) for v in o.bound_box]})
 o.hide_render=True;o.hide_set(True);return o
for index,n in enumerate(plan['nodes'][1:-1],1):
 objects=[];row=survey['samples'][n['index']];extra=n['height']-42.327
 for src in source:
  if src.type not in {'MESH','FONT','CURVE'}:continue
  if src.name.startswith('Ladder_rung'):continue
  if src.type=='FONT' and src.name.startswith('Tower_number'):
   src.data.body='%02d'%index;bpy.context.view_layer.update()
  me=bpy.data.meshes.new_from_object(src.evaluated_get(deps),depsgraph=deps);me.transform(src.matrix_world)
  ob=bpy.data.objects.new(src.name+'_route',me);col.objects.link(ob);objects.append(ob)
  centre=sum((v.co for v in me.vertices),Vector())/max(1,len(me.vertices))
  wheel=any(k in src.name for k in ['Rubber_sheave','Sheave_side_disc','Sheave_hub','Sheave_axle'])
  if wheel:
   old_a=(12*9.81*300/(2*250000))/(2*3.7);yp=centre.y
   for _ in range(8):
    os=-2*old_a*yp;yp=centre.y-os/math.sqrt(1+os*os)*.307
   ss=slope(n['y']+yp);newcentre=Vector((centre.x,yp+ss/math.sqrt(1+ss*ss)*.307,rope(n['y']+yp)-n['ground']-.307/math.sqrt(1+ss*ss)))
   for v in me.vertices:v.co+=newcentre-centre
  else:
   for v in me.vertices:
    x,y,z=v.co;fraction=max(0,min(1,(z-1.34)/(39-1.34)))
    # Blender X is mirrored into Unreal X. Foot caps follow their own sampled ground.
    foot=(row['right' if x<0 else 'left'][2]/100-n['ground'])
    v.co.z=z+extra*fraction+foot*(1-fraction)+n['grade']*y*max(0,min(1,(z-39)/3.327))
  me.update()
 # Rebuild the access rungs at 30 cm spacing instead of stretching their spacing.
 def ladder_point(z):
  t=(z-1.34)/(43.55-1.34);xx=-6.2+1.95*t;yy=.975+(.45-.975)*t+.24;f=max(0,min(1,(z-1.34)/(39-1.34)));foot=row['right'][2]/100-n['ground']
  return Vector((xx,yy,z+extra*f+foot*(1-f)+n['grade']*yy*max(0,min(1,(z-39)/3.327))))
 low=ladder_point(1.6);high=ladder_point(42.4);count=math.ceil((high-low).length/.3)
 for j in range(count+1):
  p=low.lerp(high,j/count);bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=.019,depth=.46,location=p,rotation=(0,math.pi/2,0));ob=bpy.context.object;ob.data.materials.append(bpy.data.materials['Pylon_Galvanized']);objects.append(ob)
 export(objects,'SM_Gondola_Pylon_%02d'%index)
# Entire route is exported at a small local origin for precision, metres -> FBX centimetres once.
origin=Vector(plan['rope_samples_m'][0]);dark=bpy.data.materials['Pylon_Graphite']
def curve(name,pts,radius):
 c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.bevel_depth=radius;c.bevel_resolution=2;c.resolution_u=1;c.use_fill_caps=True
 sp=c.splines.new('POLY');sp.points.add(len(pts)-1)
 for p,co in zip(sp.points,pts):p.co=(*co,1)
 o=bpy.data.objects.new(name,c);col.objects.link(o);c.materials.append(dark)
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH');return bpy.context.object
for lane,dx,dz in [('Passenger',0,0),('Return',-2.35,2.955)]:
 pts=[(-(p[0]-origin.x)+dx,p[1]-origin.y,p[2]-origin.z+dz) for p in points]
 export([curve('Cable_'+lane,pts,.032)],'SM_Gondola_Cable_'+lane)
# Side-clearing hanger adapter, in the production cabin's floor-origin frame.
adapter=[]
for a,c in [((0,.05,3.96),(.62,.05,3.96)),((.62,.05,3.96),(.62,.05,6.09)),((.62,.05,6.09),(-.21,.05,6.09)),((-.21,.05,6.09),(-.21,.05,5.927))]:
 a=Vector(a);c=Vector(c);d=c-a
 bpy.ops.mesh.primitive_cube_add(size=1,location=(a+c)/2);o=bpy.context.object;o.dimensions=(.06,.08,d.length) if abs(a.x+.21)<.001 and abs(c.x+.21)<.001 else (.14,.20,d.length);o.rotation_euler=d.to_track_quat('Z','Y').to_euler();bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(dark);adapter.append(o)
export(adapter,'SM_Gondola_Hanger_Adapter')
# Hide study objects in the editable handoff; keep them available as the untouched reference.
for o in bpy.context.scene.objects:
 if o.name not in col.objects:o.hide_render=True
bpy.ops.wm.save_as_mainfile(filepath=str(out/'Maldek_Route_Installed_Variants.blend'))
(out/'exports.json').write_text(json.dumps(exported,indent=2));print('ROUTE_EXPORT_COMPLETE',len(exported))

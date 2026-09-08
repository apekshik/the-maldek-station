"""Blender: approved tower geometry adapted to the surveyed feet and cable grade."""
import bpy,json,math,bisect
from pathlib import Path
from mathutils import Vector,Matrix
b=Path(__file__).resolve().parents[1];out=b/'gondola_route';fbx=b/'gondola_mechanism'/'fbx';fbx.mkdir(exist_ok=True)
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
base_export=export
rotor_rows=[];common={}
def export(objects,name):
 if not name.startswith('SM_Gondola_Pylon'):return base_export(objects,name)
 static=[];wheels={}
 for ob in objects:
  moving=ob.name.startswith(('Rubber_sheave','Sheave_side_disc','Sheave_hub','Return_rope_roller','Return_roller_flange'))
  if not moving:static.append(ob);continue
  center=sum((v.co for v in ob.data.vertices),Vector())/len(ob.data.vertices)
  lane='Return' if ob.name.startswith('Return_') else 'Passenger'
  key=(lane,round(center.y,2));wheels.setdefault(key,[]).append(ob)
 for (lane,y),parts in wheels.items():
  liner=next(o for o in parts if o.name.startswith(('Rubber_sheave','Return_rope_roller')))
  center=sum((v.co for v in liner.data.vertices),Vector())/len(liner.data.vertices)
  key='SM_GM_PylonRoller_'+lane
  rotor_rows.append({'mesh':key,'tower':int(name[-2:]),'center':list(center),'lane':lane,'radius_cm':30.7})
  if lane not in common:
   for ob in parts:
    for vert in ob.data.vertices:vert.co-=center
   # Visible hub fasteners make roller motion readable while retaining the real round liner.
   for side in [-1,1]:
    for j in range(5):
     angle=j*math.tau/5
     bpy.ops.mesh.primitive_cylinder_add(vertices=6,radius=.022,depth=.016,location=(side*.14,.19*math.cos(angle),.19*math.sin(angle)),rotation=(0,math.pi/2,0))
     bolt=bpy.context.object;bolt.data.materials.append(bpy.data.materials['Pylon_Graphite']);parts.append(bolt)
   base_export(parts,key);common[lane]=True
  else:
   for ob in parts:bpy.data.objects.remove(ob,do_unlink=True)
 return base_export(static,name.replace('SM_Gondola_','SM_GM_'))
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

(b/'gondola_mechanism/pylons.json').write_text(json.dumps({'meshes':exported,'rotors':rotor_rows},indent=2))

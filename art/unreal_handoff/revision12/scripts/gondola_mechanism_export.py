"""Fit approved study to installed rope tangents; separate moving parts at true pivots."""
import bpy,json,math,sys
from pathlib import Path
from mathutils import Vector,Matrix
b=Path(__file__).resolve().parents[1];repo=b.parents[2];out=b/'gondola_mechanism';fbx=out/'fbx';fbx.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(repo/'art/blender/terminal_drive_study_01/Maldek_Terminal_Drive_Study.blend'))
deps=bpy.context.evaluated_depsgraph_get();original=list(bpy.context.scene.objects);rows=[]
mapping={'Aged grey green paint':'Pylon_Faded_Grey_Green','Graphite cast iron':'Pylon_Graphite','Dull machined steel':'Pylon_Galvanized','Oxidized joints':'Pylon_Joint_Patina','Faded ochre guards':'Pylon_Safety_Amber','Rope and liner':'Pylon_Sheave_Liner','Concrete':'Pylon_Concrete','Lettering':'Pylon_Lettering'}
def export(objects,name,pivot,**meta):
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.select_set(True)
 bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();o=bpy.context.object;o.name=name
 for vert in o.data.vertices:vert.co-=Vector(pivot)
 if meta.get('part')=='Wheel':assert max(v.co.length for v in o.data.vertices)<2.5,'Wheel contains geometry from another terminal'
 o.data.update();o.location=(0,0,0)
 bpy.ops.export_scene.fbx(filepath=str(fbx/(name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,bake_anim=False)
 rows.append({'name':name,'pivot':list(pivot),'materials':[m.name for m in o.data.materials],**meta});o.hide_render=True;o.hide_set(True)
 return o
def converted(src,terminal):
 me=bpy.data.meshes.new_from_object(src.evaluated_get(deps),depsgraph=deps);me.transform(src.matrix_world)
 bb=[v.co for v in me.vertices];lo=min(v.z for v in bb);hi=max(v.z for v in bb)
 for v in me.vertices:
  x,y,z=v.co
  if terminal=='Millford':
   # Lower machine bed reaches the existing lower drive floor; upper wheel is unchanged.
   if hi<2.0:z-=3.4045
   elif lo<2.0:z-=3.4045*max(0,min(1,(7-z)/5.4))
   # Raise the lower machinery above the retained 0.9 m perimeter upstand.
   if src.name.startswith(('Finned electric motor','Cooling fin','Motor terminal box','Input shaft','SERVICE BRAKE','Service brake','Motor saddle','Lower reducer')):z+=.30
   elif src.name=='Drive concrete bed':z+=.375 if v.co.z>.1 else 0
   elif src.name=='Vertical drive shaft':z+=.30*max(0,min(1,(7-v.co.z)/5.85))
   v.co=(x,y-5,z-6.5225)
  else:
   if hi<2.0:z-=2.4
   elif lo<2.0:z-=2.4*max(0,min(1,(2.1-z)/2.1))
   v.co=(x-11.175,-y+5,z-3.5225)
 for i,m in enumerate(me.materials):
  key=mapping.get(m.name,'Pylon_Graphite');me.materials[i]=bpy.data.materials.get(key) or bpy.data.materials.new(key)
 ob=bpy.data.objects.new(src.name+'_installed',me);bpy.context.collection.objects.link(ob);return ob
def support(name,p,size):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.name=name;o.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(bpy.data.materials['Graphite cast iron']);original.append(o)
for dx in [-.32,.32]:
 for y in [-.29,.29]:support('Lower reducer mounting foot',(-2.2316+dx,y,.5125),(.17,.17,.375))
support('Upper gearbox support shelf',(-3.05,0,6.58),(2.05,.9,.17))
bpy.context.view_layer.update()
groups={t:{'Frame':[],'Wheel':[],'Shaft':[],'Input':[]} for t in ['Millford','Maldek']}
for src in original:
 if src.type not in {'MESH','CURVE'} or src.name=='Studio floor':continue
 # Curves store world-sized control points with an origin at zero. Classify by bounds.
 center=sum((src.matrix_world@Vector(v) for v in src.bound_box),Vector())/8
 terminal='Maldek' if center.x>6 else 'Millford'
 if 'continuous rope' in src.name:continue # replaced by a single continuous, unwrapped loop below
 part='Frame'
 if src.name.startswith(('DRIVE','RETURN')) or src.name in ['Bullwheel SAFETY BRAKE disc','Bullwheel output shaft','Continuous return axle']:part='Wheel'
 elif src.name=='Vertical drive shaft':part='Shaft'
 elif src.name in ['Input shaft','SERVICE BRAKE disc']:part='Input'
 groups[terminal][part].append(converted(src,terminal))
for terminal,g in groups.items():
 index=0 if terminal=='Millford' else 1
 for part,objects in g.items():
  if not objects:continue
  pivot=(-1.175,(-5 if index==0 else 5),1.4775) if part=='Wheel' else ((-2.2316,-5,-8.477) if part=='Shaft' else (-1.38,-5,-8.477)) if part in ['Input','Shaft'] else (0,0,0)
  export(objects,'SM_GM_'+terminal+'_'+part,pivot,terminal=index,part=part,axis=[.782674,0,-.622432] if part=='Wheel' else [0,0,1] if part=='Shaft' else [1,0,0],ratio=1 if part=='Wheel' else 8 if part=='Shaft' else 84.7224)
# A physical tube with UV.x in loop-distance metres and UV.y around circumference.
plan=json.loads((b/'gondola_route/plan.json').read_text());P=[Vector(p) for p in plan['rope_samples_m']];origin=P[0].copy();P=[Vector((-(p.x-origin.x),p.y-origin.y,p.z-origin.z)) for p in P];D=Vector((-2.35,0,2.955));u=-D.normalized();R=D.length/2
far=P[-1]+D/2+Vector((0,5,0));near=D/2+Vector((0,-5,0))
points=P+[far+u*R*math.cos(t)+Vector((0,1,0))*R*math.sin(t) for t in [i*math.pi/96 for i in range(97)]]+[p+D for p in reversed(P)]+[near-u*R*math.cos(t)+Vector((0,-1,0))*R*math.sin(t) for t in [i*math.pi/96 for i in range(97)]]+[P[0]]
vertices=[];faces=[];uv=[];distance=0.;sides=12
for i,p in enumerate(points):
 if i:distance+=(p-points[i-1]).length
 tangent=(points[min(i+1,len(points)-1)]-points[max(0,i-1)]).normalized();radial=Vector((1,0,0));radial=(radial-tangent*radial.dot(tangent)).normalized();other=tangent.cross(radial).normalized()
 for j in range(sides):
  t=j*math.tau/sides;vertices.append(p+.032*(radial*math.cos(t)+other*math.sin(t)));uv.append((distance,j/sides))
 if i:
  for j in range(sides):faces.append(((i-1)*sides+j,(i-1)*sides+(j+1)%sides,i*sides+(j+1)%sides,i*sides+j))
me=bpy.data.meshes.new('Continuous rope tube');me.from_pydata(vertices,[],faces);me.update();layer=me.uv_layers.new(name='LoopMetres')
for poly in me.polygons:
 poly.use_smooth=True
 for loopindex in poly.loop_indices:
  vert=me.loops[loopindex].vertex_index;d,v=uv[vert]
  if poly.vertices[0]%sides==sides-1 and v==0:v=1
  layer.data[loopindex].uv=(d,v)
ob=bpy.data.objects.new('ContinuousRope',me);bpy.context.collection.objects.link(ob);me.materials.append(bpy.data.materials['Pylon_Sheave_Liner']);export([ob],'SM_GM_Continuous_Rope',(0,0,0),terminal=0,part='Rope',loop_length_m=distance)
(out/'exports.json').write_text(json.dumps(rows,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(out/'Maldek_Integrated_Terminals.blend'))
print('TERMINAL_EXPORT_COMPLETE',len(rows),flush=True)

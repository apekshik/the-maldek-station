"""First four-area refinement. Load revision 03 in a separate background process.
Original colliders remain simple proxies; decorative meshes stay editable.
"""
import bpy, math, json, hashlib, time
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1]
OUT.mkdir(exist_ok=True)
s=bpy.context.scene
source=Path(bpy.data.filepath)
source_hash=hashlib.sha256(source.read_bytes()).hexdigest()
start=time.perf_counter()
root=bpy.data.objects['Gondola_MOVE_THIS']
before_count=len(s.objects)
COL='12_Gondola'
added=[]
def material(name,color,metal=0,rough=.5,bump=.0003):
 m=bpy.data.materials.new('R04_'+name);m.use_nodes=True;m.diffuse_color=(*color,1)
 n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF')
 p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=95;tex.inputs['Detail'].default_value=2
 b=n.new('ShaderNodeBump');b.inputs['Strength'].default_value=.18;b.inputs['Distance'].default_value=bump;l.new(tex.outputs['Fac'],b.inputs['Height']);l.new(b.outputs[0],p.inputs['Normal'])
 return m
red=material('Oxide_Enamel',(.26,.048,.023),.25,.4)
steel=material('Painted_Charcoal',(.042,.057,.052),.5,.48)
zinc=material('Galvanized_Fittings',(.3,.34,.33),.78,.43)
rubber=material('Seals',(.009,.013,.012),0,.76)
ivory=material('Instrument_Ivory',(.65,.61,.46),0,.58)
yellow=material('Safety_Ochre',(.55,.29,.035),.15,.48)
green=material('Green_Button',(.035,.23,.1),.05,.29)
concrete=bpy.data.materials['R02_Weathered_Concrete'].copy();concrete.name='R04_Concrete_Fine_Aggregate'
for n in concrete.node_tree.nodes:
 if n.type=='BUMP':n.inputs['Strength'].default_value=.28;n.inputs['Distance'].default_value=.003
 if n.type=='BSDF_PRINCIPLED':
  n.inputs['Coat Weight'].default_value=.12;n.inputs['Coat Roughness'].default_value=.3
  for link in list(n.inputs['Roughness'].links):concrete.node_tree.links.remove(link)
  n.inputs['Roughness'].default_value=.62
glass=material('Glazing',(.45,.53,.52),0,.1,.00008)
gp=glass.node_tree.nodes.get('Principled BSDF');gp.inputs['Transmission Weight'].default_value=1;gp.inputs['IOR'].default_value=1.45
def mesh(name,v,f,mat,loc=(0,0,0),collision=False):
 me=bpy.data.meshes.new('R04_'+name);me.from_pydata(v,[],f);me.update()
 o=bpy.data.objects.new('R04_'+name,me);bpy.data.collections[COL].objects.link(o);o.location=loc
 if mat:me.materials.append(mat);o.color=mat.diffuse_color
 o['collision']=collision;o['export_geometry']=True;o['refinement_area']=COL
 if COL=='12_Gondola':o.parent=root;o.matrix_parent_inverse=root.matrix_world.inverted()
 added.append(o);return o
def bevel(o,w=.008,segments=3):
 m=o.modifiers.new('Manufactured_edge_radius','BEVEL');m.width=w;m.segments=segments
 m=o.modifiers.new('Face_weighted_normals','WEIGHTED_NORMAL');m.keep_sharp=True
 return o
def box(name,loc,size,mat=steel,r=.006,collision=False):
 x,y,z=[v/2 for v in size]
 v=[(-x,-y,-z),(-x,-y,z),(-x,y,-z),(-x,y,z),(x,-y,-z),(x,-y,z),(x,y,-z),(x,y,z)]
 o=mesh(name,v,[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)],mat,loc,collision)
 return bevel(o,r) if r else o
def cyl(name,loc,radius,depth,mat=steel,axis=(0,0,1),segments=24):
 v=[(radius*math.cos(2*math.pi*i/segments),radius*math.sin(2*math.pi*i/segments),z) for z in [-depth/2,depth/2] for i in range(segments)]
 f=[tuple(reversed(range(segments))),tuple(range(segments,2*segments))]+[(i,(i+1)%segments,(i+1)%segments+segments,i+segments) for i in range(segments)]
 o=mesh(name,v,f,mat,loc);o.rotation_euler=Vector(axis).to_track_quat('Z','Y').to_euler()
 for p in o.data.polygons[2:]:p.use_smooth=True
 return bevel(o,min(.002,depth/5),2)
def rod(name,a,b,r=.025,mat=steel):
 a,b=Vector(a),Vector(b);return cyl(name,(a+b)/2,r,(b-a).length,mat,b-a)
def bar(name,a,b,width,mat=steel):
 a,b=Vector(a),Vector(b);o=box(name,(a+b)/2,(width,width,(b-a).length),mat,min(.004,width/5));o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o
bolt_templates={}
def bolt(pos,axis=(0,0,1),r=.013):
 key=(COL,r)
 if key not in bolt_templates:
  o=cyl('Hex_Bolt',pos,r,r*.7,zinc,axis,6);bolt_templates[key]=o
 else:
  template=bolt_templates[key];o=template.copy();o.data=template.data;bpy.data.collections[COL].objects.link(o);o.location=pos;o.rotation_euler=Vector(axis).to_track_quat('Z','Y').to_euler();added.append(o)
 return o
def retire(o,proxy=True):
 if proxy and o.get('collision'):
  o.hide_render=True;o.hide_set(True);o.display_type='WIRE';o['export_geometry']=False;o['collision_only']=True
 else:bpy.data.objects.remove(o,do_unlink=True)
def rounded(w,h,r,n=16):
 pts=[]
 for cx,cy,a in [(w/2-r,h/2-r,0),(-w/2+r,h/2-r,90),(-w/2+r,-h/2+r,180),(w/2-r,-h/2+r,270)]:
  for i in range(n+1):
   t=math.radians(a+90*i/n);pts.append((cx+r*math.cos(t),cy+r*math.sin(t)))
 return pts
def ring(name,center,u,v,w,h,r,band,depth,mat):
 u,v=Vector(u),Vector(v);normal=u.cross(v);center=Vector(center)
 outer=rounded(w,h,r);inner=rounded(w-2*band,h-2*band,max(.01,r-band));N=len(outer)
 verts=[tuple(center+u*x+v*y+normal*z) for z in [-depth/2,depth/2] for pts in [outer,inner] for x,y in pts]
 faces=[]
 for i in range(N):
  j=(i+1)%N
  faces += [(i,j,j+2*N,i+2*N),(i+N,i+3*N,j+3*N,j+N),(i+2*N,j+2*N,j+3*N,i+3*N),(i,j+N,j,i+N)]
 # Correct back annulus ordering.
 faces=[f for k,f in enumerate(faces) if k%4!=3]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)]
 return bevel(mesh(name,verts,faces,mat),.002,2)
def window(name,c,u,v,w,h):
 c=Vector(c);u,v=Vector(u),Vector(v);normal=u.cross(v)
 ring(name+'_Frame',c,u,v,w,h,.11,.07,.065,steel)
 ring(name+'_Gasket',c+normal*.015,u,v,w-.12,h-.12,.065,.022,.018,rubber)
 pts=rounded(w-.16,h-.16,.045)
 verts=[tuple(c+u*x+v*y-normal*.014) for x,y in pts]
 o=mesh(name+'_Glass',verts,[tuple(range(len(verts)))],glass)
 m=o.modifiers.new('Glass_thickness','SOLIDIFY');m.thickness=.008
def label(text,pos,size=.035,rotation=(0,0,0),mat=ivory):
 d=bpy.data.curves.new('R04_Label','FONT');d.body=text;d.size=size;d.align_x='CENTER';d.extrude=.0003
 o=bpy.data.objects.new('R04_'+text,d);bpy.data.collections[COL].objects.link(o);o.location=pos;o.rotation_euler=rotation;d.materials.append(mat);o['collision']=False;o['export_geometry']=True;added.append(o);return o

# GONDOLA: remove the misplaced glazing / rub strips and replace the render shell.
for o in list(bpy.data.collections[COL].objects):
 if o.type=='MESH' and o.name not in ('Gondola_Floor','Gondola_Bench','Gondola_Bench.001'):retire(o)
retire(bpy.data.objects['Gondola_Roof'])
for x in [-1.5,1.5]:
 for y in [5.08,11.02]:box('Cabin_Corner',(x,y,5.16),(.19,.22,2.38),red,.065)
 box('Side_Lower_Skin',(x,8.05,4.46),(.13,5.85,.87),red,.035)
 box('Side_Header',(x,8.05,6.16),(.15,5.86,.21),red,.03)
 for y in [5.57,10.53]:box('Side_End_Panel',(x,y,5.49),(.14,.9,1.26),red,.045)
 for y in [6.67,8.05,9.43]:window('Side_Window',(math.copysign(1.585,x),y,5.49),(0,1,0),(0,0,1),1.38,1.23)
 for y in [5.95,7.36,8.74,10.15]:
  box('Panel_Seam',(math.copysign(1.573,x),y,4.47),(.014,.012,.77),rubber,.003)
  for z in [4.16,4.78]:bolt((math.copysign(1.59,x),y,z),(1,0,0),.009)
 for z in [4.12,4.9]:bar('Horizontal_Rub_Rail',(math.copysign(1.6,x),5.15,z),(math.copysign(1.6,x),10.98,z),.055,steel)
for y in [5.03,11.07]:
 if y<6:
  for x in [-1.1,1.1]:
   box('Entry_Lower_Panel',(x,y,4.46),(.8,.14,.88),red,.04)
   window('Entry_Window',(x,y-.05,5.49),(1,0,0),(0,0,1),.8,1.23)
  for x in [-.66,.66]:box('Entry_Jamb',(x,y,5.06),(.12,.16,2.12),red,.035)
  box('Entry_Header',(0,y,6.2),(3.02,.16,.2),red,.04)
  for x in [-.78,.78]:
   rod('Boarding_Grab_Handle',(x,4.84,4.8),(x,4.84,5.3),.018,zinc)
   for z in [4.8,5.3]:rod('Handle_Mount',(x,4.84,z),(x,4.97,z),.014,zinc)
 else:
  box('Rear_Skin',(0,y,4.46),(3,.14,.88),red,.045)
  box('Rear_Header',(0,y,6.18),(3,.14,.21),red,.035)
  for x in [-.75,.75]:window('Rear_Window',(x,y+.04,5.49),(1,0,0),(0,0,1),1.45,1.23)
box('Boarding_Sill',(0,5.08,3.991),(1.2,.34,.018),zinc,.003)
floor=bpy.data.objects['Gondola_Floor'];floor.data.materials.clear();floor.data.materials.append(steel)
for x in [-1.43,1.43]:box('Undercut_Skirt',(x,8.05,3.83),(.16,5.82,.19),steel,.035)
for y in [5.15,10.94]:box('Undercut_Skirt_End',(0,y,3.83),(2.85,.16,.19),steel,.035)
# A low crowned roof with a rounded plan and separate drip lip.
verts=[];N=len(rounded(3.3,6.26,.22))
for w,h,r,z in [(3.3,6.26,.22,6.29),(3.3,6.26,.22,6.39),(3.05,6.02,.28,6.51),(2.65,5.62,.32,6.55)]:
 verts += [(x,y+8.05,z) for x,y in rounded(w,h,r)]
faces=[tuple(reversed(range(N))),tuple(range(3*N,4*N))]
for k in range(3):
 for i in range(N):j=(i+1)%N;faces.append((k*N+i,k*N+j,(k+1)*N+j,(k+1)*N+i))
bevel(mesh('Crowned_Roof',verts,faces,red),.012)
ring('Roof_Drip_Lip',(0,8.05,6.31),(1,0,0),(0,1,0),3.34,6.3,.23,.045,.055,steel)
for x in [-.4,.4]:
 box('Hanger_Roof_Saddle',(x,8.05,6.58),(.23,1,.1),steel,.015)
 bar('Hanger_Plate',(x,8.05,6.6),(math.copysign(.16,x),8.05,7.95),.13,steel)
 for y in [7.7,8.4]:bolt((x,y,6.64),r=.025)
cyl('Hanger_Pivot',(0,8.05,7.91),.16,.64,zinc,(1,0,0))
for x in [-.34,.34]:bolt((x,8.05,7.91),(1,0,0),.062)

# CONTROL ROOM: sloped sheet-metal console with actual instrument assemblies.
COL='02_Control_Room'
for o in list(bpy.data.collections[COL].objects):
 if o.name.startswith(('Control_Console','Console_Gauge')):retire(o)
 elif o.type=='MESH' and o.name.startswith('Control_') and not o.hide_render:
  o.data.materials.clear();o.data.materials.append(concrete);bevel(o,.007,2)
box('Console_Plinth',(-6.2,-.75,4.095),(2.22,.58,.19),rubber,.015)
v=[(x,y,z) for x in [-7.4,-5] for y,z in [(-1.1,4.16),(-.4,4.16),(-.4,5.2),(-1.1,4.96)]]
bevel(mesh('Folded_Console_Housing',v,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],steel),.018)
theta=math.atan2(.24,.7);u=Vector((1,0,0));v=Vector((0,math.cos(theta),math.sin(theta)));normal=u.cross(v)
base=Vector((-6.2,-.75,5.09))
panel=box('Console_Instrument_Panel',base,(2.3,.68,.02),zinc,.008);panel.rotation_euler[0]=theta
for i,x in enumerate([-7,-6.48,-5.96]):
 c=Vector((x,-.63,5.09+.12*math.tan(theta)))+normal*.035
 cyl('Gauge_Bezel',c,.155,.036,steel,normal,48)
 cyl('Gauge_Dial',c+normal*.022,.13,.006,ivory,normal,48)
 for j in range(11):
  a=math.radians(35+27*j);q=c+normal*.028
  rod('Dial_Tick',q+(u*math.cos(a)+v*math.sin(a))*.105,q+(u*math.cos(a)+v*math.sin(a))*.12,.0025,steel)
 a=math.radians(70+i*45);rod('Gauge_Needle',c+normal*.033,c+normal*.033+(u*math.cos(a)+v*math.sin(a))*.095,.003,red)
 label(['SPEED','TENSION','DRIVE'][i],c-v*.07+normal*.03,.023,(theta,0,0),steel)
for i,x in enumerate([-7.03,-6.65,-6.27,-5.89,-5.5]):
 c=Vector((x,-.97,5.09-.22*math.tan(theta)))+normal*.03
 cyl('Switch_Collar',c,.052,.022,zinc,normal)
 cyl('Switch',c+normal*.019,.035,.028,green if i in [0,2] else rubber,normal)
label('MILLFORD  /  DRIVE CONTROL',(-6.22,-1.119,4.75),.062,(math.pi/2,0,0))
c=base+u*.91+v*.05+normal*.055
cyl('Emergency_Stop_Collar',c,.1,.025,yellow,normal)
cyl('Emergency_Stop',c+normal*.045,.066,.065,red,normal)
for x in [-6.97,-6.2,-5.43]:
 box('Console_Access_Door',(x,-1.112,4.49),(.735,.022,.47),steel,.01)
 for xx in [x-.28,x+.28]:
  for z in [4.3,4.67]:bolt((xx,-1.13,z),(0,-1,0),.01)
 box('Panel_Latch',(x+.22,-1.139,4.52),(.028,.025,.075),zinc,.004)
# Window trim preserves the broad operator sightline; no central mullion.
ring('Control_Window_Frame',(-6.1,-.01,5.7),(1,0,0),(0,0,1),3.08,1.48,.035,.05,.18,steel)
box('Window_Sill',(-6.1,-.05,4.997),(3.18,.35,.055),zinc,.012)
for x in [-7.67,-4.53]:
 for z in [5.13,6.27]:bolt((x,-.111,z),(0,-1,0),.011)
rod('Wall_Conduit',(-7.7,-.18,4.35),(-7.7,-.18,6.66),.018,zinc)
rod('Wall_Conduit_Header',(-7.7,-.18,6.66),(-3.22,-.18,6.66),.018,zinc)
for z in [4.55,5.35,6.15]:box('Conduit_Saddle',(-7.7,-.17,z),(.075,.04,.025),zinc,.003)
box('Junction_Box',(-7.68,-.18,4.7),(.19,.12,.24),steel,.018)
for x0,x1 in [(-7.86,-7.4),(-5,-4.45)]:box('Wall_Base_Trim',((x0+x1)/2,-.125,4.06),(x1-x0,.03,.12),steel,.003)

# DRIVE: a finned motor, reducer, output shaft, mounted wheel and belt groove.
COL='04_Lower_Drive'
for o in list(bpy.data.collections[COL].objects):
 if o.name.startswith(('Drive_Motor','Exposed_Flywheel','Flywheel_')):retire(o,False)
box('Machine_Concrete_Pad',(.7,6.25,.06),(3.65,2.4,.12),concrete,.025,True)
for y in [5.5,6.63]:
 box('Machine_Skid',(.65,y,.2),(3.45,.15,.18),steel,.012,True)
 for x in [-.9,.25,2.2]:bolt((x,y,.3),r=.027)
for x in [-.58,.25]:box('Motor_Cross_Mount',(x,6.065,.265),(.28,1.28,.05),steel,.008,True)
cyl('Motor_Cast_Housing',(-.18,5.91,.83),.4,1.12,steel,(1,0,0),48)['collision']=True
for x in [-.8,.45]:cyl('Motor_End_Shield',(x,5.91,.83),.435,.11,steel,(1,0,0),48)
for a in range(0,360,20):
 angle=math.radians(a);y=5.91+.421*math.cos(angle);z=.83+.421*math.sin(angle)
 o=box('Motor_Cooling_Fin',(-.18,y,z),(1.05,.02,.09),steel,.003);o.rotation_euler[0]=angle-math.pi/2
for x in [-.58,.25]:
 for y in [5.52,6.3]:
  box('Motor_Foot',(x,y,.36),(.24,.23,.15),steel,.012,True);bolt((x,y,.447),r=.023)
box('Motor_Terminal_Box',(-.28,5.91,1.34),(.38,.35,.23),steel,.022,True)
box('Terminal_Lid',(-.28,5.91,1.465),(.41,.38,.027),zinc,.006)
for x in [-.43,-.13]:
 for y in [5.78,6.04]:bolt((x,y,1.485),r=.012)
rod('Motor_Cable',(-.28,6.09,1.34),(-.28,6.45,.35),.028,rubber)
cyl('Motor_Coupling',(.69,5.91,.83),.17,.32,zinc,(1,0,0))
box('Reducer_Housing',(1.47,5.93,.75),(1.22,.86,1.02),steel,.1,True)
box('Reducer_Split_Flange',(1.47,5.93,.78),(1.25,.89,.045),zinc,.022)
for x in [1.02,1.92]:
 for y in [5.61,6.25]:bolt((x,y,.815),r=.023)
rod('Output_Shaft',(2.1,6.16,1.05),(2.1,7.2,1.05),.085,zinc)
box('Output_Bearing_Base',(2.1,7.15,.25),(.68,.5,.22),steel,.022,True)
box('Bearing_Pedestal',(2.1,7.15,.57),(.37,.32,.55),steel,.025,True)
cyl('Bearing_Housing',(2.1,7.15,1.05),.2,.28,steel,(0,1,0))
for x in [1.86,2.34]:bolt((x,7.15,.373),r=.027)
# Wheel is a ring with paired flanges, rather than a solid disc.
for y in [6.61,6.79]:ring('Wheel_Rim',(2.1,y,1.05),(1,0,0),(0,0,1),1.83,1.83,.915,.07,.055,steel)
ring('Wheel_Groove',(2.1,6.7,1.05),(1,0,0),(0,0,1),1.76,1.76,.88,.06,.16,rubber)
cyl('Wheel_Hub',(2.1,6.7,1.05),.2,.32,zinc,(0,1,0))
for a in range(0,360,45):
 t=math.radians(a);bar('Wheel_Spoke',(2.1+.14*math.cos(t),6.7,1.05+.14*math.sin(t)),(2.1+.82*math.cos(t),6.7,1.05+.82*math.sin(t)),.067,steel)
for a in range(0,360,60):
 t=math.radians(a);bolt((2.1+.13*math.cos(t),6.875,1.05+.13*math.sin(t)),(0,1,0),.016)
box('Brake_Caliper',(2.96,6.7,1.03),(.2,.37,.36),yellow,.025,True)
box('Brake_Bracket',(2.96,6.7,.55),(.14,.22,.68),steel,.015,True)
box('Brake_Concrete_Foot',(2.96,6.7,.06),(.6,.72,.12),concrete,.018,True)
box('Brake_Base_Plate',(2.96,6.7,.165),(.42,.5,.09),steel,.008,True)
for x in [2.81,3.11]:
 for y in [6.51,6.89]:bolt((x,y,.218),r=.02)
box('Drive_Nameplate',(1.47,6.376,.94),(.44,.018,.16),ivory,.006)
label('M-01  /  REDUCER',(1.47,6.39,.92),.035,(math.pi/2,0,math.pi),steel)

# PLATFORM: panelized concrete surface, recessed service details and tubular rails.
COL='01_Upper_Platform'
for name in ['Platform_Main','Platform_NW','Platform_NE','Platform_North_Link']:
 o=bpy.data.objects[name];bb=[o.matrix_world@Vector(v) for v in o.bound_box]
 x0,x1=min(v.x for v in bb),max(v.x for v in bb);y0,y1=min(v.y for v in bb),max(v.y for v in bb)
 retire(o)
 nx=math.ceil((x1-x0)/2.5);ny=math.ceil((y1-y0)/2.5)
 for ix in range(nx):
  for iy in range(ny):
   a=x0+(x1-x0)*ix/nx+.006;b=x0+(x1-x0)*(ix+1)/nx-.006
   c=y0+(y1-y0)*iy/ny+.006;d=y0+(y1-y0)*(iy+1)/ny-.006
   o=box('Concrete_Slab',((a+b)/2,(c+d)/2,3.86),(b-a,d-c,.28),concrete,.004)
   # Top is a subdivided patch: broad <=1.5 mm relief, zero at slab edges.
   N=8;verts=[];faces=[]
   for j in range(N+1):
    for i in range(N+1):
     u=i/N;v=j/N;z=4-.0015*math.sin(math.pi*u)**2*math.sin(math.pi*v)**2
     verts.append((a+(b-a)*u,c+(d-c)*v,z))
   for j in range(N):
    for i in range(N):k=j*(N+1)+i;faces.append((k,k+1,k+N+2,k+N+1))
   # Lower the box face so the micro-relief mesh has no coplanar overlap.
   for v in o.data.vertices:
    if v.co.z>0:v.co.z-=.004
   mesh('Concrete_Finish',verts,faces,concrete)
 for ix in range(1,nx):
  x=x0+(x1-x0)*ix/nx;box('Recessed_Concrete_Joint',(x,(y0+y1)/2,3.991),(.012,y1-y0,.01),rubber,0)
 for iy in range(1,ny):
  y=y0+(y1-y0)*iy/ny;box('Recessed_Concrete_Joint',((x0+x1)/2,y,3.991),(x1-x0,.012,.01),rubber,0)
# Recess cut through the new render surface only. Original continuous collision stays.
def recess(name,center,size):
 cut=box('Temporary_Cut',center,size,None,0)
 for o in list(added):
  if o.name.startswith(('R04_Concrete_Slab','R04_Concrete_Finish')):
   m=o.modifiers.new(name+'_recess','BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=cut
 # Keep editable cutter hidden from render and viewport; exclude from export.
 cut.hide_render=True;cut.hide_set(True);cut.display_type='WIRE';cut['export_geometry']=False
 return cut
recess('Service_Hatch',(-5.4,3.65,4),(.84,.64,.14))
box('Hatch_Recess',(-5.4,3.65,3.95),(.84,.64,.035),rubber,.005)
box('Flush_Hatch',(-5.4,3.65,3.987),(.8,.6,.02),steel,.005)
for x in [-5.74,-5.06]:
 for y in [3.41,3.89]:bolt((x,y,3.997),r=.012)
for x in [-5.58,-5.22]:box('Hatch_Lift_Recess',(x,3.65,3.999),(.095,.027,.003),rubber,.006)
recess('Drain',(-6,6.73,4),(2.9,.19,.16))
box('Drain_Interior',(-6,6.73,3.92),(2.9,.19,.035),rubber,.006)
for y in [6.641,6.819]:box('Drain_Edge',(-6,y,3.977),(2.9,.018,.04),zinc,.003)
for i in range(72):box('Drain_Grate',(-7.42+i*.04,6.73,3.976),(.012,.16,.04),zinc,.002)
for x in [-7.46,-4.54]:box('Drain_End',(x,6.73,3.976),(.018,.19,.04),zinc,.002)
# Replace existing square rails along identical center lines; retain guard colliders.
post_positions=set()
for o in list(bpy.data.collections[COL].objects):
 if o.name.startswith('R04_') or o.type!='MESH' or o.hide_render:continue
 if o.name.startswith(('Platform_North_','Platform_South_','Dock_Extension_')) and any(t in o.name for t in ['_Top','_Mid','_Rail','_Post']):
  bb=[o.matrix_world@Vector(v) for v in o.bound_box];lo=Vector([min(v[i] for v in bb) for i in range(3)]);hi=Vector([max(v[i] for v in bb) for i in range(3)]);c=(lo+hi)/2;axis=max(range(3),key=lambda i:hi[i]-lo[i]);a=c.copy();b=c.copy();a[axis]=lo[axis];b[axis]=hi[axis]
  rod('Tubular_Guard',a,b,.027 if axis==2 or c.z>5 else .021,zinc)
  if axis==2:post_positions.add((round(c.x,4),round(c.y,4),round(lo.z,4)))
  retire(o,False)
for x,y,z in post_positions:
 box('Post_Base_Plate',(x,y,z+.012),(.18,.18,.024),zinc,.006)
 cyl('Post_Base_Socket',(x,y,z+.055),.044,.085,zinc)
 for dx in [-.06,.06]:
  for dy in [-.06,.06]:bolt((x+dx,y+dy,z+.03),r=.012)
 for h in [.55,1.08]:
  cyl('Rail_Clamp_Collar',(x,y,z+h),.038,.095,zinc)
  bolt((x,y-.043,z+h),(0,-1,0),.01)
for x,y0,y1 in [(-4,7,11.5),(3.6,8.4,11.5)]:
 box('Grating_Toe_Edge',(x,(y0+y1)/2,4.045),(.025,y1-y0,.09),zinc,.004)
 for y in [y0+.16,y1-.16]:bolt((x-.02,y,4.045),(1,0,0),.012)

# Save a self-contained model with the original night setup and focused editing view.
bpy.context.view_layer.update()
p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='OPTIX';p.refresh_devices()
for d in p.devices:d.use=d.type=='OPTIX'
s.cycles.device='GPU';s.cycles.samples=40;s.camera=bpy.data.objects['CAM_R03_Platform_Rain']
for layer in s.view_layers:layer.use=layer.name=='02_Full_Shell'
bpy.context.window.view_layer=s.view_layers['02_Full_Shell']
for screen in bpy.data.screens:
 for a in screen.areas:
  if a.type=='VIEW_3D':
   a.spaces.active.region_3d.view_location=(0,8,5.2);a.spaces.active.region_3d.view_distance=13
   a.spaces.active.shading.type='MATERIAL'
s['Status']='R04 refinement pass 01: gondola, control room, lower drive and platform. See local README; UE export pending.'
for name,pos,target,lens in [('Gondola',(-8,1,7.8),(0,8,5.2),42),('Controls',(-3.6,-3.4,5.8),(-6.2,-.65,5.15),27),('Drive',(5.8,10.8,3.4),(1.6,6.2,1),42),('Platform',(-9,1,7.5),(-2,5.5,4),37)]:
 d=bpy.data.cameras.new('R04_'+name);d.lens=lens;o=bpy.data.objects.new('CAM_R04_'+name,d);bpy.data.collections['92_Cameras_Lights'].objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
notes=bpy.data.texts.get('START_HERE')
if notes:
 notes.clear();notes.write('MILLFORD REFINEMENT 04\n\nFour-area construction detail pass: gondola, controls, drive and platform.\nSee revision_04_refinement/README.md and REFERENCES.md.\nCAM_R04_* bookmarks for inspection. Original night lighting retained.\nEarlier scenes and render-demo baseline preserved. UE export remains pending.\n')
for o in added:
 if o.type=='MESH':
  # Recalculate closed-surface normals consistently, leaving thin glass/surface sheets.
  import bmesh
  bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000001);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
stats={'source':str(source),'source_sha256':source_hash,'source_unchanged':hashlib.sha256(source.read_bytes()).hexdigest()==source_hash,'objects_before':before_count,'objects_after':len(s.objects),'added_objects':len(added),'mesh_datablocks_added':len({o.data.name for o in added if o.type=='MESH'}),'shared_bolt_meshes':len(bolt_templates),'generation_seconds':round(time.perf_counter()-start,2),'areas':{c:sum(o.get('refinement_area')==c for o in added) for c in ['12_Gondola','02_Control_Room','04_Lower_Drive','01_Upper_Platform']},'limitations':['Original simplified collision proxies retained for gondola shell and platform; detailed meshes need an evaluated-geometry UE export.','Drive is an artistic machinery assembly, not an engineered ropeway layout.']}
(OUT/'build_report.json').write_text(json.dumps(stats,indent=2))
dest=OUT/'millford_v2_refinement_04.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(dest))
print('REFINEMENT_SAVED',dest,json.dumps(stats),flush=True)

import bpy,math,json,hashlib
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1];SOURCE=OUT.parent/'passenger_lodge_02/Maldek_Combined_Station_Blockout.blend'
source_hash=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));s=bpy.data.scenes['04_Combined_Station_Blockout'];s.name='05_Material_Study';bpy.context.window.scene=s
def col(n):
 c=bpy.data.collections.new(n);s.collection.children.link(c);return c
grates=col('PL03_Open_Grating');skin=col('PL03_Corrugated_Exterior');details=col('PL03_Furniture_Details');roof=col('PL03_Removable_Roof')
steel=bpy.data.materials['VF06_Structural_steel'];zinc=bpy.data.materials['VF06_Galvanized'];blue=bpy.data.materials['VF06_Petrol_paint'];cream=bpy.data.materials['VF06_Warm_enamel'];ochre=bpy.data.materials['VF06_Safety_ochre']
def material(n,color,metal=0,rough=.5):
 m=bpy.data.materials.new(n);m.diffuse_color=(*color,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;return m
wood=material('PL03_Aged_Pine',(.24,.115,.042),0,.62)
n=wood.node_tree.nodes;l=wood.node_tree.links;tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=4;tex.inputs['Detail'].default_value=3;coord=n.new('ShaderNodeTexCoord');mapping=n.new('ShaderNodeVectorMath');mapping.operation='MULTIPLY';mapping.inputs[1].default_value=(2,55,8);l.new(coord.outputs['Generated'],mapping.inputs[0]);l.new(mapping.outputs[0],tex.inputs['Vector']);ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.09,.035,.012,1);ramp.color_ramp.elements[1].color=(.4,.22,.08,1);l.new(tex.outputs['Fac'],ramp.inputs[0]);l.new(ramp.outputs[0],n.get('Principled BSDF').inputs['Base Color'])
tile=material('PL03_Quarry_Tile',(.18,.095,.048),0,.75);rubber=material('PL03_Dark_Worktop',(.028,.036,.031),0,.5);porcelain=material('PL03_Warm_Porcelain',(.7,.68,.57),0,.22)
glass=material('PL03_Frosted_Glass',(.48,.62,.58),0,.38);glass.node_tree.nodes.get('Principled BSDF').inputs['Transmission Weight'].default_value=.65
def bounds(o):
 ps=[o.matrix_world@Vector(v) for v in o.bound_box];return [min(v[i] for v in ps) for i in range(3)],[max(v[i] for v in ps) for i in range(3)]
def assign(o,m):o.data=o.data.copy();o.data.materials.clear();o.data.materials.append(m)
def mesh(n,v,f,m,c):
 d=bpy.data.meshes.new(n);d.from_pydata(v,[],f);d.update();o=bpy.data.objects.new(n,d);c.objects.link(o);d.materials.append(m);return o
def cube(v,f,x,y,z,w,d,h):
 k=len(v);v.extend([(x,y,z),(x+w,y,z),(x+w,y+d,z),(x,y+d,z),(x,y,z+h),(x+w,y,z+h),(x+w,y+d,z+h),(x,y+d,z+h)]);f.extend([tuple(k+i for i in q) for q in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]])
def box(n,x,y,z,w,d,h,m,c=details):
 v=[];f=[];cube(v,f,x,y,z,w,d,h);return mesh(n,v,f,m,c)
# All grating replaces its opaque plate. Tile into manageable framed panels.
records=[]
def grate(n,lo,hi):
 x0,y0,z0=lo;x1,y1,z=hi;nx=max(1,math.ceil((x1-x0)/2));ny=max(1,math.ceil((y1-y0)/1.2))
 for ix in range(nx):
  for iy in range(ny):
   a=x0+(x1-x0)*ix/nx;b=x0+(x1-x0)*(ix+1)/nx;e=y0+(y1-y0)*iy/ny;g=y0+(y1-y0)*(iy+1)/ny;v=[];f=[];fw=min(.025,(b-a)/5,(g-e)/5)
   cube(v,f,a,e,z-.06,b-a,fw,.06);cube(v,f,a,g-fw,z-.06,b-a,fw,.06)
   cube(v,f,a,e+fw,z-.06,fw,g-e-2*fw,.06);cube(v,f,b-fw,e+fw,z-.06,fw,g-e-2*fw,.06)
   x=a+fw+.04
   while x<b-fw-.006:cube(v,f,x,e+fw,z-.06,.006,g-e-2*fw,.06);x+=.065
   y=e+fw+.06
   while y<g-fw-.008:cube(v,f,a+fw,y,z-.022,b-a-2*fw,.008,.012);y+=.10
   mesh(f'PL03_Grate_{n}_{ix}_{iy}',v,f,zinc,grates)
 records.append({'source':n,'lo':lo,'hi':hi})
for o in list(bpy.data.collections['PL02_New_Deck_Rails_and_Stair'].objects):
 if o.type!='MESH':continue
 if o.name.startswith(('PL02_Deck','PL02_Bypass_Stair','PL02_Bypass_Upper_Landing','PL02_Bypass_Lower_Landing')):
  lo,hi=bounds(o);grate(o.name,lo,hi);bpy.data.objects.remove(o,do_unlink=True)
 else:assign(o,blue if 'Support' not in o.name else steel)
print('Real grating complete',flush=True)
# Match lodge finishes; keep all original program components and dimensions.
exterior={'North':('Y',1),'West':('X',-1),'East':('X',1),'Coffee_east':('X',1),'Coffee_rear':('Y',-1),'WC_west':('X',-1),'WC_rear':('Y',-1),'Hall_south_entry':('Y',-1)}
clad=[]
for o in list(bpy.data.collections['PL02_Fitted_Lodge_Geometry'].objects):
 if o.type!='MESH':o.hide_render=True;continue
 name=o.name;lo,hi=bounds(o);old=o.data.materials[0].name if o.data.materials else ''
 m=cream
 if 'Pine' in old:m=wood
 elif 'Petrol' in old:m=blue
 elif 'Worktops' in old:m=rubber
 elif 'Porcelain' in old:m=porcelain
 elif 'Floor' in name:m=tile
 if 'Frosted_window' in name:m=glass
 assign(o,m)
 # Table planks replace the proxy tops/seats at identical bounds.
 if name.startswith(('FIT_Table_','FIT_Bench_')) and ('_Top' in name or '_Seat' in name):
  count=4 if '_Top' in name else 2
  for j in range(count):box(name+'_Plank',lo[0],lo[1]+j*(hi[1]-lo[1])/count,lo[2],hi[0]-lo[0],(hi[1]-lo[1])/count-.003,hi[2]-lo[2],wood)
  bpy.data.objects.remove(o,do_unlink=True);continue
 key=next((k for k in exterior if name.startswith('FIT_'+k+'_')),None)
 if key:
  axis,sign=exterior[key];ai=0 if axis=='X' else 1;ui=1-ai;a=lo[ui];b=hi[ui];edge=hi[ai] if sign>0 else lo[ai];poly=[];N=max(1,math.ceil((b-a)/.16))
  for i in range(N):
   for t,dep in [(0,.009),(.25,.009),(.4,.032),(.65,.032),(.8,.009)]:poly.append((a+(i+t)*(b-a)/N,edge+sign*dep))
  poly.extend([(b,edge+sign*.009),(b,edge+sign*.003),(a,edge+sign*.003)])
  v=[]
  for z in [lo[2],hi[2]]:
   for u,q in poly:v.append((q,u,z) if ai==0 else (u,q,z))
  n=len(poly);f=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
  ob=mesh('PL03_Cladding_'+name,v,f,blue,skin);clad.append(ob.name)
 if name.startswith('FIT_Locker_') and '_Door' in name:
  x=hi[0]-.05;y=hi[1]+.01
  box('PL03_Locker_Handle',x,y,lo[2]+.7,.018,.035,.15,zinc)
  for j in range(4):box('PL03_Locker_Vent',lo[0]+.035,y,hi[2]-.2-j*.028,hi[0]-lo[0]-.07,.007,.009,rubber)
# Roof assemblies remain independently hideable for interior review.
for name,x0,x1,y0,y1 in [('Hall',-24.3,-9.9,-7.4,4.2),('Coffee',-24.3,-18.9,-12.4,-7.4),('WC',-16.3,-9.9,-13.4,-7.4)]:
 z=7.27;box('PL03_Roof_'+name,x0,y0,z,x1-x0,y1-y0,.12,blue,roof)
 for i in range(math.ceil((x1-x0)/.42)):
  x=x0+i*.42
  box('PL03_Roof_Seam',x,y0,z+.12,.025,y1-y0,.028,zinc,roof)
 for y in [y0,y1-.035]:box('PL03_Roof_Fascia',x0,y,7.15,x1-x0,.035,.24,blue,roof)
print('Cladding, furniture and roof complete',flush=True)
def cam(n,pos,target,scale):
 d=bpy.data.cameras.new(n);o=bpy.data.objects.new(n,d);s.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=scale;return o
views=[cam('PL03_Exterior',(-48,-39,36),(-13,-1,3),55),cam('PL03_Cutaway',(-39,-29,27),(-17,-5,4),32),cam('PL03_Grating_Close',(-33,-19,10),(-25,-10,4),12),cam('PL03_Stair_Materials',(1,-21,10),(-7.2,-10.7,2.5),13)]
s.render.resolution_x=1600;s.render.resolution_y=1200;s.cycles.samples=24
report={'source_sha256':source_hash,'source_unchanged':source_hash==hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'grating':records,'cladding':clad,'materials_reused':[m.name for m in [steel,zinc,blue,cream,ochre]],'stage':'Material and construction mockup; roof is a removable flat envelope, small appliances remain proxies; no Unreal import.'}
(OUT/'material_report.json').write_text(json.dumps(report,indent=2))
s.camera=views[0];bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Maldek_Passenger_Lodge_Materials.blend'))
for i,o in enumerate(views):
 roof.hide_render=i in [1,3];s.camera=o;s.render.filepath=str(OUT/'previews'/f'{o.name}.png');bpy.ops.render.render(write_still=True,scene=s.name)
roof.hide_render=False;s.camera=views[0];bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Maldek_Passenger_Lodge_Materials.blend'))

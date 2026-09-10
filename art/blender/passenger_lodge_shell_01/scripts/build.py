import bpy,math,json,hashlib,ast
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1];SRC=OUT.parent/'passenger_lodge_03/Maldek_Passenger_Lodge_Materials.blend';before=hashlib.sha256(SRC.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(SRC));s=bpy.data.scenes['05_Material_Study'];bpy.context.window.scene=s;s.name='Shell_Polish_Review'
c=bpy.data.collections.new('PLSH_Shell_Trim');s.collection.children.link(c)
for node in ast.parse((OUT.parent/'passenger_lodge_03/scripts/build.py').read_text()).body:
 if isinstance(node,ast.FunctionDef) and node.name in ['bounds','mesh','cube','material']:exec(compile(ast.Module(body=[node],type_ignores=[]),'helpers','exec'))
def box(n,x,y,z,w,d,h,m):
 v=[];f=[];cube(v,f,x,y,z,w,d,h);return mesh('PLSH_'+n,v,f,m,c)
cream=(.57,.51,.40,1);green=(.085,.14,.115,1)
wall=material('PLSH_Painted_Plaster',cream[:3],0,.7);nt=wall.node_tree;n=nt.nodes;l=nt.links;p=n.get('Principled BSDF');uv=n.new('ShaderNodeTexCoord')
maps={}
for k in ['diff','nor_gl','rough']:
 im=bpy.data.images.load(str(OUT/'textures'/f'plastered_wall_04_{k}_4k.jpg'))
 if k!='diff':im.colorspace_settings.name='Non-Color'
 t=n.new('ShaderNodeTexImage');t.image=im;l.new(uv.outputs['UV'],t.inputs['Vector']);maps[k]=t
geo=n.new('ShaderNodeNewGeometry');sep=n.new('ShaderNodeSeparateXYZ');l.new(geo.outputs['Position'],sep.inputs[0]);low=n.new('ShaderNodeMath');low.operation='LESS_THAN';low.inputs[1].default_value=5.05;l.new(sep.outputs['Z'],low.inputs[0]);paint=n.new('ShaderNodeMixRGB');paint.inputs[1].default_value=cream;paint.inputs[2].default_value=green;l.new(low.outputs[0],paint.inputs[0]);mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=.18;l.new(paint.outputs[0],mix.inputs[1]);l.new(maps['diff'].outputs['Color'],mix.inputs[2]);l.new(mix.outputs[0],p.inputs['Base Color'])
normal=n.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.16;l.new(maps['nor_gl'].outputs['Color'],normal.inputs['Color']);l.new(normal.outputs[0],p.inputs['Normal'])
rough=n.new('ShaderNodeMapRange');rough.inputs['To Min'].default_value=.56;rough.inputs['To Max'].default_value=.78;l.new(maps['rough'].outputs['Color'],rough.inputs['Value']);l.new(rough.outputs[0],p.inputs['Roughness'])
trim=material('PLSH_Painted_Trim',(.075,.12,.10),.12,.5);ceiling=material('PLSH_Ceiling_Enamel',(.44,.43,.36),.1,.65)
floor=material('PLSH_Quarry_Floor',(.22,.12,.065),0,.68);n=floor.node_tree.nodes;l=floor.node_tree.links;p=n.get('Principled BSDF');geo=n.new('ShaderNodeNewGeometry');brick=n.new('ShaderNodeTexBrick');brick.offset=0;brick.inputs['Scale'].default_value=1;brick.inputs['Brick Width'].default_value=.3;brick.inputs['Row Height'].default_value=.3;brick.inputs['Mortar Size'].default_value=.004;brick.inputs['Mortar Smooth'].default_value=.001;brick.inputs['Color1'].default_value=(.23,.13,.075,1);brick.inputs['Color2'].default_value=(.31,.19,.105,1);brick.inputs['Mortar'].default_value=(.075,.065,.05,1);l.new(geo.outputs['Position'],brick.inputs['Vector']);l.new(brick.outputs['Color'],p.inputs['Base Color']);bump=n.new('ShaderNodeBump');bump.invert=True;bump.inputs['Distance'].default_value=.0015;bump.inputs['Strength'].default_value=.25;l.new(brick.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs[0],p.inputs['Normal'])
axes={'North':(1,[-1]),'West':(0,[1]),'East':(0,[-1]),'Coffee_east':(0,[-1]),'Coffee_rear':(1,[1]),'WC_west':(0,[1]),'WC_rear':(1,[1]),'Hall_south_coffee':(1,[-1,1]),'Hall_south_entry':(1,[1]),'Hall_south_WC':(1,[-1,1]),'WC_hall_partition':(1,[-1,1]),'WC_shared':(0,[-1,1]),'Full_height_privacy_screen':(0,[-1,1])}
changed=[];original_bounds={}
for o in list(bpy.data.collections['PL02_Fitted_Lodge_Geometry'].objects):
 if o.type!='MESH':continue
 key=next((k for k in axes if o.name.startswith('FIT_'+k)),None)
 isfloor=o.name in ['FIT_Hall_Floor','FIT_Coffee_Floor','FIT_Restrooms_Floor','FIT_Arrival_court_floor']
 if not key and not isfloor:continue
 lo,hi=bounds(o);original_bounds[o.name]=[lo,hi];o.data=o.data.copy();o.data.materials.clear();o.data.materials.append(floor if isfloor else wall);changed.append(o.name)
 # Planar per-face UVs at the scan's documented 3.2 m width.
 uv=o.data.uv_layers.get('UVMap') or o.data.uv_layers.new(name='UVMap')
 for face in o.data.polygons:
  normal=o.matrix_world.to_3x3()@face.normal;drop=max(range(3),key=lambda i:abs(normal[i]));a,b=[i for i in range(3) if i!=drop]
  for li in face.loop_indices:
   q=o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(q[a]/3.2,q[b]/3.2)
 if not key:continue
 ai,signs=axes[key];ui=1-ai;start=lo[ui]+.10;end=hi[ui]-.10
 if abs(hi[2]-7.2)<.01:
  box('Wall_Head_Closure',lo[0],lo[1],7.2,hi[0]-lo[0],hi[1]-lo[1],.07,ceiling)
 if end<=start:continue
 for sign in signs:
  edge=hi[ai] if sign>0 else lo[ai]
  for name,z,h,depth in [('Skirting',4.005,.115,.015),('Dado',5.03,.04,.012),('Cornice',7.10,.09,.025)]:
   if z<lo[2]+.001 or z+h>hi[2]+.001:continue
   q=edge if sign>0 else edge-depth
   x,y,w,d=(q,start,depth,end-start) if ai==0 else (start,q,end-start,depth)
   box(name,x,y,z,w,d,h,trim)
# Join trim across construction segments; retain gaps at real door openings.
groups={}
for o in list(c.objects):
 if not o.name.startswith(('PLSH_Skirting','PLSH_Dado','PLSH_Cornice')):continue
 lo,hi=bounds(o);axis=0 if hi[0]-lo[0]>hi[1]-lo[1] else 1;other=1-axis
 key=(o.name.split('.')[0],axis,round(lo[other],5),round(hi[other],5),round(lo[2],5),round(hi[2],5))
 groups.setdefault(key,[]).append((lo[axis],hi[axis],o))
for key,items in groups.items():
 items.sort(key=lambda q:q[0]);runs=[]
 for a,b,o in items:
  if runs and -.001<=a-runs[-1][1]<=.201:runs[-1][1]=max(b,runs[-1][1])
  else:runs.append([a,b])
  bpy.data.objects.remove(o,do_unlink=True)
 name,axis,q0,q1,z0,z1=key
 for a,b in runs:
  x,y,w,d=(a,q0,b-a,q1-q0) if axis==0 else (q0,a,q1-q0,b-a)
  box(name.removeprefix('PLSH_'),x,y,z0,w,d,z1-z0,trim)
# Roof underside receives a calm finish without changing its exterior material.
for o in bpy.data.collections['PL03_Removable_Roof'].objects:
 if not o.name.startswith('PL03_Roof_') or 'Seam' in o.name or 'Fascia' in o.name:continue
 o.data=o.data.copy();o.data.materials.append(ceiling)
 for face in o.data.polygons:
  if face.normal.z<-.9:face.material_index=len(o.data.materials)-1
 changed.append(o.name)
# Shallow roof support members; no changes to door/window apertures.
for y in [-6.5,-3,.8]:box('Ceiling_Member',-23.92,y,7.03,13.64,.10,.24,ceiling)
report={'source_sha256':before,'source_unchanged':before==hashlib.sha256(SRC.read_bytes()).hexdigest(),'material_changed_objects':changed,'original_bounds':original_bounds,'new_collection':c.name,'layout_changed':False,'integration':'Apply material/UV changes to named shell pieces only; append PLSH_Shell_Trim. Coordinate trim endpoints with opening packages. No furniture, fixture, sign, door or window meshes replaced.'}
(OUT/'shell_manifest.json').write_text(json.dumps(report,indent=2))
sources={'license':'CC0','license_url':'https://polyhaven.com/license','asset':'Plastered Wall 04','author':'Rob Tuytel','page':'https://polyhaven.com/a/plastered_wall_04','physical_width_m':3.2,'files':[{'name':p.name,'url':'https://dl.polyhaven.org/file/ph-assets/Textures/jpg/4k/plastered_wall_04/'+p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted((OUT/'textures').glob('*.jpg'))]}
(OUT/'texture_sources.json').write_text(json.dumps(sources,indent=2))
lights=[]
for x,y,power,size in [(-20,-1.5,160,3),(-14,-1.5,160,3),(-20,-5.5,160,3),(-14,-5.5,160,3),(-15,-8.2,90,1.4),(-11.8,-8.2,90,1.4)]:
 d=bpy.data.lights.new('PLSH_Review_Light','AREA');d.energy=power;d.size=size;d.color=(1,.88,.72);o=bpy.data.objects.new(d.name,d);s.collection.objects.link(o);o.location=(x,y,7.0);lights.append(o)
views=[('PLSH_Hall',(-21.8,1.9,5.65),(-15.8,-6.8,5.25),22),('PLSH_Hallway',(-15.25,-8.25,5.65),(-11.4,-8.7,5.3),20),('PLSH_Entrance',(-17.1,-6.35,5.65),(-17.1,2.3,5.35),22)]
s.render.resolution_x=1800;s.render.resolution_y=1200;s.cycles.samples=32
cams=[]
for name,pos,target,lens in views:
 d=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.lens=lens;cams.append(o)
s.camera=cams[0];bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Maldek_Lodge_Shell_Polish.blend'));bpy.ops.file.make_paths_relative()
for o in cams:s.camera=o;s.render.filepath=str(OUT/'previews'/f'{o.name}.png');bpy.ops.render.render(write_still=True,scene=s.name)
s.camera=cams[0];bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Maldek_Lodge_Shell_Polish.blend'));bpy.ops.file.make_paths_relative()

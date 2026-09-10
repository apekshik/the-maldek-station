"""Build isolated editable seating plus explicitly reference-only fitted context.
Run with Blender 5; MALDEK_SOURCE_REPO can override the reference repository.
"""
import bpy, math, json, os, hashlib
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1]; (OUT/'previews').mkdir(exist_ok=True)
SRC=Path(os.environ.get('MALDEK_SOURCE_REPO','C:/Users/apek-anna/Developer/the-maldek-station'))/'art/blender/passenger_lodge_03/Maldek_Passenger_Lodge_Materials.blend'
SHA=hashlib.sha256(SRC.read_bytes()).hexdigest()
assert SHA=='b9d78ed0d7c5c50bc28a8fb6a0d63f1c86fa83d3144c6a7eae50476ee9607796','Inspect changed source before rebuilding'
bpy.ops.wm.open_mainfile(filepath=str(SRC)); s=bpy.data.scenes['05_Material_Study'];bpy.context.window.scene=s
def signature(o):
 payload=[list(row) for row in o.matrix_world]
 if o.type=='MESH':payload += [[list(v.co) for v in o.data.vertices],[[*p.vertices] for p in o.data.polygons],[m.name if m else None for m in o.data.materials]]
 return hashlib.sha256(repr(payload).encode()).hexdigest()
context_signatures={o.name:signature(o) for o in s.objects if not o.name.startswith(('FIT_Table_','FIT_Bench_'))}
(OUT/'context_signatures.json').write_text(json.dumps(context_signatures,indent=2))
s.name='PLS_Fitted_Review'
# Keep only the approved study scene, fully local to this output file.
for sc in list(bpy.data.scenes):
 if sc!=s:bpy.data.scenes.remove(sc)
ref=bpy.data.collections.new('REFERENCE_ONLY_Source_Context_DO_NOT_EXPORT');s.collection.children.link(ref)
for c in list(s.collection.children):
 if c!=ref:s.collection.children.unlink(c);ref.children.link(c)
for o in list(s.collection.objects):s.collection.objects.unlink(o);ref.objects.link(o)
ref['export']=False
inv=json.loads((OUT/'source_inventory.json').read_text())
assert len(inv)==90
for row in inv:bpy.data.objects.remove(bpy.data.objects[row['name']],do_unlink=True)
bpy.data.collections['PL03_Removable_Roof'].hide_render=True;bpy.data.collections['PL03_Removable_Roof'].hide_viewport=True
kit=bpy.data.collections.new('PLS_Seating_Kit');s.collection.children.link(kit)
review=bpy.data.collections.new('REVIEW_ONLY_Lights_Cameras_Human');s.collection.children.link(review);review['export']=False
# Wood coordinates follow each board's long X axis. End faces get an independent material.
def wood(name,end=False):
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF');p.inputs['Roughness'].default_value=.58
 tc=n.new('ShaderNodeTexCoord');mp=n.new('ShaderNodeVectorMath');mp.operation='MULTIPLY';mp.inputs[1].default_value=(3,38,38) if not end else (3,7,7);l.new(tc.outputs['Generated'],mp.inputs[0])
 noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=3;noise.inputs['Detail'].default_value=3;l.new(mp.outputs[0],noise.inputs['Vector'])
 ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.22;ramp.color_ramp.elements[0].color=(.16,.075,.024,1);ramp.color_ramp.elements[1].position=.8;ramp.color_ramp.elements[1].color=(.53,.32,.14,1);l.new(noise.outputs['Fac'],ramp.inputs[0])
 oi=n.new('ShaderNodeObjectInfo');mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[2].default_value=(.83,.87,.90,1);l.new(oi.outputs['Random'],mix.inputs[0]);l.new(ramp.outputs[0],mix.inputs[1]);l.new(mix.outputs[0],p.inputs['Base Color'])
 bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.13;bump.inputs['Distance'].default_value=.0007;l.new(noise.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs[0],p.inputs['Normal']);m['procedural_Blender_only']=True
 return m
pine=wood('PLS_Aged_Pine_Long_Grain');end=wood('PLS_Pine_End_Grain',True)
# Scanned stained pine: crop to single-board strips so photographed seams never
# run across a solid authored board. Object random selects eight atlas strips.
n=pine.node_tree.nodes;l=pine.node_tree.links;n.clear()
p=n.new('ShaderNodeBsdfPrincipled');out=n.new('ShaderNodeOutputMaterial');l.new(p.outputs[0],out.inputs['Surface'])
tc=n.new('ShaderNodeTexCoord');oi=n.new('ShaderNodeObjectInfo');r=n.new('ShaderNodeValToRGB');r.color_ramp.interpolation='CONSTANT'
offsets=[.018,.14,.27,.38,.54,.655,.79,.91]
for i,v in enumerate(offsets):
 e=r.color_ramp.elements[i] if i<2 else r.color_ramp.elements.new(i/8)
 e.position=i/8;e.color=(0,v,0,1)
l.new(oi.outputs['Random'],r.inputs[0]);add=n.new('ShaderNodeVectorMath');add.operation='ADD';l.new(tc.outputs['UV'],add.inputs[0]);l.new(r.outputs[0],add.inputs[1])
for suffix,socket in [('diff','Base Color'),('rough','Roughness'),('nor_gl',None)]:
 im=bpy.data.images.load(str(OUT/'textures'/f'stained_pine_{suffix}_2k.jpg'));im.pack();t=n.new('ShaderNodeTexImage');t.image=im;l.new(add.outputs[0],t.inputs[0])
 if suffix!='diff':im.colorspace_settings.name='Non-Color'
 if socket:l.new(t.outputs['Color'],p.inputs[socket])
 else:
  nm=n.new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=.38;l.new(t.outputs['Color'],nm.inputs['Color']);l.new(nm.outputs[0],p.inputs['Normal'])
p.inputs['Coat Weight'].default_value=.12;p.inputs['Coat Roughness'].default_value=.38
pine['procedural_Blender_only']=False;pine['atlas_variation_requires_bake']=True
# Growth rings on exposed end faces, independently from long grain.
n=end.node_tree.nodes;l=end.node_tree.links;wave=n.new('ShaderNodeTexWave');wave.wave_type='RINGS';wave.rings_direction='X';wave.inputs['Scale'].default_value=8;wave.inputs['Distortion'].default_value=4
l.new(n.get('Texture Coordinate').outputs['Generated'],wave.inputs['Vector']);l.new(wave.outputs['Color'],n.get('Color Ramp').inputs[0])
end_ramp=n.get('Color Ramp').color_ramp
end_ramp.elements[0].color=(.07,.024,.007,1);end_ramp.elements[1].color=(.20,.088,.029,1)
steel=bpy.data.materials.get('VF06_Petrol_paint');zinc=bpy.data.materials.get('VF06_Galvanized')
if not steel:raise RuntimeError('Station material missing')
cache={};parts=[];root=None;coll=kit

def box(name,loc,dim,mat=pine,bevel=.006):
 key=('box',tuple(round(v,6) for v in dim),mat.name,bevel)
 if key not in cache:
  bpy.ops.mesh.primitive_cube_add();o=bpy.context.object;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
  o.data.materials.append(mat)
  if mat==pine:
   o.data.materials.append(end)
   axis=max(range(3),key=lambda i:dim[i]);uv=o.data.uv_layers.active
   for f in o.data.polygons:
    if abs(f.normal[axis])>.9:f.material_index=1
    other=max((i for i in range(3) if i!=axis),key=lambda i:dim[i] if abs(f.normal[i])<.5 else -1)
    for li in f.loop_indices:
     co=o.data.vertices[o.data.loops[li].vertex_index].co
     uv.data[li].uv=((co[axis]/dim[axis]+.5)*.96+.02,(co[other]/dim[other]+.5)*.075)
  mod=o.modifiers.new('Rounded finished edges','BEVEL');mod.width=bevel;mod.segments=3;bpy.ops.object.modifier_apply(modifier=mod.name)
  cache[key]=o.data;bpy.data.objects.remove(o,do_unlink=True)
 o=bpy.data.objects.new(name,cache[key]);coll.objects.link(o);o.location=loc;o.parent=root;parts.append(o);return o

def beam(name,a,b,width,depth,mat=pine):
 a,b=Vector(a),Vector(b);o=box(name,(a+b)/2,((b-a).length,width,depth),mat,.003);o.rotation_euler=(b-a).to_track_quat('X','Z').to_euler();return o

def bolt(name,loc,axis='Y',washer=False):
 key=('washer' if washer else 'bolt',)
 if key not in cache:
  # Closed annular washer; closed hex bolt head. Separate mating surfaces.
  if washer:
   verts=[];faces=[];N=24
   for z in [-.0015,.0015]:
    for r in [.006,.015]:
     verts.extend([(r*math.cos(i*2*math.pi/N),r*math.sin(i*2*math.pi/N),z) for i in range(N)])
   for i in range(N):
    j=(i+1)%N
    faces.extend([(i,j,N+j,N+i),(2*N+i,3*N+i,3*N+j,2*N+j),(i,2*N+i,2*N+j,j),(N+i,N+j,3*N+j,3*N+i)])
   me=bpy.data.meshes.new('PLS_Washer_Mesh');me.from_pydata(verts,[],faces);me.update()
   import bmesh
   bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
  else:
   bpy.ops.mesh.primitive_cylinder_add(vertices=6,radius=.010,depth=.007);tmp=bpy.context.object;me=tmp.data;bpy.data.objects.remove(tmp,do_unlink=True)
  me.materials.append(zinc);cache[key]=me
 o=bpy.data.objects.new(name,cache[key]);coll.objects.link(o);o.location=loc;o.parent=root
 if axis=='Y':o.rotation_euler.x=math.pi/2
 parts.append(o);return o

def furniture(prefix,bench=False,y=0,repair=False):
 height=.48 if bench else .78;depth=.35 if bench else .8;n=2 if bench else 5;thick=.045
 for j in range(n):box(prefix+f'_Plank_{j+1}',(0,y-depth/2+(j+.5)*depth/n,height-thick/2),(1.8,depth/n-.004,thick))
 # End trestles support the top without a deep apron across seated knees.
 for x in [-.65,.65]:
  box(prefix+'_Bearing_Rail',(x,y,height-.075),(.09,depth-.035,.06))
  for sign in [-1,1]:
   spread=.125 if bench else .285;upper=.085 if bench else .20
   beam(prefix+'_Splayed_Leg',(x,y+sign*spread,.012),(x,y+sign*upper,height-.085),.075,.075)
   box(prefix+'_Floor_Shoe',(x,y+sign*spread,.008),(.105,.095,.016),steel,.003)
  box(prefix+'_Trestle_Tie',(x,y,.15),(.095,depth-.055,.075),steel,.003)
  for sign in [-1,1]:
   yy=y+sign*((depth-.055)/2+.002)
   bolt(prefix+'_Tie_Washer',(x,yy,.15),washer=True)
   bolt(prefix+'_Tie_Bolt',(x,yy+sign*.0055,.15))
 # Upper spine connects the brace tips to both bearing rails.
 box(prefix+'_Upper_Spine',(0,y,height-.074),(1.39,.055,.058))
 # Central longitudinal stretcher, with diagonal anti-racking braces.
 box(prefix+'_Stretcher',(0,y,.19),(1.30,.065,.085))
 for sign in [-1,1]:beam(prefix+'_Knee_Brace',(sign*.56,y,.24),(sign*.25,y,height-.112),.045,.05)
 # Round flush timber plugs over concealed top fasteners.
 for x in [-.65,.65]:
  for yy in [-depth*.29,depth*.29]:
   box(prefix+'_Fixing_Plate',(x,y+yy,height-.05),(.14,.035,.006),steel,.002)
 # A small steel underside mending strap is a restrained repair detail.
 if repair:box(prefix+'_Repair_Strap',(.26,y,height-.047),(.065,depth-.02,.004),zinc,.001)

groups=[]
for row,d in enumerate([1.1,4.3,7.5]):
 for col,x in enumerate([4,10]):
  idx=row*2+col+1;name=f'PLS_Group_{idx:02}';root=bpy.data.objects.new(name,None);kit.objects.link(root);root.location=(x+.9-24.1,4-d-.4,4);root['export']=True
  start=len(parts);furniture(name+'_Table')
  furniture(name+'_Bench_N',True,.775,repair=idx==3);furniture(name+'_Bench_S',True,-.775)
  groups.append(dict(name=name,translation_m=list(root.location),rotation_euler=[0,0,0],table_top_m=[1.8,.8,.78],bench_seat_m=[1.8,.35,.48],bench_offsets_y_m=[-.775,.775],objects=[o.name for o in parts[start:]]))
# Neutral review figure, roughly 1.75m standing equivalent, hip at seat; separate excluded collection.
root=None;coll=review;human=[]
mat=bpy.data.materials.new('REVIEW_Clay_Human');mat.diffuse_color=(.22,.3,.34,1)
mat.use_nodes=True;mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.16,.22,.25,1)
cx,cy,cz=groups[2]['translation_m']
def hbox(n,loc,dim):
 o=box('REVIEW_Human_'+n,(cx+loc[0],cy+loc[1],cz+loc[2]),dim,mat,.035);human.append(o)
hbox('Pelvis',(0,-.775,.57),(.30,.23,.18));hbox('Torso',(0,-.79,.87),(.34,.22,.43));hbox('Head',(0,-.78,1.21),(.19,.20,.24))
for x in [-.105,.105]:
 hbox('Thigh',(x,-.535,.57),(.15,.43,.14));hbox('Shin',(x,-.34,.28),(.12,.12,.43));hbox('Foot',(x,-.24,.055),(.13,.29,.10))
for o in human:o['reference_only']=True
# Remove builder's figure parts from the export inventory by collection membership.
manifest=dict(source_sha256=SHA,source_scene='05_Material_Study',replacement_objects=inv,collection=kit.name,groups=groups,wall_patch=None,moving_parts=[],origin='Each group empty is at tabletop XY centre and finished floor. Child parts have local component origins.',height_correction_m=-.03,context_export=False,material_notes='Packed Poly Haven CC0 stained pine PBR textures; per-object strip selection and procedural end grain need baking for export. Station petrol paint and galvanized reused. See REFERENCES.md.',surface_ownership='Old 90 pieces removed. Planks separated by 4mm. Timber joints intentionally embed; bolt/washer interfaces are concealed, with no duplicate exposed shells.')
# Inventory includes exact mesh references, material slots, local transforms and dimensions.
bpy.context.view_layer.update()
manifest['objects']=[dict(name=o.name,mesh=o.data.name,parent=o.parent.name,location=list(o.location),rotation=list(o.rotation_euler),dimensions=list(o.dimensions),materials=[m.name for m in o.data.materials]) for o in kit.objects if o.type=='MESH']
(OUT/'replacement_manifest.json').write_text(json.dumps(manifest,indent=2))
# Lighting and saved review cameras.
for o in s.objects:
 if o.type=='LIGHT':o.hide_render=True
for pos,power,size in [((-18,0,7.0),1300,7),((-16,-5,7),1100,6),((-21,3,6),700,5)]:
 ld=bpy.data.lights.new('REVIEW_Neutral_Softbox','AREA');ld.energy=power;ld.shape='DISK';ld.size=size;o=bpy.data.objects.new(ld.name,ld);review.objects.link(o);o.location=pos
s.world.color=(.3,.3,.3)
s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True
s.render.resolution_x=1400;s.render.resolution_y=1000;s.render.resolution_percentage=100
s.view_settings.view_transform='AgX'
views=[('01_Assembly',(-16, -3.5,6.3),(-19.2,-.7,4.4),4.4,'isolated'),('02_Reverse',(-22.5,1.8,5.8),(-19.2,-.7,4.35),4.3,'isolated'),('03_Underside',(-17.1,-2.45,4.35),(-19.2,-.7,4.38),2.8,'isolated'),('04_Player_Height',(-21.4,1.5,5.65),(-17.7,-2.2,4.6),None,'fitted'),('05_All_Six',(-17.1,-.7,17),(-17.1,-.7,4),15,'overview'),('06_Seated_Proportions',(-16.9,-.9,4.85),(-19.2,-1.1,4.62),2.7,'human')]
for name,pos,target,ortho,mode in views:
 cd=bpy.data.cameras.new('REVIEW_'+name);o=bpy.data.objects.new(cd.name,cd);review.objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();cd.clip_start=.02;cd.lens=24
 if ortho:cd.type='ORTHO';cd.ortho_scale=ortho
 o['mode']=mode
s.camera=bpy.data.objects['REVIEW_04_Player_Height']
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Maldek_Passenger_Lodge_Seating.blend'),compress=True)
(OUT/'views.json').write_text(json.dumps(views,indent=2))
assert hashlib.sha256(SRC.read_bytes()).hexdigest()==SHA
print('SEATING BUILD COMPLETE')

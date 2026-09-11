"""Export twelve fitted lockers with independent hinge and cam pivots."""
import bpy,json,hashlib,math,bmesh,sys
from pathlib import Path
from mathutils import Vector,Matrix
OUT=Path(__file__).resolve().parents[1];REPO=OUT.parents[2];dest=OUT/'lockers'
for sub in ['fbx','textures']:(dest/sub).mkdir(parents=True,exist_ok=True)
src=REPO/'art/blender/passenger_lodge_04/Maldek_Passenger_Lodge_Integrated.blend';sha=hashlib.sha256(src.read_bytes()).hexdigest();assert sha=='bcf7e6301aecedd83688488981fd58a5a9719d685ef975210eef9eeb7f753f6c'
bpy.ops.wm.open_mainfile(filepath=str(src));bpy.context.scene.frame_set(1);dg=bpy.context.evaluated_depsgraph_get();kit=bpy.data.collections['PLL_Lockers']
objects=list(kit.all_objects);inventory=[{'name':o.name,'parent':o.parent.name if o.parent else None,'matrix':[list(r) for r in o.matrix_world],'type':o.type} for o in objects]
s=bpy.data.scenes.new('Locker_Export');bpy.context.window.scene=s;s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=8;s.render.threads_mode='FIXED';s.render.threads=8;s.render.bake.use_selected_to_active=False;s.render.bake.margin=12;s.render.bake.use_clear=True;s.render.bake.normal_space='TANGENT';s.view_settings.view_transform='Standard'
materials={};assets=[];groups=[]
def parented(o,p):
 while o:
  if o==p:return True
  o=o.parent
 return False
def shader(orig):
 if orig.name in materials:return materials[orig.name]
 m=orig.copy();materials[orig.name]=m;n=m.node_tree.nodes;l=m.node_tree.links;uv=n.new('ShaderNodeUVMap');uv.uv_map='SourceUV';attrs={}
 for name in ['SourceGenerated','SourceObject','SourceRandom']:
  a=n.new('ShaderNodeAttribute');a.attribute_name=name;attrs[name]=a
 for q in list(n):
  if q.type=='TEX_COORD':
   for link in list(q.outputs['UV'].links):l.new(uv.outputs[0],link.to_socket)
   for output,name in [('Generated','SourceGenerated'),('Object','SourceObject')]:
    for link in list(q.outputs[output].links):l.new(attrs[name].outputs['Vector'],link.to_socket)
  if q.type=='OBJECT_INFO':
   for link in list(q.outputs['Random'].links):l.new(attrs['SourceRandom'].outputs['Fac'],link.to_socket)
  if q.type in {'NORMAL_MAP','UVMAP'}:q.uv_map='SourceUV'
 t=n.new('ShaderNodeTexImage');t.name='BAKE_TARGET';em=n.new('ShaderNodeEmission');em.name='BAKE_EMISSION';comb=n.new('ShaderNodeCombineColor');comb.name='BAKE_ORM';comb.mode='RGB';comb.inputs[0].default_value=1;p=next(q for q in n if q.type=='BSDF_PRINCIPLED')
 for sock,i in [('Roughness',1),('Metallic',2)]:
  v=p.inputs[sock]
  if v.is_linked:l.new(v.links[0].from_socket,comb.inputs[i])
  else:comb.inputs[i].default_value=v.default_value
 return m

for i in range(1,13):
 id=f'{i:02}';prefix='PLL_'+id;objs=[o for o in objects if o.type in {'MESH','FONT','CURVE'} and o.name.startswith(prefix+'_')]
 pivot=bpy.data.objects[prefix+'_Door_Pivot'];cam=bpy.data.objects[prefix+'_Lock_Cam_Pivot'];H=pivot.matrix_world.copy()
 frames={'Static':H,'Leaf':H,'Cam':cam.matrix_world.copy()};controls={'Leaf':{'motion':'hinge','open_degrees':100}}
 keys=list(frames);copies=[];sources={k:[] for k in keys};collision={k:[] for k in keys}
 for ob in objs:
  role='Cam' if parented(ob,cam) else 'Leaf' if parented(ob,pivot) else 'Static'
  # The thin panel and folds block walking; vent openings remain available to detailed aiming traces.
  if role=='Leaf' and ('Door_Sheet' in ob.name or 'Door_Fold' in ob.name):
   pts=[H.inverted()@ob.matrix_world@Vector(v) for v in ob.bound_box];low=[min(v[j] for v in pts) for j in range(3)];high=[max(v[j] for v in pts) for j in range(3)]
   collision[role].append({'source':ob.name,'center':[(a+b)/2 for a,b in zip(low,high)],'extent':[(b-a)/2 for a,b in zip(low,high)]})
  sources[role].append(ob.name);me=bpy.data.meshes.new_from_object(ob.evaluated_get(dg),depsgraph=dg);copy=bpy.data.objects.new('EXPORT_'+ob.name,me);s.collection.objects.link(copy);copy.matrix_world=ob.matrix_world.copy()
  lo=[min(v.co[j] for v in me.vertices) for j in range(3)];hi=[max(v.co[j] for v in me.vertices) for j in range(3)];rv=int(hashlib.sha256(ob.name.encode()).hexdigest()[:8],16)/4294967296
  for attr,kind in [('SourceGenerated','FLOAT_VECTOR'),('SourceObject','FLOAT_VECTOR'),('SourceRandom','FLOAT')]:
   a=me.attributes.new(attr,kind,'POINT')
   for v,q in zip(me.vertices,a.data):
    if kind=='FLOAT':q.value=rv
    else:q.vector=[(v.co[j]-lo[j])/max(hi[j]-lo[j],1e-8) for j in range(3)] if attr=='SourceGenerated' else v.co
  a=me.attributes.new('PartIndex','INT','FACE')
  for v in a.data:v.value=keys.index(role)
  if not me.uv_layers:me.uv_layers.new(name='SourceUV')
  me.uv_layers[0].name='SourceUV';me.uv_layers.new(name='BakeUV')
  for slot in copy.material_slots:slot.material=shader(slot.material)
  copies.append(copy)
 assert all(sources.values()),{k:len(v) for k,v in sources.items()}
 bpy.ops.object.select_all(action='DESELECT')
 for ob in copies:ob.select_set(True)
 bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.join();ob=bpy.context.object;ob.data.uv_layers.active=ob.data.uv_layers['BakeUV'];bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=math.radians(66),island_margin=.006,area_weight=.3,scale_to_bounds=True);bpy.ops.object.mode_set(mode='OBJECT');textures={}
 for channel in ['BaseColor','ORM','NormalGL']:
  im=bpy.data.images.new('PLL_'+id+'_'+channel,2048,2048,alpha=False);im.colorspace_settings.name='sRGB' if channel=='BaseColor' else 'Non-Color';im.generated_color=(.5,.5,1,1) if channel=='NormalGL' else (0,0,0,1)
  for m in materials.values():
   n=m.node_tree.nodes;l=m.node_tree.links;t=n['BAKE_TARGET'];t.image=im;n.active=t;p=next(q for q in n if q.type=='BSDF_PRINCIPLED');out=next(q for q in n if q.type=='OUTPUT_MATERIAL');em=n['BAKE_EMISSION']
   if channel=='NormalGL':l.new(p.outputs[0],out.inputs['Surface'])
   else:
    for link in list(em.inputs['Color'].links):l.remove(link)
    q=p.inputs['Base Color']
    if channel=='ORM':l.new(n['BAKE_ORM'].outputs[0],em.inputs['Color'])
    elif q.is_linked:l.new(q.links[0].from_socket,em.inputs['Color'])
    else:em.inputs['Color'].default_value=q.default_value
    l.new(em.outputs[0],out.inputs['Surface'])
  print('BAKING',id,channel,flush=True);bpy.ops.object.bake(type='NORMAL' if channel=='NormalGL' else 'EMIT',uv_layer='BakeUV');file=dest/'textures'/(im.name+'.png');im.filepath_raw=str(file);im.file_format='PNG';im.save();textures[channel]={'file':str(file.relative_to(dest)),'sha256':hashlib.sha256(file.read_bytes()).hexdigest()}
  for m in materials.values():m.node_tree.nodes['BAKE_TARGET'].image=None
  bpy.data.images.remove(im)
 ob.data.uv_layers.remove(ob.data.uv_layers['SourceUV']);ob.data.uv_layers.active_index=0;ob.data.uv_layers[0].active_render=True;ob.data.transform(ob.matrix_world);ob.matrix_world=Matrix.Identity(4);parts=[]
 for role,target in frames.items():
  me=ob.data.copy();bm=bmesh.new();bm.from_mesh(me);layer=bm.faces.layers.int['PartIndex'];bmesh.ops.delete(bm,geom=[f for f in bm.faces if f[layer]!=keys.index(role)],context='FACES');bm.to_mesh(me);bm.free();part=bpy.data.objects.new('EXPORT_PART',me);s.collection.objects.link(part)
  me.transform(target.inverted());me.materials.clear();me.materials.append(bpy.data.materials.new('LockerAtlas'))
  for poly in me.polygons:poly.material_index=0
  name='SM_PLL_'+id+'_'+role;part.name=name;bpy.ops.object.select_all(action='DESELECT');part.select_set(True);bpy.context.view_layer.objects.active=part;file=dest/'fbx'/(name+'.fbx');bpy.ops.export_scene.fbx(filepath=str(file),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,bake_anim=False)
  lo=[min(v.co[j] for v in me.vertices) for j in range(3)];hi=[max(v.co[j] for v in me.vertices) for j in range(3)];assets.append({'name':name,'group':id,'role':role,'lo':lo,'hi':hi,'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'polygons':len(me.polygons)})
  parts.append({'role':role,'mesh':name,'local_matrix':[list(r) for r in H.inverted()@target],'sources':sources[role],'matrix':[list(r) for r in target],'control':controls.get(role),'collision':collision[role]});bpy.data.objects.remove(part,do_unlink=True)
 row={'id':id,'matrix':[list(r) for r in H],'textures':textures,'parts':parts}
 groups.append(row);bpy.data.objects.remove(ob,do_unlink=True)
assert sum(len(p['sources']) for g in groups for p in g['parts'])==sum(o.type in {'MESH','FONT','CURVE'} for o in objects)
assert hashlib.sha256(src.read_bytes()).hexdigest()==sha
(dest/'exports.json').write_text(json.dumps({'source_sha256':sha,'source_objects':inventory,'groups':groups,'assets':assets,'bake':'2K per numbered locker; separate fixed body, punched leaf, and cam. Source coordinates and material variants retained.'},indent=2));print('LOCKER_EXPORT_COMPLETE',flush=True)

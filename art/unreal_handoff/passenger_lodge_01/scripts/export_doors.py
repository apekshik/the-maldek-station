"""Bake opaque door finishes as atlases, then separate the authored controls.
Only PLD delivery objects are read. Patched architectural geometry is already
present in the shell/deck checkpoint and is deliberately not exported here.
"""
import bpy,json,hashlib,math,bmesh
from pathlib import Path
from mathutils import Vector,Matrix
OUT=Path(__file__).resolve().parents[1];REPO=OUT.parents[2];dest=OUT/'doors'
for sub in ['fbx','textures']:(dest/sub).mkdir(parents=True,exist_ok=True)
src=REPO/'art/blender/passenger_lodge_04/Maldek_Passenger_Lodge_Integrated.blend';sha=hashlib.sha256(src.read_bytes()).hexdigest();assert sha=='bcf7e6301aecedd83688488981fd58a5a9719d685ef975210eef9eeb7f753f6c'
bpy.ops.wm.open_mainfile(filepath=str(src));bpy.context.scene.frame_set(1);dg=bpy.context.evaluated_depsgraph_get();kit=bpy.data.collections['PLD_ASSETS'];specs=json.loads((REPO/'art/blender/passenger_lodge_doors_01/replacement_manifest.json').read_text())['doors']
objects=list(kit.all_objects);inventory=[{'name':o.name,'parent':o.parent.name if o.parent else None,'matrix':[list(r) for r in o.matrix_world],'type':o.type} for o in objects]
s=bpy.data.scenes.new('Door_Export');bpy.context.window.scene=s;s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=8;s.render.threads_mode='FIXED';s.render.threads=8;s.render.bake.use_selected_to_active=False;s.render.bake.margin=12;s.render.bake.use_clear=True;s.render.bake.normal_space='TANGENT';s.view_settings.view_transform='Standard'
materials={};assets=[];doors=[]
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
  if q.type=='NORMAL_MAP':q.uv_map='SourceUV'
 t=n.new('ShaderNodeTexImage');t.name='BAKE_TARGET';em=n.new('ShaderNodeEmission');em.name='BAKE_EMISSION';comb=n.new('ShaderNodeCombineColor');comb.name='BAKE_ORM';comb.mode='RGB';comb.inputs[0].default_value=1;p=next(q for q in n if q.type=='BSDF_PRINCIPLED')
 for sock,i in [('Roughness',1),('Metallic',2)]:
  v=p.inputs[sock]
  if v.is_linked:l.new(v.links[0].from_socket,comb.inputs[i])
  else:comb.inputs[i].default_value=v.default_value
 return m
for spec in specs:
 id=spec['id'];prefix='PLD_'+id+'_';root=bpy.data.objects[prefix+'ROOT'];hinge=bpy.data.objects[prefix+'LEAF_PIVOT'];H=hinge.matrix_world.copy();ext=spec['exterior'];W=spec['width'];side=spec['side'];center=side*.0525
 keyloc=Vector((W-.06,center-side*.086,1));K=H@Matrix.Translation(keyloc)@Matrix.Rotation(math.pi if ext>0 else 0,4,'Z')
 frames={'Leaf':H,'Glass':H,'FixedHardware':H,'KeyHousing':K,'KeyPlug':K@Matrix.Translation(Vector((0,-.034,0))),'InteriorKeyPlug':K@Matrix.Translation(Vector((0,.034,0)))@Matrix.Rotation(math.pi,4,'Z'),'FrontLever':bpy.data.objects[prefix+'HANDLE_'+('B' if ext>0 else 'A')].matrix_world.copy(),'BackLever':bpy.data.objects[prefix+'HANDLE_'+('A' if ext>0 else 'B')].matrix_world.copy(),'MovingLatch':H,'BottomSeal':H}
 keys=list(frames);copies=[];sources={k:[] for k in keys};glass_objects=[]
 for ob in objects:
  if not ob.name.startswith(prefix) or ob.type not in {'MESH','FONT','CURVE'}:continue
  name=ob.name[len(prefix):];role='Leaf'
  if not parented(ob,hinge):role='FixedHardware'
  elif name=='Glass':role='Glass'
  elif any(name.startswith(v) for v in ['Through_Leaf_Cylinder','Cylinder_Collar','Cylinder_Gasket']):role='KeyHousing'
  elif name.startswith('LATCH'):role='MovingLatch'
  elif name.startswith('BOTTOM_SEAL'):role='BottomSeal'
  elif ob.parent and 'HANDLE_' in ob.parent.name:role='FrontLever' if ob.parent.name.endswith('B' if ext>0 else 'A') else 'BackLever'
  elif ob.parent and 'KEY_PLUG_' in ob.parent.name:role='KeyPlug' if ob.parent.name.endswith('B' if ext>0 else 'A') else 'InteriorKeyPlug'
  sources[role].append(ob.name);me=bpy.data.meshes.new_from_object(ob.evaluated_get(dg),depsgraph=dg);copy=bpy.data.objects.new('EXPORT_'+ob.name,me);s.collection.objects.link(copy);copy.matrix_world=ob.matrix_world.copy()
  if role=='Glass':glass_objects.append(copy);continue
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
  im=bpy.data.images.new('PLD_'+id+'_'+channel,4096,4096,alpha=False);im.colorspace_settings.name='sRGB' if channel=='BaseColor' else 'Non-Color';im.generated_color=(.5,.5,1,1) if channel=='NormalGL' else (0,0,0,1)
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
  if role=='Glass':
   assert len(glass_objects)==1;part=glass_objects[0];me=part.data;me.transform(part.matrix_world);part.matrix_world=Matrix.Identity(4)
  else:
   me=ob.data.copy();bm=bmesh.new();bm.from_mesh(me);layer=bm.faces.layers.int['PartIndex'];bmesh.ops.delete(bm,geom=[f for f in bm.faces if f[layer]!=keys.index(role)],context='FACES');bm.to_mesh(me);bm.free();part=bpy.data.objects.new('EXPORT_PART',me);s.collection.objects.link(part)
  me.transform(target.inverted());me.materials.clear();me.materials.append(bpy.data.materials.new('Glass' if role=='Glass' else 'DoorAtlas'))
  for p in me.polygons:p.material_index=0
  name='SM_PLD_'+id+'_'+role;part.name=name;bpy.ops.object.select_all(action='DESELECT');part.select_set(True);bpy.context.view_layer.objects.active=part;file=dest/'fbx'/(name+'.fbx');bpy.ops.export_scene.fbx(filepath=str(file),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,bake_anim=False)
  lo=[min(v.co[j] for v in me.vertices) for j in range(3)];hi=[max(v.co[j] for v in me.vertices) for j in range(3)];assets.append({'name':name,'door':id,'role':role,'lo':lo,'hi':hi,'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'polygons':len(me.polygons)})
  local=H.inverted()@target;parts.append({'role':role,'mesh':name,'local_matrix':[list(r) for r in local],'sources':sources[role]});bpy.data.objects.remove(part,do_unlink=True)
 doors.append({'id':id,'hinge_matrix':[list(r) for r in H],'yaw':spec['yaw'],'open_angle':-side*100,'exterior':ext,'width':W,'height':spec['height'],'key_location_source':list(keyloc),'key_yaw':180 if ext>0 else 0,'textures':textures,'parts':parts,'leaf_collision_source':{'center':[W/2+.06,center-side*.086,(.018+spec['height']+.02)/2],'extent':[(W+.03)/2,.0225,(spec['height']+.002)/2]}});bpy.data.objects.remove(ob,do_unlink=True)
assert sum(len(p['sources']) for d in doors for p in d['parts'])==sum(o.type in {'MESH','FONT','CURVE'} for o in objects)
assert hashlib.sha256(src.read_bytes()).hexdigest()==sha
(dest/'exports.json').write_text(json.dumps({'source_sha256':sha,'source_objects':inventory,'doors':doors,'assets':assets,'bake':'4K BaseColor/ORM/NormalGL per door; generated coordinates retained, stable name-hashed variation; glass separate. Source animation remains in Blender; ten independent engine components per door.'},indent=2));print('DOOR_EXPORT_COMPLETE',flush=True)

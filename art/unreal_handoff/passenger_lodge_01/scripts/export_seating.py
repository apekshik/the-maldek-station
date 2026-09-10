"""Bake fitted seating with per-piece coordinates carried across assembly joins.
The master is read-only. Stable name-hashed variation replaces Blender object
random; generated coordinates and original UVs retain the source grain mapping.
"""
import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1];REPO=OUT.parents[2];dest=OUT/'seating';dest.mkdir(exist_ok=True)
for sub in ['fbx','textures']:(dest/sub).mkdir(exist_ok=True)
src=REPO/'art/blender/passenger_lodge_04/Maldek_Passenger_Lodge_Integrated.blend'
sha=hashlib.sha256(src.read_bytes()).hexdigest();assert sha=='bcf7e6301aecedd83688488981fd58a5a9719d685ef975210eef9eeb7f753f6c'
bpy.ops.wm.open_mainfile(filepath=str(src));bpy.context.scene.frame_set(1)
kit=bpy.data.collections['PLS_Seating_Kit'];objects=list(kit.all_objects);source_rows=[]
for ob in objects:
 if ob.type=='MESH':source_rows.append({'name':ob.name,'mesh':ob.data.name,'parent':ob.parent.name if ob.parent else None,'matrix':[list(r) for r in ob.matrix_world],'materials':[m.name for m in ob.data.materials]})
assert len(source_rows)==559
s=bpy.data.scenes.new('Seating_Export');bpy.context.window.scene=s
for ob in objects:s.collection.objects.link(ob);ob.hide_set(False);ob.hide_render=False
s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=8;s.render.threads_mode='FIXED';s.render.threads=8
s.render.bake.use_selected_to_active=False;s.render.bake.margin=12;s.render.bake.use_clear=True
s.render.bake.normal_space='TANGENT';s.render.bake.normal_r='POS_X';s.render.bake.normal_g='POS_Y';s.render.bake.normal_b='POS_Z'
s.view_settings.view_transform='Standard'
materials={}
for ob in objects:
 if ob.type!='MESH':continue
 ob.data=ob.data.copy()
 lo=[min(v.co[j] for v in ob.data.vertices) for j in range(3)];hi=[max(v.co[j] for v in ob.data.vertices) for j in range(3)]
 random_value=int(hashlib.sha256(ob.name.encode()).hexdigest()[:8],16)/4294967296
 for name,kind in [('SourceGenerated','FLOAT_VECTOR'),('SourceObject','FLOAT_VECTOR'),('SourceRandom','FLOAT')]:
  attr=ob.data.attributes.new(name,kind,'POINT')
  for v,q in zip(ob.data.vertices,attr.data):
   if kind=='FLOAT':q.value=random_value
   else:q.vector=[(v.co[j]-lo[j])/max(hi[j]-lo[j],1e-8) for j in range(3)] if name=='SourceGenerated' else v.co
 if not ob.data.uv_layers:ob.data.uv_layers.new(name='SourceUV')
 ob.data.uv_layers[0].name='SourceUV'
 for slot in ob.material_slots:
  orig=slot.material
  if orig.name not in materials:
   m=orig.copy();materials[orig.name]=m;n=m.node_tree.nodes;l=m.node_tree.links
   uv=n.new('ShaderNodeUVMap');uv.uv_map='SourceUV'
   attrs={}
   for name in ['SourceGenerated','SourceObject','SourceRandom']:
    attr=n.new('ShaderNodeAttribute');attr.attribute_name=name;attrs[name]=attr
   for tc in list(n):
    if tc.type=='TEX_COORD':
     for link in list(tc.outputs['UV'].links):l.new(uv.outputs[0],link.to_socket)
     for output,name in [('Generated','SourceGenerated'),('Object','SourceObject')]:
      for link in list(tc.outputs[output].links):l.new(attrs[name].outputs['Vector'],link.to_socket)
    if tc.type=='OBJECT_INFO':
     for link in list(tc.outputs['Random'].links):l.new(attrs['SourceRandom'].outputs['Fac'],link.to_socket)
    if tc.type=='NORMAL_MAP':tc.uv_map='SourceUV'
   image_node=n.new('ShaderNodeTexImage');image_node.name='EXPORT_BAKE_TARGET'
   p=next(x for x in n if x.type=='BSDF_PRINCIPLED');out=next(x for x in n if x.type=='OUTPUT_MATERIAL');em=n.new('ShaderNodeEmission');em.name='EXPORT_EMISSION'
   comb=n.new('ShaderNodeCombineColor');comb.mode='RGB';comb.name='EXPORT_ORM';comb.inputs[0].default_value=1
   for socket,index in [('Roughness',1),('Metallic',2)]:
    q=p.inputs[socket]
    if q.is_linked:l.new(q.links[0].from_socket,comb.inputs[index])
    else:comb.inputs[index].default_value=q.default_value
  slot.material=materials[orig.name]
records=[];assets=[];seen={}
for index in range(1,7):
 root=bpy.data.objects[f'PLS_Group_{index:02d}'];obs=[bpy.data.objects[r['name']] for r in sorted(source_rows,key=lambda x:x['name']) if r['parent']==root.name];pivot=root.matrix_world.translation.copy()
 bpy.ops.object.select_all(action='DESELECT')
 for ob in obs:ob.select_set(True);ob.data.uv_layers.new(name='BakeUV');ob.data.uv_layers.active_index=1
 bpy.context.view_layer.objects.active=obs[0]
 bpy.ops.object.join();ob=bpy.context.object;ob.data.uv_layers.active=ob.data.uv_layers['BakeUV']
 bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=math.radians(66),island_margin=.008,area_weight=.3,correct_aspect=True,scale_to_bounds=True);bpy.ops.object.mode_set(mode='OBJECT')
 print('ATLAS',index,ob.data.uv_layers.active.name,len(ob.data.vertices),len(ob.data.polygons),flush=True)
 textures={}
 for channel in ['BaseColor','ORM','NormalGL']:
  im=bpy.data.images.new(f'PLS_{index:02d}_{channel}',2048,2048,alpha=False);im.colorspace_settings.name='sRGB' if channel=='BaseColor' else 'Non-Color';im.generated_color=(0,0,0,1) if channel!='NormalGL' else (.5,.5,1,1)
  for m in materials.values():
   n=m.node_tree.nodes;l=m.node_tree.links;t=n['EXPORT_BAKE_TARGET'];t.image=im;n.active=t
   p=next(x for x in n if x.type=='BSDF_PRINCIPLED');out=next(x for x in n if x.type=='OUTPUT_MATERIAL');em=n['EXPORT_EMISSION']
   if channel=='NormalGL':l.new(p.outputs[0],out.inputs['Surface'])
   else:
    if channel=='ORM':l.new(n['EXPORT_ORM'].outputs[0],em.inputs['Color'])
    else:
     q=p.inputs['Base Color']
     for link in list(em.inputs['Color'].links):l.remove(link)
     if q.is_linked:l.new(q.links[0].from_socket,em.inputs['Color'])
     else:em.inputs['Color'].default_value=q.default_value
    l.new(em.outputs[0],out.inputs['Surface'])
  print('BAKING',index,channel,flush=True);bpy.ops.object.bake(type='NORMAL' if channel=='NormalGL' else 'EMIT',uv_layer='BakeUV')
  file=dest/'textures'/(im.name+'.png');im.filepath_raw=str(file);im.file_format='PNG';im.save();textures[channel]={'file':str(file.relative_to(dest)),'sha256':hashlib.sha256(file.read_bytes()).hexdigest()}
  for m in materials.values():m.node_tree.nodes['EXPORT_BAKE_TARGET'].image=None
  bpy.data.images.remove(im)
 # Destination UV0 is the bake layout. The source remains component-editable.
 ob.data.uv_layers.remove(ob.data.uv_layers['SourceUV']);ob.data.uv_layers.active_index=0;ob.data.uv_layers[0].active_render=True
 ob.data.materials.clear()
 for p in ob.data.polygons:p.material_index=0
 world=ob.matrix_world.copy();ob.parent=None;ob.data.transform(world)
 for v in ob.data.vertices:v.co-=pivot
 ob.matrix_world.identity();ob.name=f'SM_PLS_{index:02d}'
 lo=[min(v.co[j] for v in ob.data.vertices) for j in range(3)];hi=[max(v.co[j] for v in ob.data.vertices) for j in range(3)]
 signature=hashlib.sha256(json.dumps({'v':[[round(x,5) for x in v.co] for v in ob.data.vertices],'f':[list(p.vertices) for p in ob.data.polygons],'uv':[[round(x,5) for x in u.uv] for u in ob.data.uv_layers[0].data]}).encode()).hexdigest()
 name=seen.get(signature)
 if name is None:
  name=ob.name;seen[signature]=name;mat=bpy.data.materials.new('SeatingAtlas');ob.data.materials.append(mat)
  file=dest/'fbx'/(name+'.fbx');bpy.ops.export_scene.fbx(filepath=str(file),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,bake_anim=False)
  assets.append({'name':name,'lo':lo,'hi':hi,'vertices':len(ob.data.vertices),'polygons':len(ob.data.polygons),'sha256':hashlib.sha256(file.read_bytes()).hexdigest()})
 records.append({'label':f'MIG_PLS_{index:02d}','mesh':name,'pivot':list(pivot),'textures':textures,'sources':[r['name'] for r in source_rows if r['parent']==root.name]})
 bpy.data.objects.remove(ob,do_unlink=True)
 (dest/'progress.json').write_text(json.dumps({'complete_groups':index},indent=2))
assert hashlib.sha256(src.read_bytes()).hexdigest()==sha
(dest/'exports.json').write_text(json.dumps({'source_sha256':sha,'source_objects':source_rows,'assets':assets,'placements':records,'tables':6,'benches':12,'heights_m':[.78,.48],'bake':'2048 per group; base color, ORM (AO=1), tangent OpenGL normal. Source UV/generated coordinates retained as attributes. Stable name-hashed per-board variation substitutes Blender object random. No lighting baked.'},indent=2))
print('SEATING_EXPORT_COMPLETE',len(assets),flush=True)

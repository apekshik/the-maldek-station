"""Export only the west-services delta; preserve source and bake procedural coordinates before grouping."""
import bpy,bmesh,json,hashlib,math,re
from pathlib import Path
from mathutils import Vector,Matrix
P=Path(__file__).resolve().parents[1];src=P.parents[1]/'blender/station_dressing_01/Maldek_Station_Furnished.blend'
for f in ['fbx','textures']:(P/f).mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(src));scene=bpy.context.scene;scene.frame_set(1);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
shelf_moves=['WSR_Equipment_shelf','WSR_Shelf_bracket','WSR_Shelf_bracket.001','WSR_First_aid_bag','WSR_Bag_zipper','WSR_Bag_handle_upright','WSR_Bag_handle_upright.001','WSR_Bag_handle']
for n in shelf_moves:bpy.data.objects[n].location.x+=1.25
bpy.context.view_layer.update()
nonblocking={'WSP_Door_jamb_seal','WSP_Door_head_seal','WSR_Door_seal','WSR_Door_seal.001','WSR_Head_seal'}|{o.name for o in scene.objects if o.name.startswith(('WSE_Hinge_barrel','WSE_Cover_fastener'))}
inv=json.loads((P/'source_inventory.json').read_text());sha=hashlib.sha256(src.read_bytes()).hexdigest();assert sha==inv['sha256']
controls={}
for package in ['parcels','rescue','power']:
 d=json.loads((P.parents[1]/('blender/west_services_'+package+'_01/assembly.json')).read_text());ms=d['mechanisms'];ms=ms.items() if isinstance(ms,dict) else [(q.get('object',q.get('pivot')),q) for q in ms]
 for name,q in ms:
  if not any(k in name.lower() for k in ['hinge','slide']):continue
  axis=q.get('axis');axis='XYZ'[axis] if isinstance(axis,int) else axis
  slide=q.get('kind')=='TRANSLATION';angle=q.get('open_degrees',q.get('open',0));angle=math.degrees(angle-q.get('rest',0)) if package=='parcels' and not slide else angle
  if name=='WSE_Engine_cover_hinge':angle=-100
  root=bpy.data.objects[name];M=root.matrix_world.copy()
  if not slide and axis!='Z':M=M@Vector(tuple(1 if k==axis else 0 for k in 'XYZ')).to_track_quat('Z','Y').to_matrix().to_4x4()
  controls[name]={'matrix':[list(r) for r in M],'slide':slide,'angle':angle if not slide else 0,'offset':[q['open']-q['rest'] if k==axis else 0 for k in 'XYZ'] if slide else [0,0,0],'axis_source':axis,'collisions':[]}
export=bpy.data.scenes.new('West_Export');bpy.context.window.scene=export
export.render.engine='CYCLES';export.cycles.samples=4;export.render.bake.margin=8;export.render.bake.use_clear=True
try:
 pr=bpy.context.preferences.addons['cycles'].preferences;pr.compute_device_type='OPTIX';pr.get_devices()
 for d in pr.devices:d.use=d.type=='OPTIX'
 if any(d.use for d in pr.devices):export.cycles.device='GPU'
except Exception:pass
rows={};copies=[];matcopies={};complexmats=set();simple={}
def safe(n):return re.sub('[^A-Za-z0-9_]','_',n)
for row in inv['objects']:
 if row['type'] not in ['MESH','FONT','CURVE'] or any('REVIEW' in c for c in row['collections']):continue
 o=scene.objects[row['name']];ancestor=o;control=None
 while ancestor:
  if ancestor.name in controls:control=ancestor.name;break
  ancestor=ancestor.parent
 if control:key=control;M=Matrix(controls[control]['matrix'])
 else:
  center=[(a+b)/2 for a,b in zip(row['lo'],row['hi'])];package=next(c for c in row['collections'] if 'REVIEW' not in c)
  # localized static chunks, separately owned by collection
  key=('NONBLOCK_Hardware' if o.name in nonblocking else package)+'_'+str(math.floor(center[0]/4))+'_'+str(math.floor(center[1]/4));M=Matrix.Translation(Vector((math.floor(center[0]/4)*4,math.floor(center[1]/4)*4,0)))
 if key not in rows:rows[key]={'id':len(rows),'key':key,'matrix':[list(r) for r in M],'sources':[],'control':controls.get(control),'nonblocking':o.name in nonblocking}
 r=rows[key];r['sources'].append(o.name)
 me=bpy.data.meshes.new_from_object(o.evaluated_get(dg),depsgraph=dg)
 if not len(me.vertices):continue
 # Bake source generated/object coordinates before station transform.
 lo=[min(v.co[j] for v in me.vertices) for j in range(3)];hi=[max(v.co[j] for v in me.vertices) for j in range(3)]
 for an in ['SourceGenerated','SourceObject']:
  attr=me.attributes.new(an,'FLOAT_VECTOR','POINT')
  for v,q in zip(me.vertices,attr.data):q.vector=[(v.co[j]-lo[j])/max(hi[j]-lo[j],1e-8) for j in range(3)] if an=='SourceGenerated' else v.co
 if not me.uv_layers:me.uv_layers.new(name='SourceUV')
 me.uv_layers[0].name='SourceUV';attr=me.attributes.new('ExportGroup','INT','FACE')
 for q in attr.data:q.value=r['id']
 me.transform(o.matrix_world);ob=bpy.data.objects.new('E_'+o.name,me);export.collection.objects.link(ob);copies.append(ob)
 if control and o.type=='MESH':
  vv=[M.inverted()@o.matrix_world@Vector(v) for v in o.bound_box];a=[min(v[j] for v in vv) for j in range(3)];b=[max(v[j] for v in vv) for j in range(3)];dims=[b[j]-a[j] for j in range(3)]
  if sorted(dims)[1]>.08 and max(dims)>.18 and not any(n in o.name.lower() for n in ['hinge','knuckle','pin','glass','letter','text']):r['control']['collisions'].append({'source':o.name,'center':[(a[j]+b[j])/2 for j in range(3)],'extent':[max(.006,(b[j]-a[j])/2) for j in range(3)]})
 for slot in ob.material_slots:
  orig=slot.material
  if not orig:continue
  if orig.name not in matcopies:
   m=orig.copy();m.name='EX_'+orig.name;matcopies[orig.name]=m;n=m.node_tree.nodes;l=m.node_tree.links;bs=next(x for x in n if x.type=='BSDF_PRINCIPLED');iscomplex=any(bs.inputs[k].is_linked for k in ['Base Color','Roughness','Metallic','Normal'])
   if iscomplex:
    complexmats.add(orig.name);uv=n.new('ShaderNodeUVMap');uv.uv_map='SourceUV'
    for node in list(n):
     if node.type=='TEX_COORD':
      for output in ['Generated','Object','UV']:
       a=n.new('ShaderNodeAttribute') if output!='UV' else uv
       if output!='UV':a.attribute_name='Source'+output
       for link in list(node.outputs[output].links):l.new(a.outputs['Vector'] if output!='UV' else a.outputs[0],link.to_socket)
    # Implicit noise coordinates are Generated too.
    for node in list(n):
     if node.type=='TEX_NOISE' and not node.inputs['Vector'].is_linked:
      a=n.new('ShaderNodeAttribute');a.attribute_name='SourceGenerated';l.new(a.outputs['Vector'],node.inputs['Vector'])
   simple[orig.name]={'color':list(bs.inputs['Base Color'].default_value),'roughness':bs.inputs['Roughness'].default_value,'metallic':bs.inputs['Metallic'].default_value,'glass':'glass' in orig.name.lower()}
  slot.material=matcopies[orig.name]
# Consolidate each material for a shared bake, retaining face group IDs.
byMat={}
for ob in copies:
 if len(ob.data.materials)==1:
  name=next(k for k,v in matcopies.items() if v==ob.data.materials[0]);byMat.setdefault(name,[]).append(ob)
 else:
  for idx,m in enumerate(list(ob.data.materials)):
   me=ob.data.copy();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.material_index!=idx],context='FACES')
   if not bm.faces:bm.free();bpy.data.meshes.remove(me);continue
   for f in bm.faces:f.material_index=0
   bm.to_mesh(me);bm.free();me.materials.clear();me.materials.append(m);oo=bpy.data.objects.new('SPLIT',me);export.collection.objects.link(oo);name=next(k for k,v in matcopies.items() if v==m);byMat.setdefault(name,[]).append(oo)
  bpy.data.objects.remove(ob,do_unlink=True)
parts={r['id']:[] for r in rows.values()};textures={}
for name,obs in byMat.items():
 bpy.ops.object.select_all(action='DESELECT')
 for ob in obs:ob.select_set(True)
 bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join();ob=bpy.context.object;m=matcopies[name]
 if name in complexmats:
  ob.data.uv_layers.new(name='BakeUV');ob.data.uv_layers.active=ob.data.uv_layers['BakeUV'];bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=1.15,island_margin=.003,area_weight=.3);bpy.ops.object.mode_set(mode='OBJECT')
  n=m.node_tree.nodes;l=m.node_tree.links;bs=next(x for x in n if x.type=='BSDF_PRINCIPLED');out=next(x for x in n if x.type=='OUTPUT_MATERIAL');em=n.new('ShaderNodeEmission');target=n.new('ShaderNodeTexImage');n.active=target;tex={}
  for channel in ['BaseColor','NormalGL']:
   im=bpy.data.images.new(safe(name)+'_'+channel,2048,2048,alpha=False);im.colorspace_settings.name='sRGB' if channel=='BaseColor' else 'Non-Color';target.image=im
   if channel=='BaseColor':
    q=bs.inputs['Base Color']
    if q.is_linked:l.new(q.links[0].from_socket,em.inputs['Color'])
    else:em.inputs['Color'].default_value=q.default_value
    l.new(em.outputs[0],out.inputs['Surface']);bpy.ops.object.bake(type='EMIT')
   else:l.new(bs.outputs[0],out.inputs['Surface']);bpy.ops.object.bake(type='NORMAL')
   path=P/'textures'/(safe(name)+'_'+channel+'.png');im.filepath_raw=str(path);im.file_format='PNG';im.save();tex[channel]=path.name
  textures[name]=tex;print('BAKED',name,flush=True)
 # Split by stable face ownership after baking, preserving UVs.
 gids=set(a.value for a in ob.data.attributes['ExportGroup'].data)
 for gid in gids:
  me=ob.data.copy();bm=bmesh.new();bm.from_mesh(me);layer=bm.faces.layers.int.get('ExportGroup');bmesh.ops.delete(bm,geom=[f for f in bm.faces if f[layer]!=gid],context='FACES');bm.to_mesh(me);bm.free();oo=bpy.data.objects.new('PART_'+str(gid),me);export.collection.objects.link(oo);parts[gid].append(oo)
 bpy.data.objects.remove(ob,do_unlink=True)
assets=[]
for r in rows.values():
 obs=parts[r['id']];bpy.ops.object.select_all(action='DESELECT')
 for ob in obs:ob.select_set(True)
 bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join();ob=bpy.context.object;M=Matrix(r['matrix']);ob.data.transform(M.inverted());ob.data.update();name='SM_WS_'+safe(r['key']);ob.name=name
 r['mesh']=name;r['materials']=[next(k for k,v in matcopies.items() if v==m) for m in ob.data.materials];r['lo']=[min(v.co[j] for v in ob.data.vertices) for j in range(3)];r['hi']=[max(v.co[j] for v in ob.data.vertices) for j in range(3)];r['vertices']=len(ob.data.vertices)
 if r['control'] and not r['control']['collisions']:
  a,b=r['lo'],r['hi'];r['control']['collisions']=[{'source':'Wire door blocking envelope','center':[(a[j]+b[j])/2 for j in range(3)],'extent':[max(.006,(b[j]-a[j])/2-.003) for j in range(3)]}]
 bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free()
 path=P/'fbx'/(name+'.fbx');bpy.ops.export_scene.fbx(filepath=str(path),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,bake_anim=False,use_tspace=True,mesh_smooth_type='FACE');r['sha256']=hashlib.sha256(path.read_bytes()).hexdigest();assets.append(r)
 bpy.data.objects.remove(ob,do_unlink=True)
(P/'exports.json').write_text(json.dumps({'source':str(src),'source_sha256':sha,'assets':assets,'materials':simple,'textures':textures,'integration_repairs':{'shelf_shift_x_m':1.25,'shelf_objects':shelf_moves,'nonblocking_hardware':sorted(nonblocking),'engine_cover_degrees':-100}},indent=2));print('EXPORT COMPLETE',len(assets),sum(len(r['sources']) for r in assets),flush=True)

"""Bake evaluated Blender surface shaders into reusable 2K BC, DirectX normal and ORM sets."""
import bpy,json,hashlib,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
OUT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(OUT.parents[2]/'art/blender/visual_fidelity_09/Maldek_Service_Apron_Refinement.blend'),load_ui=False)
source=bpy.context.scene;deps=bpy.context.evaluated_depsgraph_get()
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
manifest_name=args[0] if args else 'probe_manifest.json'
handoff=json.loads((OUT/'handoff_manifest.json').read_text());handoff['materials']={k:v for k,v in handoff['materials'].items() if v['source_material']=='VF08_Oxide_Red'}
folder=OUT/'textures';folder.mkdir(exist_ok=True)
report_path=OUT/'baked_materials.json'
report=json.loads(report_path.read_text()) if report_path.exists() else {'sets':{},'materials':{}}
def value(v):
 if isinstance(v,(str,bool,int,float)):return v
 try:return list(v)
 except Exception:return getattr(v,'name',str(type(v)))
def fingerprint(m):
 nodes=list(m.node_tree.nodes);rows=[]
 for n in nodes:
  row={'type':n.bl_idname,'inputs':{s.identifier:value(s.default_value) for s in n.inputs if hasattr(s,'default_value')}}
  for attr in ['operation','blend_type','projection','noise_dimensions','normalize','interpolation']:
   if hasattr(n,attr):row[attr]=value(getattr(n,attr))
  if hasattr(n,'color_ramp'):row['ramp']=[[e.position,list(e.color)] for e in n.color_ramp.elements]
  if n.type=='TEX_IMAGE' and n.image:row['image']=n.image.filepath
  rows.append(row)
 links=[(nodes.index(l.from_node),l.from_socket.identifier,nodes.index(l.to_node),l.to_socket.identifier) for l in m.node_tree.links]
 return hashlib.sha256(json.dumps([rows,links],sort_keys=True).encode()).hexdigest()
scene=bpy.data.scenes.new('R12_Surface_Bake');bpy.context.window.scene=scene
scene.render.engine='CYCLES';scene.cycles.samples=16;scene.cycles.use_denoising=False
prefs=bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type='OPTIX';prefs.get_devices()
for device in prefs.devices:device.use=device.type=='OPTIX'
scene.cycles.device='GPU'
scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB';scene.render.image_settings.color_depth='8'
scene.render.bake.use_clear=True;scene.render.bake.margin=8
scene.render.bake.normal_space='TANGENT';scene.render.bake.normal_r='POS_X';scene.render.bake.normal_g='NEG_Y';scene.render.bake.normal_b='POS_Z'
me=bpy.data.meshes.new('Eight_metre_surface');me.from_pydata([(-4,-4,0),(4,-4,0),(4,4,0),(-4,4,0)],[],[(0,1,2,3)]);me.update()
uv=me.uv_layers.new(name='SurfaceUV')
for i,p in enumerate([(0,0),(1,0),(1,1),(0,1)]):uv.data[i].uv=p
plane=bpy.data.objects.new('Bake_surface',me);scene.collection.objects.link(plane);plane.select_set(True);bpy.context.view_layer.objects.active=plane
for name,info in sorted(handoff['materials'].items()):
 original=bpy.data.materials[info.get('source_material',name)];key=fingerprint(original)
 cached=report['sets'].get(key)
 if cached and all((OUT/p).exists() for p in cached['textures'].values()):
  report['materials'][name]={'set':key,**info};continue
 material=original.copy();me.materials.clear();me.materials.append(material)
 nodes=material.node_tree.nodes;links=material.node_tree.links
 principled=next(n for n in nodes if n.type=='BSDF_PRINCIPLED')
 output=next(n for n in nodes if n.type=='OUTPUT_MATERIAL' and n.is_active_output)
 original_surface=output.inputs['Surface'].links[0].from_socket
 emission=nodes.new('ShaderNodeEmission');emission.inputs['Strength'].default_value=1
 target=nodes.new('ShaderNodeTexImage');textures={};ranges={}
 for channel in ['BaseColor','ORM','NormalDX']:
  image=bpy.data.images.new('Bake_'+channel,width=2048,height=2048,alpha=False,float_buffer=False)
  image.colorspace_settings.name='sRGB' if channel=='BaseColor' else 'Non-Color'
  target.image=image
  for n in nodes:n.select=False
  target.select=True;nodes.active=target
  if channel=='NormalDX':links.new(original_surface,output.inputs['Surface']);kind='NORMAL'
  else:
   links.new(emission.outputs[0],output.inputs['Surface']);kind='EMIT'
   if channel=='BaseColor':
    inp=principled.inputs['Base Color']
    if inp.is_linked:links.new(inp.links[0].from_socket,emission.inputs['Color'])
    else:emission.inputs['Color'].default_value=inp.default_value
   else:
    combine=nodes.new('ShaderNodeCombineColor');combine.mode='RGB';combine.inputs[0].default_value=1
    for index,param in [(1,'Roughness'),(2,'Metallic')]:
     inp=principled.inputs[param]
     if inp.is_linked:links.new(inp.links[0].from_socket,combine.inputs[index])
     else:combine.inputs[index].default_value=inp.default_value
    links.new(combine.outputs[0],emission.inputs['Color'])
  print('BAKING',name,channel,flush=True)
  bpy.ops.object.bake(type=kind,use_selected_to_active=False)
  path=folder/f'T_R12_{key[:16]}_{channel}.png';image.filepath_raw=str(path);image.file_format='PNG';image.save()
  textures[channel]=str(path.relative_to(OUT));ranges[channel]={'width':2048,'height':2048,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
  bpy.data.images.remove(image)
 report['sets'][key]={'textures':textures,'files':ranges,'source_material':name,'tile_metres':8,'pixels_per_metre':256,'normal_convention':'DirectX (-Y tangent normal)','occlusion':'1 for a shared unoccluded surface; geometric contact/shadowing remains real-time','base_color':'Evaluated shader color without scene lighting','orm_channels':['occlusion','roughness','metallic']}
 report['materials'][name]={'set':key,**info};report_path.write_text(json.dumps(report,indent=2))
 bpy.data.materials.remove(material)
report_path.write_text(json.dumps(report,indent=2))
print('SURFACE_BAKES_COMPLETE',len(report['sets']),flush=True)

"""Translate the authored shell palette and finishes into migration-owned graphs."""
import unreal,json,hashlib,re
from pathlib import Path
OUT=Path(__file__).resolve().parents[1];REPO=OUT.parents[2];root='/Game/MaldekRefinement/PassengerLodge/Surfaces'
ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert w.get_name()=='Station_Lodge_Migration' and not ls.is_in_play_in_editor()
lib=unreal.EditorAssetLibrary;at=unreal.AssetToolsHelpers.get_asset_tools();ml=unreal.MaterialEditingLibrary
data=json.loads((OUT/'material_audit.json').read_text());baseline=json.loads((OUT/'before.json').read_text());o=baseline['origin'];created=[];bindings={};report=[]
baked=json.loads((REPO/'art/unreal_handoff/revision12/baked_materials.json').read_text())
def node(m,kind,**props):
 n=ml.create_material_expression(m,getattr(unreal,'MaterialExpression'+kind))
 for k,v in props.items():n.set_editor_property(k,v)
 return n
def con(a,b,pin='',output=''):assert ml.connect_material_expressions(a,output,b,pin),(a.get_class().get_name(),pin,output)
def prop(a,key,output=''):assert ml.connect_material_property(a,output,getattr(unreal.MaterialProperty,'MP_'+key)),key
def num(m,x):return node(m,'Constant',r=float(x))
def vec(m,x):return node(m,'Constant3Vector',constant=unreal.LinearColor(*x[:3],1))
def calc(m,kind,a,b):
 n=node(m,kind);con(a,n,'A');con(b,n,'B');return n
def mix(m,a,b,t):
 n=node(m,'LinearInterpolate');con(a,n,'A');con(b,n,'B');con(t,n,'Alpha');return n
def custom(m,code,inputs,out=unreal.CustomMaterialOutputType.CMOT_FLOAT1):
 pins=[]
 for k in inputs:
  pin=unreal.CustomInput();pin.set_editor_property('input_name',k);pins.append(pin)
 n=node(m,'Custom',code=code,output_type=out,inputs=pins)
 for k,v in inputs.items():con(v,n,k)
 return n
def pos(m):
 world=node(m,'WorldPosition');offset=calc(m,'Subtract',world,vec(m,o));return calc(m,'Multiply',offset,vec(m,[-.01,.01,.01])),world
def bump(m,height,world,amount):
 nrm=node(m,'VertexNormalWS')
 n=custom(m,'float3 dx=ddx(P),dy=ddy(P); float3 r1=cross(dy,N),r2=cross(N,dx); float det=dot(dx,r1); return normalize(N-sign(det)*(ddx(H)*r1+ddy(H)*r2)*S/max(abs(det),1e-6));',{'P':world,'N':nrm,'H':height,'S':num(m,amount)},unreal.CustomMaterialOutputType.CMOT_FLOAT3)
 m.set_editor_property('tangent_space_normal',False);prop(n,'NORMAL')
textures={}
for key in ['diff','rough','nor_gl']:
 path=REPO/'art/blender/passenger_lodge_shell_01/textures'/f'plastered_wall_04_{key}_4k.jpg';name='T_Lodge_Plaster_'+key;dst=root+'/Textures/'+name
 tex=lib.load_asset(dst)
 if not tex:
  t=unreal.AssetImportTask();t.filename=str(path);t.destination_path=root+'/Textures';t.destination_name=name;t.automated=True;t.save=True;at.import_asset_tasks([t]);tex=lib.load_asset(dst)
 assert tex
 tex.set_editor_property('srgb',key=='diff');tex.set_editor_property('compression_settings',unreal.TextureCompressionSettings.TC_NORMALMAP if key=='nor_gl' else unreal.TextureCompressionSettings.TC_DEFAULT if key=='diff' else unreal.TextureCompressionSettings.TC_MASKS)
 if key=='nor_gl':tex.set_editor_property('flip_green_channel',True)
 assert lib.save_loaded_asset(tex);textures[key]=tex
def sample(m,key):return node(m,'TextureSample',texture=textures[key],sampler_type=unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL if key=='nor_gl' else unreal.MaterialSamplerType.SAMPLERTYPE_COLOR if key=='diff' else unreal.MaterialSamplerType.SAMPLERTYPE_MASKS)
for name,info in data.items():
 clean=re.sub(r'[^a-zA-Z0-9_]','_',name);path=root+'/Materials/M_'+clean
 if JOB.get('resume'):
  m=lib.load_asset(path);assert m,path;bindings[name]=m;created.append(m)
  mode='existing Blender-baked station BaseColor/ORM/NormalDX; source-metre triplanar mapping' if name.startswith(('VF06_','VF07_')) else 'original plaster maps and dado height' if name=='PLSH_Painted_Plaster' else '300mm quarry tiles and 4mm grout' if name=='PLSH_Quarry_Floor' else 'local frosted scene transmission' if 'Opal_Glass' in name else 'authored constant finish / clear-pane settings'
  report.append({'source':name,'asset':path,'translation':mode});continue
 m=lib.load_asset(path) or at.create_asset('M_'+clean,root+'/Materials',unreal.Material,unreal.MaterialFactoryNew());ml.delete_all_material_expressions(m)
 m.set_editor_property('blend_mode',unreal.BlendMode.BLEND_OPAQUE);m.set_editor_property('two_sided',False);m.set_editor_property('tangent_space_normal',True)
 bs=next(n for n in info['nodes'] if n['type']=='BSDF_PRINCIPLED')['inputs'];color=vec(m,bs['Base Color']);rough=num(m,bs['Roughness']);metal=num(m,bs['Metallic']);p,world=pos(m);mode='constant authored finish'
 ramps=[n for n in info['nodes'] if n['type']=='VALTORGB']
 if name.startswith(('VF06_','VF07_')) and ramps:
  source_name=re.sub(r'\.\d+$','',name);entry=next(v for v in baked['materials'].values() if v['source_material']==source_name);texture_set=baked['sets'][entry['set']];sn=calc(m,'Multiply',node(m,'VertexNormalWS'),vec(m,[-1,1,1]));samples={}
  for channel,file in texture_set['textures'].items():
   tex=lib.load_asset('/Game/MaldekRefinement/R12/Textures/'+Path(file.replace('\\','/')).stem);assert tex,file
   obj=node(m,'TextureObject',texture=tex,sampler_type=unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL if channel=='NormalDX' else unreal.MaterialSamplerType.SAMPLERTYPE_MASKS if channel=='ORM' else unreal.MaterialSamplerType.SAMPLERTYPE_COLOR)
   prefix='float3 w=pow(abs(N),4); w/=max(dot(w,float3(1,1,1)),1e-6); float3 q=P/T; '
   if channel=='NormalDX':
    code=prefix+'float3 a=UnpackNormalMap(Texture2DSample(Tex,TexSampler,float2(q.y,-q.z))); float3 b=UnpackNormalMap(Texture2DSample(Tex,TexSampler,float2(q.x,-q.z))); float3 c=UnpackNormalMap(Texture2DSample(Tex,TexSampler,float2(q.x,-q.y))); float3 r=normalize(float3(a.z*sign(N.x),a.x,-a.y)*w.x+float3(b.x,b.z*sign(N.y),-b.y)*w.y+float3(c.x,-c.y,c.z*sign(N.z))*w.z); return r*float3(-1,1,1);'
   else:code=prefix+'return Texture2DSample(Tex,TexSampler,float2(q.y,-q.z)).rgb*w.x+Texture2DSample(Tex,TexSampler,float2(q.x,-q.z)).rgb*w.y+Texture2DSample(Tex,TexSampler,float2(q.x,-q.y)).rgb*w.z;'
   samples[channel]=custom(m,code,{'P':p,'N':sn,'T':num(m,texture_set['tile_metres']),'Tex':obj},unreal.CustomMaterialOutputType.CMOT_FLOAT3)
  color=samples['BaseColor'];rough=custom(m,'return V.g;',{'V':samples['ORM']});metal=custom(m,'return V.b;',{'V':samples['ORM']});m.set_editor_property('tangent_space_normal',False);prop(samples['NormalDX'],'NORMAL')
  mode='existing Blender-baked station BaseColor/ORM/NormalDX; source-metre triplanar mapping'
 elif name=='PLSH_Painted_Plaster':
  low=custom(m,'return P.z < 5.05 ? 1.0 : 0.0;',{'P':p});paint=mix(m,vec(m,[.57,.51,.40]),vec(m,[.085,.14,.115]),low)
  diffuse=sample(m,'diff');color=calc(m,'Multiply',paint,mix(m,vec(m,[1,1,1]),diffuse,num(m,.18)))
  r=sample(m,'rough');rough=custom(m,'return lerp(.56,.78,R.r);',{'R':r})
  normal=sample(m,'nor_gl');normal=custom(m,'return normalize(float3(N.xy*.16,N.z));',{'N':normal},unreal.CustomMaterialOutputType.CMOT_FLOAT3);prop(normal,'NORMAL')
  mode='original 4K CC0 maps; original 3.2m planar UVs; 1.05m dado height'
 elif name=='PLSH_Quarry_Floor':
  # Source geometry-position tile layout: 300mm square tiles and 4mm mortar.
  grout=custom(m,'float2 q=P.xy/.3; float2 edge=min(frac(q),1-frac(q))*.3; float a=max(fwidth(P.x),fwidth(P.y)); return 1-smoothstep(.004-a,.004+a,min(edge.x,edge.y));',{'P':p})
  variation=custom(m,'float2 c=floor(P.xy/.3); return frac(sin(dot(c,float2(12.9898,78.233)))*43758.5453);',{'P':p})
  color=mix(m,mix(m,vec(m,[.23,.13,.075]),vec(m,[.31,.19,.105]),variation),vec(m,[.075,.065,.05]),grout)
  bump(m,grout,world,-.0375);mode='300mm world-position quarry tiles; 4mm grout; authored palette'
 elif 'Glass' in name:
  m.set_editor_property('blend_mode',unreal.BlendMode.BLEND_TRANSLUCENT);m.set_editor_property('two_sided',True)
  if 'Opal' in name:
   total=None;weights=[1,2,1]
   for x in range(-1,2):
    for y in range(-1,2):
     sc=node(m,'SceneColor',input_mode=getattr(unreal.MaterialSceneAttributeInputMode,next(k for k in unreal.MaterialSceneAttributeInputMode.__dict__ if 'OFFSET' in k.upper())),const_input=unreal.Vector2D(x*.006,y*.006));term=calc(m,'Multiply',sc,num(m,weights[x+1]*weights[y+1]/16*.85));total=calc(m,'Add',total,term) if total else term
   prop(total,'EMISSIVE_COLOR');prop(num(m,1),'OPACITY');mode='local 9-tap frosted scene transmission; rough specular surface'
  else:prop(num(m,.09),'OPACITY');mode='inner clear pane; translucent roughness 0.08'
 prop(color,'BASE_COLOR');prop(rough,'ROUGHNESS');prop(metal,'METALLIC')
 surface='Metal' if bs['Metallic']>.05 or name.startswith('VF06_') and 'Concrete' not in name else 'Concrete'
 pm=lib.load_asset('/Game/MaldekRefinement/ForestTest/Audio/Surfaces/PM_'+surface)
 if pm:m.set_editor_property('phys_material',pm)
 ml.recompile_material(m);assert lib.save_loaded_asset(m);created.append(m);bindings[name]=m;report.append({'source':name,'asset':path,'translation':mode})
errors=list(unreal.StationMigrationLibrary.validate_material_shaders(created));assert not errors,errors
for kind in ['Shell','Deck']:
 manifest=json.loads((OUT/(kind.lower()+'_exports.json')).read_text())
 for r in manifest['assets']:
  mesh=lib.load_asset('/Game/MaldekRefinement/PassengerLodge/'+kind+'Pilot/Meshes/'+r['name']);assert mesh
  assert len(mesh.static_materials)==len(r['materials'])
  changed=False
  for i,mat in enumerate(r['materials']):
   if mesh.get_material(i)!=bindings[mat]:mesh.set_material(i,bindings[mat]);changed=True
  if changed:assert lib.save_loaded_asset(mesh)
assert hashlib.sha256((REPO/'game/Content/MaldekRefinement/R12/Station_R12.umap').read_bytes()).hexdigest()==baseline['map_sha256']
RESULT={'materials':report,'shader_errors':errors,'original_map_unchanged':True,'source_textures':['art/blender/passenger_lodge_shell_01/texture_sources.json','art/unreal_handoff/revision12/baked_materials.json'],'limitations':'Tile randomization translated to UE. No weather accumulation function added. Frosted glass uses local screen-space transmission.'}
(OUT/'surface_materials.json').write_text(json.dumps(RESULT,indent=2))

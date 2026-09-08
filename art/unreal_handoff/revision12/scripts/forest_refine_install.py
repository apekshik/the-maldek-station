"""Install reversible R12 terrain and materials; never edit sky or weather."""
import unreal,json,shutil,time
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'forest_refine';root='/Game/MaldekRefinement/R12/ForestRefine'
ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);actors={a.get_actor_label():a for a in aa.get_all_level_actors()}
lib=unreal.EditorAssetLibrary;at=unreal.AssetToolsHelpers.get_asset_tools();ml=unreal.MaterialEditingLibrary
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert w.get_name()=='Station_R12'
# Save current user lighting before the first change, keeping a local rollback map.
backup=out/'backup/Station_R12.umap'
if not backup.exists():
 assert ls.save_current_level();backup.parent.mkdir(exist_ok=True);shutil.copy2(b.parents[2]/'game/Content/MaldekRefinement/R12/Station_R12.umap',backup)
def material(name):
 m=lib.load_asset(root+'/Materials/'+name) or at.create_asset(name,root+'/Materials',unreal.Material,unreal.MaterialFactoryNew());ml.delete_all_material_expressions(m);return m
def node(m,kind,**props):
 n=ml.create_material_expression(m,getattr(unreal,'MaterialExpression'+kind))
 for k,v in props.items():n.set_editor_property(k,v)
 return n
def link(a,b,pin='',output=''):assert ml.connect_material_expressions(a,output,b,pin)
def scalar(m,value):return node(m,'Constant',r=value)
def mul(m,a,b):
 n=node(m,'Multiply');link(a,n,'A');link(b,n,'B');return n
def mix(m,a,b,t):
 n=node(m,'LinearInterpolate');link(a,n,'A');link(b,n,'B');link(t,n,'Alpha');return n
def tex(m,name,uv,normal=False):
 n=node(m,'TextureSample',texture=lib.load_asset('/Game/MWLandscapeAutoMaterial/Textures/Ground/TEX_MWAM_'+name));n.set_editor_property('sampler_type',unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL if normal else unreal.MaterialSamplerType.SAMPLERTYPE_COLOR);link(uv,n,'UVs');return n
m=material('M_Woodland_Ground');uv=node(m,'TextureCoordinate');soil=tex(m,'Dirt_col',uv);grass=tex(m,'Grass_col',uv)
pos=node(m,'WorldPosition');macro=node(m,'Noise',scale=.0015,levels=2)
alpha=mul(m,macro,scalar(m,.6));base=mix(m,mul(m,soil,scalar(m,.65)),mul(m,grass,scalar(m,.38)),alpha)
# Three planar samples avoid vertical streaks on the new descent.
normal=node(m,'VertexNormalWS');an=node(m,'Abs');link(normal,an);rockparts=[];weights=[]
for coord,axis in [('gb','r'),('rb','g'),('rg','b')]:
 mask=node(m,'ComponentMask',r='r' in coord,g='g' in coord,b='b' in coord);link(pos,mask)
 coords=mul(m,mask,scalar(m,.0025));sample=tex(m,'Rock_col',coords)
 weight=node(m,'ComponentMask',r=axis=='r',g=axis=='g',b=axis=='b');link(an,weight)
 power=node(m,'Power',const_exponent=4.);link(weight,power,'Base');weights.append(power);rockparts.append(mul(m,sample,power))
def add(a,c):
 n=node(m,'Add');link(a,n,'A');link(c,n,'B');return n
rocksum=add(add(rockparts[0],rockparts[1]),rockparts[2]);ws=add(add(weights[0],weights[1]),weights[2]);rock=node(m,'Divide');link(rocksum,rock,'A');link(ws,rock,'B')
nz=node(m,'ComponentMask',r=False,g=False,b=True);link(an,nz);inv=node(m,'OneMinus');link(nz,inv);slope=node(m,'Saturate');link(mul(m,inv,scalar(m,2.4)),slope)
color=mix(m,base,mul(m,rock,scalar(m,.55)),slope);ml.connect_material_property(color,'',unreal.MaterialProperty.MP_BASE_COLOR)
ml.connect_material_property(scalar(m,.92),'',unreal.MaterialProperty.MP_ROUGHNESS)
dn=tex(m,'Dirt_nrm',uv,True);ml.connect_material_property(dn,'RGB',unreal.MaterialProperty.MP_NORMAL)
m.set_editor_property('phys_material',lib.load_asset('/Game/MaldekRefinement/ForestTest/Audio/Surfaces/PM_Soil'));ml.recompile_material(m);lib.save_loaded_asset(m)
unreal.SystemLibrary.execute_console_command(w,'Interchange.FeatureFlags.Import.FBX 0')
t=unreal.AssetImportTask();t.filename=str(out/'SM_Forest_Refined_Terrain.fbx');t.destination_path=root+'/Meshes';t.automated=True;t.save=True;t.replace_existing=True
opt=unreal.FbxImportUI();opt.import_mesh=True;opt.import_materials=False;opt.import_textures=False;opt.automated_import_should_detect_type=False;opt.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
d=opt.static_mesh_import_data;d.combine_meshes=True;d.auto_generate_collision=False;d.convert_scene=True;d.convert_scene_unit=True;d.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_COMPUTE_NORMALS;t.options=opt;at.import_asset_tasks([t])
mesh=lib.load_asset(root+'/Meshes/SM_Forest_Refined_Terrain');assert mesh
mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE);mesh.set_material(0,m);lib.save_loaded_asset(mesh)
a=actors['VF10_Parking_Terrain'];c=a.static_mesh_component;c.set_static_mesh(mesh);c.set_editor_property('override_materials',[]);c.set_collision_profile_name('BlockAll');c.set_phys_material_override(lib.load_asset('/Game/MaldekRefinement/ForestTest/Audio/Surfaces/PM_Soil'))
# Retire the isolated pale scanned disks. Keep the parking pass's moved patch.
retired=[]
for label,a in actors.items():
 if label.startswith('FT_RockPatch_') and label!='FT_RockPatch_04':
  a.static_mesh_component.set_static_mesh(None);a.set_actor_hidden_in_game(True);a.set_is_temporarily_hidden_in_editor(True);a.set_actor_enable_collision(False);retired.append(label)
assert ls.save_current_level();(out/'install.json').write_text(json.dumps({'terrain':mesh.get_path_name(),'material':m.get_path_name(),'retired_rock_patches':retired,'backup':str(backup),'saved':True},indent=2));RESULT={'saved':True,'retired_rock_patches':len(retired)}

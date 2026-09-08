import unreal,json
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'gondola_mechanism';root='/Game/MaldekRefinement/R12/GondolaMechanism';lib=unreal.EditorAssetLibrary;at=unreal.AssetToolsHelpers.get_asset_tools();ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
# Rope strands are advected by measured travel, never by unbounded global time.
mat=lib.load_asset(root+'/Materials/M_Moving_Rope') or at.create_asset('M_Moving_Rope',root+'/Materials',unreal.Material,unreal.MaterialFactoryNew())
ml=unreal.MaterialEditingLibrary;ml.delete_all_material_expressions(mat)
def node(cls,**props):
 n=ml.create_material_expression(mat,getattr(unreal,'MaterialExpression'+cls))
 for k,v in props.items():n.set_editor_property(k,v)
 return n
def link(a,b,pin):
 assert ml.connect_material_expressions(a,'',b,pin),(str(a),str(b),pin)
def constant(v):return node('Constant',r=v)
uv=node('TextureCoordinate');u=node('ComponentMask',r=True,g=False,b=False,a=False);v=node('ComponentMask',r=False,g=True,b=False,a=False);link(uv,u,'');link(uv,v,'')
phase=node('ScalarParameter',parameter_name='RopeTravelMeters',default_value=0.);along=node('Subtract');link(u,along,'A');link(phase,along,'B')
lay=node('Multiply');link(along,lay,'A');link(constant(8),lay,'B');around=node('Multiply');link(v,around,'A');link(constant(6),around,'B');sumuv=node('Add');link(lay,sumuv,'A');link(around,sumuv,'B');sine=node('Sine');link(sumuv,sine,'');half=node('Multiply');link(sine,half,'A');link(constant(.5),half,'B');remap=node('Add');link(half,remap,'A');link(constant(.5),remap,'B')
color=node('LinearInterpolate');link(node('Constant3Vector',constant=unreal.LinearColor(.018,.023,.022,1)),color,'A');link(node('Constant3Vector',constant=unreal.LinearColor(.19,.22,.20,1)),color,'B');link(remap,color,'Alpha');ml.connect_material_property(color,'',unreal.MaterialProperty.MP_BASE_COLOR);ml.connect_material_property(constant(.7),'',unreal.MaterialProperty.MP_ROUGHNESS);ml.connect_material_property(constant(.45),'',unreal.MaterialProperty.MP_METALLIC);ml.recompile_material(mat);lib.save_loaded_asset(mat)

errors=list(unreal.StationMigrationLibrary.validate_material_shaders([mat]));assert not errors,errors
RESULT={'shader_errors':errors,'connections_checked':True};(out/'rope_shader.json').write_text(json.dumps(RESULT,indent=2))

import unreal
lib=unreal.EditorAssetLibrary;ml=unreal.MaterialEditingLibrary;root='/Game/MaldekRefinement/R06/Materials/'
def snow_blend(m,base):
 n=ml.create_material_expression(m,unreal.MaterialExpressionVertexNormalWS);mask=ml.create_material_expression(m,unreal.MaterialExpressionComponentMask);mask.set_editor_property('r',False);mask.set_editor_property('g',False);mask.set_editor_property('b',True);ml.connect_material_expressions(n,'',mask,'')
 clamp=ml.create_material_expression(m,unreal.MaterialExpressionClamp);assert ml.connect_material_expressions(mask,'',clamp,'')
 power=ml.create_material_expression(m,unreal.MaterialExpressionPower);power.set_editor_property('const_exponent',4);ml.connect_material_expressions(clamp,'',power,'Base')
 snow=ml.create_material_expression(m,unreal.MaterialExpressionConstant3Vector);snow.set_editor_property('constant',unreal.LinearColor(.38,.43,.49,1))
 lerp=ml.create_material_expression(m,unreal.MaterialExpressionLinearInterpolate);ml.connect_material_expressions(base,'RGB' if isinstance(base,unreal.MaterialExpressionTextureSample) else '',lerp,'A');ml.connect_material_expressions(snow,'',lerp,'B');ml.connect_material_expressions(power,'',lerp,'Alpha');ml.connect_material_property(lerp,'',unreal.MaterialProperty.MP_BASE_COLOR)
 r=ml.create_material_expression(m,unreal.MaterialExpressionConstant);r.r=.88;ml.connect_material_property(r,'',unreal.MaterialProperty.MP_ROUGHNESS)
 ml.recompile_material(m);lib.save_loaded_asset(m)
m=lib.load_asset(root+'M_Snowy_Terrain');ml.delete_all_material_expressions(m);m.set_editor_property('use_material_attributes',False)
b=ml.create_material_expression(m,unreal.MaterialExpressionConstant3Vector);b.set_editor_property('constant',unreal.LinearColor(.075,.083,.09,1));snow_blend(m,b)
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
 if a.get_actor_label() not in ['R04_13_Roofs','R04_01_Upper_Platform','R04_07_Overlook']:continue
 c=a.static_mesh_component
 for i in range(c.get_num_materials()):
  source=c.get_material(i)
  if not source or not isinstance(source,unreal.Material) or source.get_editor_property('blend_mode')!=unreal.BlendMode.BLEND_OPAQUE:continue
  dest=root+source.get_name()+'_Snow';m=lib.load_asset(dest)
  if not m:
   m=lib.duplicate_asset(source.get_path_name(),dest);base=ml.get_material_property_input_node(m,unreal.MaterialProperty.MP_BASE_COLOR)
   if base:snow_blend(m,base)
  c.set_material(i,m)
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()


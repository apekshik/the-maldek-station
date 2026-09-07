import unreal
lib=unreal.EditorAssetLibrary;ml=unreal.MaterialEditingLibrary;root='/Game/MaldekRefinement/R06/Materials/'
for path in lib.list_assets(root,recursive=False):
 m=lib.load_asset(path)
 if not isinstance(m,unreal.Material):continue
 visited=set()
 def visit(n):
  if not n or n.get_path_name() in visited:return
  visited.add(n.get_path_name())
  if isinstance(n,unreal.MaterialExpressionComponentMask):
   n.set_editor_property('r',False);n.set_editor_property('g',False);n.set_editor_property('b',True);n.set_editor_property('a',False)
  for child in ml.get_inputs_for_material_expression(m,n):visit(child)
 visit(ml.get_material_property_input_node(m,unreal.MaterialProperty.MP_BASE_COLOR))
 if m.get_name().endswith('_Snow'):
  metal=ml.create_material_expression(m,unreal.MaterialExpressionConstant);metal.r=0;ml.connect_material_property(metal,'',unreal.MaterialProperty.MP_METALLIC)
 ml.recompile_material(m);lib.save_loaded_asset(m)
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
 if not isinstance(a,unreal.StaticMeshActor):continue
 c=a.static_mesh_component
 for i in range(c.get_num_materials()):
  m=c.get_material(i)
  if isinstance(m,unreal.Material) and m.get_path_name().startswith(root) and m.get_name().endswith('_Snow') and ml.get_material_property_input_node(m,unreal.MaterialProperty.MP_EMISSIVE_COLOR):
   original=lib.load_asset('/Game/MaldekRefinement/Materials/'+m.get_name()[:-5])
   if original:c.set_material(i,original)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()

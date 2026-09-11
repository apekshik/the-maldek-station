import unreal,json
from pathlib import Path
root=Path(__file__).resolve().parents[4];out=root/'art/blender/cassette_01'
ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
t=unreal.AssetImportTask();t.filename=str(out/'SM_ServiceCassette.fbx');t.destination_path='/Game/Inspection/Cassette';t.destination_name='SM_ServiceCassette';t.automated=True;t.replace_existing=True;t.save=True
o=unreal.FbxImportUI();o.import_mesh=True;o.import_materials=False;o.import_textures=False;o.import_as_skeletal=False;o.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
o.static_mesh_import_data.combine_meshes=True;o.static_mesh_import_data.auto_generate_collision=False;o.static_mesh_import_data.generate_lightmap_u_vs=False;t.options=o
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t]);mesh=unreal.load_asset('/Game/Inspection/Cassette/SM_ServiceCassette');assert mesh
mats={};ml=unreal.MaterialEditingLibrary
for spec in json.loads((out/'export_report.json').read_text())['materials']:
 name='M_'+spec['name'];path='/Game/Inspection/Cassette/'+name;m=unreal.load_asset(path)
 if not m:m=unreal.AssetToolsHelpers.get_asset_tools().create_asset(name,'/Game/Inspection/Cassette',unreal.Material,unreal.MaterialFactoryNew())
 ml.delete_all_material_expressions(m)
 c=ml.create_material_expression(m,unreal.MaterialExpressionConstant3Vector);c.constant=unreal.LinearColor(*spec['color'],1);ml.connect_material_property(c,'',unreal.MaterialProperty.MP_BASE_COLOR)
 for prop,val in [(unreal.MaterialProperty.MP_METALLIC,spec['metallic']),(unreal.MaterialProperty.MP_ROUGHNESS,spec['roughness'])]:
  n=ml.create_material_expression(m,unreal.MaterialExpressionConstant);n.r=val;ml.connect_material_property(n,'',prop)
 if spec['window']:
  m.set_editor_property('blend_mode',unreal.BlendMode.BLEND_TRANSLUCENT);m.set_editor_property('two_sided',True)
  n=ml.create_material_expression(m,unreal.MaterialExpressionConstant);n.r=.22;ml.connect_material_property(n,'',unreal.MaterialProperty.MP_OPACITY)
 ml.recompile_material(m);unreal.EditorAssetLibrary.save_loaded_asset(m);mats[spec['name']]=m
slots=[]
for i,slot in enumerate(mesh.static_materials):
 name=str(slot.material_slot_name);assert name in mats,name
 mesh.set_material(i,mats[name]);slots.append(name)
sm=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem);sm.remove_collisions(mesh);sm.add_simple_collisions(mesh,unreal.ScriptingCollisionShapeType.BOX);unreal.EditorAssetLibrary.save_loaded_asset(mesh)
RESULT={'reimported':True,'slots':slots}

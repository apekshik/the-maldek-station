"""Import only door-owned assets. Does not modify the map or shared materials."""
import unreal,json,hashlib
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'doors';manifest=json.loads((out/'door_manifest.json').read_text())
assert not unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).is_in_play_in_editor()
lib=unreal.EditorAssetLibrary;at=unreal.AssetToolsHelpers.get_asset_tools();ml=unreal.MaterialEditingLibrary;sm=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
root='/Game/MaldekRefinement/R12/Doors';mats={};created=[]
def material(name):
 m=lib.load_asset(root+'/Materials/'+name)
 if not m:m=at.create_asset(name,root+'/Materials',unreal.Material,unreal.MaterialFactoryNew())
 ml.delete_all_material_expressions(m);return m
def value(m,v,prop):
 vec=isinstance(v,(tuple,list));n=ml.create_material_expression(m,unreal.MaterialExpressionConstant3Vector if vec else unreal.MaterialExpressionConstant)
 n.set_editor_property('constant' if vec else 'r',unreal.LinearColor(*v[:3],1) if vec else v);assert ml.connect_material_property(n,'',prop);return n
for name,info in manifest['materials'].items():
 slot=info['slot'];m=lib.load_asset('/Game/MaldekRefinement/R12/Materials/Instances/MI_'+slot) if name.startswith('VF06_') else None
 if not m:
  m=material('M_'+slot)
  value(m,info['base_color'],unreal.MaterialProperty.MP_BASE_COLOR);value(m,info['metallic'],unreal.MaterialProperty.MP_METALLIC);value(m,info['roughness'],unreal.MaterialProperty.MP_ROUGHNESS)
  if name=='D03_Status_red':
   n=ml.create_material_expression(m,unreal.MaterialExpressionVectorParameter);n.set_editor_property('parameter_name','StatusColor');n.set_editor_property('default_value',unreal.LinearColor(1,.025,.005,1));ml.connect_material_property(n,'RGB',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
  elif info.get('emission_strength',0)>0:value(m,[x*info['emission_strength'] for x in info['emission_color'][:3]],unreal.MaterialProperty.MP_EMISSIVE_COLOR)
  if info['glass']:
   # Local frosted transmission: average scene-color samples through this pane.
   # This affects only the glass, not the camera or the rest of the level.
   m.set_editor_property('blend_mode',unreal.BlendMode.BLEND_TRANSLUCENT);m.set_editor_property('two_sided',True)
   total=None;weight_sum=0
   for x in range(-2,3):
    for y in range(-2,3):
     weight=[1,4,6,4,1][x+2]*[1,4,6,4,1][y+2];weight_sum+=weight
     n=ml.create_material_expression(m,unreal.MaterialExpressionSceneColor);n.set_editor_property('input_mode',unreal.MaterialSceneAttributeInputMode.MSAIM_OFFSET_FRACTION);n.set_editor_property('const_input',unreal.Vector2D(x*.005,y*.005))
     mul=ml.create_material_expression(m,unreal.MaterialExpressionMultiply);mul.set_editor_property('const_b',float(weight));ml.connect_material_expressions(n,'',mul,'A')
     if total:
      add=ml.create_material_expression(m,unreal.MaterialExpressionAdd);ml.connect_material_expressions(total,'',add,'A');ml.connect_material_expressions(mul,'',add,'B');total=add
     else:total=mul
   avg=ml.create_material_expression(m,unreal.MaterialExpressionMultiply);avg.set_editor_property('const_b',.88/weight_sum);ml.connect_material_expressions(total,'',avg,'A');ml.connect_material_property(avg,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
   value(m,1.0,unreal.MaterialProperty.MP_OPACITY)
  ml.recompile_material(m);assert lib.save_loaded_asset(m);created.append(m)
 mats[slot]=m
errors=list(unreal.StationMigrationLibrary.validate_material_shaders(created));assert not errors,errors
unreal.SystemLibrary.execute_console_command(None,'Interchange.FeatureFlags.Import.FBX 0')
report=[]
for row in manifest['chunks']:
 file=out/row['file'];assert hashlib.sha256(file.read_bytes()).hexdigest()==row['sha256']
 task=unreal.AssetImportTask();task.filename=str(file);task.destination_path=root+'/Meshes';task.automated=True;task.save=True;task.replace_existing=True
 opt=unreal.FbxImportUI();opt.import_materials=False;opt.import_textures=False;opt.automated_import_should_detect_type=False;opt.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
 d=opt.static_mesh_import_data;d.combine_meshes=True;d.auto_generate_collision=False;d.convert_scene=True;d.convert_scene_unit=True;d.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS;task.options=opt
 at.import_asset_tasks([task]);mesh=lib.load_asset(root+'/Meshes/'+row['name']);assert mesh
 box=mesh.get_bounding_box();actual=[box.min.to_tuple(),box.max.to_tuple()];lo,hi=row['bounds'];wanted=[[100*lo[0],-100*hi[1],100*lo[2]],[100*hi[0],-100*lo[1],100*hi[2]]]
 err=max(abs(actual[j][i]-wanted[j][i]) for j in range(2) for i in range(3));assert err<.2,(row['name'],err)
 for i,slot in enumerate(mesh.static_materials):mesh.set_material(i,mats[str(slot.material_slot_name)])
 sm.remove_collisions(mesh);ns=mesh.get_editor_property('nanite_settings');ns.set_editor_property('enabled',False);sm.set_nanite_settings(mesh,ns,True)
 assert lib.save_loaded_asset(mesh);report.append({'asset':mesh.get_path_name(),'bounds_error_cm':err,'triangles':row['triangles']})
RESULT={'success':True,'assets':report,'materials':{k:v.get_path_name() for k,v in mats.items()},'shader_errors':errors,'map_modified':False}
(out/'import.json').write_text(json.dumps(RESULT,indent=2))

import unreal,json
from pathlib import Path
out={};levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert levels.load_level('/Game/MaldekRefinement/Maps/BlockOut_R04')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
ml=unreal.MaterialEditingLibrary
land=next(a for a in actors if a.get_class().get_name()=='Landscape')
materials=[land.get_editor_property('landscape_material'),unreal.load_asset('/Game/MaldekRefinement/Materials/M_R04_Local_Terrain'),unreal.load_asset('/Game/MaldekRefinement/Materials/M_R02_Weathered_Concrete')]
for m in materials:
 chain=[]
 while m:
  row={'path':m.get_path_name(),'class':m.get_class().get_name()}
  for p in ['shading_model','blend_mode','use_material_attributes','scalar_parameter_values','vector_parameter_values']:
   try:row[p]=str(m.get_editor_property(p))
   except Exception:pass
  if isinstance(m,unreal.Material):
   row['inputs']={}
   for prop in [unreal.MaterialProperty.MP_BASE_COLOR,unreal.MaterialProperty.MP_EMISSIVE_COLOR,unreal.MaterialProperty.MP_MATERIAL_ATTRIBUTES]:
    n=ml.get_material_property_input_node(m,prop);row['inputs'][str(prop)]=str(n)
  chain.append(row)
  m=m.get_editor_property('parent') if isinstance(m,unreal.MaterialInstance) else None
 out[chain[0]['path']]=chain
out['lights']=[]
for a in actors:
 if 'Sky' in a.get_class().get_name() or 'Weather' in a.get_class().get_name():
  row={'actor':a.get_actor_label(),'components':[]}
  for c in a.get_components_by_class(unreal.LightComponent):
   cr={'name':c.get_name(),'class':c.get_class().get_name()}
   for p in ['intensity','light_color','cast_shadows','affect_dynamic_indirect_lighting','affect_translucent_lighting']:
    try:cr[p]=str(c.get_editor_property(p))
    except Exception:pass
   row['components'].append(cr)
  out['lights'].append(row)
(Path(__file__).resolve().parents[1]/'lighting_audit.json').write_text(json.dumps(out,indent=2))

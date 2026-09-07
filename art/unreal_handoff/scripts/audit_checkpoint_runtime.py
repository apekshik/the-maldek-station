"""Read-only runtime/editor dependency audit for the pre-migration checkpoint."""
import unreal,json
from pathlib import Path
out=Path(__file__).resolve().parents[2]/'checkpoints/pre_vf07'
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
def value(o,n):
 try:return str(o.get_editor_property(n))
 except Exception:return None
rows=[]
for a in actors:
 row={'path':a.get_path_name(),'label':a.get_actor_label(),'hidden':a.is_hidden_ed(),'bounds':str(a.get_actor_bounds(False)),'properties':{},'components':[]}
 for n in ['actor_guid','tags','root_component','can_be_damaged','initial_life_span']:
  row['properties'][n]=value(a,n)
 for c in a.get_components_by_class(unreal.SceneComponent):
  properties={n:value(c,n) for n in ['relative_location','relative_rotation','relative_scale3d','mobility','visible','hidden_in_game']}
  if isinstance(c,unreal.PrimitiveComponent):
   properties.update({n:value(c,n) for n in ['cast_shadow','receives_decals','body_instance','translucency_sort_priority']})
   properties['collision_profile']=str(c.get_collision_profile_name())
  if isinstance(c,unreal.LightComponentBase):
   properties.update({n:value(c,n) for n in ['intensity','light_color','temperature','attenuation_radius','volumetric_scattering_intensity']})
  row['components'].append({'path':c.get_path_name(),'class':c.get_class().get_path_name(),'properties':properties})
 rows.append(row)
registry=unreal.AssetRegistryHelpers.get_asset_registry()
options=unreal.AssetRegistryDependencyOptions(include_soft_package_references=True,include_hard_package_references=True)
queue=[world.get_outermost().get_name()] if hasattr(world,'get_outermost') else [world.get_path_name().split('.')[0]]
seen=set();missing=[];dependencies={}
while queue:
 p=queue.pop()
 if p in seen or not p.startswith('/Game/'):continue
 seen.add(p)
 if not unreal.EditorAssetLibrary.does_asset_exist(p):missing.append(p);continue
 deps=[str(d) for d in registry.get_dependencies(p,options)]
 dependencies[p]=deps;queue.extend(deps)
report={'world':world.get_path_name(),'actors':rows,'world_settings':{n:value(world.get_world_settings(),n) for n in ['default_game_mode','kill_z','world_to_meters']},'dependencies':dependencies,'missing_game_packages':missing,'automation_stat_api':[n for n in dir(unreal.AutomationLibrary) if 'stat' in n.lower()], 'play_settings_api':[n for n in dir(unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.LevelEditorPlaySettings'))) if not n.startswith('_')]}
settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.LevelEditorPlaySettings'))
report['play_settings']={n:value(settings,n) for n in ['NewWindowWidth','NewWindowHeight','LastExecutedPlayModeType','CenterNewWindow']}
report['stat_help']=unreal.AutomationLibrary.get_stat_inc_average.__doc__
report['known_authoring_dependency_issue']='Five missing Beech_Branch instance inputs are referenced by the imported PVE_European_Beech_01 authoring graph. Preserve and report; do not silently claim a fully resolved dependency graph.'
(out/'runtime_dependencies.json').write_text(json.dumps(report,indent=2))



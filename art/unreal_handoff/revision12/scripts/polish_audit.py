import unreal,json,time,traceback
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'polish';out.mkdir(exist_ok=True)
ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert not ls.is_in_play_in_editor()
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert w.get_name()=='Station_R12'
gm=w.get_world_settings().get_editor_property('default_game_mode');cdo=unreal.get_default_object(gm);bp=unreal.load_asset('/Game/MaldekRefinement/ForestTest/BP_ForestWalker')
sub=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem);fn=unreal.SubobjectDataBlueprintFunctionLibrary
components=[]
for h in sub.k2_gather_subobject_data_for_blueprint(bp):
 c=fn.get_object(fn.get_data(h));row={'name':c.get_name(),'class':c.get_class().get_name()}
 for prop in ['relative_location','relative_rotation','relative_scale3d','intensity','attenuation_radius','shadow_bias','shadow_slope_bias','cast_raytraced_shadow','light_function_material','source_radius','contact_shadow_length','walk_speed','sprint_speed']:
  try:row[prop]=str(c.get_editor_property(prop))
  except Exception:pass
 components.append(row)
report={'game_mode':gm.get_path_name(),'pawn':cdo.get_editor_property('default_pawn_class').get_path_name(),'components':components,'actors':[]}
for a in aa.get_all_level_actors():
 report['actors'].append({'name':a.get_name(),'label':a.get_actor_label(),'location':list(a.get_actor_location().to_tuple()),'rotation':list(a.get_actor_rotation().to_tuple())})
report['saved_current_level']=ls.save_current_level()
(out/'initial_audit.json').write_text(json.dumps(report,indent=2));RESULT={'success':True,'components':len(components),'actors':len(report['actors'])}

"""Keep the inherited start in the parking bay, clear of the retained car's authored collision."""
import unreal,json,re
from pathlib import Path
base=Path(__file__).resolve().parents[1];aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert not levels.is_in_play_in_editor()
inv=json.loads((base/'replacement_inventory.json').read_text());r=next(r for r in inv if r['label']=='PlayerStart');a=next(a for a in aa.get_all_level_actors() if a.get_path_name()==r['r12_path'])
origin=json.loads((base.parent/'working_level_report.json').read_text())['station_origin'];p=unreal.Vector(origin[0]+3500,origin[1]-6050,origin[2]+10)
a.set_actor_location(p,False,True)
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();hit=unreal.SystemLibrary.capsule_trace_single(w,p,p+unreal.Vector(0,0,1),34,96,unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,False,[a],unreal.DrawDebugTrace.NONE,True);assert not (hit and hit.to_tuple()[0]),str(hit)
file=base/'actor_adjustments.json';adjustments=json.loads(file.read_text()) if file.exists() else {}
adjustments[a.get_path_name()]={'old_transform':r['transform'],'new_transform':str(a.get_actor_transform()),'reason':'Move parking spawn 1 metre clear of the retained car. Original center was only 10 cm from car geometry, less than the 34 cm player radius. Class, rotation, capsule, movement and route remain inherited.'}
file.write_text(json.dumps(adjustments,indent=2));assert levels.save_current_level();RESULT={'success':True,'actor':a.get_path_name(),'displacement_cm':100,'capsule_clear':True}

import unreal,json
from pathlib import Path
out=Path(__file__).resolve().parents[1];world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors();origin=json.loads((out/'working_level_report.json').read_text())['station_origin'];rows=[]
ignore=[a for a in actors if a.get_class().get_name()!='Landscape' and a.get_actor_label()!='R04_Local_Terrain']
for x,y in [(0,8),(0,12),(0,18),(5,12),(-5,12),(12,5),(48,13)]:
 wx=origin[0]-x*100;wy=origin[1]+y*100;hit=unreal.SystemLibrary.line_trace_single(world,unreal.Vector(wx,wy,origin[2]+500),unreal.Vector(wx,wy,origin[2]-6000),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,False,ignore,unreal.DrawDebugTrace.NONE)
 h=hit.to_tuple();rows.append({'xy':[x,y],'relative_ground_m':(h[5].z-origin[2])/100,'actor':h[9].get_actor_label() if h[9] else None})
(out/'revision06/cliff_validation.json').write_text(json.dumps(rows,indent=2))

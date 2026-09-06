import unreal,json
from pathlib import Path
OUT=Path(__file__).resolve().parents[1]
origin=json.loads((OUT/'working_level_report.json').read_text())['station_origin']
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
ignore=[a for a in actors if a.get_class().get_name()!='Landscape']
rows=[]
for y in range(-64,65,2):
 row=[]
 for x in range(-64,65,2):
  wx=origin[0]-x*100;wy=origin[1]+y*100
  hit=unreal.SystemLibrary.line_trace_single(world,unreal.Vector(wx,wy,80000),unreal.Vector(wx,wy,-80000),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,False,ignore,unreal.DrawDebugTrace.NONE)
  assert hit,'Missing terrain sample'
  row.append((hit.to_tuple()[5].z-origin[2])/100)
 rows.append(row)
(OUT/'terrain_samples.json').write_text(json.dumps({'origin':origin,'min':-64,'max':64,'step':2,'heights':rows}))
unreal.log('R04_TERRAIN_SAMPLED 4225')

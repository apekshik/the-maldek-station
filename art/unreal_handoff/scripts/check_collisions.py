import unreal,json
from pathlib import Path
OUT=Path(__file__).resolve().parents[1]
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level('/Game/MaldekRefinement/Maps/BlockOut_R04')
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
for a in actors:
 if not a.get_actor_label().startswith('R04_'):continue
 c=a.get_components_by_class(unreal.StaticMeshComponent)[0]
# Meshes are compiled by the interactive editor before this check.
 c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
 c.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
landscape=next(a for a in actors if a.get_class().get_name()=='Landscape')
origin=json.loads((OUT/'working_level_report.json').read_text())['station_origin']
samples={'control':(-6.5,-1.8,4),'platform':(-4,3,4),'gondola':(0,8.05,4),'waiting':(-11,-2,4),'lower_drive':(2,4,0),'generator':(2,-3,0),'yard':(10,-3,0),'overlook':(12,5,4),'arrival':(-17,-12,0)}
result={}
for label,(x,y,z) in samples.items():
 p=unreal.Vector(origin[0]-x*100,origin[1]+y*100,origin[2]+z*100)
 row={}
 for kind,ignore in [('floor',[]),('terrain',[a for a in actors if a!=landscape])]:
  top=p.z+80 if kind=='floor' else p.z+3000
  hit=unreal.SystemLibrary.line_trace_single(world,unreal.Vector(p.x,p.y,top),unreal.Vector(p.x,p.y,p.z-5000),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,False,ignore,unreal.DrawDebugTrace.NONE)
  if hit:
   h=hit.to_tuple();row[kind]={'blocking':h[0],'point':[h[5].x,h[5].y,h[5].z],'actor':h[9].get_actor_label() if h[9] else None}
  else:row[kind]=None
 floor_hit=row['floor']
 if floor_hit and floor_hit['blocking']:
  bottom=floor_hit['point'][2]
  capsule=unreal.SystemLibrary.capsule_trace_single(world,unreal.Vector(p.x,p.y,bottom+92),unreal.Vector(p.x+1,p.y,bottom+92),34,88,unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,False,[],unreal.DrawDebugTrace.NONE)
  h=capsule.to_tuple() if capsule else None
  row['capsule']={'blocked':bool(h and h[0]),'actor':h[9].get_actor_label() if h and h[9] else None}
 result[label]=row
(OUT/'collision_review.json').write_text(json.dumps(result,indent=2))
import runpy
runpy.run_path(str(Path(__file__).with_name('verify_working_level.py')))




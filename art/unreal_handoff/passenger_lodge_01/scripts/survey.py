"""Read-only snapshot of the live site before any replacement."""
import unreal,json,hashlib
from pathlib import Path
OUT=Path(__file__).resolve().parents[1];REPO=OUT.parents[2]
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert w.get_name()=='Station_R12' and not ls.is_in_play_in_editor()
origin=json.loads((OUT.parent/'working_level_report.json').read_text())['station_origin']
def v(p):return [p.x,p.y,p.z]
def source(p):return [-(p.x-origin[0])/100,(p.y-origin[1])/100,(p.z-origin[2])/100]
def wp(x,y,z):return unreal.Vector(origin[0]-x*100,origin[1]+y*100,origin[2]+z*100)
actors=aa.get_all_level_actors();rows=[]
for a in actors:
 center,extent=a.get_actor_bounds(False);comps=[]
 for c in a.get_components_by_class(unreal.PrimitiveComponent):
  mesh=c.get_editor_property('static_mesh') if isinstance(c,unreal.StaticMeshComponent) else None
  comps.append({'name':c.get_name(),'class':c.get_class().get_name(),'mesh':mesh.get_path_name() if mesh else None,'collision':str(c.get_collision_enabled()),'visible':c.is_visible()})
 r=a.get_actor_rotation()
 rows.append({'label':a.get_actor_label(),'name':a.get_name(),'class':a.get_class().get_name(),'path':a.get_path_name(),'location':v(a.get_actor_location()),'source_location':source(a.get_actor_location()),'rotation':[r.pitch,r.yaw,r.roll],'scale':v(a.get_actor_scale3d()),'center':source(center),'extent_m':[extent.x/100,extent.y/100,extent.z/100],'components':comps})
terrain=[a for a in actors if 'landscape' in a.get_class().get_name().lower() or a.get_actor_label() in ['R11_Current_Terrain','R11_Terrain']]
ignore=[a for a in actors if a not in terrain]
heights=[]
for xi in range(-34,-4):
 for yi in range(-24,11):
  hit=unreal.SystemLibrary.line_trace_single(w,wp(xi,yi,15),wp(xi,yi,-30),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,ignore,unreal.DrawDebugTrace.NONE,True)
  heights.append({'xy':[xi,yi],'z':source(hit.to_tuple()[5])[2] if hit and hit.to_tuple()[0] else None})
report={'world':w.get_path_name(),'origin':origin,'actor_count':len(rows),'actors':rows,'terrain':[a.get_actor_label() for a in terrain],'height_grid':heights,'map_sha256':hashlib.sha256((REPO/'game/Content/MaldekRefinement/R12/Station_R12.umap').read_bytes()).hexdigest()}
(OUT/'before.json').write_text(json.dumps(report,indent=2));RESULT={'actor_count':len(rows),'terrain':report['terrain'],'height_hits':sum(p['z'] is not None for p in heights),'save_map_doc':str(unreal.EditorLoadingAndSavingUtils.save_map.__doc__)}

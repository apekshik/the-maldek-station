import unreal,json
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'parking'
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert world and not unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).is_in_play_in_editor()
origin=json.loads((out.parents[1]/'working_level_report.json').read_text())['station_origin']
def xyz(v):return [v.x,v.y,v.z]
rows=[]
for a in aa.get_all_level_actors():
 p=a.get_actor_location();x=(origin[0]-p.x)/100;y=(p.y-origin[1])/100
 if (-50<x<-25 and -70<y<-47) or a.get_actor_label() in ['R12_Retained_Parking','R12_Forest_Approach_Aligned','R13_Terrain']:
  rows.append({'path':a.get_path_name(),'label':a.get_actor_label(),'location':xyz(p),'source_xy':[x,y],'components':[{'name':c.get_name(),'mesh':c.static_mesh.get_path_name() if c.static_mesh else None,'materials':[c.get_material(i).get_path_name() if c.get_material(i) else None for i in range(c.get_num_materials())]} for c in a.get_components_by_class(unreal.StaticMeshComponent)]})
assets=[]
for letter in 'ABCD':
 p='/Game/MWLandscapeAutoMaterial/Meshes/Plants/SM_MWAM_Grass'+letter;m=unreal.load_asset(p)
 if m:
  b=m.get_bounds();assets.append({'path':p,'origin':xyz(b.origin),'extent':xyz(b.box_extent)})
r={'world':world.get_path_name(),'actors':rows,'grass_assets':assets}
allactors=aa.get_all_level_actors();land=next(a for a in allactors if isinstance(a,unreal.Landscape));ignore=[a for a in allactors if a!=land];clear=[]
def wp(x,y,z):return unreal.Vector(origin[0]-100*x,origin[1]+100*y,origin[2]+100*z)
for x,y,old,z in json.loads((out/'handoff.json').read_text())['terrain_changes']:
 hit=unreal.SystemLibrary.line_trace_single(world,wp(x,y,20),wp(x,y,-100),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,ignore,unreal.DrawDebugTrace.NONE,True)
 if hit:clear.append(z-(hit.to_tuple()[5].z-origin[2])/100)
r['landscape_samples']=len(clear);r['minimum_underlay_clearance']=min(clear) if clear else None
(out/'live_before.json').write_text(json.dumps(r,indent=2));RESULT={'actors':len(rows),'grass_assets':assets}

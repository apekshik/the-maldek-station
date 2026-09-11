import unreal,json
from pathlib import Path
OUT=Path(__file__).resolve().parents[1];dest=OUT/'kitchen';w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert w.get_name()=='Station_Lodge_Migration'
actors={a.get_actor_label():a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()};data=json.loads((dest/'exports.json').read_text());rows=[]
for g in data['groups']:
 for part in g['parts']:
  if not part['control']:continue
  a=actors['MIG_PLK_'+g['id']+'_'+part['role']]
  for step in range(1,21):
   f=step/20;pose=unreal.Transform(location=a.open_offset*f if a.sliding else unreal.Vector(),rotation=unreal.Rotator(yaw=0 if a.sliding else a.open_angle*f));rotation=unreal.Rotator(yaw=a.get_actor_rotation().yaw+(0 if a.sliding else a.open_angle*f))
   for c,e,source in zip(a.collision_centers,a.collision_extents,part['collision']):
    q=unreal.MathLibrary.transform_location(a.get_actor_transform(),unreal.MathLibrary.transform_location(pose,c));hit=unreal.SystemLibrary.box_trace_single(w,q,q+unreal.Vector(.001,0,0),e-unreal.Vector(.05,.05,.05),rotation,unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,[a],unreal.DrawDebugTrace.NONE,True);h=hit.to_tuple() if hit else None
    if h and h[0]:rows.append({'label':a.get_actor_label(),'fraction':f,'source':source['source'],'hit':h[9].get_actor_label() if h[9] else None});break
   else:continue
   break
(dest/'motion_probe.json').write_text(json.dumps(rows,indent=2));RESULT=rows

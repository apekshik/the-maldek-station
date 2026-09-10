"""Relocate only shrubs buried by the enlarged shoulder or shifted arrival stair."""
import unreal,json,math
from pathlib import Path
OUT=Path(__file__).resolve().parents[1];b=json.loads((OUT/'before.json').read_text());o=b['origin']
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert w.get_name()=='Station_Lodge_Migration'
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);actors=aa.get_all_level_actors();lookup={a.get_actor_label():a for a in actors}
names=['FR_Understorey_034_0','FR_Understorey_036_0','FR_Understorey_037_0','FR_Understorey_042_0','FR_Understorey_042_1','FR_Understorey_043_0','FR_Understorey_083_0','FR_Understorey_086_0']
assert not (OUT/'vegetation_moves.json').exists(),'Moves already applied; verify instead of repeating.'
terrain=[lookup[n] for n in ['Landscape0','VF10_Parking_Terrain','VF10_Parking_Ground']];ignore=[a for a in actors if a not in terrain]
def wp(x,y,z):return unreal.Vector(o[0]-100*x,o[1]+100*y,o[2]+100*z)
occupied=[a['source_location'][:2] for a in b['actors'] if a['class']=='SkeletalMeshActor' and a['label'] not in names];rows=[]
for name in names:
 old=next(a for a in b['actors'] if a['label']==name);a=lookup[name];p=a.get_actor_location();assert max(abs(v-k) for v,k in zip([p.x,p.y,p.z],old['location']))<.1
 x,y,z=old['source_location'];candidates=sorted([(xx,y+dy) for xx in [-34,-35.5,-37,-39,-41,-43] for dy in range(-12,13,2)],key=lambda q:(q[0]-x)**2+(q[1]-y)**2)
 chosen=None
 for xx,yy in candidates:
  if min((math.hypot(xx-px,yy-py) for px,py in occupied),default=100)<2.0:continue
  h=unreal.SystemLibrary.line_trace_single(w,wp(xx,yy,150),wp(xx,yy,-200),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,ignore,unreal.DrawDebugTrace.NONE,True)
  if h and h.to_tuple()[0]:chosen=(xx,yy,(h.to_tuple()[5].z-o[2])/100-.06);break
 assert chosen,name
 assert a.set_actor_location(wp(*chosen),False,True);occupied.append(chosen[:2]);rows.append({'label':name,'before':old['source_location'],'after':chosen})
 (OUT/'vegetation_progress.json').write_text(json.dumps(rows,indent=2))
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
(OUT/'vegetation_moves.json').write_text(json.dumps(rows,indent=2));RESULT={'relocated':len(rows),'deleted':0}

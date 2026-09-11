import unreal,json,math,sys
from pathlib import Path
P=Path(__file__).resolve().parents[1];sys.path.insert(0,str(P/'scripts'));from routes import paths
B=json.loads((P/'baseline.json').read_text());o=B['origin'];w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert w.get_name()=='Station_Lodge_Migration';actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors();opened=[]
for a in actors:
 if isinstance(a,unreal.StationCabinet) and a.get_actor_label().startswith('MIG_WS_') and any(n in a.get_actor_label() for n in ['WSP_Door_hinge','WSR_Door_','WSE_Door_hinge']):
  a.pivot.set_relative_rotation(unreal.Rotator(pitch=0,yaw=a.open_angle,roll=0),False,False);opened.append(a)
def wp(p):return unreal.Vector(o[0]-100*p[0],o[1]+100*p[1],o[2]+100*p[2])
rows=[]
for name,pts in paths.items():
 fails=[];count=0
 for a,b in zip(pts,pts[1:]):
  n=max(1,math.ceil(math.dist(a,b)/.22))
  for i in range(n+1):
   p=[x+(y-x)*i/n for x,y in zip(a,b)];count+=1
   foot=unreal.SystemLibrary.sphere_trace_single(w,wp([p[0],p[1],p[2]+.25]),wp([p[0],p[1],p[2]-.35]),8,unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,[],unreal.DrawDebugTrace.NONE,True);f=foot.to_tuple() if foot else None
   if not f or not f[0]:fails.append({'point':p,'issue':'support'});continue
   z=f[5].z;c=wp(p);c.z=z+99
   h=unreal.SystemLibrary.capsule_trace_single(w,c,c+unreal.Vector(.1,0,0),34,96,unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,[],unreal.DrawDebugTrace.NONE,True);t=h.to_tuple() if h else None
   if t and t[0]:fails.append({'point':p,'issue':'body','actor':t[9].get_actor_label() if t[9] else None,'component':t[10].get_name() if t[10] else None})
 rows.append({'name':name,'samples':count,'passed':not fails,'failures':fails})
for a in opened:a.pivot.set_relative_rotation(unreal.Rotator(),False,False)
report={'routes':rows,'passed':all(r['passed'] for r in rows),'capsule':[34,96],'source':'Editor collision queries; actual movement checked separately.'};(P/'routes_editor.json').write_text(json.dumps(report,indent=2));RESULT={'passed':report['passed'],'failures':{r['name']:len(r['failures']) for r in rows}}

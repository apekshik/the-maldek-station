"""Exact lodge remnants and bounded vegetation moves in the migration map only."""
import unreal,json,math,hashlib
from pathlib import Path
OUT=Path(__file__).resolve().parents[1];REPO=OUT.parents[2];base=json.loads((OUT/'before.json').read_text());o=base['origin']
ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert w.get_name()=='Station_Lodge_Migration' and not ls.is_in_play_in_editor()
assert not (OUT/'cleanup_report.json').exists(),'Cleanup already completed'
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);actors=aa.get_all_level_actors();by={a.get_actor_label():a for a in actors}
def xyz(p):return [p.x,p.y,p.z]
def src(p):return [-(p.x-o[0])/100,(p.y-o[1])/100,(p.z-o[2])/100]
def wp(p):return unreal.Vector(o[0]-100*p[0],o[1]+100*p[1],o[2]+100*p[2])
snapshot=[{'label':a.get_actor_label(),'name':a.get_name(),'position':xyz(a.get_actor_location()),'rotation':[a.get_actor_rotation().pitch,a.get_actor_rotation().yaw,a.get_actor_rotation().roll],'scale':xyz(a.get_actor_scale3d()),'meshes':{c.get_name():c.static_mesh.get_path_name() if c.static_mesh else None for c in a.get_components_by_class(unreal.StaticMeshComponent)}} for a in actors]
(OUT/'cleanup_baseline.json').write_text(json.dumps(snapshot,indent=2))
terrain=[by[n] for n in ['Landscape0','VF10_Parking_Terrain','VF10_Parking_Ground']];ignore=[a for a in actors if a not in terrain]
def ground(x,y):
 h=unreal.SystemLibrary.line_trace_single(w,wp([x,y,150]),wp([x,y,-200]),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,ignore,unreal.DrawDebugTrace.NONE,True);assert h and h.to_tuple()[0];return h.to_tuple()[5].z
report={'removed':[],'moves':[],'foliage':[],'tape_endpoints':[]}
def save(): (OUT/'cleanup_progress.json').write_text(json.dumps(report,indent=2))
def move(a,p,reason):
 old=a.get_actor_location();assert a.set_actor_location(p,False,True);report['moves'].append({'label':a.get_actor_label(),'before':xyz(old),'after':xyz(p),'reason':reason});save()
# Native foliage info, not render-only instance updates, so moves survive reopening.
fol=by['InstancedFoliageActor0'];native=dict(unreal.StationMigrationLibrary.get_foliage_instance_transforms(fol));candidates=json.loads((OUT/'foliage_audit.json').read_text())
(OUT/'cleanup_foliage_baseline.json').write_text(json.dumps({k:xyz(t.translation) for k,t in native.items()}))
for r in candidates:
 expected=wp(r['position']);matches=[(k,t) for k,t in native.items() if (t.translation-expected).length()<.1];assert len(matches)==1,r
 key,t=matches[0];type_path,index=key.rsplit('|',1);new=r['position'].copy();new[0]-=max(0,r['hi'][0]+30.35)
 p=wp(new);p.z=ground(new[0],new[1])-.06*100
 assert unreal.StationMigrationLibrary.move_r12_foliage_instance(fol,type_path,int(index),expected,p),key
 report['foliage'].append({'key':key,'before':xyz(expected),'after':xyz(p),'mesh':r['mesh']});save()
# Move the alder away from the upper stair turn.
a=by['FR_Black_Alder_073_2'];p=src(a.get_actor_location());p[0]-=8.7;q=wp(p);q.z=ground(p[0],p[1])-6;move(a,q,'Canopy outside arrival stair and western guard')
# Preserve the crossing anchors. Shift only the three station-side perimeter trees.
tree_deltas={}
for i in range(3):
 a=by[f'PoliceTape_PerimeterTree_0_{i}'];old=a.get_actor_location();p=src(old);p[0]-=8;p[1]-=6;q=wp(p);q.z=ground(p[0],p[1])-22
 tree_deltas[a.get_actor_label()]=(old,q-old);move(a,q,'Clear branches from stair flight; preserve cordon attachment')
 wrap=by[f'PoliceTape_PerimeterWrap_0_{i}'];move(wrap,wrap.get_actor_location()+q-old,'Follow relocated perimeter tree')
for a in actors:
 if a.get_class().get_name()!='StationPoliceTape' or a.get_actor_label()=='PoliceTape_MainCrossing':continue
 for prop in ['left_anchor','right_anchor']:
  local=a.get_editor_property(prop);point=unreal.MathLibrary.transform_location(a.get_actor_transform(),local)
  matches=[(n,delta) for n,(old,delta) in tree_deltas.items() if math.hypot(point.x-old.x,point.y-old.y)<120]
  if not matches:continue
  assert len(matches)==1,(a.get_actor_label(),prop,matches)
  n,delta=matches[0];new=unreal.MathLibrary.inverse_transform_location(a.get_actor_transform(),point+delta)
  a.set_editor_property(prop,new);report['tape_endpoints'].append({'actor':a.get_actor_label(),'property':prop,'tree':n,'before':xyz(local),'after':xyz(new)});a.reset_tape();save()
# Remove only confirmed former-hall assemblies. Control-room fittings stay intact.
targets=['R12_Door_Hall_north','R12_Door_Hall_south','R08_WallLight_Waiting_Hall_Entry']+[f'R12_VF06_Transferred_Details_{i:03d}_{k}' for i,k in enumerate(['solid','thin','signage','solid','thin'])]
for name in targets:
 a=by[name];assert aa.destroy_actor(a),name;report['removed'].append(name);save()
for suffix in ['WestRear','WestFront']:
 for part in ['Base','Lens','Spill']:
  a=by[f'R12_EdgeMarker_{suffix}_{part}'];move(a,a.get_actor_location()+unreal.Vector(430,0,0),'Follow west guard from source X -25.15 to -29.45')
assert ls.save_current_level()
assert hashlib.sha256((REPO/'game/Content/MaldekRefinement/R12/Station_R12.umap').read_bytes()).hexdigest()==base['map_sha256']
(OUT/'cleanup_report.json').write_text(json.dumps(report,indent=2));RESULT={'removed':len(report['removed']),'actor_moves':len(report['moves']),'foliage_moves':len(report['foliage']),'tape_endpoints':len(report['tape_endpoints'])}

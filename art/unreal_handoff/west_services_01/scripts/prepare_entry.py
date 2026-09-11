import unreal,json
from pathlib import Path
P=Path(__file__).resolve().parents[1];ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor();aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);by={a.get_actor_label():a for a in aa.get_all_level_actors()};o=json.loads((P/'baseline.json').read_text())['origin'];a=by['MIG_Lodge_Sheltered_Storm'];ledger=P/'entry_acoustics.json'
def xyz(v):return [v.x,v.y,v.z]
if ledger.exists():base=json.loads(ledger.read_text())
else:base={'original_centers':[xyz(v) for v in a.room_centers],'original_extents':[xyz(v) for v in a.room_extents]}
centers=[unreal.Vector(*v) for v in base['original_centers']];extents=[unreal.Vector(*v) for v in base['original_extents']]
for pos,e in [([-34.45,-2.45,5.95],[2.62,2.17,1.35]),([-34.45,2.45,5.95],[2.62,2.17,1.35]),([-34.45,0,2.775],[2.62,4.62,1.575])]:
 wp=unreal.Vector(o[0]-100*pos[0],o[1]+100*pos[1],o[2]+100*pos[2]);centers.append(unreal.MathLibrary.inverse_transform_location(a.get_actor_transform(),wp));extents.append(unreal.Vector(*[v*100 for v in e]))
a.room_centers=centers;a.room_extents=extents;base['centers']=[xyz(v) for v in centers];base['extents']=[xyz(v) for v in extents]
checks=[]
for pos,expected in [([-34.45,-2.45,6],1),([-34.45,2.45,6],1),([-34.45,0,2.8],1),([-30,0,6],0),([-39,0,2.8],0)]:
 v=a.weight_at(unreal.Vector(o[0]-100*pos[0],o[1]+100*pos[1],o[2]+100*pos[2]));assert abs(v-expected)<.01;checks.append({'station':pos,'weight':v})
base['checks']=checks
# Restore the actual R12 arrival start; the checkpoint retained a temporary peek-test start.
r=next(r for r in json.loads((P/'r12_reconciliation.json').read_text())['r12'] if r['class']=='/Script/Engine.PlayerStart');start=next(a for a in aa.get_all_level_actors() if isinstance(a,unreal.PlayerStart));start.set_actor_location(unreal.Vector(*r['position']),False,True);start.set_actor_rotation(unreal.Rotator(pitch=r['rotation'][0],yaw=r['rotation'][1],roll=r['rotation'][2]),True);start.set_actor_label(r['label']);base['player_start']=r
assert ls.save_current_level();ledger.write_text(json.dumps(base,indent=2));RESULT={'acoustic_rooms':len(centers),'checks':checks,'arrival_start':r['position']}

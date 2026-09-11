import unreal,json
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'police_tape';aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor();actors={a.get_actor_label():a for a in aa.get_all_level_actors()};rows=json.loads((out/'wrap_fit/fitted.json').read_text());centres={}
for r in rows:
 a=actors[r['wrap']];poly=r['mid_ring_m'];p=unreal.Vector(100*sum(v[0] for v in poly)/len(poly),-100*sum(v[1] for v in poly)/len(poly),0);centres[r['wrap']]=unreal.MathLibrary.transform_location(a.get_actor_transform(),p)
def setends(a,left,right):
 if not a.crossing:
  delta=right-left;a.set_actor_location((left+right)*.5,False,True);a.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(unreal.Vector(),unreal.Vector(delta.x,delta.y,0)),False)
 tr=a.get_actor_transform();a.set_editor_property('left_anchor',unreal.MathLibrary.inverse_transform_location(tr,left));a.set_editor_property('right_anchor',unreal.MathLibrary.inverse_transform_location(tr,right));a.reset_tape()
main=actors['PoliceTape_MainCrossing'];ends=[]
for i in range(2):
 points=[centres[f'PoliceTape_Wrap_{i}_{j}'] for j in range(3)];p=(points[0]+points[1]+points[2])/3;p.z=points[0].z-(97 if i==0 else 172);ends.append(p)
setends(main,*ends)
for k in range(2):
 previous=centres[f'PoliceTape_Wrap_{1 if k==0 else 0}_2']
 for j in range(3):
  target=centres[f'PoliceTape_PerimeterWrap_{k}_{j}'];setends(actors[f'PoliceTape_Perimeter_{k}_{j}'],previous,target);previous=target
assert ls.save_current_level();RESULT={'anchors_join_fitted_bark':True,'saved':True};(out/'wrap_fit/anchors.json').write_text(json.dumps(RESULT))

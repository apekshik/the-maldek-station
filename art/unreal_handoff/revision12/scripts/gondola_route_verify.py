import unreal,json
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'gondola_route';aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
actors={a.get_actor_label():a for a in aa.get_all_level_actors()};g=actors['BP_GondolaSystem'];g.set_editor_property('arrival_trigger_radius',15000.)
def v(p):return [p.x,p.y,p.z]
parts=list(g.cabin_parts);assert len(parts)==24
assert len([l for l in actors if l.startswith('R12_Route_Pylon_')])==5
sp=g.get_components_by_class(unreal.SplineComponent)[0];assert 141500<sp.get_spline_length()<141800
rows=[]
for label,a in actors.items():
 if label.startswith('R12_Route_'):
  rows.append({'label':label,'position':v(a.get_actor_location()),'bounds':[v(x) for x in a.get_actor_bounds(False)],'components':[{'name':c.get_name(),'collision':str(c.get_collision_enabled()),'mesh':c.static_mesh.get_path_name() if c.static_mesh else None} for c in a.get_components_by_class(unreal.StaticMeshComponent)]})
assert ls.save_current_level()
RESULT={'saved':True,'length_m':sp.get_spline_length()/100,'assembly_parts':len(parts),'arrival_radius_m':g.arrival_trigger_radius/100,'actors':rows,'current_camera':str(unreal.EditorLevelLibrary.get_level_viewport_camera_info())}
(out/'verification.json').write_text(json.dumps(RESULT,indent=2))

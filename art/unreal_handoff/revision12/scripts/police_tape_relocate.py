import unreal,json,math,shutil
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'police_tape';dest=out/'relocation';aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor();w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();actors={a.get_actor_label():a for a in aa.get_all_level_actors()};info=json.loads((out/'installation.json').read_text());survey=json.loads((out/'wrap_fit/survey.json').read_text());origin=json.loads((b.parent/'working_level_report.json').read_text())['station_origin'];path=json.loads((b/'forest_arrival_alignment.json').read_text())['path']
def wp(p):return unreal.Vector(origin[0]-100*p[0],origin[1]+100*p[1],origin[2]+100*p[2])
def xyz(p):return [p.x,p.y,p.z]
ground=[a for a in actors.values() if isinstance(a,unreal.Landscape) or a.get_actor_label() in ['VF10_Parking_Terrain','VF10_Parking_Ground','VF10_Parking_Forest_Connector']];ignore=[a for a in actors.values() if a not in ground]
def floor(p):
 h=unreal.SystemLibrary.line_trace_single(w,p+unreal.Vector(0,0,3000),p-unreal.Vector(0,0,5000),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,ignore,unreal.DrawDebugTrace.NONE,True);assert h;return h.to_tuple()[5].z
if not (dest/'before_installation.json').exists():shutil.copy2(out/'installation.json',dest/'before_installation.json');shutil.copy2(out/'wrap_fit/survey.json',dest/'before_survey.json')
centre=wp(path[80]);centre.z=floor(centre);forward=wp(path[81])-wp(path[79]);forward.z=0;forward=forward/forward.length();side=unreal.Vector(forward.y,-forward.x,0);oldcentre=unreal.Vector(*info['centre_world']);oldforward=unreal.Vector(*info['forward']);yaw=math.degrees(math.atan2(forward.y,forward.x)-math.atan2(oldforward.y,oldforward.x));angle=math.radians(yaw)
def rotate(p):return unreal.Vector(p.x*math.cos(angle)-p.y*math.sin(angle),p.x*math.sin(angle)+p.y*math.cos(angle),p.z)
main=actors['PoliceTape_MainCrossing'];main.set_actor_location(centre,False,True);rot=main.get_actor_rotation();rot.yaw+=yaw;main.set_actor_rotation(rot,False)
newgrounds=[]
for i in range(2):
 tree=actors[f'PoliceTape_AnchorTree_{i}'];old=tree.get_actor_location();p=centre+side*(225 if i else -225);z=floor(p);newgrounds.append(z);p.z=z+(old.z-info['tree_ground_world_z'][i]);tree.set_actor_location(p,False,True);rot=tree.get_actor_rotation();rot.yaw+=yaw;tree.set_actor_rotation(rot,False)
 for j in range(3):
  a=actors[f'PoliceTape_Wrap_{i}_{j}'];r=next(r for r in survey if r['wrap']==a.get_actor_label());q=p+rotate(unreal.Vector(*r['wrap_position'])-unreal.Vector(*r['tree_position']));a.set_actor_location(q,False,True);rot=a.get_actor_rotation();rot.yaw+=yaw;a.set_actor_rotation(rot,False)
 proxy=actors[f'PoliceTape_AnchorCollision_{i}'];proxy.set_actor_location(unreal.Vector(p.x,p.y,z+400),False,True)
# Extend the cordon into planted trees on both flanks, keeping all side spans off the trail.
for k in range(2):
 for j,(lateral,along) in enumerate([(440,-70),(570,100),(680,200)]):
  label=f'PoliceTape_PerimeterWrap_{k}_{j}';r=next(r for r in survey if r['wrap']==label);source=actors[r['tree']];name=f'PoliceTape_PerimeterTree_{k}_{j}';p=centre+side*(lateral if k==0 else -lateral)+forward*along;p.z=floor(p)-22;tree=actors.get(name) or aa.spawn_actor_from_class(unreal.SkeletalMeshActor,p);tree.set_actor_label(name);tree.set_folder_path('R12/PoliceTape');tree.skeletal_mesh_component.set_skeletal_mesh_asset(source.skeletal_mesh_component.get_skeletal_mesh_asset());tree.skeletal_mesh_component.set_collision_profile_name('NoCollision');tree.set_actor_scale3d(unreal.Vector(*r['tree_scale']));tree.set_actor_location(p,False,True);rot=source.get_actor_rotation();rot.yaw+=yaw;tree.set_actor_rotation(rot,False)
  wrap=actors[label];offset=unreal.Vector(*r['wrap_position'])-unreal.Vector(*r['tree_position']);wrap.set_actor_location(p+rotate(offset),False,True);rot=wrap.get_actor_rotation();rot.yaw+=yaw;wrap.set_actor_rotation(rot,False)
lamp=actors['Parking_Navigation_Sign_Light'];lc=lamp.get_component_by_class(unreal.SpotLightComponent);lc.set_intensity(0);lc.set_visibility(False);lamp.set_actor_hidden_in_game(True)
info.update(centre_world=xyz(centre),forward=xyz(forward),side=xyz(side),path_index=80,base_world_z=centre.z,ground_world_z=centre.z,tree_ground_world_z=newgrounds);(out/'installation.json').write_text(json.dumps(info,indent=2));assert ls.save_current_level();RESULT={'saved':True,'path_index':80,'moved_distance_m':(centre-oldcentre).length()/100,'station_path_end_distance_m':(centre-wp(path[-1])).length()/100,'sign_light_intensity':lc.intensity};(dest/'placement.json').write_text(json.dumps(RESULT,indent=2))

"""Place a development return marker clear of the control-room service door swing."""
import unreal,json
from pathlib import Path
ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);assert not ls.is_in_play_in_editor()
actors=aa.get_all_level_actors();before={a.get_actor_label():a.get_actor_transform() for a in actors}
d=next(a for a in actors if a.get_actor_label()=='R12_Door_Control_side')
marker=next((a for a in actors if a.actor_has_tag('DoorTestCheckpoint')),None)
pos=unreal.MathLibrary.transform_location(d.get_actor_transform(),unreal.Vector(65,150,102/d.get_actor_scale3d().z));rot=unreal.Rotator(yaw=d.get_actor_rotation().yaw-90)
if marker is None:marker=aa.spawn_actor_from_class(unreal.TargetPoint,pos,rot)
marker.set_actor_label('R12_Door_Test_Checkpoint');marker.set_editor_property('tags',['DoorTestCheckpoint']);marker.set_actor_location_and_rotation(pos,rot,False,True);marker.set_folder_path('Doors/Testing')
for a in actors:assert a.get_actor_transform()==before[a.get_actor_label()]
assert ls.save_current_level()
RESULT={'success':True,'label':marker.get_actor_label(),'position':pos.to_tuple(),'rotation':rot.to_tuple(),'shortcut':'F6','console':'StationDoorCheckpoint','scope':'PIE and non-shipping development builds; original opening spawn retained'}
(Path(__file__).resolve().parents[1]/'doors/key_lock/checkpoint_install.json').write_text(json.dumps(RESULT,indent=2))

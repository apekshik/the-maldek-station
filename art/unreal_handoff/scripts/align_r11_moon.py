import unreal,math,json
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'revision11';sky=next(a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors() if a.get_actor_label()=='Ultra_Dynamic_Sky')
angle=math.radians(90-sky.get_actor_rotation().yaw)
sky.set_editor_property('Manually Position Moon Target',True);sky.set_editor_property('Moon Target',unreal.Vector(50*math.cos(angle),50*math.sin(angle),50*math.tan(math.radians(20))))
(out/'moon_alignment.json').write_text(json.dumps({'target_world_azimuth':90,'target_elevation':20,'result':str(sky.get_editor_property('Moon World Rotation'))},indent=2))

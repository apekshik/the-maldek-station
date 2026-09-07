import unreal,json
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'revision11';sky=next(a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors() if a.get_actor_label()=='Ultra_Dynamic_Sky');r={'actor':str(sky.get_actor_transform()),'methods':[n for n in dir(sky) if 'moon' in n.lower()]}
for n in ['Moon Handle','Moon Parent','Moon','Moon Target','Moon World Rotation','Sun Angle','Sun Yaw','Sun Pitch']:
 try:
  v=sky.get_editor_property(n);r[n]=str(v.get_world_transform()) if isinstance(v,unreal.SceneComponent) else str(v)
 except:pass
(out/'moon_audit.json').write_text(json.dumps(r,indent=2))

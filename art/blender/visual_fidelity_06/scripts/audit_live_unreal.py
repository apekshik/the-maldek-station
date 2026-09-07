import unreal,json,datetime
from pathlib import Path
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
rows=[]
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
 label=a.get_actor_label()
 if not any(s in label.lower() for s in ['r04','r10','r11','gondola','station','drive','platform','stair','control','hall','relay','generator','workshop']):continue
 p=a.get_actor_location();r=a.get_actor_rotation();s=a.get_actor_scale3d()
 comps=[]
 for c in a.get_components_by_class(unreal.StaticMeshComponent):
  if c.static_mesh:comps.append(c.static_mesh.get_path_name())
 rows.append(dict(label=label,location=[p.x,p.y,p.z],rotation=[r.pitch,r.yaw,r.roll],scale=[s.x,s.y,s.z],meshes=comps))
out=Path('C:/Users/apek-anna/Developer/the-maldek-station/art/blender/visual_fidelity_06/live_unreal_audit.json')
out.write_text(json.dumps(dict(world=world.get_path_name(),time=datetime.datetime.now().isoformat(),actors=rows),indent=2))
unreal.log('VF06 read-only live layout audit saved')

import unreal,json
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'revision06';world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors();land=next(a for a in actors if a.get_class().get_name()=='Landscape')
rt=unreal.RenderingLibrary.create_render_target2d(world,4033,4033,unreal.TextureRenderTargetFormat.RTF_RGBA8)
assert land.landscape_export_heightmap_to_render_target(rt,True)
unreal.RenderingLibrary.export_render_target(world,rt,str(out),'landscape_before.png')
report={}
for a in actors:
 if 'Ultra_Dynamic' in a.get_actor_label():
  d={}
  for n in dir(a):
   if any(w in n.lower() for w in ['fog','snow','cloud','time_of_day']):
    try:
     v=a.get_editor_property(n)
     if isinstance(v,(int,float,bool,str)):d[n]=v
    except:pass
  report[a.get_actor_label()]=d
(out/'weather_properties.json').write_text(json.dumps(report,indent=2))

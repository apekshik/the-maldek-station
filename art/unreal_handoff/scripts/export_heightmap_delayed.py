import unreal,time
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'revision06';world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();land=next(a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors() if a.get_class().get_name()=='Landscape')
rt=unreal.RenderingLibrary.create_render_target2d(world,4033,4033,unreal.TextureRenderTargetFormat.RTF_RGBA8)
assert land.landscape_export_heightmap_to_render_target(rt,True)
when=time.monotonic()+3
def tick(delta):
 if time.monotonic()<when:return
 unreal.RenderingLibrary.export_render_target(world,rt,str(out),'landscape_before.png');unreal.unregister_slate_post_tick_callback(handle)
handle=unreal.register_slate_post_tick_callback(tick)

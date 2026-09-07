import unreal,time,json,traceback
from pathlib import Path
base=Path(__file__).resolve().parents[1];world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert world.get_name()=='Station_R12'
land=next(a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors() if isinstance(a,unreal.Landscape))
owned=list(unreal.StationMigrationLibrary.get_landscape_heightmap_paths(land));assert owned
for path in owned:assert '/R12/Station_R12.' in path,('Shared landscape texture: cannot edit',path)
rt=unreal.RenderingLibrary.create_render_target2d(world,4033,4033,unreal.TextureRenderTargetFormat.RTF_RGBA8)
state={'stage':0,'next':time.monotonic()+5}
def tick(dt):
 if time.monotonic()<state['next']:return
 if state['stage']==0:
  assert land.landscape_export_heightmap_to_render_target(rt,True)
  state.update(stage=1,next=time.monotonic()+5);return
 try:
  unreal.RenderingLibrary.export_render_target(world,rt,str(base),'landscape_before.png')
  (base/'landscape_ownership.json').write_text(json.dumps({'actor':land.get_path_name(),'transform':str(land.get_actor_transform()),'r12_owned_heightmaps':sorted(set(owned)),'components':len(owned),'exported':True,'pixel_validation_required':True},indent=2))
 finally:unreal.unregister_slate_post_tick_callback(handle)
handle=unreal.register_slate_post_tick_callback(tick);RESULT={'started':True,'components':len(owned)}

import unreal,gc,types,runpy,json
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'revision11'
# Cancel only this revision's temporary capture callback if its viewport is occluded.
for obj in gc.get_objects():
 if isinstance(obj,types.FunctionType) and obj.__name__=='tick' and obj.__code__.co_filename.endswith('render_r11.py'):
  h=obj.__globals__.get('handle')
  if h:
   try:unreal.unregister_slate_post_tick_callback(h)
   except:pass
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in aa.get_all_level_actors():
 if a.get_actor_label()=='TEMP_R11_Inspection':aa.destroy_actor(a)
runpy.run_path(str(Path(__file__).with_name('finalize_r11_materials.py')))
(out/'play_ready.json').write_text(json.dumps({'saved_without_inspection_lights':True}))

import unreal,gc,types
count=0
for obj in gc.get_objects():
 if isinstance(obj,types.FunctionType) and obj.__name__=='tick' and str(obj.__globals__.get('__file__','')).endswith('police_tape_playtest.py'):
  g=obj.__globals__
  if 'handle' in g:
   try:unreal.unregister_slate_post_tick_callback(g['handle']);count+=1
   except Exception:pass
  if 'settings' in g:g['settings'].set_editor_property('bThrottleCPUWhenNotForeground',g['throttle'])
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
RESULT={'cleaned':count}

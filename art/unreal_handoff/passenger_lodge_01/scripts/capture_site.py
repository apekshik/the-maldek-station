import unreal,json,time,traceback
from pathlib import Path
OUT=Path(__file__).resolve().parents[1];dest=OUT/'previews';dest.mkdir(exist_ok=True);o=json.loads((OUT/'before.json').read_text())['origin']
assert unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_name()=='Station_Lodge_Migration'
def wp(p):return unreal.Vector(o[0]-100*p[0],o[1]+100*p[1],o[2]+100*p[2])
views=[('overhead',[-16,-4,32],[-16,-4,4]),('arrival',[-14,-22,12],[-16,-3,4]),('west',[-31,-5,12],[-18,-4,5]),('bypass',[-7.2,-16.7,2],[-7.2,-10,3])]
state={'i':0,'phase':'set','next':0};rows=[]
def tick(dt):
 if time.monotonic()<state['next']:return
 try:
  if state['i']==len(views):
   unreal.unregister_slate_post_tick_callback(handle)
   (OUT/'capture_report.json').write_text(json.dumps({'mode':'Unlit site geometry review; provisional materials','views':rows},indent=2));return
  name,p,target=views[state['i']];path=dest/(name+'.png')
  if state['phase']=='set':
   unreal.EditorLevelLibrary.set_level_viewport_camera_info(wp(p),unreal.MathLibrary.find_look_at_rotation(wp(p),wp(target)));state.update(phase='capture',next=time.monotonic()+3)
  elif state['phase']=='capture':
   unreal.AutomationLibrary.take_high_res_screenshot(1600,900,str(path));state.update(phase='wait',next=time.monotonic()+4)
  else:
   assert path.exists() and path.stat().st_size>10000,str(path)
   rows.append({'name':name,'position':p,'target':target,'file':str(path)});state.update(i=state['i']+1,phase='set',next=0)
 except Exception:
  unreal.unregister_slate_post_tick_callback(handle);(OUT/'capture_error.txt').write_text(traceback.format_exc())
handle=unreal.register_slate_post_tick_callback(tick);RESULT={'started':True}

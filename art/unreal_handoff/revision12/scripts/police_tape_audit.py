import unreal,json
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'police_tape';out.mkdir(exist_ok=True)
ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert not ls.is_in_play_in_editor(),'PIE active'
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert w.get_name()=='Station_R12'
origin=json.loads((b.parent/'working_level_report.json').read_text())['station_origin']
def v(p):return [p.x,p.y,p.z]
def local(p):return [(origin[0]-p.x)/100,(p.y-origin[1])/100,(p.z-origin[2])/100]
rows=[]
for a in aa.get_all_level_actors():
 p=local(a.get_actor_location());label=a.get_actor_label()
 if -45<p[0]<-15 and -56<p[1]<-25:
  rows.append({'label':label,'path':a.get_path_name(),'world':v(a.get_actor_location()),'local':p,'class':a.get_class().get_name(),'bounds':[v(x) for x in a.get_actor_bounds(False)]})
(out/'audit.json').write_text(json.dumps({'origin':origin,'actors':rows},indent=2))
assert ls.save_current_level()
RESULT={'saved':True,'actors':len(rows)}
if JOB.get('close'):unreal.SystemLibrary.quit_editor()

import unreal,json,os
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'police_tape/relocation';aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor();origin=json.loads((b.parent/'working_level_report.json').read_text())['station_origin'];rows=[]
for a in aa.get_all_level_actors():
 p=a.get_actor_location();local=[(origin[0]-p.x)/100,(p.y-origin[1])/100,(p.z-origin[2])/100];label=a.get_actor_label()
 if label.startswith('PoliceTape') or 'Stair' in label or 'Sign' in label or (-36<local[0]<-10 and -35<local[1]<-10) or isinstance(a,unreal.PlayerStart):
  rows.append({'label':label,'class':a.get_class().get_name(),'local':local,'world':[p.x,p.y,p.z],'rotation':[a.get_actor_rotation().pitch,a.get_actor_rotation().yaw,a.get_actor_rotation().roll]})
report={'pid':os.getpid(),'actors':rows};(out/'audit.json').write_text(json.dumps(report,indent=2));RESULT={'pid':os.getpid(),'count':len(rows)}

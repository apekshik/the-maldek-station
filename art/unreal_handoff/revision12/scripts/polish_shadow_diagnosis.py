"""Controlled light/shadow A/B in PIE; all render overrides restored at completion."""
import unreal,json,time,traceback
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'polish'/JOB.get('output','shadow_diagnosis');out.mkdir(parents=True,exist_ok=True)
ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
o=json.loads((b.parent/'working_level_report.json').read_text())['station_origin']
def wp(p):return unreal.Vector(o[0]-100*p[0],o[1]+100*p[1],o[2]+100*p[2])
variants=JOB.get('variants',['original','torch_shadows_off','ray_shadows_off','nanite_off','glass_hidden'])
shots=JOB.get('shots',[('control_sill',(-5,1.5,5.05),(-5,-.15,4.75)),('hall_threshold',(-9.7,1.5,4.7),(-9.7,-.2,4.03))])
s={'phase':'start','next':time.monotonic()+10,'i':0,'j':0,'images':[],'busy':False}
old={};glass=[]
def tick(dt):
 if s['busy'] or time.monotonic()<s['next']:return
 s['busy']=True
 try:
  if s['phase']=='cleanup':
   if ls.is_in_play_in_editor():return
   s['success']='error' not in s;(out/'report.json').write_text(json.dumps(s,indent=2));unreal.unregister_slate_post_tick_callback(handle);return
  w=unreal.EditorLevelLibrary.get_game_world()
  if not w:return
  p=unreal.GameplayStatics.get_player_pawn(w,0);pc=unreal.GameplayStatics.get_player_controller(w,0)
  if not p or not pc:return
  light=p.get_components_by_class(unreal.SpotLightComponent)[0]
  if s['phase']=='start':
   unreal.StationMigrationLibrary.set_pie_render_size(1920,1080)
   p.character_movement.set_movement_mode(unreal.MovementMode.MOVE_FLYING)
   for key in ['r.RayTracing.Shadows','r.Nanite','r.Lumen.HardwareRayTracing']:old[key]=unreal.SystemLibrary.get_console_variable_int_value(key)
   s['original_console']=old.copy();s['light']={k:str(light.get_editor_property(k)) for k in ['cast_raytraced_shadow','cast_shadows','shadow_bias','shadow_slope_bias','source_radius','contact_shadow_length']}
   for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.StaticMeshActor):
    if a.static_mesh_component.static_mesh and a.static_mesh_component.static_mesh.get_path_name().startswith('/Game/MaldekRefinement/R12/Meshes/') and '_glass' in a.static_mesh_component.static_mesh.get_name():glass.append(a.static_mesh_component)
   s['phase']='place'
  if s['phase']=='place':
   for k,v in old.items():unreal.SystemLibrary.execute_console_command(w,f'{k} {v}')
   light.set_cast_shadows(True)
   for c in glass:c.set_visibility(True)
   mode=variants[s['j']]
   if mode.startswith('focus_'):
    p.get_component_by_class(unreal.StationPlayerPresentationComponent).set_focus(float(mode.split('_')[1]))
   if mode=='torch_shadows_off':light.set_cast_shadows(False)
   elif mode=='ray_shadows_off':unreal.SystemLibrary.execute_console_command(w,'r.RayTracing.Shadows 0')
   elif mode=='nanite_off':unreal.SystemLibrary.execute_console_command(w,'r.Nanite 0')
   elif mode=='lumen_hw_off':unreal.SystemLibrary.execute_console_command(w,'r.Lumen.HardwareRayTracing 0')
   elif mode=='glass_hidden':
    for c in glass:c.set_visibility(False)
   name,pos,target=shots[s['i']];pos=wp(pos)
   p.set_actor_location(pos-unreal.Vector(0,0,p.base_eye_height) if JOB.get('eye_positions') else pos,False,True);pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(pos,wp(target)))
   s.update(phase='capture',next=time.monotonic()+6);return
  if s['phase']=='capture':
   file=out/(shots[s['i']][0]+'_'+variants[s['j']]+'.png');unreal.AutomationLibrary.take_high_res_screenshot(1920,1080,str(file));s['images'].append(str(file));s['j']+=1
   if s['j']==len(variants):s['j']=0;s['i']+=1
   s.update(phase='finish' if s['i']==len(shots) else 'place',next=time.monotonic()+3);return
  if s['phase']=='finish':
   for k,v in old.items():unreal.SystemLibrary.execute_console_command(w,f'{k} {v}')
   unreal.StationMigrationLibrary.set_pie_render_size(0,0);ls.editor_request_end_play();s.update(phase='cleanup',next=time.monotonic()+2)
 except Exception:
  s['error']=traceback.format_exc()
  for k,v in old.items():unreal.SystemLibrary.execute_console_command(None,f'{k} {v}')
  ls.editor_request_end_play();s.update(phase='cleanup',next=time.monotonic()+2)
 finally:s['busy']=False
handle=unreal.register_slate_post_tick_callback(tick);ls.editor_request_begin_play();RESULT={'started':True}

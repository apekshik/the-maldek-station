"""Temporary PIE-only A/B probes for thin geometry ray tracing and added light shadows."""
import unreal,json,time,traceback,statistics
from pathlib import Path
b=Path(__file__).resolve().parents[1];ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
o=json.loads((b.parent/'working_level_report.json').read_text())['station_origin']
m=json.loads((b/'handoff_manifest.json').read_text());detail_names={c['name'].replace('SM_','') for c in m['chunks'] if c['role'] in JOB.get('roles',['grating','thin'])}
settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'));throttle=settings.get_editor_property('bThrottleCPUWhenNotForeground');settings.set_editor_property('bThrottleCPUWhenNotForeground',False)
shots=[('service',(17,-7,2),(5,1,1)),('bridge',(18,28,5.6),(12,9,4.8)),('dock',(4,9,5.6),(0,7,5.4)),('forest',(-31.7,-46.4,.9),(-26,-37,.9))]
variants=JOB.get('variants',['original','detail_rt_off','new_light_shadows_off','both'])
state={'phase':'await','i':0,'variant':0,'results':[],'next':0,'busy':False,'deadline':time.monotonic()+300}
components=[];lights=[];terrain=[]
def wp(p):return unreal.Vector(o[0]-100*p[0],o[1]+100*p[1],o[2]+100*p[2])
def finish():
 if 'editor_realtime_off' in variants:ls.editor_set_viewport_realtime(True,'FourPanes2x2.Viewport 1.Viewport1')
 settings.set_editor_property('bThrottleCPUWhenNotForeground',throttle);unreal.StationMigrationLibrary.set_pie_render_size(0,0)
 (b/JOB.get('report','cost_probe.json')).write_text(json.dumps(state,indent=2));ls.editor_request_end_play();unreal.unregister_slate_post_tick_callback(handle)
def tick(dt):
 if state['busy'] or time.monotonic()<state['next']:return
 state['busy']=True
 try:
  now=time.monotonic();assert now<state['deadline']
  w=unreal.EditorLevelLibrary.get_game_world();p=unreal.GameplayStatics.get_player_pawn(w,0) if w else None
  if not p:return
  pc=unreal.GameplayStatics.get_player_controller(w,0)
  if state['phase']=='await':
   assert unreal.StationMigrationLibrary.set_pie_render_size(2560,1440)
   for cmd in ['r.VSync 0','t.MaxFPS 0','r.GPUStatsEnabled 1','stat none','stat unit']:unreal.SystemLibrary.execute_console_command(w,cmd)
   for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.Actor):
    if a.get_actor_label()=='R12_Terrain':
     c=a.get_component_by_class(unreal.StaticMeshComponent);terrain.append((c,c.static_mesh))
    if a.get_actor_label() in detail_names:
     for c in a.get_components_by_class(unreal.StaticMeshComponent):components.append((c,c.get_editor_property('visible_in_ray_tracing'),c.get_editor_property('forced_lod_model'),c.is_visible(),c.get_editor_property('cast_shadow')))
    if a.get_actor_label() in ['R12_Control_Ceiling_Practical','R12_Quarters_Ceiling_Practical','R12_Generator_North_Practical','R12_Cabin_Rear_Practical']:
     c=a.get_component_by_class(unreal.LightComponent);lights.append((c,c.get_editor_property('cast_shadows')))
   assert components and len(lights)==4
   state.update(phase='variant',next=now+12,detail_components=len(components),light_components=len(lights));return
  if state['phase']=='variant':
   variant=variants[state['variant']]
   for c,old in terrain:
    c.set_static_mesh(unreal.load_asset('/Game/MaldekRefinement/R12/Diagnostics/SM_TerrainNaniteProbe') if variant=='terrain_nanite' else old)
    c.set_visibility(variant!='terrain_hidden',False)
   if 'editor_realtime_off' in variants:ls.editor_set_viewport_realtime(variant!='editor_realtime_off','FourPanes2x2.Viewport 1.Viewport1')
   for c,old,lod,visible,shadow in components:
    c.set_editor_property('visible_in_ray_tracing',False if variant in ['detail_rt_off','both'] else old)
    c.set_forced_lod_model(3 if variant=='detail_lod3' else lod)
    c.set_visibility(False if variant=='detail_hidden' else visible,False)
    c.set_editor_property('cast_shadow',False if variant=='detail_shadow_off' else shadow)
   for c,old in lights:c.set_cast_shadows(False if variant in ['new_light_shadows_off','both'] else old)
   state.update(phase='place',i=0)
  if state['phase']=='place':
   name,v,q=shots[state['i']];p.character_movement.set_movement_mode(unreal.MovementMode.MOVE_FLYING);p.set_actor_location(wp(v),False,True);pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(wp(v),wp(q)))
   state.update(phase='sample',next=now+5,end=now+10,samples=[]);return
  if state['phase']=='sample':
   sample=dict(unreal.StationMigrationLibrary.capture_pie_frame_stats());state['samples'].append(sample)
   if now<state['end']:return
   state['results'].append({'variant':variants[state['variant']],'view':shots[state['i']][0],'samples':len(state['samples']),'gpu_ms':statistics.mean(r['gpu_ms'] for r in state['samples']),'frame_ms':statistics.mean(r['frame_ms'] for r in state['samples'])})
   state['i']+=1;state.update(phase='place',next=now+1)
   if state['i']==len(shots):
    state['variant']+=1;state['phase']='variant'
    if state['variant']==len(variants):state['success']=True;finish()
 except Exception:state.update(success=False,error=traceback.format_exc());finish()
 finally:state['busy']=False
handle=unreal.register_slate_post_tick_callback(tick);ls.editor_request_begin_play();RESULT={'started':True}

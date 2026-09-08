"""Open the quarters sightline and add matching red rail-top markers."""
import unreal,json,re
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'platform_refine';out.mkdir(exist_ok=True)
ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);actors={a.get_actor_label():a for a in aa.get_all_level_actors()};w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert w.get_name()=='Station_R12'
o=json.loads((b.parent/'working_level_report.json').read_text())['station_origin']
def wp(x,y,z):return unreal.Vector(o[0]-x*100,o[1]+y*100,o[2]+z*100)
if not (out/'preserve.json').exists():(out/'preserve.json').write_text(json.dumps({k:re.sub(r'\(0x[0-9A-Fa-f]+\)','',str(a.get_actor_transform())) for k,a in actors.items()},indent=2))
remove=['R12_VF06_Canopy_Junction_000_solid','R12_VF06_Canopy_Junction_001_solid','R12_01_Upper_Platform_000_solid','R12_VF07_Public_Guards_018_solid','R09_Canopy_Left_Housing','R09_Canopy_Left_Lens','R09_Canopy_Right_Housing','R09_Canopy_Right_Lens','R09_Light_Canopy_Left','R09_Light_Canopy_Right']
old=json.loads((out/'installation.json').read_text()) if (out/'installation.json').exists() else {};removed=old.get('removed',[])
for label in remove:
 a=actors.get(label)
 if a:
  removed.append({'label':label,'class':a.get_class().get_name(),'transform':str(a.get_actor_transform())});assert aa.destroy_actor(a)
actors={a.get_actor_label():a for a in aa.get_all_level_actors()}
base=unreal.load_asset('/Game/MaldekRefinement/R12/GondolaMarkers/M_Marker_Base');lens=unreal.load_asset('/Game/MaldekRefinement/R12/GondolaMarkers/M_Marker_Red_Lens');assert base and lens
cylinder=unreal.load_asset('/Engine/BasicShapes/Cylinder');sphere=unreal.load_asset('/Engine/BasicShapes/Sphere')
points=[('WestRear',-25.15,-15.15),('WestFront',-25.15,7.35),('BoardingWestTurn',-4,7.35),('BoardingWestEnd',-4,11.5),('BoardingEastEnd',3.6,11.5),('EastFront',17.3,8.4),('EastRear',17.3,2),('RearCorner',1.5,-13.2),('BridgeNearLeft',12.2,10),('BridgeNearRight',13.8,10),('BridgeMidLeft',16.63,22.46),('BridgeMidRight',18.2,22.2),('BridgeEndLeft',16.5,37),('BridgeEndRight',21.5,37)]
# Snap bridge middle markers to surveyed rail post centres.
mf=json.loads((b/'handoff_manifest.json').read_text());posts=[]
for chunk in mf['chunks']:
 if 'Lookout_Bridge' not in chunk['name']:continue
 for box in chunk.get('collision_boxes',[]):
  if box['source'].startswith('Guard_Post'):posts.append([(box['min'][j]+box['max'][j])/2 for j in range(2)])
markers=[]
for name,x,y in points:
 if name.startswith(('BridgeNear','BridgeMid')):x,y=min(posts,key=lambda p:(p[0]-x)**2+(p[1]-y)**2)
 guards=[a for label,a in actors.items() if 'Public_Guards' in label or 'Lookout_Bridge' in label]
 ignore=[a for a in actors.values() if a not in guards]
 hit=unreal.SystemLibrary.line_trace_single(w,wp(x,y,5.6),wp(x,y,4.8),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,ignore,unreal.DrawDebugTrace.NONE,True)
 assert hit,('No rail beneath marker',name,x,y)
 z=(hit.to_tuple()[5].z-o[2])/100
 assert 5.05<z<5.2,(name,z)
 for part,mesh,mat,scale,h in [('Base',cylinder,base,(.16,.16,.025),.0125),('Lens',sphere,lens,(.12,.12,.065),.048)]:
  label='R12_EdgeMarker_'+name+'_'+part;a=actors.get(label) or aa.spawn_actor_from_class(unreal.StaticMeshActor,wp(x,y,z+h));a.set_actor_label(label);a.set_actor_location(wp(x,y,z+h),False,True);a.set_folder_path('R12/PlatformMarkers');c=a.static_mesh_component;c.set_static_mesh(mesh);c.set_material(0,mat);c.set_collision_profile_name('NoCollision');c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION);c.set_cast_shadow(False);a.set_actor_scale3d(unreal.Vector(*scale))
 label='R12_EdgeMarker_'+name+'_Spill';a=actors.get(label) or aa.spawn_actor_from_class(unreal.PointLight,wp(x,y,z+.09));a.set_actor_label(label);a.set_actor_location(wp(x,y,z+.09),False,True);a.set_folder_path('R12/PlatformMarkers');c=a.point_light_component;c.set_mobility(unreal.ComponentMobility.MOVABLE);c.set_intensity_units(unreal.LightUnits.LUMENS);c.set_intensity(.045);c.set_attenuation_radius(90);c.set_light_color(unreal.LinearColor(1,.006,.002,1));c.set_cast_shadows(False);c.set_indirect_lighting_intensity(0);c.set_volumetric_scattering_intensity(0)
 markers.append({'name':name,'position':[x,y,z],'rail_hit':bool(hit)})
assert ls.save_current_level();RESULT={'saved':True,'removed':removed,'markers':markers,'marker_count':len(markers)}
(out/'installation.json').write_text(json.dumps(RESULT,indent=2))

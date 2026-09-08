import unreal,json,math
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'gondola_route';plan=json.loads((out/'plan.json').read_text());aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();actors={a.get_actor_label():a for a in aa.get_all_level_actors()};lib=unreal.EditorAssetLibrary;root='/Game/MaldekRefinement/R12/GondolaRoute'
g=actors['BP_GondolaSystem'];g.get_components_by_class(unreal.WidgetComponent)[0].set_material(0,lib.load_asset('/Game/MaldekRefinement/R12/Doors/M_DoorInteractionPrompt'))
# Broad overlapping fog banks replace the visibly bounded bright spheres from the first preview.
fog=[]
for i,(distance,radius,density) in enumerate([(2000,1650,2.5),(2900,2200,2.8),(3900,2750,3.0)],1):
 a=actors['R12_Route_Fog_%02d'%i];a.set_actor_location(unreal.Vector(plan['nodes'][0]['x']*100,(plan['nodes'][0]['y']+distance)*100,30000),False,True);a.set_actor_scale3d(unreal.Vector(radius/5,radius/5,radius/5))
 c=a.get_components_by_class(unreal.LocalFogVolumeComponent)[0];c.set_radial_fog_extinction(density);c.set_height_fog_extinction(.15);c.set_fog_albedo(unreal.LinearColor(.3,.32,.34,1));c.set_fog_emissive(unreal.LinearColor(0,0,0,1));fog.append({'distance_m':distance,'radius_m':radius,'density':density})
terrain=[a for a in actors.values() if isinstance(a,unreal.LandscapeProxy) or isinstance(a,unreal.StaticMeshActor) and any(k in a.get_actor_label().lower() for k in ['terrain','gorge','bedrock'])]
ignore=[a for a in actors.values() if a not in terrain]
def ground(x,y):
 h=unreal.SystemLibrary.line_trace_single(w,unreal.Vector(x,y,180000),unreal.Vector(x,y,-150000),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,ignore,unreal.DrawDebugTrace.NONE);assert h.to_tuple()[0];return h.to_tuple()[5].z
def cube(label,p,d,material):
 a=actors.get(label) or aa.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(*p));a.set_actor_label(label);a.set_folder_path('R12/Gondola Route');a.set_actor_location(unreal.Vector(*p),False,True);a.set_actor_scale3d(unreal.Vector(*[x/100 for x in d]));c=a.static_mesh_component;c.set_static_mesh(lib.load_asset('/Engine/BasicShapes/Cube'));c.set_material(0,material);c.set_collision_profile_name('BlockAll');actors[label]=a;return a
n=plan['nodes'][-1];x=n['x']*100;y=n['y']*100;z=(n['z']-plan['rope_offset_m'])*100;concrete=lib.load_asset(root+'/Materials/M_Pylon_Concrete');steel=lib.load_asset(root+'/Materials/M_Pylon_Graphite')
cube('R12_Route_Maldek_Boarding_Apron',[x,y-405,z-30],[320,200,60],concrete)
feet=[]
for i,(dx,dy) in enumerate([(220,-400),(660,-400),(220,600),(660,600),(-110,-445),(110,-445)]):
 gz=ground(x+dx,y+dy);bottom=gz-180;top=z-60
 assert top>bottom
 cube('R12_Route_Maldek_Foundation_%d'%i,[x+dx,y+dy,(top+bottom)/2],[65,65,top-bottom],concrete);feet.append({'xy':[x+dx,y+dy],'ground_z':gz,'embedment_cm':180})
for label,p,d in [('Rear',[x,y-510,z+105],[340,8,8]),('Left',[x-168,y-407,z+105],[8,200,8]),('Side',[x+728,y+100,z+105],[8,1200,8])]:
 cube('R12_Route_Maldek_Rail_'+label,p,d,steel)
for i,(dx,dy) in enumerate([(-168,-505),(-168,-310),(160,-505),(728,-495),(728,0),(728,695)]):cube('R12_Route_Maldek_Rail_Post_%d'%i,[x+dx,y+dy,z+52],[8,8,104],steel)
assert ls.save_current_level();RESULT={'saved':True,'fog':fog,'foundation_samples':feet};(out/'polish.json').write_text(json.dumps(RESULT,indent=2))

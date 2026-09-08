import unreal,json
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'gondola_route';aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
actors={a.get_actor_label():a for a in aa.get_all_level_actors()};g=actors['BP_GondolaSystem'];plan=json.loads((out/'plan.json').read_text());n=plan['nodes'][-1];floor=(n['z']-plan['rope_offset_m'])*100;x=n['x']*100;y=n['y']*100
lib=unreal.EditorAssetLibrary;root='/Game/MaldekRefinement/R12/GondolaRoute'
bridge=actors['R12_Route_Maldek_Boarding_Apron'];bridge.static_mesh_component.set_mobility(unreal.ComponentMobility.MOVABLE);bridge.set_actor_location(unreal.Vector(x+480,y-405,floor),False,True);bridge.set_actor_scale3d(unreal.Vector(3.2,2,.1));bridge.static_mesh_component.set_material(0,lib.load_asset(root+'/Materials/M_Pylon_Galvanized'))
bridge_parts=[]
locations={'R12_Route_Maldek_Rail_Rear':[0,-510,105],'R12_Route_Maldek_Rail_Left':[-168,-407,105],'R12_Route_Maldek_Rail_Post_0':[-168,-505,52],'R12_Route_Maldek_Rail_Post_1':[-168,-310,52],'R12_Route_Maldek_Rail_Post_2':[160,-505,52]}
for label,p in locations.items():
 a=actors[label];a.static_mesh_component.set_mobility(unreal.ComponentMobility.MOVABLE);a.set_actor_location(unreal.Vector(x+p[0]+480,y+p[1],floor+p[2]),False,True);bridge_parts.append(a)
for i in [4,5]:
 a=actors.get('R12_Route_Maldek_Foundation_%d'%i)
 if a:aa.destroy_actor(a)
g.set_editor_property('far_boarding_bridge',bridge);g.set_editor_property('far_bridge_parts',bridge_parts);g.set_editor_property('far_bridge_parked',unreal.Vector(x+480,y-405,floor));g.set_editor_property('far_bridge_deployed',unreal.Vector(x,y-405,floor))
# Warm interior lamps make the approaching cabin readable through its existing glass.
for i,dy in enumerate([-150,150]):
 label='R12_Gondola_Interior_Light_%d'%i;a=actors.get(label) or aa.spawn_actor_from_class(unreal.PointLight,unreal.Vector());a.set_actor_label(label);a.set_folder_path('R12/Gondola Route')
 start=plan['nodes'][0];a.set_actor_location(unreal.Vector(start['x']*100,start['y']*100+dy,(start['z']-plan['rope_offset_m'])*100+230),False,True)
 c=a.point_light_component;c.set_mobility(unreal.ComponentMobility.MOVABLE);c.set_editor_property('intensity_units',unreal.LightUnits.LUMENS);c.set_intensity(350);c.set_light_color(unreal.LinearColor(1,.64,.32,1));c.set_attenuation_radius(500);c.set_cast_shadows(True);actors[label]=a
parts=[a for label,a in actors.items() if label.startswith(('R12_12_Gondola_','R12_VF06_Gondola_Details_','R12_Gondola_'))];g.set_editor_property('cabin_parts',parts)
for i in range(1,4):actors['R12_Route_Fog_%02d'%i].get_components_by_class(unreal.LocalFogVolumeComponent)[0].set_fog_emissive(unreal.LinearColor(.00006,.00008,.0001,1))
assert ls.save_current_level();RESULT={'saved':True,'cabin_parts':len(parts),'bridge_rails':len(bridge_parts),'bridge_travel_cm':480};(out/'bridge.json').write_text(json.dumps(RESULT,indent=2))

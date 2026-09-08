"""Idempotent R12 route installation, preserving the user's terrain/sky and cabin materials."""
import unreal,json,math
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'gondola_route';plan=json.loads((out/'plan.json').read_text());survey=json.loads((out/'survey.json').read_text())
ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert w.get_name()=='Station_R12'
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);actors={a.get_actor_label():a for a in aa.get_all_level_actors()}
lib=unreal.EditorAssetLibrary;at=unreal.AssetToolsHelpers.get_asset_tools();ml=unreal.MaterialEditingLibrary;root='/Game/MaldekRefinement/R12/GondolaRoute'
def vec(p):return unreal.Vector(*p)
def node(m,kind,**props):
 n=ml.create_material_expression(m,getattr(unreal,'MaterialExpression'+kind))
 for k,v in props.items():n.set_editor_property(k,v)
 return n
def connect(a,c,pin='',output=''):assert ml.connect_material_expressions(a,output,c,pin)
def scalar(m,v):return node(m,'Constant',r=v)
palette={'Pylon_Faded_Grey_Green':([.26,.31,.28],.12,.83),'Pylon_Graphite':([.055,.07,.065],.25,.84),'Pylon_Galvanized':([.27,.29,.265],.4,.76),'Pylon_Sheave_Liner':([.014,.019,.023],.0,.7),'Pylon_Concrete':([.28,.30,.28],0,.92),'Pylon_Marker_Red':([.7,.008,.004],0,.4),'Pylon_Safety_Amber':([.48,.30,.085],.06,.86),'Pylon_Lettering':([.7,.72,.65],0,.8),'Pylon_Joint_Patina':([.19,.072,.021],.1,.92)}
mats={}
for name,(color,metal,rough) in palette.items():
 m=lib.load_asset(root+'/Materials/M_'+name) or at.create_asset('M_'+name,root+'/Materials',unreal.Material,unreal.MaterialFactoryNew());ml.delete_all_material_expressions(m)
 base=node(m,'Constant3Vector',constant=unreal.LinearColor(*color,1));result=base
 if name not in ['Pylon_Marker_Red','Pylon_Lettering','Pylon_Sheave_Liner']:
  pos=node(m,'WorldPosition');stretch=node(m,'Multiply');connect(pos,stretch,'A');connect(node(m,'Constant3Vector',constant=unreal.LinearColor(.07,.07,.004,1)),stretch,'B')
  noise=node(m,'Noise',scale=1.,levels=2);connect(stretch,noise,'World Position')
  mask=node(m,'Power',const_exponent=4.);connect(noise,mask,'Base')
  rust=node(m,'Constant3Vector',constant=unreal.LinearColor(.13,.054,.022,1));result=node(m,'LinearInterpolate');connect(base,result,'A');connect(rust,result,'B');connect(mask,result,'Alpha')
 ml.connect_material_property(result,'',unreal.MaterialProperty.MP_BASE_COLOR)
 ml.connect_material_property(scalar(m,rough),'',unreal.MaterialProperty.MP_ROUGHNESS);ml.connect_material_property(scalar(m,metal),'',unreal.MaterialProperty.MP_METALLIC)
 if name=='Pylon_Marker_Red':
  glow=node(m,'Multiply');connect(base,glow,'A');connect(scalar(m,8),glow,'B');ml.connect_material_property(glow,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
 ml.recompile_material(m);lib.save_loaded_asset(m);mats[name]=m
unreal.SystemLibrary.execute_console_command(w,'Interchange.FeatureFlags.Import.FBX 0')
meshes={}
for item in json.loads((out/'exports.json').read_text()):
 name=item['name'];t=unreal.AssetImportTask();t.filename=str(out/'fbx'/(name+'.fbx'));t.destination_path=root+'/Meshes';t.automated=True;t.save=True;t.replace_existing=True
 opt=unreal.FbxImportUI();opt.import_mesh=True;opt.import_materials=False;opt.import_textures=False;opt.automated_import_should_detect_type=False;opt.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
 d=opt.static_mesh_import_data;d.combine_meshes=True;d.auto_generate_collision=False;d.convert_scene=True;d.convert_scene_unit=True;d.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS;t.options=opt;at.import_asset_tasks([t])
 mesh=lib.load_asset(root+'/Meshes/'+name);assert mesh,name
 for i,slot in enumerate(mesh.get_editor_property('static_materials')):
  slotname=str(slot.get_editor_property('imported_material_slot_name'));key=next((k for k in palette if slotname.startswith(k)),None);assert key,slotname;mesh.set_material(i,mats[key])
 mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
 lib.save_loaded_asset(mesh);meshes[name]=mesh
def actor(label,cls,position):
 a=actors.get(label) or aa.spawn_actor_from_class(cls,vec(position));a.set_actor_label(label);a.set_folder_path('R12/Gondola Route');a.set_actor_location(vec(position),False,True);actors[label]=a;return a
def static(label,mesh,position,collision=True):
 a=actor(label,unreal.StaticMeshActor,position);c=a.static_mesh_component;c.set_static_mesh(mesh);c.set_editor_property('override_materials',[]);c.set_collision_profile_name('BlockAll' if collision else 'NoCollision');a.set_actor_rotation(unreal.Rotator(pitch=0,yaw=180,roll=0),True);return a
for i,n in enumerate(plan['nodes'][1:-1],1):
 a=static('R12_Route_Pylon_%02d'%i,meshes['SM_Gondola_Pylon_%02d'%i],[n['x']*100+25,n['y']*100,n['ground']*100]);a.set_actor_scale3d(unreal.Vector(1,1,1))
origin=[v*100 for v in plan['rope_samples_m'][0]];origin[0]+=25
for lane in ['Passenger','Return']:static('R12_Route_Cable_'+lane,meshes['SM_Gondola_Cable_'+lane],origin,False)
controller=actors['BP_GondolaSystem'];sp=controller.get_components_by_class(unreal.SplineComponent)[0]
controller.set_actor_scale3d(unreal.Vector(1,1,1));sp.clear_spline_points(False)
for p in plan['rope_samples_m']:sp.add_spline_point(unreal.Vector(p[0]*100,p[1]*100,(p[2]-plan['rope_offset_m'])*100),unreal.SplineCoordinateSpace.WORLD,False)
for i in range(len(plan['rope_samples_m'])):sp.set_spline_point_type(i,unreal.SplinePointType.LINEAR,False)
sp.update_spline()
mesh=controller.get_components_by_class(unreal.StaticMeshComponent)[0];mesh.set_mobility(unreal.ComponentMobility.MOVABLE);mesh.set_static_mesh(None);mesh.set_world_scale3d(unreal.Vector(1,1,1));mesh.set_collision_profile_name('NoCollision')
adapter=static('R12_Gondola_Hanger_Adapter',meshes['SM_Gondola_Hanger_Adapter'],survey['start'],False)
parts=[a for label,a in actors.items() if label.startswith(('R12_12_Gondola_','R12_VF06_Gondola_Details_','R12_Gondola_'))]
for a in parts:
 for c in a.get_components_by_class(unreal.SceneComponent):c.set_mobility(unreal.ComponentMobility.MOVABLE)
 a.set_actor_hidden_in_game(False)
controller.set_editor_property('cabin_parts',parts)
for key,value in {'stage_first_arrival':True,'arrival_trigger_location':vec([survey['start'][0],survey['start'][1]-1000,survey['start'][2]]),'arrival_trigger_radius':15000.,'first_arrival_distance':3048.,'cruise_speed':350.,'approach_speed':80.,'acceleration':40.,'slow_zone_distance':2500.,'travel_time':420.,'wait_time_at_maldek':180.,'cabin_dock_rotation':unreal.Rotator(0,0,0)}.items():controller.set_editor_property(key,value)
# Local valley fog, leaving the user's sky/global fog parameters untouched.
for i,(distance,radius,density) in enumerate([(580,210,1.8),(920,320,2.4),(1250,300,2.8)],1):
 p=min(plan['rope_samples_m'],key=lambda p:abs(p[1]-plan['nodes'][0]['y']-distance))
 a=actor('R12_Route_Fog_%02d'%i,unreal.LocalFogVolume,[p[0]*100,p[1]*100,p[2]*100]);a.set_actor_scale3d(unreal.Vector(radius/5,radius/5,radius/5))
 c=a.get_components_by_class(unreal.LocalFogVolumeComponent)[0];c.set_radial_fog_extinction(density);c.set_height_fog_extinction(.25);c.set_fog_albedo(unreal.LinearColor(.42,.48,.53,1));c.set_fog_emissive(unreal.LinearColor(.002,.003,.004,1))
# A small service landing meets the far cabin floor, beside the retained remote station.
n=plan['nodes'][-1];floor=(n['z']-plan['rope_offset_m'])*100;cube=lib.load_asset('/Engine/BasicShapes/Cube')
landing=static('R12_Route_Maldek_Landing',cube,[n['x']*100+440,n['y']*100+100,floor-30]);landing.set_actor_scale3d(unreal.Vector(5.6,12,.6));landing.static_mesh_component.set_material(0,mats['Pylon_Concrete'])
for i,(x,y) in enumerate([(220,-400),(660,-400),(220,600),(660,600)]):
 # Foundation columns extend into the surveyed mountain envelope.
 a=static('R12_Route_Maldek_Foundation_%d'%i,cube,[n['x']*100+x,n['y']*100+y,floor-450]);a.set_actor_scale3d(unreal.Vector(.65,.65,8.4));a.static_mesh_component.set_material(0,mats['Pylon_Concrete'])
assert ls.save_current_level()
errors=unreal.StationMigrationLibrary.validate_material_shaders(list(mats.values()));assert not errors,errors
RESULT={'saved':True,'length_m':sp.get_spline_length()/100,'cabin_parts':len(parts),'pylons':5,'materials':len(mats),'fog_volumes':3,'shader_errors':list(errors)}
(out/'install.json').write_text(json.dumps(RESULT,indent=2))

import unreal,json,math
from pathlib import Path
b=Path(__file__).resolve().parents[1];repo=b.parents[2];out=b/'gondola_mechanism';root='/Game/MaldekRefinement/R12/GondolaMechanism';oldroot='/Game/MaldekRefinement/R12/GondolaRoute'
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
actors={a.get_actor_label():a for a in aa.get_all_level_actors()};lib=unreal.EditorAssetLibrary;at=unreal.AssetToolsHelpers.get_asset_tools();sms=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();unreal.SystemLibrary.execute_console_command(w,'Interchange.FeatureFlags.Import.FBX 0')
plan=json.loads((b/'gondola_route/plan.json').read_text());rows=json.loads((out/'exports.json').read_text());pylons=json.loads((out/'pylons.json').read_text());shell=json.loads((out/'lower_shell.json').read_text())
meshes={}
for row in rows+pylons['meshes']+shell:
 name=row['name'];t=unreal.AssetImportTask();t.filename=str(out/'fbx'/(name+'.fbx'));t.destination_path=root+'/Meshes';t.automated=True;t.save=True;t.replace_existing=True
 opt=unreal.FbxImportUI();opt.import_mesh=True;opt.import_materials=False;opt.import_textures=False;opt.automated_import_should_detect_type=False;opt.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
 d=opt.static_mesh_import_data;d.combine_meshes=True;d.auto_generate_collision=False;d.convert_scene=True;d.convert_scene_unit=True;t.options=opt;at.import_asset_tasks([t]);mesh=lib.load_asset(root+'/Meshes/'+name);assert mesh
 for i,slot in enumerate(mesh.get_editor_property('static_materials')):
  key=str(slot.get_editor_property('imported_material_slot_name'));mat=lib.load_asset(oldroot+'/Materials/M_'+key) if key.startswith('Pylon_') else lib.load_asset('/Game/MaldekRefinement/R12/Materials/Instances/MI_'+key)
  assert mat,(name,key);mesh.set_material(i,mat)
 mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
 if name=='SM_GM_Continuous_Rope':
  settings=sms.get_lod_build_settings(mesh,0);settings.set_editor_property('use_full_precision_u_vs',True);sms.set_lod_build_settings(mesh,0,settings)
 lib.save_loaded_asset(mesh);meshes[name]=mesh
# Rope strands are advected by measured travel, never by unbounded global time.
mat=lib.load_asset(root+'/Materials/M_Moving_Rope') or at.create_asset('M_Moving_Rope',root+'/Materials',unreal.Material,unreal.MaterialFactoryNew())
ml=unreal.MaterialEditingLibrary;ml.delete_all_material_expressions(mat)
def node(cls,**props):
 n=ml.create_material_expression(mat,getattr(unreal,'MaterialExpression'+cls))
 for k,v in props.items():n.set_editor_property(k,v)
 return n
def link(a,b,pin):
 assert ml.connect_material_expressions(a,'',b,pin),(str(a),str(b),pin)
def constant(v):return node('Constant',r=v)
uv=node('TextureCoordinate');u=node('ComponentMask',r=True,g=False,b=False,a=False);v=node('ComponentMask',r=False,g=True,b=False,a=False);link(uv,u,'');link(uv,v,'')
phase=node('ScalarParameter',parameter_name='RopeTravelMeters',default_value=0.);along=node('Subtract');link(u,along,'A');link(phase,along,'B')
lay=node('Multiply');link(along,lay,'A');link(constant(8),lay,'B');around=node('Multiply');link(v,around,'A');link(constant(6),around,'B');sumuv=node('Add');link(lay,sumuv,'A');link(around,sumuv,'B');sine=node('Sine');link(sumuv,sine,'');half=node('Multiply');link(sine,half,'A');link(constant(.5),half,'B');remap=node('Add');link(half,remap,'A');link(constant(.5),remap,'B')
color=node('LinearInterpolate');link(node('Constant3Vector',constant=unreal.LinearColor(.018,.023,.022,1)),color,'A');link(node('Constant3Vector',constant=unreal.LinearColor(.19,.22,.20,1)),color,'B');link(remap,color,'Alpha');ml.connect_material_property(color,'',unreal.MaterialProperty.MP_BASE_COLOR);ml.connect_material_property(constant(.7),'',unreal.MaterialProperty.MP_ROUGHNESS);ml.connect_material_property(constant(.45),'',unreal.MaterialProperty.MP_METALLIC);ml.recompile_material(mat);lib.save_loaded_asset(mat)
manager=actors.get('R12_Gondola_Mechanism') or aa.spawn_actor_from_class(unreal.GondolaMechanism,unreal.Vector());manager.set_actor_label('R12_Gondola_Mechanism');manager.set_folder_path('R12/Gondola Mechanism');manager.gondola=actors['BP_GondolaSystem']
rotors=[];ropeparts=[];installed=[]
def spawn(name,mesh,p,moving=False):
 a=actors.get(name) or aa.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(*p));a.set_actor_label(name);a.set_folder_path('R12/Gondola Mechanism');a.static_mesh_component.set_mobility(unreal.ComponentMobility.MOVABLE if moving else unreal.ComponentMobility.STATIC);a.static_mesh_component.set_static_mesh(mesh);a.set_actor_rotation(unreal.Rotator(pitch=0,yaw=180,roll=0),True);a.set_actor_location(unreal.Vector(*p),False,True);a.static_mesh_component.set_collision_profile_name('NoCollision' if moving else 'BlockAll');installed.append(name);return a
def rotor(a,axis,radius,ratio):
 r=unreal.GondolaRotor();r.actor=a;r.world_axis=unreal.Vector(*axis);r.pitch_radius_cm=radius;r.ratio=ratio;rotors.append(r)
terminalorigins=[]
for idx in [0,-1]:
 p=plan['rope_samples_m'][idx];terminalorigins.append([p[0]*100+25,p[1]*100,p[2]*100])
for row in rows:
 origin=terminalorigins[row['terminal']];p=row['pivot'];pos=[origin[0]-p[0]*100,origin[1]+p[1]*100,origin[2]+p[2]*100];moving=row['part'] in ['Wheel','Shaft','Input'];a=spawn(row['name'].replace('SM_GM_','R12_GM_'),meshes[row['name']],pos,moving)
 if moving:rotor(a,row['axis'],188.7758,row['ratio'])
 if row['part']=='Rope':a.static_mesh_component.set_material(0,mat);a.static_mesh_component.set_collision_profile_name('NoCollision');ropeparts.append(a)
for row in pylons['meshes']:
 if row['name'].startswith('SM_GM_Pylon_'):
  index=int(row['name'][-2:]);old=actors['R12_Route_Pylon_%02d'%index];old.static_mesh_component.set_static_mesh(meshes[row['name']])
for index,row in enumerate(pylons['rotors']):
 tower=actors['R12_Route_Pylon_%02d'%row['tower']];o=tower.get_actor_location();p=row['center'];a=spawn('R12_GM_Roller_%02d'%index,meshes[row['mesh']],[o.x-p[0]*100,o.y+p[1]*100,o.z+p[2]*100],True);rotor(a,[1,0,0],row['radius_cm'],-1 if row['lane']=='Passenger' else 1)
for row in shell:actors[row['replace_label']].static_mesh_component.set_static_mesh(meshes[row['name']])
for label in ['R12_Route_Terminal_Millford','R12_Route_Terminal_Maldek','R12_Route_Cable_Passenger','R12_Route_Cable_Return','R12_04_Lower_Drive_001_thin','R12_04_Lower_Drive_004_signage']:
 actors[label].static_mesh_component.set_static_mesh(None)
# Retire the always-on flywheel loop: new sources follow drive state.
actors['R12_Audio_Flywheel'].get_component_by_class(unreal.AudioComponent).set_sound(None)
manager.rotors=rotors;manager.rope_parts=ropeparts
# Foundation legs reach terrain under both frames; no floating pads over the gorge.
terrain_names=json.loads((b/'gondola_route/survey.json').read_text())['terrain'];terrain=[actors[n] for n in terrain_names];ignore=[a for a in aa.get_all_level_actors() if a not in terrain]
for terminal,xs,ys,top in [(0,[-4,2.2],[-5],terminalorigins[0][2]-10.127*100),(1,[-3.175,.825],[2.8,6.9],terminalorigins[1][2]-6.1225*100)]:
 for x in xs:
  for y in ys:
   o=terminalorigins[terminal];px=o[0]-x*100;py=o[1]+y*100;hit=unreal.SystemLibrary.line_trace_single(w,unreal.Vector(px,py,180000),unreal.Vector(px,py,-150000),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,ignore,unreal.DrawDebugTrace.NONE)
   assert hit.to_tuple()[0];bottom=min(top-100,hit.to_tuple()[5].z-180);a=spawn('R12_GM_Foundation_%d_%s_%s'%(terminal,x,y),lib.load_asset('/Engine/BasicShapes/Cube'),[px,py,(top+bottom)/2]);a.set_actor_scale3d(unreal.Vector(1.1,1.1,(top-bottom)/100));a.static_mesh_component.set_material(0,lib.load_asset(oldroot+'/Materials/M_Pylon_Concrete'))
# Place the decorative distant facade behind the mechanical terminal envelope.
survey=json.loads((b/'gondola_route/survey.json').read_text());delta=survey['remote'][1]+1100-actors['R10_Distant_Station'].get_actor_location().y
for label,a in actors.items():
 if label=='R10_Distant_Station' or label.startswith('R10_Distant_Window_'):a.set_actor_location(a.get_actor_location()+unreal.Vector(0,delta,0),False,True)
assert ls.save_current_level();RESULT={'saved':True,'rotors':len(rotors),'rope_parts':len(ropeparts),'installed':installed,'terminal_origins':terminalorigins};(out/'install.json').write_text(json.dumps(RESULT,indent=2))

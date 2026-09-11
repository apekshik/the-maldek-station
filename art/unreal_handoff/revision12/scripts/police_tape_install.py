# Existing relocated installations must keep their authored station-approach placement.
from pathlib import Path
import runpy
_revision=Path(__file__).resolve().parents[1]
if (_revision/'police_tape/relocation/placement.json').exists():
 runpy.run_path(str(_revision/'scripts/police_tape_fit_install.py'))
 runpy.run_path(str(_revision/'scripts/police_tape_fit_anchors.py'))
 RESULT={'saved':True,'relocated_placement_preserved':True}
else:
 import unreal,json,math,shutil,traceback
 from pathlib import Path
 b=Path(__file__).resolve().parents[1];repo=b.parents[2];out=b/'police_tape';root='/Game/MaldekRefinement/R12/PoliceTape'
 ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);lib=unreal.EditorAssetLibrary;at=unreal.AssetToolsHelpers.get_asset_tools();ml=unreal.MaterialEditingLibrary
 assert not ls.is_in_play_in_editor()
 w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert w.get_name()=='Station_R12'
 origin=json.loads((b.parent/'working_level_report.json').read_text())['station_origin']
 def wp(p):return unreal.Vector(origin[0]-100*p[0],origin[1]+100*p[1],origin[2]+100*p[2])
 def vec(p):return [p.x,p.y,p.z]
 actors={a.get_actor_label():a for a in aa.get_all_level_actors()}
 backup=out/'backup/Station_R12.umap'
 if not backup.exists():
  assert ls.save_current_level();backup.parent.mkdir(exist_ok=True);shutil.copy2(repo/'game/Content/MaldekRefinement/R12/Station_R12.umap',backup)
 unreal.SystemLibrary.execute_console_command(w,'Interchange.FeatureFlags.Import.FBX 0')
 def imp(file,name,mesh=False):
  if lib.does_asset_exist(root+'/'+name):return lib.load_asset(root+'/'+name)
  t=unreal.AssetImportTask();t.filename=str(file);t.destination_path=root;t.destination_name=name;t.automated=True;t.save=True;t.replace_existing=True
  if mesh:
   opt=unreal.FbxImportUI();opt.import_mesh=True;opt.import_materials=False;opt.import_textures=False;opt.automated_import_should_detect_type=False;opt.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH;opt.static_mesh_import_data.combine_meshes=True;opt.static_mesh_import_data.auto_generate_collision=False;t.options=opt
  at.import_asset_tasks([t]);return lib.load_asset(root+'/'+name)
 mesh=imp(repo/'art/blender/police_tape_03/exports/SM_Tape_RuntimeSegment.fbx','SM_Tape_RuntimeSegment',True)
 wrap=imp(repo/'art/blender/police_tape_03/exports/SM_Tape_TrunkWrap.fbx','SM_Tape_TrunkWrap',True)
 texture=imp(repo/'art/blender/police_tape_01/textures/T_PoliceTape_BaseColor.png','T_PoliceTape')
 m=lib.load_asset(root+'/M_PoliceTape') or at.create_asset('M_PoliceTape',root,unreal.Material,unreal.MaterialFactoryNew());ml.delete_all_material_expressions(m);m.set_editor_property('two_sided',True)
 def node(kind,**props):
  n=ml.create_material_expression(m,getattr(unreal,'MaterialExpression'+kind))
  for k,v in props.items():n.set_editor_property(k,v)
  return n
 def link(a,c,pin='',output=''):assert ml.connect_material_expressions(a,output,c,pin)
 uv=node('TextureCoordinate');u=node('ComponentMask',r=True,g=False,b=False);v=node('ComponentMask',r=False,g=True,b=False);link(uv,u);link(uv,v)
 length=node('ScalarParameter',parameter_name='TileLength',default_value=1.);offset=node('ScalarParameter',parameter_name='TileOffset',default_value=0.)
 mul=node('Multiply');link(u,mul,'A');link(length,mul,'B');add=node('Add');link(mul,add,'A');link(offset,add,'B');append=node('AppendVector');link(add,append,'A');link(v,append,'B')
 link(v,append,'B')
 sample=node('TextureSample',texture=texture);link(append,sample,'UVs');ml.connect_material_property(sample,'RGB',unreal.MaterialProperty.MP_BASE_COLOR)
 rough=node('Constant',r=.43);ml.connect_material_property(rough,'',unreal.MaterialProperty.MP_ROUGHNESS)
 ml.recompile_material(m);lib.save_loaded_asset(m)
 for asset in [mesh,wrap]:asset.set_material(0,m);lib.save_loaded_asset(asset)
 def progress(text):(out/'progress.txt').write_text(text)
 progress('assets ready')
 ground=[a for a in actors.values() if isinstance(a,unreal.Landscape) or a.get_actor_label() in ['VF10_Parking_Terrain','VF10_Parking_Ground','VF10_Parking_Forest_Connector']]
 ignore=[a for a in actors.values() if a not in ground]
 def floor(p):
  h=unreal.SystemLibrary.line_trace_single(w,p+unreal.Vector(0,0,2000),p-unreal.Vector(0,0,3000),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,ignore,unreal.DrawDebugTrace.NONE,True)
  assert h,'Ground trace failed';return h.to_tuple()[5].z
 progress('tracing ground')
 path=json.loads((b/'forest_arrival_alignment.json').read_text())['path'];centre=wp(path[28]);q=wp(path[29]);p=wp(path[27]);forward=q-p;forward.z=0;forward=forward/forward.length();side=unreal.Vector(forward.y,-forward.x,0)
 centre.z=floor(centre);treepoints=[centre-side*225,centre+side*225];heights=[floor(p) for p in treepoints]
 basez=max(centre.z,max(heights)-70);centre.z=basez
 progress('loading anchor tree')
 tree_mesh=lib.load_asset('/Game/Megaplant_Library/Tree_European_Beech/Tree_European_Beech_01/SK_European_Beech_01_B');assert tree_mesh
 for i,(p,z) in enumerate(zip(treepoints,heights)):
  progress('spawning tree '+str(i))
  label=f'PoliceTape_AnchorTree_{i}';a=actors.get(label) or aa.spawn_actor_from_class(unreal.SkeletalMeshActor,p);a.set_actor_label(label);a.set_folder_path('R12/PoliceTape')
  scale=.85;bounds=tree_mesh.get_bounds();p.z=z-(bounds.origin.z-bounds.box_extent.z)*scale-22;a.set_actor_location(p,False,True);a.set_actor_scale3d(unreal.Vector(scale,scale,scale));a.skeletal_mesh_component.set_skeletal_mesh_asset(tree_mesh);a.skeletal_mesh_component.set_collision_profile_name('NoCollision')
  label=f'PoliceTape_AnchorCollision_{i}';proxy=actors.get(label) or aa.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(p.x,p.y,z+400));proxy.set_actor_label(label);proxy.set_folder_path('R12/PoliceTape');proxy.static_mesh_component.set_static_mesh(lib.load_asset('/Engine/BasicShapes/Cylinder'));proxy.set_actor_scale3d(unreal.Vector(.3,.3,8));proxy.set_actor_location(unreal.Vector(p.x,p.y,z+400),False,True);proxy.static_mesh_component.set_collision_profile_name('BlockAll');proxy.set_actor_hidden_in_game(True);proxy.set_is_temporarily_hidden_in_editor(True)
 def tape_actor(label,start,end,crossing):
  mid=(start+end)*.5;direction=end-start;yaw=math.degrees(math.atan2(direction.y,direction.x));a=actors.get(label) or aa.spawn_actor_from_class(unreal.StationPoliceTape,mid,unreal.Rotator(yaw=yaw));a.set_actor_label(label);a.set_folder_path('R12/PoliceTape');a.set_actor_location(mid,False,True);a.set_actor_rotation(unreal.Rotator(yaw=yaw),False)
  distance=math.hypot(direction.x,direction.y);a.set_editor_property('left_anchor',unreal.Vector(-distance/2,0,start.z-mid.z));a.set_editor_property('right_anchor',unreal.Vector(distance/2,0,end.z-mid.z));a.set_editor_property('crossing',crossing);a.set_editor_property('ribbon_mesh',mesh);a.set_editor_property('tape_material',m);a.reset_tape();return a
 progress('spawning runtime crossing')
 a0=centre-side*210;a1=centre+side*210;cross=tape_actor('PoliceTape_MainCrossing',a0,a1,True)
 wraps=[]
 def add_wrap(label,p,z):
  a=actors.get(label) or aa.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(p.x,p.y,z));a.set_actor_label(label);a.set_folder_path('R12/PoliceTape');a.static_mesh_component.set_static_mesh(wrap);a.static_mesh_component.set_collision_profile_name('NoCollision');a.set_actor_location(unreal.Vector(p.x,p.y,z),False,True);wraps.append(label)
 for i,p in enumerate(treepoints):
  for j,h in enumerate(([97,171,124] if i==0 else [172,98,140])):add_wrap(f'PoliceTape_Wrap_{i}_{j}',p,basez+h)
 # Extend sideways into existing forest trunks; do not string across another trail.
 chains=[(treepoints[1],['FT_European_Beech_004','FT_European_Aspen_039','FT_European_Aspen_017']), (treepoints[0],['FT_European_Aspen_002','FT_European_Beech_038','FT_European_Aspen_016'])]
 perimeter=[]
 for k,(start,labels) in enumerate(chains):
  previous=unreal.Vector(start.x,start.y,basez+128)
  for j,label in enumerate(labels):
   target=actors[label].get_actor_location();target.z=floor(target)+130
   d=target-previous;d.z=0;d=d/d.length();seg=tape_actor(f'PoliceTape_Perimeter_{k}_{j}',previous+d*20,target-d*20,False);seg.set_actor_tick_enabled(False);perimeter.append(seg.get_actor_label());add_wrap(f'PoliceTape_PerimeterWrap_{k}_{j}',target,target.z);previous=target
 assert ls.save_current_level()
 report={'saved':True,'centre_world':vec(centre),'side':vec(side),'forward':vec(forward),'path_index':28,'ground_world_z':floor(centre),'base_world_z':basez,'tree_ground_world_z':heights,'crossing':cross.get_path_name(),'perimeter':perimeter,'wraps':wraps,'segment_bounds':str(mesh.get_bounds()),'material':m.get_path_name()}
 (out/'installation.json').write_text(json.dumps(report,indent=2));RESULT=report
 
 
 # Preserve the height-specific bark fitting when rebuilding this installation.
 if (out/'wrap_fit/fitted.json').exists():
  import runpy
  runpy.run_path(str(b/'scripts/police_tape_fit_install.py'))
  runpy.run_path(str(b/'scripts/police_tape_fit_anchors.py'))

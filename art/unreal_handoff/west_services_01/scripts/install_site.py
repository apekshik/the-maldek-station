"""Fit bounded ground and relocate native vegetation with persistent transforms."""
import unreal,json,math,hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[1];B=json.loads((P/'baseline.json').read_text());o=B['origin'];aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert w.get_name()=='Station_Lodge_Migration' and not ls.is_in_play_in_editor();assert not (P/'site_install.json').exists()
actors=aa.get_all_level_actors();by={a.get_actor_label():a for a in actors};root='/Game/MaldekRefinement/WestServices/Ground';lib=unreal.EditorAssetLibrary
unreal.SystemLibrary.execute_console_command(w,'Interchange.FeatureFlags.Import.FBX 0');task=unreal.AssetImportTask();task.filename=str(P/'fbx/SM_WS_Site_Ground.fbx');task.destination_path=root;task.automated=True;task.save=False;opt=unreal.FbxImportUI();opt.import_mesh=True;opt.import_materials=False;opt.import_textures=False;opt.automated_import_should_detect_type=False;opt.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH;d=opt.static_mesh_import_data;d.combine_meshes=True;d.auto_generate_collision=False;d.convert_scene=True;d.convert_scene_unit=True;d.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_COMPUTE_NORMALS;task.options=opt;unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task]);mesh=lib.load_asset(root+'/SM_WS_Site_Ground');assert mesh
c=by['VF10_Parking_Terrain'].static_mesh_component;old=c.static_mesh;assert 'SM_Lodge_Site_Ground' in old.get_name()
for i in range(len(mesh.static_materials)):mesh.set_material(i,c.get_material(min(i,len(old.static_materials)-1)))
mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE);assert lib.save_loaded_asset(mesh);c.set_static_mesh(mesh)
def xyz(v):return [v.x,v.y,v.z]
def wp(p):return unreal.Vector(o[0]-100*p[0],o[1]+100*p[1],o[2]+100*p[2])
terrain=[by[n] for n in ['Landscape0','VF10_Parking_Terrain','VF10_Parking_Ground']];ignore=[a for a in actors if a not in terrain]
def ground(x,y):
 h=unreal.SystemLibrary.line_trace_single(w,wp([x,y,50]),wp([x,y,-100]),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,ignore,unreal.DrawDebugTrace.NONE,True);assert h and h.to_tuple()[0];return (h.to_tuple()[5].z-o[2])/100
fol=by['InstancedFoliageActor0'];native=dict(unreal.StationMigrationLibrary.get_foliage_instance_transforms(fol));(P/'native_foliage_baseline.json').write_text(json.dumps({k:xyz(t.translation) for k,t in native.items()}))
V=json.loads((P/'vegetation_baseline.json').read_text());moves=[];treeindex=0
for r in V:
 if r['actor']!='InstancedFoliageActor0':continue
 x,y,z=r['position'];conflict=r['lo'][0]<-28.7 and r['hi'][0]>-40.7 and r['lo'][1]<11 and r['hi'][1]>-13.7 and r['lo'][2]<8.5 and r['hi'][2]>.8
 if not conflict and not (-51<x<-28.15 and -16<y<16):continue
 expected=unreal.Vector(*r['world']);matches=[(k,t) for k,t in native.items() if (t.translation-expected).length()<.1];assert len(matches)==1,(r['actor'],r['index'],len(matches));key,t=matches[0]
 if conflict:
  if 'Pine' in r['mesh']:
   # Staggered outer canopy line; keep full bounds outside the new platform.
   y=-17+(treeindex//2)*5.2+(1.7 if treeindex%2 else 0);x=-42.0-(r['hi'][0]-r['position'][0])-(2.2 if treeindex%2 else 0);treeindex+=1
  else:x=-42.2-(r['hi'][0]-r['position'][0]);y=-5+len(moves)%12
 gz=ground(x,y);new=wp([x,y,gz-.06])
 if not conflict and abs(new.z-expected.z)<12:continue
 typ,idx=key.rsplit('|',1);assert unreal.StationMigrationLibrary.move_r12_foliage_instance(fol,typ,int(idx),expected,new),key
 moves.append({'key':key,'mesh':r['mesh'],'before':r['world'],'after':xyz(new),'source_after':[x,y,gz-.06],'reason':'clear platform and provide outward canopy' if conflict else 'ground reseat after bounded bank shaping'});(P/'foliage_moves_progress.json').write_text(json.dumps(moves,indent=2))
assert ls.save_current_level();RESULT={'ground_mesh':mesh.get_path_name(),'previous_ground_mesh':old.get_path_name(),'moves':moves,'relocated_canopy_trees':treeindex};(P/'site_install.json').write_text(json.dumps(RESULT,indent=2))

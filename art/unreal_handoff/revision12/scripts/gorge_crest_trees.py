"""Near-edge treetops supply a first depth cue using existing light only."""
import unreal,json,sys,random
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'gorge';sys.path.insert(0,str(Path(__file__).resolve().parent))
from gorge_shape import lip
ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert not ls.is_in_play_in_editor()
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);actors=aa.get_all_level_actors();w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();o=json.loads((b.parent/'working_level_report.json').read_text())['station_origin']
def wp(x,y,z):return unreal.Vector(o[0]-100*x,o[1]+100*y,o[2]+100*z)
ground=[a for a in actors if isinstance(a,unreal.Landscape) or a.get_actor_label()=='VF10_Parking_Terrain'];ignore=[a for a in actors if a not in ground]
source=unreal.load_asset('/Game/MaldekRefinement/R06/Foliage/FT_R06_Pine_0');mesh=source.get_editor_property('mesh');bd=mesh.get_bounds();lib=unreal.EditorAssetLibrary
path='/Game/MaldekRefinement/R12/Gorge/Foliage/FT_Gorge_Crest';ft=unreal.load_asset(path) or lib.duplicate_asset(source.get_path_name(),path)
ft.set_editor_property('cull_distance',unreal.Int32Interval(min=16000,max=20000));lib.save_loaded_asset(ft)
rng=random.Random(719);trans=[];rows=[]
for i,x in enumerate([-44,-37,-31,-25,-20,-14,14,21,29,39,50,62]):
 y=lip(x)+rng.uniform(8,11)
 hit=unreal.SystemLibrary.line_trace_single(w,wp(x,y,30),wp(x,y,-160),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,ignore,unreal.DrawDebugTrace.NONE,True);assert hit
 z=(hit.to_tuple()[5].z-o[2])/100;desired_top=rng.uniform(-2,-.7);scale=min(1.2,(desired_top-z)/(2*bd.box_extent.z/100));bottom=(bd.origin.z-bd.box_extent.z)*scale/100
 trans.append(unreal.Transform(location=wp(x,y,z-bottom-.18),rotation=unreal.Rotator(yaw=i*137),scale=unreal.Vector(scale,scale,scale)));rows.append({'xy':[x,y],'root_z':z,'canopy_top':desired_top-.18,'scale':scale})
unreal.InstancedFoliageActor.remove_all_instances(w,ft);unreal.InstancedFoliageActor.add_instances(w,ft,trans);assert ls.save_current_level()
RESULT={'trees':len(rows),'mesh':mesh.get_path_name(),'mesh_height_m':2*bd.box_extent.z/100};(out/'crest_trees.json').write_text(json.dumps({'result':RESULT,'trees':rows},indent=2))

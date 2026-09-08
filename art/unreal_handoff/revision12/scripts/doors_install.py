"""Install approved standard doors only. Keypad blueprint remains unplaced for review."""
import unreal,json
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'doors';root='/Game/MaldekRefinement/R12/Doors';lib=unreal.EditorAssetLibrary;at=unreal.AssetToolsHelpers.get_asset_tools();aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert hasattr(unreal,'StationDoor') and hasattr(unreal.StationDoor,'submit_code'),'Final keypad native build must be loaded'
assert not ls.is_in_play_in_editor();w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert w.get_name()=='Station_R12'
assert json.loads((out/'import.json').read_text())['success']
classes={}
for name,secured in [('BP_StationDoor_Standard',False),('BP_StationDoor_Keypad',True)]:
 bp=lib.load_asset(root+'/'+name)
 if not bp:
  factory=unreal.BlueprintFactory();factory.set_editor_property('parent_class',unreal.StationDoor);bp=at.create_asset(name,root,unreal.Blueprint,factory)
 cdo=unreal.get_default_object(bp.generated_class())
 for prop,part in [('leaf','Leaf'),('glass','Glass'),('fixed_hardware','Fixed'),('keypad','Keypad'),('interior_electronics','InteriorElectronics'),('electronic_strike','ElectronicStrike')]:
  cdo.get_editor_property(prop).set_static_mesh(lib.load_asset(root+'/Meshes/SM_StationDoor_'+part))
 cdo.set_editor_property('has_keypad',secured);cdo.set_editor_property('locked',secured);cdo.set_editor_property('access_code','')
 unreal.BlueprintEditorLibrary.compile_blueprint(bp);assert lib.save_loaded_asset(bp,False);classes[name]=bp.generated_class()
actors={a.get_actor_label():a for a in aa.get_all_level_actors()}
preserved={k:[list(a.get_actor_location().to_tuple()),list(a.get_actor_rotation().to_tuple()),list(a.get_actor_scale3d().to_tuple())] for k,a in actors.items() if not k.startswith('R12_Door_')}
origin=json.loads((b.parent/'working_level_report.json').read_text())['station_origin']
def wp(p):return unreal.Vector(origin[0]-100*p[0],origin[1]+100*p[1],origin[2]+100*p[2])
# Two measured 1.3 x 2.4 m control entries. No frame or threshold replacement.
placements=[('Control_front',(-2.654,.035,4),0),('Control_side',(-8.035,-2.504,4),-90)]
made=[]
for name,p,yaw in placements:
 label='R12_Door_'+name;a=actors.get(label)
 if a:assert isinstance(a,unreal.StationDoor)
 else:a=aa.spawn_actor_from_class(classes['BP_StationDoor_Standard'],wp(p),unreal.Rotator(yaw=yaw))
 a.set_actor_label(label);a.set_folder_path('R12/Architecture/Doors');a.set_actor_location(wp(p),False,True);a.set_actor_rotation(unreal.Rotator(yaw=yaw),False)
 a.set_editor_property('has_keypad',False);a.set_editor_property('locked',False);made.append({'label':label,'position':list(a.get_actor_location().to_tuple()),'yaw':yaw})
for k,v in preserved.items():
 a=actors[k];assert v==[list(a.get_actor_location().to_tuple()),list(a.get_actor_rotation().to_tuple()),list(a.get_actor_scale3d().to_tuple())],k
assert ls.save_current_level()
RESULT={'success':True,'placed':made,'unplaced_keypad_blueprint':root+'/BP_StationDoor_Keypad','keypad_locations':'Awaiting user review','other_actor_transforms_preserved':len(preserved),'existing_building_meshes_modified':False}
(out/'install.json').write_text(json.dumps(RESULT,indent=2))

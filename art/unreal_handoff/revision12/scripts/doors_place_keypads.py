"""User-approved keypad placement: control front and both distant relay entries, code 1234."""
import unreal,json
from pathlib import Path
b=Path(__file__).resolve().parents[1];out=b/'doors';root='/Game/MaldekRefinement/R12/Doors';aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);lib=unreal.EditorAssetLibrary
assert not ls.is_in_play_in_editor()
assert unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_name()=='Station_R12'
actors={a.get_actor_label():a for a in aa.get_all_level_actors()}
preserved={n:a.get_actor_transform() for n,a in actors.items() if not n.startswith('R12_Door_')}
origin=json.loads((b.parent/'working_level_report.json').read_text())['station_origin']
def wp(p):return unreal.Vector(origin[0]-p[0]*100,origin[1]+p[1]*100,origin[2]+p[2]*100)
bp=lib.load_asset(root+'/BP_StationDoor_Keypad');cdo=unreal.get_default_object(bp.generated_class());cdo.set_editor_property('access_code','1234');unreal.BlueprintEditorLibrary.compile_blueprint(bp);assert lib.save_loaded_asset(bp,False)
# Relay clear openings measured in evaluated VF07 geometry: 1.2m x 2.3m.
# Keep 6mm side/head gaps and 10mm clearance above the existing 24mm threshold.
sx=1.188/1.288;sz=2.26/2.36;dz=.034*(1-sz)
placements=[('Control_front',None,0,(1,1,1),True),('Control_side',None,-90,(1,1,1),False),('Relay_north',(48.6-.006+.002*sx,15.035,3+dz),0,(sx,1,sz),True),('Relay_south',(47.4+.006-.002*sx,10.965,3+dz),180,(sx,1,sz),True)]
rows=[]
for name,pos,yaw,scale,secured in placements:
 label='R12_Door_'+name;a=actors.get(label)
 if not a:
  assert pos is not None;a=aa.spawn_actor_from_class(bp.generated_class(),wp(pos),unreal.Rotator(yaw=yaw))
 assert isinstance(a,unreal.StationDoor)
 a.set_actor_label(label);a.set_folder_path('R12/Architecture/Doors');a.set_editor_property('has_keypad',secured);a.set_editor_property('locked',secured);a.set_editor_property('access_code','1234' if secured else '');a.set_editor_property('open_angle',95)
 if pos:a.set_actor_location(wp(pos),False,True);a.set_actor_rotation(unreal.Rotator(yaw=yaw),False)
 a.set_actor_scale3d(unreal.Vector(*scale))
 for c in [a.keypad,a.interior_electronics,a.electronic_strike,a.get_editor_property('KeypadDisplay')]:c.set_visibility(secured)
 a.get_editor_property('KeypadDisplay').set_text('LOCKED')
 rows.append({'label':label,'secured':secured,'code':a.access_code,'location':list(a.get_actor_location().to_tuple()),'scale':list(scale),'yaw':yaw})
for name,t in preserved.items():assert actors[name].get_actor_transform()==t,name
assert ls.save_current_level()
RESULT={'success':True,'doors':rows,'other_actor_transforms_preserved':len(preserved),'relay_clear_opening_metres':[1.2,2.3],'relay_leaf_metres':[1.188,2.26],'threshold_clearance_metres':.010}
(out/'keypad_install.json').write_text(json.dumps(RESULT,indent=2))


"""PIE regression: physical keypad hints, exterior security and unrestricted inside exit."""
import unreal, time, json, traceback, math
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'doors'/'prompt_egress'
out.mkdir(parents=True,exist_ok=True)
ls=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert not ls.is_in_play_in_editor()
s={'phase':0,'index':0,'next':time.monotonic()+10,'deadline':time.monotonic()+180,'checks':{}}
labels=['R12_Door_Control_front','R12_Door_Relay_north','R12_Door_Relay_south']
def check(name,value):
    s['checks'][labels[s['index']]+'_'+name]=bool(value)
    assert value,name
def key(k):
    unreal.StationMigrationLibrary.send_pie_key(k,True)
    unreal.StationMigrationLibrary.send_pie_key(k,False)
def place(y,x=65):
    p.set_actor_location(unreal.MathLibrary.transform_location(d.get_actor_transform(),unreal.Vector(x,y,105/d.get_actor_scale3d().z)),False,True)
    p.character_movement.stop_movement_immediately()
    pc.set_control_rotation(unreal.Rotator(yaw=d.get_actor_rotation().yaw+(-90 if y>0 else 90)))
def finish(error=None):
    s.update(success=error is None,error=error)
    (out/'runtime.json').write_text(json.dumps(s,indent=2))
    unreal.StationMigrationLibrary.set_pie_render_size(0,0)
    unreal.unregister_slate_post_tick_callback(handle)
    ls.editor_request_end_play()
def shot(suffix):
    unreal.SystemLibrary.execute_console_command(w,'Shot SHOWUI filename='+str(out/(labels[s['index']]+'_'+suffix+'.png')))
def tick(dt):
    global w,p,pc,d,doors,prompt,first_rotation
    now=time.monotonic()
    if now<s['next']:return
    try:
        assert now<s['deadline'],'timeout'
        w=unreal.EditorLevelLibrary.get_game_world()
        if not w:return
        p=unreal.GameplayStatics.get_player_pawn(w,0);pc=unreal.GameplayStatics.get_player_controller(w,0)
        if not p:return
        phase=s['phase']
        if phase==0:
            unreal.StationMigrationLibrary.set_pie_render_size(1280,720)
            # Remove only the PIE tutorial instance so its introduction card does
            # not cover the door UI screenshots; saved gameplay is untouched.
            opening=p.get_component_by_class(unreal.StationOpeningComponent)
            if opening:opening.destroy_component(p)
            doors={a.get_actor_label():a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.StationDoor)}
            s.update(phase=1,next=now+.2);return
        if phase==1:
            d=doors[labels[s['index']]];prompt=d.get_editor_property('InteractionPrompt')
            place(145);s.update(phase=2,next=now+1);return
        if phase==2:
            check('starts_locked',d.is_locked());check('world_prompt_visible',prompt.is_visible())
            check('world_space',prompt.get_widget_space()==unreal.WidgetSpace.WORLD)
            check('nonblocking_prompt',prompt.get_collision_enabled()==unreal.CollisionEnabled.NO_COLLISION)
            first_rotation=prompt.get_world_rotation();shot('outside');place(145,95)
            s.update(phase=3,next=now+1);return
        if phase==3:
            rotation=prompt.get_world_rotation()
            check('turns_toward_player',abs(rotation.yaw-first_rotation.yaw)>3)
            eye=unreal.GameplayStatics.get_player_camera_manager(w,0).get_camera_location()
            direction=eye-prompt.get_world_location();forward=prompt.get_forward_vector()
            dot=(direction.x*forward.x+direction.y*forward.y+direction.z*forward.z)/math.sqrt(direction.x**2+direction.y**2+direction.z**2)
            check('faces_camera',dot>.99);shot('angled');key('E');s.update(phase=4,next=now+1);return
        if phase==4:
            check('outside_enters_keypad',d.is_using_keypad());check('outside_stays_locked',d.is_locked())
            shot('inspection');d.cancel_keypad_interaction();place(-145);s.update(phase=5,next=now+1);return
        if phase==5:
            check('inside_hint_visible',prompt.is_visible());shot('inside');key('E');s.update(phase=6,next=now+.4);return
        if phase==6:
            check('inside_releases_lock',not d.is_locked());check('inside_skips_inspection',not d.is_using_keypad())
            check('inside_preserves_controls',not pc.is_move_input_ignored() and not pc.is_look_input_ignored())
            check('inside_bolt_audio',d.get_editor_property('LockAudio').sound==d.unlock_sound)
            s.update(phase=7,next=now+2.5);return
        if phase==7:
            check('inside_opens_fully',abs(d.get_open_angle()-d.open_angle)<.1)
            d.try_interact();s.update(phase=8,next=now+3);return
        if phase==8:
            check('closing_relocks',d.is_locked() and abs(d.get_open_angle())<.01)
            check('closing_bolt_audio',d.get_editor_property('LockAudio').sound==d.lock_sound)
            place(145);s.update(phase=9,next=now+.8);return
        if phase==9:
            key('E');s.update(phase=10,next=now+1);return
        if phase==10:
            check('outside_still_requires_code_after_exit',d.is_using_keypad() and d.is_locked())
            check('wrong_code_rejected',not d.submit_code('9999') and d.is_locked())
            check('correct_code_accepted',d.submit_code('1234') and not d.is_locked())
            d.lock();pc.set_control_rotation(unreal.Rotator(yaw=d.get_actor_rotation().yaw+90));s.update(phase=11,next=now+.8);return
        if phase==11:
            check('hint_hides_when_looking_away',not prompt.is_visible())
            s['index']+=1
            if s['index']==len(labels):finish();return
            s.update(phase=1,next=now+.2)
    except Exception:finish(traceback.format_exc())
handle=unreal.register_slate_post_tick_callback(tick)
ls.editor_request_begin_play()
RESULT={'started':True}

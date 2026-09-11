import unreal
w=unreal.EditorLevelLibrary.get_game_world();a=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.StationInspectable) if a.actor_has_tag('ParkingInspectionCassette'))
a.set_actor_location(a.get_actor_location()+unreal.Vector(0,0,3),False,True)
RESULT={'raised_3cm_for_visual_comparison':True}

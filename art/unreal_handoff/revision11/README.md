# R11: exposed lookout and separate maintenance building

Open `/Game/MaldekRefinement/R11/BlockOut_R11` in UE 5.7. Press Play to start at the remote parking approach; WASD/mouse to explore, F to toggle the hand flashlight. R11 inherits the R10 pawn and game mode. The central control room is unchanged.

## Layout

- A 24.16 m steel bridge, 1.5 m wide, bends toward a 5 x 6 m lookout over the canyon. Grating, edge channels, guards, truss members, towers, stays and terrain-grounded footings provide the structural blockout. Walking collision uses continuous simple floor proxies.
- A 24.84 m service path bends around a rock shoulder to a separate 6 x 8 m generator room, a 3 x 5 m workshop, and a 9 x 5 m outdoor tank yard. Equipment is relocated from the previous lower rooms.
- The inherited R10 pass patches gondola-side floor gaps, opens access to the side grating, removes the floating stair rail, enlarges the waiting hall and moves parking along a roughly 58 m forest approach.
- Canyon terrain replaces the immediate green setting; the far drop beneath the lookout is approximately 120 m. Terrain and cliff surfaces remain coarse blockout geometry.
- Five restrained, housed light fixtures mark the new destinations. Trees were cleared from circulation and the bridge span; 150 pines remain. Quiet looping forest wind and Ultra Dynamic Weather wind are enabled.
- The moon is aligned outward along the gondola direction at 20 degrees elevation. A distant station proxy sits on a ridge about 1.4 km away; its readability through the final fog still needs an artistic review.

## Validation

`geometry_verification.json`: continuous route floor traces and doorway clearance passed. `play_verification.json`: the actual player walked both gondola-side routes, the full bridge, service path and workshop doorway without falling or becoming blocked. The gondola transform remained fixed and wind audio was playing.

`flashlight_toggle.json`: physical F presses changed visibility true -> false -> true in PIE after a successful full Development Editor build and restart. `beam_hotspot.png` shows the revised hotspot, spill and soft halo on a wall; `flashlight_off.png` captures the off state.

`final_saved.json`: the corrected bridge support mesh and map were saved. The final support adjustment affects below-floor structure; walkable geometry is unchanged from the successful play test.

The two `renders/06_final_bridge_structure.png` and `07_final_maintenance_layout.png` views use temporary bright inspection lighting to show geometry. That light is removed before saving the playable night scene. Earlier numbered renders predate final material/tree/support corrections.

1440p at 60 FPS is the target, not a measured result. A packaged performance pass and detailed cliff/structure art are still needed.

## Sources and reproduction

Blender source: `station_layout.blend`; exported chunks: `fbx/`. Build layout with `build_r11_layout.py` against R10 `station_patched.blend`; generate terrain using `build_r11_terrain.py`. R11 scripts live in `../scripts/`. Asset import uses the legacy FBX importer with supplied UCX collision. The final bridge-only reimport is `finish_r11.py`. Existing R10 assets remain dependencies.

Flashlight optics use a UE light-function material with a central hotspot, broad weaker spill, subtle corona and feathered edge. References: [Epic light functions](https://dev.epicgames.com/documentation/en-us/unreal-engine/using-light-functions-in-unreal-engine?application_version=5.7) and [Fenix beam examples](https://www.fenixlight.com/review-fenix-wf26r-flashlight/). This is an authored approximation, not a measured photometric profile.

Local build prerequisite: the installed Gaea Unreal Tools plugin required a project-local source copy to compile with this UE 5.7 installation. That licensed copy is excluded from Git in `.git/info/exclude`; another workstation needs its own compatible Gaea plugin installation. No plugin vendor source is included in this revision.

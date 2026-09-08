# Standard and digital-keypad door integration

## Current room coverage, sounds and interaction prompt

Ten interactable doors are installed: three keypad doors (control front and both relay entrances, code 1234) and seven standard doors with physical key locks. The six newly filled entrances are quarters, waiting hall north/south, generator south/west and the shared workshop doorway. Generator/workshop coordinates follow the current VF09/R13 service hall, not the older VF07 footprint. Existing control-side access remains standard.

The quarters and south generator leaves open inward to keep the stair landing and fuel-area approach clear. Their hinges, stops, pivot-relative geometry and collision centre are authored for that direction; their front plaques say PUSH TO OPEN. The other leaves pull outward. Current placements retain each building's existing reveals, headers and thresholds. The generator shell variant removes only the five old parked-door parts; all remaining shell collision boxes match the source exactly.

A world-facing prompt beside the door hardware uses a warm ink-brown panel, sharp brass-gold double borders, a square gold E keycap and warm cream action lettering. The shared StationInteractionStyle palette establishes the same restrained early-1990s station style for future interaction prompts. The same panel offers Return to door in the keypad close-up. It never intercepts mouse clicks. Key press, CLR, accepted OK and rejected OK now use externally sourced hardware recordings. Spatial latch, hinge and closing sounds follow actual door motion. A blocked door stops its hinge loop and does not play the closing impact until fully shut. Secured doors re-lock only after fully closing, with a separate recorded bolt click. Keypad, latch, bolt and motion playback are independent. Run doors_recorded_install.py after any legacy room installation, then doors_recorded_test.py, doors_recorded_edges.py and doors_recorded_finish.py. See art/audio/doors/README.md for source credits, preparation and current validation.

Legacy room reproduction (follow with the current key integration below): export doors_export_rooms.py, doors_export_inward.py and doors_export_service_shell.py with Blender. Run doors_install_rooms.py and doors_import_service_shell.py in the exclusive editor session. Run doors_test_rooms.py, doors_test_audio.py, doors_capture_rooms.py and doors_finish_rooms.py for validation. rooms/runtime.json, audio_review/runtime.json and room_previews/capture.json are the current evidence; older reports below describe earlier stages.

## Physical key locks

The seven standard doors now use the rounded brass Blender key and cylinder. From outside, E enters an angled close-up; hold the key head and drag toward the lock. Full insertion turns and withdraws the key automatically, unlocks, and returns to the player view. E then opens the door. Partial insertion can be resumed or reversed; E/right-click cancels. The key is available automatically. Inside E opens directly without a key or code.

Current reproduction and validation: [key lock integration](key_lock/README.md). Export doors_export_keys.py, build the native targets, then install with doors_install_keys.py. The earlier installers and reports below describe prior stages and must not replace the current key assets/settings.

## Keypad inspection camera

Press E while looking at a locked door to blend into a fixed, slightly elevated oblique close-up of its keypad. The camera uses a constrained 16:9 frame so the reader and hints stay visible across viewport shapes. Mouse movement controls a visible cursor; each click is ray-projected against the measured 3 x 4 physical key layout, including scaled relay instances. Digits appear as masked characters on the reader display. CLR clears the whole entry and OK submits it. Wrong codes leave the door locked and show TRY AGAIN. Correct code 1234 returns to the player view; E then opens the unlocked door normally.

E or right-click cancels without unlocking. Escape also cancels in standalone play (the editor may intercept it to stop PIE). Number keys/numpad, Backspace and Enter remain keyboard alternatives. Movement/look are paused and held meshes hidden during the close-up; previous player view, movement mode, input locks and mesh visibility are restored on exit or actor teardown. The first-person motion/torch settings are unchanged.

Reproduce actual cursor-click, cancellation, re-entry, wrong-code, CLR and unlock/open checks using doors_test_camera.py. Camera screenshots and runtime results are in camera/. Win64 Development game and editor builds passed; Mac runtime validation remains outstanding.

## Approved placement update

The user selected temporary code **1234** for the main control-room entrance and the distant relay station. Both relay entrances use that keypad code; the control-room side door remains standard. Relay openings are 1.2 x 2.3 metres, verified against evaluated VF07 geometry in relay_openings.json. The relay leaf plaque reads R / 01 and RELAY; relay_label_import.json verifies identical bounds and unchanged walking collision. The shared door assembly is fitted to those openings with per-instance width/height scaling, retaining its thickness, existing reveals, thresholds, 6 mm side/head gaps and 10 mm threshold clearance.

After the baseline installation below, export the relay-labelled leaf with Blender using doors_export_relay_label.py. Run doors_place_keypads.py, doors_import_relay_label.py, doors_test_keypads.py, doors_capture_keypads.py and doors_finish_keypads.py through the exclusive editor dispatcher. The keypad-prefixed reports supersede the original two-standard-door reports. All three secured entrances passed actual PIE keyboard entry of 1234, rejection of 9999, locked opening refusal, full 95-degree opening, player passage and closing. The side door remains standard. Final neutral/night captures and save/reopen verification also passed; keypad_saved_verification.json confirms all three code 1234 entrances reload locked and the side door reloads unlocked.

## Original validated baseline

Current source: `art/blender/door_study_03/Maldek_Digital_Door_Variants.blend`.
The mechanical padlock experiment is superseded and must not be installed.

Completed: Blender standard/keypad models, twelve-button geometry verification, evaluated FBX exports with shared hinge pivots, native `StationDoor` implementation, successful Win64 Development game and editor builds, and six imported meshes with validated material shaders.

Two standard doors are installed at the control room's front and side entrances. Existing building meshes, frames and thresholds are retained. The 105-degree study swing encountered an obstruction near 99 degrees in the installed assembly; the installed variants use a 95-degree target. Actual PIE verification passes E input, walking through the control entrance, closing, wrong/empty code rejection, numeric-key entry to unlock and stopping when the player obstructs closing. `runtime.json` contains the results. `previews/capture.json` and `saved_verification.json` record successful final captures and save/reopen checks. Twelve captures cover both openings under neutral and night lighting with small viewpoint changes.

The sheltered side entry uses the existing interior material variants on its leaf and fixed hardware, avoiding outdoor snow accumulation inside the adjoining hall. The front entry retains the exterior materials. These are per-component overrides; shared materials and global weather are unchanged.

Reproduce through the existing editor dispatcher in order, with exclusive editor ownership:

1. `doors_import.py` — imports only door-owned assets and materials; shader and dimensions checks. It uses the latest `door_manifest.json`, whose six mesh chunks contain no mechanical padlock assets.
2. `doors_install.py` — creates standard and digital-keypad blueprints; places only two standard doors at the measured control-room front/side openings, preserving original frames, thresholds and all other actor transforms. Keypad blueprint remains unplaced and has no assigned code.
3. `doors_test.py` — actual PIE E input, walking passage, closed/open state, wrong/empty-code rejection, digit entry, and player obstruction tests. A temporary editor test actor is cloned into PIE and removed afterward; it is never saved.
4. Capture both control openings under neutral and actual night/torch lighting; inspect rapid small-viewpoint sequences, preserve current global light settings, save/reopen and verify persistence as required by `art/MESH_AUTHORING.md`.

`StationDoor` expects E to interact. A secured door enters the close-up described above; numeric keys and Enter are optional alternatives to clicking its buttons. Codes are configured per instance (up to eight digits); an empty configured code rejects every entry. No secure locations or final codes were selected by the user. The keypad display and status light update when unlocked. Opening uses the moving leaf's collision volume and subdivided obstruction checks. The temporary test code is assigned only to the unsaved test actor; the reusable keypad blueprint has an empty default.

The frosted pane uses a local scene-color blur material rather than changing global camera effects. Its shaders compile on the tested Win64 D3D12 renderer. This is a screen-space approximation, not a physical transmission simulation; dedicated Mac rendering and performance validation are still required. Blender renders are not evidence of Unreal appearance.

Preserve the concurrent sensory settings: foot volume 3.5, idle sway 5, head bob 1.5, walk sway 1.8, run sway 3, held motion .15 and TorchV2 detailed mesh. Do not restore an older map or pawn to install doors.

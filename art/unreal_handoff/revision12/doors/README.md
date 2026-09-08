# Standard and digital-keypad door integration

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

`StationDoor` expects E to interact. A secured door accepts numeric keys, E/Enter to submit and Backspace to delete a digit. Codes are configured per instance (up to eight digits); an empty configured code rejects every entry. No secure locations or final codes were selected by the user. The keypad display and status light update when unlocked. Opening uses the moving leaf's collision volume and subdivided obstruction checks. The temporary test code is assigned only to the unsaved test actor; the reusable keypad blueprint has an empty default.

The frosted pane uses a local scene-color blur material rather than changing global camera effects. Its shaders compile on the tested Win64 D3D12 renderer. This is a screen-space approximation, not a physical transmission simulation; dedicated Mac rendering and performance validation are still required. Blender renders are not evidence of Unreal appearance.

Preserve the concurrent sensory settings: foot volume 3.5, idle sway 5, head bob 1.5, walk sway 1.8, run sway 3, held motion .15 and TorchV2 detailed mesh. Do not restore an older map or pawn to install doors.

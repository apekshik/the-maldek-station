# Digital door handoff — pending editor installation

Current source: `art/blender/door_study_03/Maldek_Digital_Door_Variants.blend`.
The mechanical padlock experiment is superseded and must not be installed.

Completed: Blender standard/keypad models, twelve-button geometry verification, evaluated FBX exports with shared hinge pivots, native `StationDoor` implementation, successful Win64 Development game build. The initial editor build predates the user's digital-keypad correction; a final editor rebuild/restart is required before installation.

Pending: editor rebuild, asset import, shader verification, standard-door placement, runtime and visual validation. The shared editor was handed to the forest task for its final pass; wait for explicit handoff before restarting or writing the level. Nothing here has yet been installed into Station_R12.

After handoff, run through the existing editor dispatcher in order:

1. `doors_import.py` — imports only door-owned assets and materials; shader and dimensions checks. It uses the latest `door_manifest.json`, whose six mesh chunks contain no mechanical padlock assets.
2. `doors_install.py` — creates standard and digital-keypad blueprints; places only two standard doors at the measured control-room front/side openings, preserving original frames, thresholds and all other actor transforms. Keypad blueprint remains unplaced and has no assigned code.
3. `doors_test.py` — actual PIE E input, walking passage, closed/open state, wrong/empty-code rejection, digit entry, and player obstruction tests. Test keypad actor exists only in PIE.
4. Capture both control openings under neutral and actual night/torch lighting; inspect rapid small-viewpoint sequences, preserve current global light settings, save/reopen and verify persistence as required by `art/MESH_AUTHORING.md`.

`StationDoor` expects E to interact. A secured door accepts numeric keys, E/Enter to submit and Backspace to clear. Codes are configured per instance (up to eight digits); an empty configured code rejects every entry. No locations or final codes were selected by the user. The keypad display and status light update when unlocked. Opening uses the moving leaf's collision volume and subdivided obstruction checks; gameplay verification remains pending.

The frosted pane uses a local scene-color blur material rather than changing global camera effects. Its engine appearance and performance still require validation. Blender renders are not evidence of Unreal appearance.

Preserve the concurrent sensory settings: foot volume 3.5, idle sway 5, head bob 1.5, walk sway 1.8, run sway 3, held motion .15 and TorchV2 detailed mesh. Do not restore an older map or pawn to install doors.

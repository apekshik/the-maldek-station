# Window reveal overlap repair

Extends the door repair to `Window_return` and `Window_head_sill` faces. Insulated wall cores shared the exact reveal planes, producing competing surfaces around the window openings. The export copy recesses those core faces 4 mm into the wall, retaining the steel returns, visible sill/head profiles, glass and mullions.

44 cores across seven assemblies are affected: control room, waiting hall, quarters, maintenance and relay. Existing door recesses and quarters beam separation are applied before selective export, so the window repair does not undo them. The approved VF07 source is hash checked and untouched. Material slots and authored collision boxes must match the previous handoff exactly or export fails.

Reproduce with Blender running `scripts/window_source_audit.py`, then `scripts/window_recess_cores.py`. Import only `changed_assets` from `core_recess.json` using the established Architecture importer. `scripts/window_verify.py` verifies imports, hashes, materials, placements and retained actor transforms. `before/` and `burst/` use matched control, hall and quarters close-ups in the production lighting. This is a visual mesh repair; no player, torch or stair tuning changes are included.

The final rapid capture is `burst/`: six images each at the control, hall and quarters windows (18 files verified). Capture requests wait for each previous image to finish saving, avoiding lost frames from Unreal's asynchronous screenshot queue. The first and last images at each location were visually compared; the broad competing wall stripe is absent and reveal surfaces are stable. `visual_review.json` and `verification.json` record acceptance; collision is byte-equivalent in the handoff records, so existing movement route acceptance is retained.

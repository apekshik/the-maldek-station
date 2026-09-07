# VF10 parking in Station_R12

Blender source and design notes: `art/blender/visual_fidelity_10`.

Apply through the established R12 editor dispatcher, with PIE stopped:
1. `parking_audit.py` records the current area and Landscape collision clearance.
2. `parking_import.py` with `dry_run: true`, then `dry_run: false`.
3. `parking_planting.py` adds deterministic clumps and moves exact audited conflicts.
4. `run_routes.py` with the three additional routes recorded in `routes.json`.
5. `parking_capture.py` for night/inspection images; `parking_verify.py` to save/check.

Do not repeat the initial audit after applying the migration: `live_before.json`
is the immutable placement/material baseline for reruns. Import targets are
R12_Retained_Parking, R12_Forest_Approach_Aligned and R13_Terrain. Their components
are retired after all five replacements import successfully. The car is retained.
The service terrain input hash must match; regenerate exports if it changes.

Rock shapes are authored study meshes; the intended next art pass substitutes
the user's Fab geology assets. Grass uses four installed MWLandscape variants;
trees use existing Megaplant species. No assets were purchased.

Rollback uses the preserved pre-parking map at commit dbb0eca. Avoid restoring
that entire map after later unrelated changes; use the explicit replacement and
planting manifests to reverse only this pass in that case.

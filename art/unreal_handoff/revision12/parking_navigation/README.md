# Parking trailhead navigation

The old connector left the east edge of the parking lot and doubled back north,
while the sign stood behind the player beside the bays. This pass creates a
3.2 m north-facing entrance, a gently graded taper to the existing forest path,
and a south-facing sign on the left of the entrance with a right-pointing arrow.
The east curb closes the misleading former opening. A small hooded warm light
illuminates the sign; the first route marker and an encroaching willow move aside.

## Scope and source

- Map: `/Game/MaldekRefinement/R12/Station_R12`.
- Two replacement meshes under `/Game/MaldekRefinement/R12/ParkingNavigation`.
- Existing furniture and connector actors retain their transforms and receive
  the new meshes. Ground, parked vehicles, player start and downstream forest
  path remain in place. Terrain meshes are not modified.
- `before.json` is the live placement/material baseline; do not overwrite it on reruns.
- `source_audit.json` preserves the previous connector vertices. New geometry
  rejoins its exact cross-section 16 and retains all following cross-sections.
- `handoff.blend`, FBXs and `handoff.json` are the reproducible mesh delivery.
  `plan.json` records the opening, centreline and sign orientation.
- Gentle grading clears the existing terrain. Gravel shoulder faces close the
  new ribbon edges below the terrain without a second overlapping top surface.

## Reproduce

1. Run `../scripts/parking_navigation_build.py` in background Blender 5.0.
2. With R12 open and PIE stopped, dispatch `parking_navigation_install.py`
   using the established R12 local editor dispatcher.
3. Dispatch `parking_navigation_ground_details.py` to retain the relocated
   willow and marker's terrain-relative base offsets.
4. Run `parking_navigation_prepare_routes.py` with local Python. It dispatches
   eight ordinary player walks: full approach, left/right entrance clearance,
   and parking bays, each forward and reverse. Results: `routes.json`.
5. Dispatch `parking_navigation_verify.py` with `reopen: true` to check the
   saved level, mesh assignments, preserved placements and 51 ground samples.
6. Dispatch `parking_navigation_capture.py` for the before/after player views.
   The capture helper removes its temporary inspection light and restores PIE.

`installation.json` records imported bounds/hulls and exact actor replacements.
`grounded_details.json`, `reopen.json`, and `final/capture.json` record the final
grounding, persistence and visual checks. `completion.json` summarizes results.

To reverse this pass, restore only the two mesh assignments and five moved actor
positions from `before.json`, then remove `Parking_Navigation_Sign_Light`.
Do not replace the whole level with an older version over later unrelated work.

# Woodland and station slope refinement

User review: sparse rear/side forest, pale isolated rock patches, repeated ground
texture, and the artificial canyon directly in front of the platform. Inspect
under the user's brighter sky settings; the installation never edits lighting.

The input is the combined service-and-parking terrain in
`../parking/terrain_grid.json`. The old front cut descended about 145 m in 10 m.
The replacement varies the lip and retains the eastern relay shoulder. A later
live trace diagnosed a much larger, flat-bottomed Landscape excavation extending
300 m beyond the mesh. The shared valley profile therefore spans both the local
mesh and the Landscape, blending back into existing hills by 650 m. It only raises
ground inside the bounded valley mask; parking and approach elevations remain
unchanged, and occupied floor meshes remain untouched. `build.json` records each
changed vertex. The original parking terrain
asset is retained; its actor now references the new mesh.

`M_Woodland_Ground` uses the installed MW dirt/grass/rock textures, with broad
color variation and three-axis rock projection on steep slopes. Soil physical
material remains assigned for the recorded footsteps. Source materials and
textures are not edited.

Planting uses the installed Megaplants common hazel, goat willow and young beech,
plus MW grass and stone meshes. Seed 1709 produces irregular clusters with
explicit approach, parking, station, relay and gondola clearance masks. Grass and
stones use instanced foliage, with distance culling; shrubs are separate skeletal
actors. The pale FT rock patches are retired except the parking pass's patch 04.

Scripts, in execution order, are under `../scripts/`:

1. `forest_refine_audit.py`: read the current map and camera.
2. `forest_refine_build.py`: run in Blender; creates FBX and combined height grid.
3. `forest_refine_install.py`: back up the saved current map locally, import the
   new terrain/material and retire old rock patches.
4. `forest_refine_plant.py`: deterministic placement, idempotent actor names and
   dedicated foliage types.
5. `forest_refine_export_landscape.py`, `forest_refine_sculpt.py`, and
   `forest_refine_apply_landscape.py`: export current owned heightmaps, prepare the
   bounded offline valley edit, and apply it without touching other map assets.
6. `forest_refine_grounding.py`: trace the live terrain for all placed Megaplants
   and painted pines, bury mesh bases by 22–25 cm, and move matching trunk collision
   proxies with them. Species, scale and rotation remain unchanged.
7. `forest_refine_finish.py` and `forest_refine_verify.py`: persistent retirement,
   grass shadow cost, live collision, placement and preservation checks.
8. `forest_refine_capture.py`: fixed PIE views, no lighting overrides.

The ignored `backup/Station_R12.umap` preserves the user's map immediately before
installation. It is a rollback copy, not another playable map. Check reports and
the `before/` and `after/` images before judging the pass complete.

The user's follow-up adds banks beside the path (up to 2.3 m of local raise),
denser understorey and Black Alder. The 1.85 m half-width walking strip and the
parking footprint are excluded from the bank displacement. Grass and stones are
noncolliding. The current planting report supersedes earlier preview counts.
The user's RockEnv_Pack and VehicleVarietyPack arrived during final review.
Their original assets are retained; local placement/material scripts live beside
the forest scripts, with audit reports under `rocks/` and `vehicles/`.

The final library pass places 44 partly buried rocks using broad forms 8, 12,
20 and 28 plus smaller companions. Parking's previous study rock mesh is retired.
A hatchback and pickup replace the retained study car, at slightly different
angles and offsets. Local body-material copies retain the original maps and add
uneven dirt and higher roughness; glass, interior and tire materials are original.

`forest_refine_cover.py` assigns a snow-disabled local material instance to 24
Landscape components around the station-side valley. The distant mountain
material remains unchanged. A whole-Landscape assignment repeatedly exceeded
available rendering/commit memory during the blocking grass rebuild, including
with batch size 1. The bounded component override saved successfully. These
failed attempts never replaced the saved map. The editor grass rebuild batch
remains 1 for the current session after a failed script; normal restart restores
its default. No persistent rendering configuration was changed.

The final `forest_refine_snow_blend.py` removes the square edge that a constant
snow override produced: a local copy of the MW snow-mask function fades the snow
mask over a smooth 100 by 155 m ellipse centered 40 m down the valley, returning
to the original snow mask before the component boundary. Local grass/dirt/rock
color correction also matches the darker foreground ground material. Both pixel
and grass snow outputs receive the same fade, with zero snow in the center.
The final master keeps the remaining original function connections. An earlier
full function-copy trial broke normal inputs and is removed by the cleanup script.
Original library functions are unchanged. `forest_refine_parking_edge.py` adds 10 grounded trees and 20 shrubs
outside the occupied clearing, closing the exposed vehicle backdrop.

Validation so far:

- Live terrain collision at 11 sample points matches the imported surface.
- 80 Landscape traces confirm the former flat floor is now a varying valley;
  distant samples beyond the edit match the original readings.
- 189 Megaplant actors and 136 painted pines were grounded from live collision.
  Matching hidden trunk proxies moved with their trees.
- Arrival stairs and the short entry pass in both directions. The longer woodland
  route also passes both ways using the current `forest_arrival_alignment.json`.
  The first run used the obsolete pre-alignment endpoint and hit the existing
  stair rail; its report is retained separately in `walking.json`.
- `walking_aligned.json` records the corrected current path test. The final visual
  review of final geometry and assets is under `final_confirmed/`; earlier folders
  and the alternate snow-mask `valley_check/` are intermediate iterations.

Final completion: `walking_complete.json` passes the entire parking-to-station
route in both directions with ordinary movement. `completion.json` confirms the
saved two vehicles, 44 imported rocks, 30 additional parking-edge plants, and
removal of 16 unused trial shader assets. The final preservation and collision
checks in `verification.json` pass. Cleanup/validation ran at the coordinated
editor handoff, before the separate user-requested fog adjustment.

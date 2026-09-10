# Fitted seating checkpoint

The migration map contains all six tables and twelve benches from the integrated
Blender master, including the mending strap on group 03. The 559 source components
are recorded individually in `exports.json`; no reference building, proxy or
review equipment is exported. No existing actor is removed or relocated.

Each table and its two benches form one static engine mesh at the original group
floor origin. Six meshes retain their individual atlas layouts and board variation.
This reduces actor/material overhead while leaving the source's 17 shared meshes
and component editability intact in the unchanged integrated Blender file. Sitting
animation, movable furniture and physics simulation are not part of this import.

## Materials and provenance

The export bakes 2K BaseColor, ORM and tangent normal atlases per group. Source
UVs and per-piece generated coordinates are retained across joining, including
separate end-grain faces. Stable name-hashed per-board values substitute Blender's
object-random values: the eight strip choices remain, but their selection is not
pixel-identical to Blender. The source's scanned pine, end grain, station paint,
metal roughness and normal detail are evaluated into the atlases without lighting.
AO is left at one; Unreal supplies scene occlusion. The small separate varnish
coat layer is not translated in this standard BaseColor/roughness/metallic graph.
OpenGL normal maps are imported with their green channel flipped for Unreal.

Upstream images and CC0 provenance remain in
`art/blender/passenger_lodge_seating_01/REFERENCES.md`, `texture_api.json` and
`textures/`. No new downloaded or generated imagery, credentials or product
photographs are used. SHA-256 values accompany every export and baked image.

## Reproduction and verification

Run `../scripts/export_seating.py` in background Blender, then use the local
Unreal dispatcher for `install_seating.py`. The installer is confined to
`Station_Lodge_Migration` and checks imported mesh bounds and compiled shaders.
Meshes use detailed static triangle collision, with Nanite disabled for this
small kit; no enclosing box blocks the spaces between the table and benches.
Performance/LOD tuning remains part of the full-lodge migration review.

Run `verify_seating.py` with `reopen: true`. Its saved-file checks cover original
actor transforms, six assembly transforms, all 18 table/bench top heights,
material/texture dependencies, normal conventions, 219 interior capsule samples
and the existing 280 perimeter samples. Heights remain 780/480 mm above the floor.
`playtest_site.py` with `seating: true` exercises the main aisle in both directions
and both cross-aisles with the actual player. These tests do not certify clearance
against furniture or moving assemblies that have yet to be imported.

All saved-file checks and all four player traversals passed. The 1,155 preceding
actors retain their transforms. Six neutral views and nine nighttime frames were
reviewed, including low underside and repair-strap views; no crossing furniture
faces were observed. The close torch views retain visible stepped shadow edges
under the current renderer settings; this pass does not claim a lighting polish.

`review_surfaces.py` and `review_surface_night.py`, each with `seating: true`,
capture separate evidence in `../previews/seating` and `../previews/seating_night`.
Neutral lights are temporary and removed; the nighttime set uses actual PIE
lighting and the player flashlight. Reports are `install.json`, `verification.json`,
`playtest.json`, `review.json` and `night_review.json` in this directory.

The original R12 map, source Blender master and unrelated working changes remain
untouched. Public/staff doors, restrooms, kitchen, lockers and wall displays are
still pending. The existing StationDoor class has hinge/key controls, but the new
door package's independent lever, cylinder, latch and gasket controls need explicit
mapping; simply assigning the old leaf mesh slots would discard those mechanisms.

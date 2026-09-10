# Integrated passenger lodge

Open **Maldek_Passenger_Lodge_Integrated.blend** in Blender 5.0.1. Scene `Lodge_Integrated` contains the polished shell and all seven finished handoffs in their approved station positions. Units are metres, Z up, finished floor Z=4. The file opens at frame 1 with the roof visible and mechanisms closed. Select the `Cutaway` view layer to inspect the interior without the roof; it is disabled for batch rendering by default.

## Assembly and ownership

| Package | Included collection | Source variant |
|---|---|---|
| Windows | PLW_Assets | Two fitted frosted window assemblies |
| Public/staff doors | PLD_ASSETS | Corrected frames, seals and flush thresholds |
| Restrooms | PLR_Assets | Latest rounded basins and weathered finishes |
| Kitchen | PLK_Assets | Weathered asset-only library |
| Seating | PLS_Seating_Kit | Six tables, twelve benches; 780/480 mm top heights |
| Lockers | PLL_Lockers | Twelve keyed lockers, aged paint |
| Wall displays | PLG_Wall_Details | Artwork, map, notices, plaques and clock |

The three separately completed packages were copied from their tracked deliveries: seating `bfcef19`, lockers `aa6a593`, wall displays `4cef358`. Their complete source packages, editable artwork, texture provenance, manifests and verification reports are retained beside this directory. `reconciliation.json` records exact blend hashes and collection inventories. No package reference building or temporary package lighting was appended. `PLI_REVIEW_ONLY` contains the shell review cameras/lights; these are not installed fixtures.

The assembly retires 222 exact proxy/temporary-text objects, keeps 2,944 delivered objects, and preserves shared meshes, material graphs, parent relationships and animation actions. Kitchen menu and cubby artwork replace only temporary text; the kitchen owns the physical frames. The old reversed `Service_lettering.001` is retired; other station lettering remains.

Public/staff cuts are replayed locally through wall layers, floors and affected grating. Restroom jamb/header patches are applied without replacing the shell wholesale. Patched wall faces regain the shell's 3.2 m planar UV mapping and cream/green plaster material. Fifteen trim runs are shortened/split only where installed fittings occupy them, with 2 mm end clearance.

A whole-panel threshold boolean welded touching grating bars into a four-face edge away from the aperture. `finish.py` reconstructs that one panel from its 44 original disconnected bars and cuts only the 20 intersecting bars individually. No platform relocation or opaque grating backing is introduced.

## Review and validation

`previews/` contains 13 views: exterior beside control, platform frontage, both hall directions, kitchen, both restroom hallway directions, women's fixtures, overhead cutaway, arrival threshold, window detail, open lockers and dim warm hall. Lighting is temporary Blender review lighting, not the live game's lighting. `review_views.json` records the cameras and poses.

`verification.json` checks the saved/reopened delivery: exact collection inventories, retired proxies, component transforms, retained context bounds, packed textures, evaluated topology and cross-package moving-part intersections. Sweep samples span frames 1–100 in five-frame increments, including the final pose; this is a sampled geometry test, not continuous simulation. Existing within-package mechanism checks remain in their source deliveries.

`routes.json` checks 15 combined circulation routes with a 340 mm radius and 1.8 m height, including fixture approaches, open lockers and the working kitchen. Public/restroom/locker doors are open and kitchen cabinets closed for circulation. A further 355 support samples cover the entrance, platform, west deck, bypass and bypass stair. These conservative Blender checks do not replace Unreal collision/traversal tests.

## Reproduce and inspect mechanisms

Run the following in order from the asset repository, using Blender's `--background --python` option:

1. `art/blender/passenger_lodge_04/scripts/integrate.py`
2. `art/blender/passenger_lodge_04/scripts/finish.py`
3. `art/blender/passenger_lodge_04/scripts/verify.py`
4. `art/blender/passenger_lodge_04/scripts/routes.py`
5. `art/blender/passenger_lodge_04/scripts/review.py`

The builder starts from the immutable polished shell and verifies the approved lodge 03 hash. It never saves over those sources. Finish is deterministic when rerun: it reconstructs the affected grating from the original bars. Verification and rendering reopen the result without resaving it. Textures are packed in the master.

Frame 1 closes everything. Frame 40 shows restroom doors and kitchen mechanisms open, frame 80 fully opens public/staff doors. Locker cams turn by frame 8, lockers 04–06 open by frame 50, and all lockers open by frame 100. These are independent demonstration actions sharing a review timeline; they are not gameplay states. Individual mechanisms retain their authored pivots and can be inspected separately.

## Remaining work

This is the integrated Blender authoring master. The retained cleaning-cupboard blockout and inherited station context are unchanged; no unassigned furniture redesign was added. Wall-display schedule text remains provisional dressing. Unreal imports, collision authoring, material baking, LOD/export grouping, interactions, sounds and actual night/torch playtesting remain a subsequent phase. No live map or gameplay files are changed by this package.

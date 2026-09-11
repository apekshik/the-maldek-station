# Kitchen migration

The weathered PLK collection from the integrated Blender master is installed in
Station_Lodge_Migration. The original R12 map and Blender master remain unchanged.
The enclosed preparation room, serving counter, wash sink, hand basin, urn,
kettle, microwave, fridge, dry shelving, cups/tins, snack display and lost-property
cubby retain their source positions. Existing staff door, hatch, walls and trim
are retained. No proxy or old actor is deleted in this package import.

## Controls

Fifteen native StationCabinet actors retain the source pivots: five drawers,
eight cabinet leaves, fridge door and microwave door. Aim at a front and press E
to open or close it. The shared square gold interaction treatment labels the
action. Per-piece collision leaves drawer interiors hollow. Movement is sampled
at no more than 2 degrees or 5 mm between obstruction queries; a blocked front
stops and offers Retry after the obstruction is cleared. Existing recorded door
audio is reused at a quieter furniture volume.

Appliance heating/cooling, taps and plumbing are decorative. Kettle/urn lids stay
closed. Their original editable lifting mechanisms remain in Blender. The
source's menu and cubby lettering was already removed during reconciliation;
the physical backing/frames remain for the separate wall-display import.

## Export and materials

export_kitchen.py reads only PLK_Assets at frame 1. No reference architecture,
review lights or cameras are exported. Source matrices, names, material names,
group assignments, pivots, movement limits and hashes accompany the export.
Nine atlas groups become 25 meshes/actors: 15 movable mechanisms, nine fixed
assemblies and separate snack-display glass. Fixed meshes use triangle collision;
moving meshes use authored per-piece boxes for movement and a detailed visual
mesh for aiming. No physics simulation is enabled.

Storage and appliance atlases are 2K BaseColor/ORM/NormalGL; miscellaneous fixtures
use 4K. Source generated/object coordinates and source UVs are retained during
baking. Normal green channels are flipped in Unreal. The downloaded weathering
maps retain provenance in art/blender/passenger_lodge_kitchen_01/weathering.
No new generated images or synthesized sounds are used. Display glass is a
separate translucent material; its simplified tint/roughness does not reproduce
every source scuff. Coat/transmission elsewhere are approximated by the standard
opaque material. Fine lettering and very small fittings share the atlas budget.
Nanite is disabled; whole-lodge LOD/performance work remains later.

## Verification and reproduction

1. Run survey_kitchen_source.py and export_kitchen.py in background Blender 5.
   The optional --fixtures-only flag reuses recorded storage exports while
   rebaking only the fixture atlas.
2. Build gameEditor with the StationCabinet class, reopen the migration map and
   run install_kitchen.py through the bounded editor dispatcher.
3. Run verify_kitchen.py to save/reopen, compare all previous actor transforms,
   verify bounds/textures/collision pieces, and sample kitchen/perimeter routes.
4. Run test_kitchen.py for actual E input and walking; test_kitchen_safety.py for
   blocked movement/retry. Runtime tests change only PIE copies.
5. Run review_kitchen.py for temporary neutral lighting and close-angle views;
   its lights are removed afterward. Runtime captures use actual night lighting.
6. Run finalize_kitchen.py to check evidence and save everything closed.

The static source check used a 30 cm walking radius; the migration check uses
the game's larger 34 cm radius / 96 cm half-height capsule. The staff doorway
and all five source preparation routes are included. Closed storage preserves
circulation; an open door/drawer can temporarily occupy part of an aisle, as a
solid piece of furniture should. This is not a guarantee that every storage
front can be opened simultaneously while maintaining every walking route.

The combined collision check diagnosed a false obstruction at roughly 74 degrees
on the second hot-equipment cabinet leaf: the square approximation of a 12 mm
round hinge barrel touched the adjacent drawer's collision box. The source mesh
trace remained clear. export_kitchen.py excludes the sixteen tiny hinge barrels
from physical boxes while keeping their visible/aimable geometry; the 76 panel,
drawer and other moving-piece boxes remain. collision_repair.json records the
exact source names. No hinge, panel, pivot or opening dimensions were changed.

Lockers, wall displays and whole-lodge promotion into the original game map
remain separate migration steps.

The Development Editor build passed. runtime.json records 96 passing checks,
including all fifteen E-driven open/close cycles and six actual walking routes;
the maximum standing-floor deviation was 0.86 cm. safety.json records 46 passing
checks covering player obstruction, clear-and-retry, and final closing for every
mechanism. Neutral review lighting includes fill on both sides of the hatch to
avoid overexposing the kitchen when viewed from the darker hall. These review
lights are temporary; the night captures retain the actual game lighting.

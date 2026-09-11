# Restroom migration

The PLR delivery collection is installed in Station_Lodge_Migration: two entrance
doors, three cubicles and stall doors, three toilets, two basins, urinal/privacy
divider, mirrors, plumbing, dispensers, bins and hardware. Only the integrated
master's 280 PLR objects are considered; five hinge empties supply the origins
for the 275 renderable pieces. No reference building or review equipment is
imported. The master remains editable and unchanged.

## Construction and controls

Eight source groups become 32 mesh components in five native StationDoor actors
and six static fixture actors. Door leaves, two levers per door, stall bolts and
indicator faces remain separate. Static cubicle partitions and toilets belong
to separate actors so the native door collision test includes them. Fixed hinge
hardware remains with its door. Entrance swings are 85 and 90 degrees inward;
all three 780 mm stall leaves swing 90 degrees outward. Positions, jambs and
the screened hallway follow the integrated source. The earlier shell import
already contains its five restroom wall opening patches; this pass recuts none.

E opens/closes a door. On a closed stall, look at the bolt from inside and press E
to lock or unlock it. The existing sharp gold interaction border identifies the
action. The outside indicator turns red when locked and green when vacant.
An outside interaction cannot release the bolt. From inside, E on the door away
from the bolt unlocks and opens it, preserving an exit path. Privacy starts
vacant, does not require an inventory key, and does not relock automatically.
This indicates the bolt's state, not automatic detection of a person in a stall.

Existing recorded station door and lock sounds accompany the actions. No new
audio is synthesized. Flushing, running water, sitting and functional dispensers
are not implemented; these fixtures are detailed environment meshes.

## Materials and export

export_restrooms.py reads the integrated blend without saving it. Each group
has 2K BaseColor, ORM and OpenGL-normal atlases. The source's PLR_Metric_2m UVs,
generated coordinates and PLR_Deposit basin-staining attribute survive joining
and baking. The source uses Poly Haven Metal Plate 02 CC0 textures; URLs, hashes
and provenance remain in art/blender/passenger_lodge_restrooms_01/textures and
MATERIALS.md. No new online or generated imagery is required. ORM uses AO=1;
Unreal supplies scene occlusion. Normal green channels are flipped on import.
Coat/transmission lobes are approximated by standard roughness/metallic shading.
Mirror and bowl-water surfaces are baked opaque reflective materials, without
planar reflection captures or water simulation. Privacy faces use an independent
state-color material. Geometry remains the approved source dimensions.

The static fixtures use detailed triangle collision; leaves use measured moving
boxes. Nanite is disabled for this small kit. Full-lodge performance and LOD
tuning remain later migration work. exports.json records individual source names,
parents/matrices, group/component pivots, bounds and file hashes. install_restrooms.py
is confined to the migration map, retaining a before-actor ledger.

## Verification

verify_restrooms.py saves/reopens the map, verifies the preceding 1,164 actor
transforms, 32 component bounds, closed door collision from both sides and
compiled materials. With doors posed open, it checks the documented routes to
all fixtures using a 34 cm radius / 96 cm half-height capsule, floor support and
the existing 280-sample perimeter routes. It restores doors closed before saving.
This does not certify clearance against the kitchen, lockers and wall displays
which have yet to be installed.

test_restrooms.py exercises E-driven motion, both levers, recorded movement
audio, stall locking/unlocking, bolt translation, indicator colors, outside
rejection, inside egress and actual walking through all nine documented routes.
review_restrooms.py provides neutral fixtures/hallway/reveal views with the roof
visible. Temporary lights are removed afterward. PIE images retain the actual
nighttime scene and player flashlight. Reports and review results accompany this
directory; the R12 map and Blender master are checked unchanged.

The final runtime pass succeeded after centering the authored door prompts and
reducing the privacy prompt's size so the bolt remains visible. All nine routes
passed with a maximum floor-height deviation below 3 cm. The neutral set contains
26 views, including both hallway directions, basins, toilet, urinal, hardware and
small angle changes around both entrance headers. The entry leaves retain their
source's 20 mm top clearance; the reveal liners remain fitted to the wall.

The turquoise panel already present at the far end of the screened hallway also
appears in the preceding surfaces/hallway.png checkpoint. It is not introduced or
removed by PLR. hall_probe.json records read-only hallway collision queries; all
documented hallway traversal checks remain clear. This pass preserves preceding
actors rather than guessing ownership of other pending package geometry.

The native build preserves pre-existing uncommitted click/pointer-hit-area edits
in StationDoor.cpp; those edits are excluded from this checkpoint's commit.

The final Development Editor build succeeded. test_restroom_safety.py passed
player obstruction at roughly 19 degrees for the entrances and 17 degrees for
the stalls, followed by safe closing and full reopening after clearing the arc.
The older control-side mechanical door still enters/cancels its key camera,
swings and relocks; the control-front keypad rejects 0000 and accepts 1234.
finalize_restrooms.py validates completed evidence, checks source hashes and
saves five closed, vacant doors with no temporary review lights.

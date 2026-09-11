# Fitted public and staff doors

Three native StationDoor actors now occupy the integrated master's arrival,
gondola and coffee-staff openings in Station_Lodge_Migration. Their authored
hinge origins and -100/-100/+100 degree swings are preserved. Each contains ten
separate exported components: leaf, glass, fixed hardware, lock housing, two lock
plugs, two levers, latch and bottom seal. Exporting the complete leaf as one static
mesh would lose these independent mechanisms. No existing actor is removed,
relocated or recut in this checkpoint; shell and grating openings were already
transferred in the earlier shell import.

## Controls and motion

All three start closed and keyed, with the key already available. E enters the
existing angled inspection camera. Hold and drag the key forward to seat it;
the key and plug then turn with the existing recorded sound at volume 4. E can
cancel an incomplete insertion. After unlocking, E opens the leaf. Closing
relocks it, while the interior side permits free egress without possessing a key.
The later inventory hook remains the existing KeyAvailable property.

The opt-in authored hardware configuration allows each door's lock location,
orientation, face depth and interior side to match its Blender assembly. Levers
depress, the latch retracts 14 mm and the bottom seal lifts 12 mm. A 0.22-second
release precedes opening. The existing obstruction checks, half-degree rotation
substeps and recorded opening/closing audio remain active. Old station doors
retain default hardware configuration and their previous dimensions.

## Materials, provenance and reproduction

Run ../scripts/export_doors.py in Blender, then install_doors.py through the local
Unreal dispatcher. Only PLD_ASSETS delivery objects are evaluated; the source
master is checked by SHA-256 and never saved. exports.json retains source object
matrices, parent names, component pivots, bounds and file hashes. The editable
source and original actions remain in art/blender/passenger_lodge_04 and the
passenger_lodge_doors_01 package.

Each door has 4K BaseColor/ORM/OpenGL-normal atlases, baked without lighting from
the existing station paint, metal, brass and rubber materials. Source UV and
generated coordinates survive joining. Stable object-name hashes replace
Blender object-random values. AO is one; the standard Unreal material omits
separate coat lobes. Normals import with their green channel flipped. No new
online textures, synthesized audio or credentials are used.

Glass uses the existing lodge opal-glass material, separately from the opaque
atlas. This is an Unreal screen-space approximation, not a pixel-identical
translation of Blender transmission: bright review lights and weather can
remain prominent through it. This checkpoint does not claim final lighting or
glass-optics polish. Small mechanism meshes have Nanite disabled. Fixed frames
use triangle collision; the moving leaf uses an explicit box including its glass.

## Verification

The Development Editor game module and generated headers built successfully.
verify_doors.py saved/reopened the map and checked all 30 component bounds
(maximum error below 0.001 cm), 1,161 preceding actor transforms, six closed-door
blocking traces and compiled materials. With doors temporarily posed open,
210 interior capsule samples and 280 perimeter samples passed; poses were
restored closed before saving. The source R12 map hash remains unchanged.

test_doors.py passed actual E/pointer insertion, invalid click/drag, partial and
reverse drag, cancellation, camera/input restoration, audible turn/movement,
independent hardware movement, full swing, character traversal, relocking,
missing-key gating and interior egress on all three doors. runtime.json records
each assertion and the nighttime review images. Test key events deliberately
ignore InputKey's event-consumption return value and validate observed behavior.

test_door_safety.py also passed blocked swings against the player at about 25
degrees on each new door, safe closing and unobstructed reopening. Its legacy
checks cover the old control-side key camera, cancellation, swing and relocking,
plus rejected 0000 and accepted 1234 on the control-front keypad. These are PIE
tests; they do not change saved lock state. The runtime build includes pre-existing
uncommitted pointer-hit-area and click-interaction edits, which this checkpoint
preserves but excludes from its commit. New key tests use E and the grip centre.

Neutral close-ups use review_surfaces.py with doors:true. Add headers:true for
changed-angle header/reveal views. Temporary lighting is removed after capture;
PIE runtime images use the actual nighttime scene and flashlight. The original
Blender master and R12 map remain unchanged. Restrooms, kitchen, lockers and wall
displays are still pending migration, so their combined clearance remains a later
checkpoint.

Review includes 12 neutral detail views, 18 header views from both sides with
small viewpoint changes, and 12 nighttime interaction frames. Frames, threshold
plates and grating transitions remain fitted; no alternating reveal faces were
observed in the reviewed angle changes. finalize_doors.py checks completed reports,
removes no assets, verifies both source hashes and saves the closed map state.

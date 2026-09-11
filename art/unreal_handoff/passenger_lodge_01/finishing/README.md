# Locker and wall-display checkpoint

Installed in `/Game/MaldekRefinement/PassengerLodge/Station_Lodge_Migration`.
The original R12 map is preserved; this does not promote the migration map to
startup or change its story progression.

## Delivery

Twelve lockers retain their approved bodies, shelves, hooks, punched vents,
folded doors, hinges and separate rear lock cams. E opens/closes each locker;
the cam releases before the leaf swings and returns after closing. Recorded
station latch/door audio is reused. Lockers are initially accessible, without
an inventory key requirement. The shared gold, square double-border prompt is
used. Structural leaves/folds supply five moving collision boxes per locker;
small visible hardware does not create oversized physical obstruction boxes.

The wall package adds posters, timetable, visitor map, community notices,
wayfinding, clock, menu and lost-property insert. Fixed screw-retained cases
remain fixed. Clock hands retain the source 10:10 pose. Printed content is
period dressing; timetable entries do not drive gondola logic. Inspectable
clues, inventory rewards and journal text remain a separate narrative pass.
Kitchen frames stay in place around the new menu/cubby artwork.

All seven delivered furnishing packages are now represented in the migration
map, including six tables, twelve benches and twelve lockers. The previous
1,200 actors were preserved without transform changes. No terrain, trees,
platform, stairs or control-room geometry changed in this checkpoint.

## Source and material fidelity

Read-only source: `art/blender/passenger_lodge_04/Maldek_Passenger_Lodge_Integrated.blend`.
Source SHA256: bcf7e6301aecedd83688488981fd58a5a9719d685ef975210eef9eeb7f753f6c.
Only PLL_Lockers and PLG_Wall_Details delivery collections are exported.
Original editable hierarchies, shared meshes and Blender actions remain there.
Unreal motion uses native components with the authored pivots and sweep angles.

Lockers use twelve 2K BaseColor/ORM/normal atlas sets, preserving the delivered
weathering/paint variants. Wall frames use one 4K atlas set; twenty ink images
are extracted byte-for-byte from packed source images, retaining their source
UVs and full printed detail. Glass is a separate translucent Unreal material.
Procedural finishes are baked; Blender lighting is not baked into base color.
Sources/licenses remain in passenger_lodge_lockers_01 and
passenger_lodge_wall_details_01. The wall package uses its delivered vector
artwork, with no additional generation, credentials or external service calls.

Exports: 36 locker meshes, 23 wall meshes and 59 texture files. Installed actors:
12 native lockers + 12 bodies + 23 fixed wall actors. Each package manifest
records parts, bounds, frames, source matrices and texture hashes. Original
proxy/lettering replacements already happened in the integrated source; no
unrelated arrival lettering was removed during this Unreal pass.

## Reproduction and evidence

Run survey_finishing.py, export_lockers.py and export_wall_displays.py with
Blender. With the migration map open, run install_lockers.py then
install_wall_displays.py through scripts/session.py. Run verify_finishing.py
after saving/reopening. Runtime scripts use the existing native migration test
library and do not save their PIE poses to the editor map.

- verification.json: saved/reopened actor preservation, all 59 mesh component
  bounds, 59 texture dependencies/hashes, twelve closed lockers, sixty moving
  boxes, 1,025 combined interior capsule samples and 280 perimeter samples.
- runtime.json: actual E focus/open/close/cam tests for all twelve lockers and
  actual walking along eighteen routes with open locker/public/restroom doors.
- safety.json: obstruction/retry/close regression for all 27 native storage
  fronts (fifteen kitchen mechanisms plus twelve lockers).
- review.json and previews/finishing: neutral Lit review, roof visible, temporary
  lights removed and locker poses restored at the end. Views 03-04 show review
  poses only. previews/lockers_night contains actual gameplay flashlight images.

Editor C++ build passed for the optional StationCabinet cam extension. Final
verification is rerun after reviews; saved mechanisms are closed. Package
import completion is not a performance/cooking certification or a finished
puzzle system.

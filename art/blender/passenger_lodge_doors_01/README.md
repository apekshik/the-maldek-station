# Passenger lodge public and staff doors

Open **Maldek_Passenger_Lodge_Doors.blend**, scene `PLD_Fitted_Doors`.
The three editable keyed assemblies are in `PLD_ASSETS`. Frames 1, 40 and 80
show closed, 45-degree and 100-degree poses. These are Blender review poses;
there is no new game interaction, digital keypad or Unreal import.

## Openings and handing

| Door | Fixed clear opening | Swing choice |
|---|---|---|
| Arrival court | Local X 6.4–7.6, depth 11.02; 1.2 × 2.3 m | East jamb, outward to court. Parks beside the east court wall. An inward version failed the coffee queue clearance test by 217 mm during its arc. |
| Gondola-facing public exit | Local X 6.4–7.6, depth 0; 1.2 × 2.3 m | East jamb, inward to hall. Keeps moving hardware off the grating promenade and parks clear of table/bench footprints. |
| Coffee staff | Coffee east wall at local X 4.82, depth 14–15; 1.0 × 2.2 m | Depth-15 jamb, outward to court. Preserves kitchen prep and storage space and parks south of the staff crossing. |

The staff opening is fixed for the kitchen task. Wall thickness is 180 mm and
exterior corrugation projects up to 32 mm; an assembly origin at the cladding
face does **not** change the opening coordinates. All thresholds are flush at
station Z=4, preserving the full stated height above the finished floor.

An open leaf can clear a route even when its intermediate arc does not. The
arrival handing was selected using that distinction. Passage through a moving
doorway remains occupied until the door is open; the check does not imply that
a character can walk through a closed or moving leaf.

## Exact transforms

Blender metres, Z up. Shared mapping: `(local x − 24.1, −depth + 4, local z + 4)`.
Asset `u` runs from the hinge-side clear jamb toward the latch. Asset `v` completes
a right-handed basis; all handed hardware geometry follows the chosen side.

| Assembly | Root translation XYZ (m) | Root yaw | Leaf pivot in root coordinates (m) | Pivot in station XYZ (m) | Full angle about local Z |
|---|---|---|---|---|---|
| ARRIVAL | (−16.5, −7.232, 4) | 180° | (−0.060, +0.086, 0) | (−16.440, −7.318, 4) | +100° |
| GONDOLA | (−16.5, 3.820, 4) | 180° | (−0.060, +0.086, 0) | (−16.440, 3.734, 4) | +100° |
| STAFF | (−19.068, −11, 4) | 90° | (−0.060, −0.086, 0) | (−18.982, −11.060, 4) | −100° |

`replacement_manifest.json` supplies full matrices, object dimensions, material
slots, parent relationships and local transforms. Root and hardware scales are
one. Each leaf has its own `PLD_<ID>_LEAF_PIVOT`; handles and cylinder plugs have
separate local-Y controls, the latch moves on local X, and the bottom gasket
retracts vertically before opening. No interaction code is attached.

## Construction and reference use

See [references.md](references.md) for manufacturer references, dimensions used,
project studies and retrieval limitations. The doors use 45 mm steel leaves,
cream inside faces, 8 mm etched upper glass, replaceable stainless kick plates,
return levers, brass keyed cylinders, seals and independent steel surrounds.
The wider public doors have four hinges; staff has three. Handles, cylinders,
hinge sections and screw sizes are authored at fixed physical sizes.

The glass sits in an actual rebated aperture. The cylinder passes through a real
bore, and each plug has a recessed open keyway. Hinge knuckles have pin bores and
alternate between fixed and moving parts. The grips are continuous bent tubes,
not overlapping capped cylinders. No bathroom entrance or stall door is included.
The existing control door retains its independent keypad design.

## Wall, cladding and threshold patches

`wall_patches.json` records each exact source object, replacement name, cutter
matrix and cutter dimensions. Only the three neighbouring core segments and
three cladding segments at each opening are cut. Their original names are:

- Arrival: `FIT_Hall_south_entry_0_0`, `_1_2.3`, `_2_0`, plus corresponding
  `PL03_Cladding_` objects.
- Gondola: `FIT_North_2_0`, `_3_2.3`, `_4_0`, plus corresponding cladding.
- Staff: `FIT_Coffee_east_0_0`, `_1_2.2`, `_2_0`, plus corresponding cladding.

The rough cut extends 64 mm outside the nominal aperture at jambs and head;
the 60 mm reveal occupies that recess and leaves a concealed 4 mm core gap.
Cover profiles bridge the concealed joint. No frame member reduces clear width
or height. The lining spans the complete core-plus-cladding depth. Local floor
pockets seat the flush pans without duplicate floor faces; the gondola pan also
cuts only intersecting grating bars beneath its small exterior overlap.

The final visual review also caught a 6 mm height overlap between the jamb and
head cover faces. `evidence/cover_joint_before.png` preserves the initial staff
inside view; `previews/STAFF_Face_B.png` is the corrected view. Jamb covers now
end at the head-cover boundary, and the verifier checks that limit. The retained
`scripts/refine_frame_joints.py` records the repair; the generator directly
authors the corrected joint. This applies the existing R12 lesson to a new
trim junction rather than hiding the artifact with rendering changes.

`scripts/apply_opening_patches.py` replays these exact cuts into a fresh
**package-owned** source copy. It does not save over the master. When merging
other packages, replay the local cuts rather than replacing an entire shared
floor or wall from this review file. Source names are explicit; unexpected names
fail instead of broadening the patch.

Original door proxies were hidden sweep curves (`FIT_Court_door_sweep`,
`FIT_North_door_sweep`, `FIT_Staff_door_sweep`), not installed leaves.
Restroom proxies are outside this replacement mapping.

## Review and verification

`previews/` contains nine views per opening: both closed faces, both hardware
close-ups, closed/partial/open source-fitted plans, and partial/open player-height
views. The plan legend is **amber = tip sweep**, **green = route centre and
±340 mm body envelope**. Lines crossing the closed leaf denote an occupied
doorway, not a passed traversal. Temporary neutral lights are review-only.

`verification.json` records saved/reopened evaluated topology, sampled mesh
surface collisions, clear-aperture rays, glass aperture checks, source preservation
and retained reference transforms. It measures route margins beyond the source
layout's 340 mm radius proxy. The exact measured values and pass state are in that
file; this is not an engine capsule or continuous collision proof.

Final checks passed: 419 evaluated asset meshes are manifold with no degenerate
faces, 63 sampled assembly poses have no detected collisions with the tested
stationary meshes, all 75 clear-aperture rays pass, and 6,831 retained reference
transforms match. The lowered bottom seals bridge continuously to the flush pans.

| Protected route | Minimum margin beyond 340 mm body radius |
|---|---:|
| Coffee queue, throughout arrival swing | 1.164 m |
| Remote arrival-court route, throughout arrival swing | 0.189 m |
| Grating promenade, throughout gondola-door swing | 1.312 m |
| Main arrival route, throughout staff swing | 0.465 m |
| Arrival / gondola door passage, fully open | 0.273 m each |
| Staff passage, fully open | 0.173 m |

Reference collections and `PLD_REVIEW_ONLY` are excluded from delivery exports.
Reference roof objects are retained in an independently hidden collection. All
reference matrices are snapshotted before detaching parents to avoid double
transforms or lost gondola placement. The approved source hash is
`b9d78ed0d7c5c50bc28a8fb6a0d63f1c86fa83d3144c6a7eae50476ee9607796`.

## Reproduce

Run from the repository root with Blender 5.0:

```powershell
& 'C:/Program Files/Blender Foundation/Blender 5.0/blender.exe' --background --python art/blender/passenger_lodge_doors_01/scripts/survey.py
& 'C:/Program Files/Blender Foundation/Blender 5.0/blender.exe' --background --python art/blender/passenger_lodge_doors_01/scripts/build.py
& 'C:/Program Files/Blender Foundation/Blender 5.0/blender.exe' --background --python art/blender/passenger_lodge_doors_01/scripts/verify.py
& 'C:/Program Files/Blender Foundation/Blender 5.0/blender.exe' --background --python art/blender/passenger_lodge_doors_01/scripts/render.py
```

The optional patch replay creates `Opening_Patch_Review.blend` here. Source
lodge files, door studies, unrelated packages and the live map are not written.
Run `scripts/verify_patch_replay.py` afterward to compare it with the delivered
patches. The recorded replay passed for all 22 affected objects; the largest
evaluated vertex-to-surface difference was under 0.002 mm.

Remaining integration work: user design review, export grouping and UV/bakes,
optimized collision and capsule traversal, engine material/lighting checks,
obstruction handling and keyed interaction/sound logic. This package does not
claim load capacity, weather certification, code compliance or PIE validation.

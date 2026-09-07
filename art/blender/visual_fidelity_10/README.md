# VF10 parking and arrival

Source: VF09 `Maldek_Service_Apron_Refinement.blend`; previous revisions are untouched.

The parking shelf grows from 8 × 6 m to 14.5 × 12 m. Three gravel bays sit beside
an arrival pocket with a bench, information board and drainage strip. A 5.5 m
lane lies in front of the bays. Wheel stops and embedded divider stones define
parking without road paint on loose gravel. The existing car remains at its
original position. Five rock groups establish edges for later layered planting.

The red rectangular object is the inherited Blender car proxy, not a new vehicle.
Rock geometry is authored placeholder geology that can be replaced with the
user's preferred Fab scans. The design previews do not represent final Unreal
lighting, foliage or material quality.

## Reproduce

Run Blender background with `scripts/build_parking.py`, then `scripts/export_parking.py`.
The latter exports only parking ground, furniture, rocks, the revised beginning
of the forest path and a combined terrain. It does not re-export the station or
car. Handoff files are under `art/unreal_handoff/revision12/parking`.

The combined terrain starts from the concurrent service migration's
`revision13/terrain_grid.json`. Its hash is checked at import. Parking grading
affects only a two-metre falloff around x[-44.6,-29.9], y[-64.1,-51.9]; service
terrain and forest beyond that mask remain numerically unchanged.

The enlarged lot replaces the old parking surface. The first 16 cross sections
of the old forest approach are replaced with an entrance at the lot's east edge;
the rest of the route retains its source vertices, except for clamping its first
west edge to the lot boundary where necessary. This removes the old path
surface from beneath the new lot, following the project's surface-ownership rule.

## Integration status

Imported into Station_R12 after the service task's dbb0eca checkpoint. Five
assemblies replace three exact components; car and player remain in place.
Unreal planting adds 47 grass clumps and four trees, with one existing tree and
its trunk proxy moved out of the new lane. The first path marker moves into the
arrival pocket and one old rock patch moves onto the verge.

Six actual-player route checks passed (three routes, both directions). Bounds,
materials, underlying Landscape clearance and nearby transform preservation
checks are recorded in `revision12/parking`. Night and temporary inspection
captures are under its `views` and `reviews` folders. Inspection lights are
removed before saving. Existing audio, service buildings, bridge and station
architecture remain in the current map.

This is the initial parking/planting pass. Preferred Fab rock scans, additional
ground-cover species and a measured foliage performance pass remain follow-up
work. No packaged-build or 60 FPS claim is made for this pass.

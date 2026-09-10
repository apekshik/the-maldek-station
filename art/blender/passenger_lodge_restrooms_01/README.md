# Complete restroom mesh package — PLR

Editable source: `Maldek_Passenger_Lodge_Restrooms.blend`, scene `PLR_Fitted_Review`.
Append/export **PLR_Assets only**. `PLR_REFERENCE_ONLY` is retained station context;
`PLR_REVIEW_ONLY` contains temporary lighting and swing diagrams. Neither is a
delivery asset collection. Source collection exclusions are preserved as per-object visibility when grouping the reference copy, so obsolete station geometry stays hidden. The master lodge and live Unreal map were not edited.

The package contains both restroom entrance assemblies, two women's cubicles,
one men's cubicle, all three stall doors, three close-coupled toilets, two modeled
wall basins, a urinal, privacy divider, exposed plumbing, mirrors, dispensers,
bins and supporting hardware. Bathroom doors are wholly owned here.

## Fit and operation

The approved 6 x 6 m annex and screened hallway remain. World conversion is
`(local_x - 24.1, 4 - local_depth, local_z + 4)` in metres, Z up. Finished floor
is world Z=4. Mesh origins are centered on their components; moving components
are parented to real hinge-axis empties. Exact matrices, dimensions and material
slots are in `asset_inventory.json`; pivots and replacement names are in
`replacement_manifest.json`.

- Entrance liners preserve the nominal 0.900 x 2.200 m apertures. Each leaf is
  0.896 x 2.160 x 0.044 m. Women: right hinge, inward 85 degrees; men: right
  hinge, inward 90 degrees. Physical floor stops mark the open positions.
- The existing 1.20 x 1.60 m women's and 1.25 x 1.60 m men's cubicle envelopes
  are retained. Stall leaves are 0.780 x 1.850 x 0.036 m with a 150 mm bottom
  clearance and 90-degree outward swings. These let an occupant close the door
  from inside the compact stall. They swing into the restroom apron, clear of
  the screened hallway. No basin or hall locker was moved into that hallway.
- Frame 1 shows all doors closed; frame 40 shows their working open poses.
  Intermediate frames show the motion. No runtime animation/import is implied.
- Basins have thick bowl interiors, rims, rear tap decks, drains with perforations,
  mixers, overflow details, traps, valves, supplies and brackets. Women's basin
  center is local (8.46, 14.18); men's is (13.54, 14.50), at rim height 0.87 m.
  Mounting against the side walls replaces floating proxy placement.
- The urinal has a projecting lower bowl, backsplash, top flush pipe/valve and
  outlet. Its divider now runs across the approach at depth 15.35, from X=13.21
  to 13.82, so there is standing room in front of the fixture. This replaces the
  longitudinal proxy divider, which restricted use of the urinal.
- Doors, levers and attached hardware remain individually editable. Stall latches
  include a visible vacant indicator, inside bolt, keeper/stop and coat hook.
  Occupancy-state logic is later integration work; the supplied state is vacant.

## Surface ownership and opening patch

`opening_patch.py` changes only the three jamb-adjacent wall pieces and two
header undersides belonging to these entrances. It is already applied to the
reference copy in this package. It never opens or saves another file.

The jamb core strips recess 22 mm into the existing wall, only below local
Z=2.226. Header undersides recess 26 mm. The 18 mm metal jamb liners and 22 mm
head liners own the finished reveals, with 4 mm concealed separation. Face trim
bridges these joints on both sides. Upper wall extents remain unchanged; no
whole-wall relocation, annex expansion or cladding changes are required.
Replay `opening_patch.apply()` on an integration copy before appending the assets.
The exact five object names and patch regions are in the replacement manifest.

## Verification and review

Run with Blender 5.0 from the repository root:

```text
blender --background --python art/blender/passenger_lodge_restrooms_01/scripts/build.py
blender --background --python art/blender/passenger_lodge_restrooms_01/scripts/render.py
blender --background --threads 4 --python art/blender/passenger_lodge_restrooms_01/scripts/verify.py
blender --background --python art/blender/passenger_lodge_restrooms_01/scripts/verify_materials.py
blender --background --python art/blender/passenger_lodge_restrooms_01/scripts/report.py
```

The verifier reopens the saved blend. It checks evaluated manifold topology and
degenerate faces, door-plus-hardware sweeps at 5-degree intervals, door apertures,
floor support, waiting-hall sightlines and routes to every fixture with the source
layout's 0.34 m radius / 1.8 m high walking envelope. Route geometry uses convex
XY projections of evaluated lodge/fixture meshes, sampled at intervals no larger
than 25 mm. Detailed results and tightest obstacles are in `verification.json`.
These are Blender layout checks, not Unreal capsule/collision or PIE validation.

`previews/` contains both hallway directions, each restroom interior, both entry
assemblies from the inside, stall latch detail, both basin details, a toilet,
the urinal and a roof-hidden overhead plan with all five swings. Temporary review
area lights are explicitly named `PLR_TEMP_REVIEW_AREA`; they are not installed
luminaires. Camera positions and poses are in `previews/views_all.json`.

## References and remaining integration

See `REFERENCES.md` for manufacturer references used for the ceramic forms,
exposed connections and partition hardware. This is an original station design,
not a branded replica or claim that current catalog products date from 1990.

Materials now include packed 2K CC0 scan textures and adjustable procedural
weathering. See `MATERIALS.md` for sources, mapping, controls and limitations.
Both basins are rounded rectangular, 620 x 510 mm, with 75 mm outer corner
radii and integrated tap decks; their centers and maximum projections remain
unchanged. The obsolete separate tap-deck blocks were removed.
Texture baking, export LODs,
engine material conversion, collision authoring, door/indicator interaction and
actual player traversal remain integration work. Preserve the documented swing
limits and check the narrow stall gates against the final player collision.

Approved source SHA-256:
`b9d78ed0d7c5c50bc28a8fb6a0d63f1c86fa83d3144c6a7eae50476ee9607796`.

# Mesh authoring lessons: prevent overlapping surfaces

## Integration booleans on touching grating bars

The passenger-lodge reconciliation found that a whole-panel EXACT boolean welded
two originally disconnected, touching grating bars into one four-face edge away
from the threshold cutter. A package's asset-only topology check did not cover
that patched reference panel. Replaying the threshold cut independently on each
original bar preserved the construction and restored manifold component topology.
Inspect modified context geometry as well as newly appended assets. This is a
specific touching-bar case, not a general reason to split every boolean operand.
See [repair](blender/passenger_lodge_04/scripts/finish.py) and
[saved-file verification](blender/passenger_lodge_04/verification.json).

Project memory from the R12 door and window repairs, September 2026. Read this
before authoring or exporting additional station buildings. Prevent the defect
in source geometry rather than repeatedly patching it after import.

## What happened

Insulated wall cores and steel door/window reveals occupied the same planes.
The renderer alternated between competing surfaces: beige stripes, ragged borders
and flickering at jambs, headers and sills. One still image could conceal the
problem; rapid captures and small viewpoint changes exposed it. This was visual
**z-fighting**, not the player's collision geometry.

A separate, earlier defect involved overly simplified Nanite fallback geometry
producing incorrect traced lighting around opening details. That repair fixed
some sill artifacts but did not remove the coplanar wall faces. Similar-looking
symptoms can have different causes.

## Rules for future meshes

- **Assign one owner to each visible surface.** Decide which mesh supplies the
  finished reveal. A core, lining or panel behind it must not expose another face
  on the same plane. Check across separate objects, not only duplicate vertices
  within an object.
- Give layered construction real thickness and intentional concealed separation.
  Trim may cover a joint, but do not leave coincident exposed polygons, duplicate
  shells or an old wall behind its replacement.
- Cut openings through every relevant wall layer. Inspect both sides, head,
  sill/threshold and corners. Apply the same rule to roof/ceiling junctions,
  floor/beam tops and platform transitions.
- Preserve clear opening width, headroom, glass placement and walking collision.
  Trim or recess the concealed core instead of moving visible trim into a doorway
  or shifting the whole building.
- Do not prescribe a universal tiny offset. R12 used **4 mm of concealed core
  recess** at metre-scale architecture; that is proven for these assets, not a
  required distance for every model. A separate quarters beam/floor repair used
  3 mm. Choose separation for the asset's scale and validate the evaluated result.

## How we resolved R12

1. Reproduced the defect at a known camera position and inspected source bounds.
   Coplanar core/trim faces were confirmed within 0.00001 m in this axis-aligned
   construction.
2. Moved only the conflicting core boundary faces **into the core by 0.004 m**.
   Steel profiles, glass, mullions and opening dimensions stayed intact. The
   competing surface disappeared without creating an exterior gap.
3. Applied accepted door recesses and quarters beam separation before exporting
   the window changes. Rebuilding from approved source must replay earlier
   corrections or a later export can silently undo them.
4. Re-exported affected assemblies while retaining pivots, slots, replacement
   mappings and collision. Assertions required material slots and authored
   collision boxes to match the previous handoff exactly.
5. Imported, saved and reviewed the actual Unreal meshes. The window repair
   affected 44 core pieces in seven assemblies; the door repair affected 42 cores
   in twelve assemblies. Approved VF07 source was untouched; editable export
   copies and reproducible repair scripts were retained.

For new architecture, encode surface ownership and clearance in its generator or
editable source from the outset. R12's scripts target named, axis-aligned objects:
their bounding-box comparison is not a general detector for rotated, curved or
arbitrary intersecting meshes. Those need face-level inspection or an appropriate
geometry check.

## Diagnose before changing rendering settings

| Observation/check | Next action |
| --- | --- |
| Material stripes flicker and source faces are coplanar | Repair competing geometry, including concealed layers. |
| No competing faces; artifact changes when traced lighting is isolated | Inspect actual built fallback geometry against source detail. |
| Player capsule catches at a threshold or frame | Inspect collision separately; visual z-fighting does not establish a collision fault. |

Use controlled, temporary rendering comparisons and restore settings afterward.
Do not conceal geometry defects with global lighting changes, shadow bias or by
disabling Nanite/Lumen across the scene.

The effective R12 fallback repair explicitly selected
`NaniteFallbackTarget.PERCENT_TRIANGLES`, with 100% fallback triangles on affected
assemblies, and rebuilt them. An Auto-target trial was ineffective. Verify built
triangles after import/reopen and preserve the setting in the manifest/importer.
Full fallback geometry is not the default for every asset: it adds tracing cost
that needs measurement.

## Completion checks for future mesh work

1. Inspect evaluated geometry after modifiers: openings through all wall layers,
   thickness, surface ownership and concealed clearances. Include close-ups of
   each unique opening construction, not only a whole-building beauty render.
2. Verify export units, orientation, pivots, material slots and collision. R12
   already converts metres to centimetres; do not add a second scale conversion.
3. Inspect in Unreal under neutral light and actual night/torch lighting. Check
   glancing angles, both sides of openings, and nearby/distant viewpoints.
4. Capture a rapid sequence and move the viewpoint slightly. Compare reveal
   surfaces across frames; distinguish moving weather and lighting noise from
   geometry. Our window review captured six frames at each of three locations.
   Unreal screenshots are asynchronous: wait for each image to finish before
   requesting the next, and verify every expected file exists.
5. Save/reopen and confirm persistence. If collision or clearances changed,
   repeat affected routes with the actual player capsule. Retain before/after
   evidence and update this memory when a new failure mode is confirmed.

## Evidence and implementation

- [Door diagnosis and repair](unreal_handoff/revision12/trim2/README.md) and
  [exact changed faces](unreal_handoff/revision12/trim2/core_recess.json).
- [Window diagnosis and reproduction](unreal_handoff/revision12/window_fix/README.md),
  [window changes](unreal_handoff/revision12/window_fix/core_recess.json) and
  [rapid captures](unreal_handoff/revision12/window_fix/burst/report.json).
- [Cumulative repair implementation](unreal_handoff/revision12/scripts/trim2_recess_cores.py),
  [window entry point](unreal_handoff/revision12/scripts/window_recess_cores.py) and
  [import verification](unreal_handoff/revision12/scripts/window_verify.py).
- [Separate Nanite fallback diagnosis](unreal_handoff/revision12/polish/README.md).

These are confirmed examples, not a promise that every future flicker has the
same cause. Extend the diagnostic history when a different cause is established.

## Hinged-door swing direction

A door authored with an exterior hinge pivot cannot be made inward-opening by only negating its target angle. The R12 door's exterior pivot is 35 mm in front of the leaf centre plane; simply setting -95 degrees stopped at about -6 degrees against the existing jamb. The quarters landing and south generator approach needed inward swings.

The verified inward variant moves the pivot to the opposite side, mirrors the hinge hardware and frame stops/seals, re-exports leaf/glass/fixed components around that pivot, and updates the leaf collision centre from -3.5 cm to +3.5 cm. Moving the installed actor by the corresponding 7 cm preserves the closed leaf plane and opening clearances. It does not widen or move the building's doorway. Both inward doors then reached -95 degrees and passed actual player-capsule traversal. Keep this as an assembly change, including hardware and collision, rather than only an animation-sign change.

Evidence: [initial pivot diagnosis](unreal_handoff/revision12/doors/rooms/swing_diagnosis.json), [inward export](unreal_handoff/revision12/scripts/doors_export_inward.py), [placement](unreal_handoff/revision12/doors/rooms_install.json), and [runtime traversal](unreal_handoff/revision12/doors/rooms/runtime.json). Service-area openings come from VF09/R13, which supersedes the VF07 generator/workshop footprint; inspect the current live assembly before applying older opening coordinates.

## Long route imports: verify basis with asymmetric geometry

The gondola route FBX used Blender `axis_forward='-Y', axis_up='Z'`; in this
import configuration its long +Y cable arrived along Unreal -Y. A symmetric
twin-leg tower concealed that mistake. Compare the actual imported endpoints,
not only symmetric bounds or expected axis labels. The route assemblies use an
explicit 180-degree yaw to produce the intended (-X,+Y,+Z) mapping. Existing
cabin assets use their original export pipeline and were not rotated.

Use named fields for Python rotations: `unreal.Rotator(pitch=0, yaw=180, roll=0)`.
The positional call `unreal.Rotator(0,180,0)` in this environment produced a pitch
half-turn, normalized to yaw=180/roll=180, and inverted the tower vertically.
The failed bounds assertion exposed it before saving. Evidence:
[diagnostic transform](unreal_handoff/revision12/gondola_route/bounds_probe.json),
[corrected cable bounds](unreal_handoff/revision12/gondola_route/orientation.json),
and [correction script](unreal_handoff/revision12/scripts/gondola_orientation_fix.py).

## Appended cabin hierarchies and capped curves

The cabin source contains a movable parent above its shell pieces. Translating both
that parent and its children while recentering an appended collection applied the
origin shift twice. Snapshot each object's world matrix, detach while restoring
those matrices, then apply the origin shift once. The saved cabin review verifies
166 retained mesh bounds against the original inventory within 0.37 mm.

Blender 5.0 evaluated capped curve tubes also retained disconnected coincident cap
rings on the new wiring and hooks. Convert those tubes to mesh and weld the matching
rings before delivery; merely enabling curve fill caps did not make the evaluated
mesh manifold. This is a topology repair with no silhouette change. See the
[reproducible refinement](blender/gondola_cabin_01/scripts/refine_fittings.py) and
[saved-file geometry checks](blender/gondola_cabin_01/verification.json).

For the outboard sliding doors, a dark beauty render concealed air gaps at the
head and jambs. Neutral light showed that the leaf stopped below the header and
the brushes did not reach the wall core. Extend the closed leaf above the clear
opening and bridge the concealed depth with seals; keep the stationary brushes
outside the required clear width and height. The cabin refinement and saved-file
checks above encode that overlap without reducing the 1.20 × 2.10 m opening.

## Splitting terminal curves and compiling material graphs

When separating distant terminal assemblies, classify source curves by evaluated
world-space bounds rather than object origins. A curve can keep its origin at zero
while its control points describe a distant wheel rim. Origin-based grouping put
the Maldek rim into Millford's rotating mesh. The corrected
[mechanism export](unreal_handoff/revision12/scripts/gondola_mechanism_export.py)
uses bounds centres and rejects wheel vertices farther than 2.5 m from their pivot.

In this UE version, the single-input pins on MaterialExpressionSine and
ComponentMask are addressed by an empty pin name. A failed connection left the
rope material with a missing Sine input. Assert graph-connection return values
and inspect compiled shader errors, as in the
[rope material builder](unreal_handoff/revision12/scripts/gondola_mechanism_rope_material.py)
and its [successful shader check](unreal_handoff/revision12/gondola_mechanism/rope_shader.json).

## Joined furniture material bakes

The lodge seating export found that joining objects reset the active UV layer.
Smart-project then modified the source grain UVs while the bake still targeted
the original overlapping destination layout. The resulting atlas contained large
overlapping hardware shapes instead of individually packed board faces. Explicitly
reselect the destination `BakeUV` **after joining**, then unwrap and bake; keep
source texture nodes bound to the separate source UV layer. Inspect the atlas
before importing, as shader compilation does not detect this mapping mistake.
The corrected [export](unreal_handoff/passenger_lodge_01/scripts/export_seating.py)
also carries per-piece generated coordinates as attributes and documents its
stable replacement for object-random variation. See the corrected
[atlas](unreal_handoff/passenger_lodge_01/seating/textures/PLS_01_BaseColor.png)
and [Unreal close-up](unreal_handoff/passenger_lodge_01/previews/seating/table_detail.png).

## Small hardware collision beside moving storage

The kitchen's second hot-cabinet leaf stopped near 74 degrees in Unreal even
though source geometry and an engine mesh trace were clear. The obstruction log
identified a box approximating a 12 mm circular hinge barrel against the adjacent
drawer's collision box. The box's rotating corners extended beyond the round
hardware. Keep these small barrels visual/aimable and use the structural panels
for physical blocking; do not move the authored pivot or enlarge cabinet gaps to
accommodate an oversized approximation. The [export](unreal_handoff/passenger_lodge_01/scripts/export_kitchen.py)
and [exact repair ledger](unreal_handoff/passenger_lodge_01/kitchen/collision_repair.json)
retain the 76 other moving-piece boxes. This diagnosis concerns small round hinge
hardware; it does not justify removing collision from door leaves or drawer sides.

## Mating hinge hardware and leaf collision

The east-wall first-aid cabinet initially stopped on its fixed hinge pins and
knuckles. The source hinge mates intentionally at the panel edge, while the
Unreal moving collision approximates the panel with a rectangular box. An
engine obstruction and a Blender BVH probe identified those six fixed pieces.
Inset only that collision box's hinge edge by 7 mm; preserve the visible panel
and authored pivot. Real E-input open/close and all three nearby walking routes
then passed. This is specific to this hinge, not a general clearance to apply
to every door. See [repair](unreal_handoff/passenger_lodge_01/east_wall/collision_repair.json)
and [runtime checks](unreal_handoff/passenger_lodge_01/east_wall/runtime.json).

## Replacing concealed furnishing placeholders

The furnished west-services source had replaced `FIT_Cleaning_cupboard` with an
open carcass and stocked shelves, but the older Unreal lodge still contained the
solid placeholder inside `SM_Lodge_Shell_005`. Import bounds and route checks
passed while the placeholder hid all the new supplies. A flashlight review and
engine sight-line trace identified the retained source owner. Replace that one
member through a localized shared-mesh export, retaining the five wall/privacy
members, rather than hiding the entire shared actor or disabling its collision.
See the [replacement ledger](unreal_handoff/west_services_01/janitor_patch_install.json)
and [visible shelves](unreal_handoff/west_services_01/previews/gameplay_night/janitor.png).

For west-services motion, mating seals and hinge barrels also blocked approximate
leaf boxes. Exact source BVH probes identified the contacts. Separate the small
fixed hardware collision where appropriate; the parcels structural leaf retains
its box with measured 25 mm hinge-edge and 20 mm latch-edge insets. The generator
cover required an actual fuel-line reroute, and the rescue cupboard required a
shelf relocation. These were geometry-specific repairs, not a reason to remove
blocking collision from the mechanisms. All 17 mechanisms then passed full
open/close, real E-input focus and player-obstruction/retry tests; see the
[manifest](unreal_handoff/west_services_01/exports.json) and
[runtime safety report](unreal_handoff/west_services_01/safety.json).

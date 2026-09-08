# Mesh authoring lessons: prevent overlapping surfaces

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

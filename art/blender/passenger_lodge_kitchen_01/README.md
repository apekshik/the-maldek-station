# Passenger lodge coffee preparation package

An optional [weathered finish variant](weathering/README.md) adds downloaded CC0
dust, water marks, scuffs, smudges and worn furniture textures. It includes a
separate fitted blend, asset library and matching review renders; clean files below
remain the geometry baseline.

Editable, fitted Blender assembly for the enclosed coffee annex. Open `Maldek_Passenger_Lodge_Kitchen.blend`, scene `PLK_Fitted_Review`. `PLK_Assets.blend` is a separate appendable collection library without station context. Finished meshes are in `PLK_Assets` beneath `PLK_Assembly`. Everything under `REFERENCE_ONLY_Source_Context`, all other source scenes, and every `PLK_REVIEW_*` collection are context/review only and must be excluded from asset exports.

## Fit and ownership

Source: `../passenger_lodge_03/Maldek_Passenger_Lodge_Materials.blend`, SHA-256 `b9d78ed0d7c5c50bc28a8fb6a0d63f1c86fa83d3144c6a7eae50476ee9607796`. The source matches the shared contract. The source file is never saved by these scripts.

Units are metres, Z up. Package coordinates are `(x, -depth, z)` with one assembly translation `(-24.1, 4, 4)`. There is no scale conversion or mirroring at the root. Each component has a local root and each moving leaf/drawer has its own parent/pivot. `replacement_manifest.json` records every part's closed transform, dimensions, material slots, parent and motion properties.

The serving assembly replaces the exact 3.00 × 0.65 m proxy footprint, X=1–4, depth=10.85–11.50. Its top is 1.00 m above the finished floor, with 40 mm slab thickness. A pine customer panel, recessed petrol kick and rear carcass close the bottom of the mockup's low aperture. The panel is the sole public-facing closure; there is no masonry infill hidden behind it and no duplicate sill. The original partition retains its existing jambs and 2.20 m opening head. The result is a fixed open serving hatch with a clear opening above the counter. **No wall/cladding patch is required.**

The coffee staff door, leaf, frame, reveal and swing remain entirely owned by the doors package. No door is included here. Its current handoff manifest describes an outward swing from the depth-15 jamb. This package reserves the interior doorway approach at X=3.70–4.82, depth=13.72–15.04. Final frame/collision integration still belongs to that package.

The hall, tables, benches, lockers, restroom walls, building footprint and public routes are retained as source context. New public geometry stays within the original counter/cubby footprints.

## Working layout

- West equipment run: X=0.25–0.95, depth=12.00–14.95; separate hot-equipment cabinet, three drawers and wash cabinet. Worktop height 0.90 m, slab 35 mm, 18 mm carcass panels, recessed plinth and 3 mm perimeter margins and 6 mm meeting gaps between hinged fronts.
- Urn: separate rolled vessel/lid, carry grips, draw-off spout and lever, thermostat dial, gauge and drip tray. Kettle: steel bell silhouette, lid/knob, raised dark handle, tapered spout, switch and short cord.
- Wash sink: real worktop cutout and recessed radiused bowl with drain and strainer, separate ribbed drainer and two indexed cross-head valves feeding a swan-neck tap.
- Hand basin: relocated from the cramped rear-west proxy position to X=4.46, depth=13.24, Z=0.86, yaw=180°. It has its own tap, splash back/side screen, soap, towel dispenser, brackets and visible waste. The new standing position is clear of rear cabinets and the staff door.
- Rear worktop: X=1.05–4.55, depth=15.30–15.95. The fridge has an open 760 mm bay at X=2.20–2.96, with no overlapping cabinet carcass/plinth. Its shelves, gasket, inner door racks and feet are separate meshes. The rear top keeps a 1.40 × 0.58 m clear preparation rectangle at X=2.20–3.60, depth=15.32–15.90.
- Microwave: panel-built shell/cavity, recessed screened window, rotary controls/ticks, separate hinged door and ventilation details. Unbranded practical appliance modeling only.
- Dry shelving retains its original 1.05 × 0.55 × 2.10 m envelope, with real uprights, shelves and a rear brace. The upper open wall shelf has brackets and a small saucer stack.
- Dressing is limited to a service tray, four cups/saucers, three labelled tins, small biscuit display, a pedal bin and the two-level public lost-property cubby. Text remains editable Blender FONT objects. No branded artwork or generated textures.

## Review and reproduction

Run with Blender 5 in this order, from the repository root:

```powershell
& 'C:\Program Files\Blender Foundation\Blender 5.0\blender.exe' --background --python art/blender/passenger_lodge_kitchen_01/scripts/build.py
& 'C:\Program Files\Blender Foundation\Blender 5.0\blender.exe' --background --python art/blender/passenger_lodge_kitchen_01/scripts/refine.py
& 'C:\Program Files\Blender Foundation\Blender 5.0\blender.exe' --background --python art/blender/passenger_lodge_kitchen_01/scripts/check_mechanisms.py
& 'C:\Program Files\Blender Foundation\Blender 5.0\blender.exe' --background --python art/blender/passenger_lodge_kitchen_01/scripts/verify.py
& 'C:\Program Files\Blender Foundation\Blender 5.0\blender.exe' --background --python art/blender/passenger_lodge_kitchen_01/scripts/render.py
```

Verification passes: 402 manifold meshes, all five sampled walking routes, a clear doorway approach, a clear 1.40 × 0.58 m preparation rectangle, and 17 sampled hinge/slide/lift mechanisms. Mesh BVH contact checks sample hinges every 5 degrees and translations in ten steps with other parts closed; this is not a continuous sweep or a simultaneous-operation guarantee.

The file opens at frame 1, closed. Frame 40 demonstrates the microwave, fridge and one rear cabinet door plus a west drawer opening. Paired cabinet leaves use opposite outer hinges with ±90° travel; microwave and fridge use 95°. The kettle lid has 35 mm lift clearance under its handle; a full tilted removal is not modeled. The serving drawer bank is at X=1.0–1.6, away from dry shelving. Individual pivot custom properties record the intended hinge/slide/lift axis and travel. They are modeling poses, not game logic.

`previews/` contains customer-side and staff-side counter views, the staff-entry kitchen view, rear preparation, washing, handwashing, overhead access, an open-mechanism view, and cubby/beverage-equipment details. All perspective kitchen views use 1.65 m eye height. Neutral temporary area lights and a roof-hidden review make fittings readable; these are not installed fixtures. The green overhead markings are review geometry only.

`verification.json` is generated after reopening the saved file. It checks mesh topology, proxy removal, source hash, walking samples with a 0.30 m radius, doorway approach and sink cutout rays; it also records individual open-leaf extents. Bounds-based clearance tests are conservative authoring checks, not Unreal collision. See the report for the actual results.

## References, materials and integration limits

See `references.md` for real product photographs, manufacturer drawings and the specific features adopted. These are generic period-informed interpretations; current reference products are not claimed as exact early-1990s models.

Reused station finishes include petrol paint, warm enamel, pine and porcelain. New materials cover stainless, chrome, laminate, carcass interiors, dark handles, paper and display glass. `material_manifest.json` flags procedural Blender-only graphs; materials have not been baked for Unreal. Modeling includes visible fixture geometry, not electrical or plumbing simulation.

Later work: asset export with reference collections excluded, UV/material baking, game collision and player traversal, coordinated staff-door integration, appliance/cabinet interactions, utility connections, inspectable evidence and wear refinement. No Unreal session, import or PIE validation was performed for this package.

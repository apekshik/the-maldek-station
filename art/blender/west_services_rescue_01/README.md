# Maldek west services — rescue room 01

Editable, local-coordinate Blender fittings for the approved north rescue / first-aid room. Original maintained alpine visitor-station equipment, with analog controls and restrained unbranded lettering. No shell, floor, roof, shared wall, ramp or staircase is authored by this package.

## Open and review

- `Maldek_Rescue_Hut_Editable.blend`: append **WSR_ASSETS**. Metres, Z up, +Y north / gondola, +X east. Editable mesh parts, bevel modifiers, font lettering, procedural materials and individual UV layouts.
- `Maldek_Rescue_Hut_Fitted_Review.blend`: saved reference-copy assembly; never append its reference architecture as rescue assets. The immutable source and inherited context remain in the review copy. Distant non-WS context is hidden for close review efficiency.
- `previews/`: 11 fitted neutral images, covering porch closed/open, interior door, cot, open equipment cupboards, folded/deployed stretcher, overhead, window, threshold and heater/radio.
- Frame **1 / NORMAL_EMPTY**: unattended room, doors and cupboards closed, stretcher folded on brackets. Frame **40 / READY_FOR_ARRIVAL**: inward leaves held at 90°, stretcher deployed beside cot. Frame **80 / EQUIPMENT_OPEN**: doors open, cupboards open, stretcher deployed. Named poses use constant interpolation; intermediate frames are not a certified folding or deployment animation. A prepared cot blanket is present in both empty and arrival arrangements; “empty” means no occupant.

## Assembly and ownership

Frozen reference: `../west_services_01/Maldek_West_Services_Blockout.blend`, scene `West_Services_Combined`; SHA-256 `54bb3f1e54a6c84ebd1b90c5664e6e7b328be6e6139bac0f6fd9f49ea630b6aa`. The source hash was checked before reading and before fitted assembly. `reference_inspection.json` records the saved scene inventory and world bounds.

Add **(-37.45, 0, 4.60) metres once**, with identity rotation and unit scale. `assembly.json` supplies the 4×4 matrix, every object's parent/rest matrix/dimensions/material slots, mechanism pivots and the asymmetric east/north markers. Parent top-level asset objects to an assembly root at this translation, as the review script does; do not also translate animated child coordinates. Do not convert to centimetres in Blender. The later exporter must apply its engine-unit conversion only once and verify basis with both asymmetric markers.

Replace only `WS_RESCUE_PROXY`, deleting exactly:

1. `WS_RescueCot`
2. `WS_RescueBlankets`
3. `WS_RescueHeater`
4. `WS_RescueSign`

No other proxies are removed. No master mesh/object/face patch is required or supplied: **patch ledger is empty**. Frame jambs are inset 4 mm from the rough aperture boundaries, with concealed packing. Frame profiles own the finished opening reveals; the original wall opening faces sit outside the finished reveal. The narrow interior seal profiles bridge the frame to the inward leaf plane. The low metal threshold is the sole finished threshold top, 12 mm above the shared slab; it does not duplicate a floor. Shared structure/roof meshes remain unchanged in the fitted copy, confirmed by saved/reopened bounds checks.

## Mechanisms and use

- Active/passive door pivots: `(5.768, 1.28, 0)` and `(5.768, 2.82, 0)`, respectively, rotating around local Z to +90° / −90°. The closed leaf centre plane is X=5.741, inside the wall; hardware and stops are authored for this inward motion. Open both for transfer. Rest leaf gap is 4 mm with an active-leaf meeting seal. Flush bolts belong to the passive leaf. Hold-open catches are outside the central transfer line.
- The window glass is separate. The blind fabric has `Raised` and `Lowered` shape keys: bottom heights 1.776 m and 1.10 m. The normal raised position leaves a standing view through the lower glazing. The roller, pull and cleat are separate geometry. `WSR_Privacy_blind_ROLL` marks the roller operation; the fabric shape key controls coverage.
- The folding transport stretcher is separate from the narrow cot. Two tensioned canvas sections have their own rails, crossbars, carry grips, restraints, buckles, offset hinge cheeks and pins. Independent U-leg pivots fold under each half for stow/carry and lower to the floor in the ready pose; release these legs before folding the main hinge. Its root relocates from the wall brackets to the ready anchor. The second half folds 180° around its Y hinge, offset 75 mm above the rail plane. Two `WSR_Stretcher_LOCK_SLIDE_*` roots release 160 mm toward the head before folding and return across the joint when deployed. Do not animate a fold with sleeves locked. `assembly.json` preserves the rest hierarchy; the Blender poses provide released/locked states.
- Cupboard and first-aid doors have independent Z pivots and stocked interiors. Thermostat and radio controls are separate Y-axis pivots. Small barrels, pointers, text, cords and trim are visual parts; do not give them oversized blocking boxes.
- The heater stays at the north wall, away from the stored blankets and bags. This is a fictional small refuge appliance; electrical capacity and circuit behavior are later integration work.

Named interaction empties: `WSR_STRETCHER_STOW`, `WSR_STRETCHER_READY`, `WSR_BLANKET_PLACE`, `WSR_HEATER_CONTROL`, `WSR_READINESS_CARD`, `WSR_RADIO_POINT`. Controls are 1.15–1.47 m above the room floor. The local +Y axis of each anchor points toward the controlled object; each records its approach direction and height.

## Handling evidence and limits

`verification.json` and `handling_plan.svg` document the route. The JSON records every sampled stretcher centre, angle, four plan corners and separating-axis margin. The loaded envelope is **2.2 × 0.75 m**, tested through height **0.62–1.40 m**. Start on the porch facing along Y, translate toward the doorway, rotate with a small northward shift while crossing the opening, then move inward and turn beside the cot. Follow the recorded waypoints; a turn about one fixed porch centre clips the jamb. The final path's smallest conservative separating-axis margin is about **52 mm**. This is clearance for the stretcher envelope, not a claim that two carrying operators fit at every point.

The independent walking check uses a **0.34 m radius / 1.8 m height** envelope, includes the deployed stretcher as an obstacle, and routes around its north end. Path samples are no farther than 25 mm apart; stretcher angular samples no farther than 1°. Obstacles use conservative evaluated mesh AABBs, tested against the oriented stretcher rectangle by separating axes. Door coverage/clearance uses 713 rays in each state across a 1.50 × 2.15 m opening. Leaf/frame/wall surface intersections are tested every 2° of swing using evaluated triangle BVHs. Check logs include topology, UV presence, same-facing coplanar rectangular-face candidates, proxy absence and shared mesh bounds.

These are saved/reopened **Blender** checks, not continuous collision proof or engine verification. Curved/intersecting small hardware is visually inspected; the rectangular coplanar-face audit is not a universal surface solver. `asset_geometry.json` records evaluated mesh topology and conservative mechanism swept bounds.

## Reproduce

Use an independent background Blender 5.0 process. All outputs remain in this folder. From any shell, use absolute paths to these scripts:

```text
blender.exe -b -t 4 --python <package>/scripts/inspect_reference.py
blender.exe -b -t 4 --python <package>/scripts/build.py
blender.exe -b -t 5 --python <package>/scripts/review.py
blender.exe -b -t 5 --python <package>/scripts/window_rest_review.py
blender.exe -b -t 3 --python <package>/scripts/service_connections.py
blender.exe -b -t 5 --python <package>/scripts/render_service_detail.py
blender.exe -b -t 3 --python <package>/scripts/verify.py
blender.exe -b -t 3 --python <package>/scripts/pose_audit.py
blender.exe -b -t 3 --python <package>/scripts/finalize.py
```

Run sequentially and wait for completion. `review.py -- 01 02` can render selected prefixes; it always rebuilds the fitted copy from the immutable source. `finalize.py` writes the integration metadata and hashes after successful verification. Review cameras/lights and reference objects never belong to the asset export set.

## Provenance and integration gates

All meshes, text and material graphs are original procedural work. No external images or textures are used or redistributed; there are no external texture dependencies to pack. The research sources describe equipment relationships, not a historical certification or copied commercial model:

- [Moffat Mountain Rescue equipment](https://www.moffatmrt.org.uk/what-we-do/equipment/): maintained, checked, organized equipment.
- [Arrochar Mountain Rescue equipment](https://www.arrocharmrt.org.uk/equipment.html): small selection of stretcher, blankets/bags, splints, rope and radio relationships; contemporary electronics omitted.
- [Mountain Rescue education pack](https://www.mountainrescue.org.uk/wp-content/uploads/2020/08/Education-Pack.pdf): overview cited by the approved handoff; no artwork copied.
- [Ferno stretcher reference](https://ferno.it/barelle-sar-e-toboga/barella-toboga-71-unica-arancione-con-4-cinture-incluse/): carrying grips/restraints and subdued orange rescue cue; this folding canvas design is not a replica or claimed historic Ferno product.

Later work: shared-shell refinement and combined-room assembly; export copies with converted lettering; procedural material baking and consolidated non-overlapping atlas UVs as needed; LODs; collision setup and actual capsule/carried-stretcher traversal; moving door and cupboard interaction; engine basis/units and material-slot checks; neutral/night/torch and nearby/distant glancing-motion review; engine save/reopen verification. No FBX, runtime behavior, Unreal asset, map or code is modified by this delivery. The optional collision recipe is guidance for the future exporter, not verified engine collision.





# Emergency power / WSE 01

Editable source: `Maldek_Emergency_Power.blend`, collection **WSE_ASSETS**.
Fitted review: `Maldek_Emergency_Power_Fitted.blend`. Context is copied from the frozen master and translated into the local review basis. The source master is never saved or modified.

## Assembly

Blender metres, Z up, +Y toward gondola. Add **(-37.45, -5.00, 1.20)** once, identity rotation and unit scale. `assembly.json` contains the matrix, asymmetric +Y / east markers, exact proxy deletion names, object bounds/material slots, interaction anchors and sampled mechanism swept bounds. Move root objects only: children already inherit their root transform. Do not translate every child again.

Append only WSE_ASSETS from the asset source. Delete exactly the `WS_POWER_PROXY` names in assembly.json, including provisional lettering. Do not delete either other room proxy collection. Exclude fitted context, review lights/camera and orientation/interaction empties from render-mesh export (retain the empties as assembly metadata). No structural floor, shared wall, roof, walkway or staircase is delivered as a power asset.

The fitted file keeps the master structure in its own collections; its default view hides upper architecture, east/north walls and exterior access structures for inspection. Restore their render visibility for full context. The west-entrance renders use full shared context. The images of open mechanisms are static review poses, not game behavior.

## Equipment and operating rule

A small original, unbranded diesel set has an engine, alternator, cooling fins, radiator casing, guarded belt, injector lines, filters, starter, coolant hose, drain pan, integral day tank and vibration feet. The frame remains 2.50 × 1.30 m. The detachable control pod projects approximately 0.12 m north of the skid; this is a documented service-side fitting, with the walking aisle beyond it clear. The battery cabinet sits beside the alternator with short DC cables. AC wiring rises above walking head height before reaching the wall controls.

The panel uses analog meters, start/stop, run/fault lenses and an emergency stop. The wall selector is labeled NORMAL / OFF / EMERGENCY. The distribution cabinet has three separate circuits: LIGHTING, RADIO and RESCUE HEAT. Its label explicitly says **NO GONDOLA DRIVE**. No main-drive circuit, LCD, runtime power logic, fuel grind, sound or new narrative behavior is added.

`assembly.json` records the separate service-door leaves, cabinet door, battery lid, engine cover, transfer selector, breaker handles and fuel lever. The running image changes indication only. Switch positions are authored review states; interlocks and electrical behavior require later gameplay work.

## Door and machine handling

The west frame fits the fixed 1.60 × 2.30 m rough hole. Nominal finished frame opening is 1.43 m wide; the 90-degree inward leaves retain approximately **1.41 m** including the flush push plates, with more than **2.17 m** head clearance above the threshold. The hinge line is behind the frame on the room side. No door opening is cut into the master by this package.

Removal sequence: isolate and disconnect the AC/DC leads, fuel connection, exhaust flex and radiator flexible duct; detach the control pod and open/remove both leaves as needed. Translate the 1.30 m wide skid north into the clear handling bay, align its long X axis normal to the west doorway, then slide it west through the finished opening. There is about 55 mm nominal clearance per side. Unbolt the frame if additional rigging clearance is needed; the 1.60 m rough opening is unchanged. The package does **not** establish a crane position, lift capacity, structural load capacity or a way to carry the set down the service stairs. The elevated walkway requires a separately designed temporary lift/landing and rigging plan before any real installation interpretation.

## Air and exhaust interfaces

The southern west louvre is **DISCHARGE**, the northern one **INTAKE**. The radiator connects to the discharge through a sealed hollow transition, including its flexible first section. Discharge terminates west of the wall; a substantial exterior separator prevents a direct lateral path to the intake. The intake admits fresh air to the room, allowing it to pass the alternator and engine. This retains both approved west apertures, with no new cooling-air opening and no airflow into occupied rooms. Wind-dependent external recirculation, pressure drop, free area and thermal capacity remain unvalidated design assumptions; the separator is not a CFD result or a guarantee against recirculation.

The exhaust is a separate continuous insulated route: engine outlet, flex bellows, silencer/reducers, south-wall sleeve, exterior riser, standoffs/clamps and weather cap. The top is near world Z 8.93 m, at X -35.20, Y -5.30, away from the public porch. It does not discharge into the radiator duct.

`shell_patch.json` specifies the one required shell edit: a radius 0.157 m Y-axis bore through **WS_BaseSouth**, centered at world (-35.20, -4.875, 3.15). `scripts/review.py::apply_patch()` applies that cutter after translating context to local coordinates. The replay script `scripts/patch_world.py` exposes the equivalent world-space patch for a future integration copy; it refuses to operate on the frozen master file. No replacement wall is delivered. The sleeve owns the visible bore finish; the annular seal occupies the concealed gap. Its material represents a seal only, not a certified firestop assembly.

Door/louvre frames sit inside the rough openings with geometric separation from the shell. No blanket wall offset or reveal-face recession is needed for these inset frames. The continuous discharge duct sits inside the louvre frame with a distinct surface owner. `surface_audit.json` records evaluated coplanar polygon intersections; opposite-facing buried assembly contacts are distinguished from same-facing competing surfaces.

## Review and verification

The numbered PNGs in `reviews/` cover neutral overview, service side, stopped/running controls, closed/open entrance, open mechanisms, louvre section, temporary duct cutaway, complete exhaust, sleeve close-up, player-height view, open distribution and open battery. Section cutting affects the review render only and is removed before the fitted file is saved.

`verification.json` is generated by reopening both saved Blender files, evaluating modifiers, checking manifold edges/zero-area faces/UV presence and sampling a 0.34 m radius × 1.80 m tall walking envelope at 50 mm path increments. Cable paths use per-face conservative bounds to avoid treating the empty interior of their large route boxes as solid. The shell sleeve Boolean is also checked for topology. `mechanism_verification.json` records additional moving-panel checks. `handling_verification.json` checks the disconnected skid handling envelope into the doorway; the supported path stops before the skid leaves the walkway footprint. These are source-geometry checks, **not Unreal collision validation**.

## Reproduction

Use your own Blender 5.0 background process. Run scripts in this order, with each process complete before the next:

1. `blender -b --python scripts/inspect_reference.py`
2. `blender -b --python scripts/build.py`
3. `blender -b --python scripts/surface_audit.py`
4. `blender -b --python scripts/review.py`
5. `blender -b --python scripts/verify.py`
6. `blender -b --python scripts/mechanism_verify.py`
7. `blender -b --python scripts/handling_verify.py`
8. `blender -b --python scripts/finalize.py`

All scripts resolve their own package directory. Use absolute script paths from other working directories. The package generator has no dependency on another task's output. No background process belonging to another task needs to be stopped or reused.

## Materials, UVs and provenance

Original geometry authored procedurally for this package. Petrol enamel, cream controls, galvanized metal, dark rubber, restrained tray/contact darkening and analog markings are parameterized Blender node materials; there are no externally sourced textures or copyrighted images to pack. Text remains editable Blender font geometry. Each mesh has a usable per-part smart-projected UV layer. Before engine export, convert text on export copies, choose shared texel density/atlas strategy, bake any desired wear, author LODs and collision, and verify coordinate conversion only once. Material slot names are enumerated in assembly.json. No engine-ready FBX or collision import is claimed.

Construction references read September 11, 2026:

- Logistics Cluster, generator installation: https://log.logcluster.org/fr/groupes-electrogenes — engine/alternator arrangement, handling, separate cooling/exhaust concepts.
- Cummins T-030 application manual, mechanical design sections: https://powersuite.cummins.com/sites/powersuite/files/2024-04/t030.pdf — flexible connections, radiator discharge directly outdoors, recirculation considerations. Applied as construction cues, not an engineered selection.
- Curvent louvre installation reference: https://www.curvent.co.za/post/2018/07/16/louvres-lower-heat-in-generator-rooms — supplied research direction; live page fetch failed in this run. No image copied.
- AKMEL: https://akmel.eu/ — open generator construction/silhouette reference; no product reproduced and no branding copied.

The shared `references.md` and handoff supply the period/style direction. This is a fictional game asset, with no claim of historical product accuracy or engineering certification.

## Integration gates

Final thermal/load/fuel sizing, ventilation under wind/snow, exhaust backpressure and support loads, acoustic and fire separation below occupied rooms, firestop specification, door seals/security hardware requirements and machine-lift design remain integration/design responsibilities. The existing blockout shell is not upgraded by this room package. Unreal neutral/night/torch lighting, glancing/moving captures, import scale/orientation/material checks, actual capsule traversal, interaction reach and save/reopen in-engine remain required. Coordinate the shared shell patch once with the later integration task. No Unreal, runtime code, maps, branch switches, commits, pushes or publications are part of this delivery.



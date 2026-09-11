# Furnished station → Unreal integration plan

Status: planned, September 11, 2026. This document changes no game assets, maps or runtime code. It is based on saved repository evidence, not a fresh live-editor survey.

## Outcome and starting point

Extend the existing playable lodge migration with the parcels office, rescue hut, emergency power room, shared raised structure, wraparound lower platform and final janitor/rescue/power dressing. Preserve the lodge work already imported, including engine-only additions and interaction refinements. Deliver a saved, reopened, traversable and packaged station checkpoint before changing the normal game entry flow.

Use `art/blender/station_dressing_01/Maldek_Station_Furnished.blend`, scene `Station_Furnished`, as the combined source for new geometry. Recorded SHA-256: `d4c5a3a7b4848dcd7221f9c5662e55d591002a7a777435cd510741c1aca2c8ab`. Verify the actual bytes before export. The source has 141 dressing objects, including 125 meshes, and seven passing sampled Blender routes (762 samples). These are not Unreal collision tests.

The existing delivery map is `/Game/MaldekRefinement/PassengerLodge/Station_Lodge_Migration`. Repository reports document the lodge shell, deck, windows, seating, doors, restrooms, kitchen, lockers, wall displays, east-wall additions and audio refinements there. The original `/Game/MaldekRefinement/R12/Station_R12` is separate. `game.uproject` targets UE 5.7. Current config still names R12 as the editor startup map and Engine/Maps/Entry as the game default; changing only the editor startup map would not establish the shipping game flow.

**Transfer the delta, not the entire station.** The furnished Blender file contains inherited context. Reimporting all of it would duplicate the existing lodge and could overwrite engine changes absent from that Blender master, such as the later east-wall package.

## Delivery structure and ownership

Continue in the existing migration map after a fresh checkpoint backup. Give all new assets their own root `/Game/MaldekRefinement/WestServices`, with Shared, Parcels, Rescue, Power, Dressing, Materials and Textures subfolders. Use `MIG_WS_*` actor identifiers and stable source IDs. Keep scripts, manifests, export copies and evidence in `art/unreal_handoff/west_services_01/`.

One integration manifest owns every placement and replacement. The three room packages remain independent export groups, but their shared shell, roof, exhaust interfaces, porch and platform belong to the common-structure group. Do not import three additional shells from individual fitted review scenes.

| Group | Source ownership | Engine grouping |
| --- | --- | --- |
| Shared structure and circulation | Verified WS shared collections, access structure, WS02 wrap platform and finish | Separate wall/opening, roof, floor, stair, rail and support chunks; localized culling and explicit collision |
| Parcels | WSP_ASSETS | Counter/shelves/cabinet bodies; separate door, shutter leaves, drawer and trays; trolley kept separate |
| Rescue | WSR_ASSETS | Fixed fittings; separate entrance leaves, cupboard/first-aid leaves, blind and stretcher parts |
| Emergency power | WSE_ASSETS | Generator, distribution/battery assemblies, ducts/exhaust; separate lids, leaves and control parts |
| New dressing | SD_JANITOR, SD_RESCUE_DRESSING, SD_POWER_DRESSING | Cupboard/rack assemblies and economical prop groups; preserve any future pickup identity in metadata |
| Exterior loose props | WS02_STORAGE_CLUTTER | A few static clusters or repeated instances outside routes |

Enumerate exact members from the saved scene before export; collection names alone are not a sufficient replacement ledger. Exclude inherited station context, retired proxies, all review collections/cameras/lights, orientation helpers and Blender demonstration actions. Export empties only as pivot/anchor metadata. If the old cleaning cupboard exists in Unreal, resolve its exact owning actor/component; if combined into a larger mesh, rebuild that affected chunk. A text search of the handoff metadata has not established an installed cupboard replacement target.

## 1. Establish the real engine baseline

1. Survey the current editor/map state without importing. Record map paths, dirty state, actor/component IDs, transforms, mesh references, foliage instances, material dependencies, player settings and latest interaction state. Preserve unsaved work; do not force reload over it.
2. Confirm all latest lodge checkpoints are present. Snapshot the migration map and any external packages it owns, plus affected shared runtime code and configuration. Record source/map hashes and a dated baseline ledger. A map copy alone is insufficient rollback for shared assets or code.
3. Record matching before views: west promenade, intended compound footprint, lodge janitor corridor, arrival/bypass stairs, control-room connection and nearby ground.
4. Sample actual blocking surfaces under the entire lower platform, piers, stair foot and approaches. Include Landscape AND custom ground meshes; the previous migration proved Landscape-only measurements misleading. Inventory foliage and route conflicts in the same footprint.
5. Confirm origin/basis against at least three retained station anchors and an asymmetric object. The existing importer uses station-world mapping `U = origin + (-100*x, +100*y, +100*z)` and a corresponding imported-mesh basis/actor rotation. Historical origin is `(-44282.305974972965, 18474.707549061975, 9898.5)` cm. Treat this as a candidate to verify, not a new guessed placement.

Deliver `baseline.json`, `source_inventory.json`, `ground_survey.json`, `replacement_plan.json` and before captures. Gate: no ambiguous replacement owners, unexplained baseline drift or unverified terrain support.

## 2. Produce reproducible export copies

Read the furnished master without saving it. Capture evaluated world matrices at rest, then detach/recenter copies once. The package offsets are already applied in the combined master; do not add them again. Individual assembly manifests remain authoritative for mechanisms and anchors, not an instruction to place the combined objects twice.

Reuse the lodge FBX importer/exporter conventions first. Preserve evaluated normals, triangulation, material-slot order, existing source UVs and authored pivot frames. Convert fonts/curves on copies. Serialize each mesh's source members, local pivot matrix, station transform, bounds, material slots, collision role and hash. Normalize the three different mechanism schemas: parcels use numeric axes and radians/absolute slide positions; rescue uses named axes and degrees; power uses named axes/degrees. Store slide deltas relative to rest, never the absolute open coordinate.

Choose chunking by spatial assembly and motion ownership. Join fixed shelf boards/hardware where sensible; retain glass and moving pieces separately. Reuse truly identical props through instances after verifying geometry/material equivalence. Do not make every screw an actor or join the whole compound into one mesh.

Before bulk export, import a small probe containing an asymmetric frame, labeled orientation marker, floor patch and one hinged part. Compare endpoints, pivot, scale and opening dimensions. The existing pipeline converts metres to centimetres; do not multiply vertex positions by 100 again. Use named Python Rotator arguments. Target the existing demonstrated bounds tolerance of 0.2 cm; investigate discrepancies rather than silently scaling actors.

Deliver `exports.json`, FBXs, editable export-only blend and per-part collision/anchor metadata. Gate: correct orientation, no duplicate geometry, openings through every layer, source hash unchanged and exact moving-part membership.

## 3. Fit the common structure and platform first

Install shared walls, floors, roof, porch, ramp, steps, service stair and lower wrap platform with temporary review materials. Preserve the approved source levels: retained promenade Z=4.0 m, upper rooms Z=4.6 m, lower room/platform Z=1.2 m. The lower wrap bounds are X[-40.45,-28.95], Y[-7.5,10.6] in Blender station space.

Replace only verified west-edge guard segments and other conflicting components. If a segment is joined with retained deck, re-export the owning chunk with an exact before/after source list. Keep all unaffected public deck, arrival stair and control-room connections.

Fit foundations and small ground interfaces to the surveyed game terrain. Prefer bounded support/ground adjustments over moving the entire approved building. Record every altered ground region and foliage move; preserve unaffected vertices/instances. Retain the already resolved exhaust wall sleeve, roof bore, flashing and interrupted seam; never reconstruct the old unpatched roof over them.

Provide walkable collision across grating and stair surfaces without sealing visible openings. Use deliberate ramp/tread collision and accurate platform edges, with guard collision where needed. Avoid convex hulls that fill doors or the entire lower service space. Review underside headroom and the intended route around the low stair underside.

Gate: actual player traversal of the old promenade, new upper approaches, lower door approach and complete wrap loop in both directions. Resolve geometry and terrain failures before detailed furnishing imports.

## 4. Translate materials and install room assets

Reuse compatible existing station material instances; create new ones under the new asset root rather than editing shared materials used elsewhere. Bake procedural wood, paint variation and metal finishes where simple Unreal parameters cannot reproduce them. Preserve packed printed artwork and source UVs when available. Convert small SD labels to mesh or a readable atlas on export copies, retaining wording and orientation.

Use BaseColor, packed roughness/metallic (and AO if deliberately connected), and normal maps. BaseColor is sRGB; packed masks are linear. Match the established OpenGL-normal bake/green-channel flip convention and verify a directional detail in-engine. Explicitly select destination BakeUV after joining; keep procedural/source UVs separate. Inspect atlases before import. Begin at 1K for small shared prop sets and 2K for room assemblies; increase only where close inspection demonstrates need. Preserve readable documents separately rather than shrinking all text into one room atlas. Do not bake Blender review lighting into albedo.

Keep translucent glass separate. Benchmark Nanite on substantial opaque structure; small props and moving fittings can start with conventional meshes, following the existing lodge path. Check grating, thin trim and traced fallback geometry directly. Do not enable full fallback detail everywhere or hide surface defects with global lighting changes.

Import in this order: parcels fixed fittings, rescue fixed fittings, power fixed fittings, janitor cupboard, rescue/power shelf dressing, then exterior clutter. Run a placement/dependency check after each group. Retain shelving and doors as meaningful collision; tiny bottles, cloths and hardware generally need no player-blocking collision. Keep query collision separately where future inspection requires it.

Gate: correct material slots and shader compilation, readable labels, no default materials, no exposed coplanar surfaces, and matching neutral + actual night/torch views.

## 5. Restore useful interactions without inventing a new quest

| Assembly | Initial transfer behavior | Separate gameplay scope |
| --- | --- | --- |
| Parcels entry | Existing StationDoor presentation, authored swing and latch/key parts; accessible for transfer testing | Narrative key ownership and access restrictions |
| Clerk drawer, secure cabinet and three trays | Obstruction-aware E open/close; trays usable only with cabinet clear | Parcel deposits, collection receipts, inventory rewards |
| Two service shutters | Individually controlled or coordinated authored leaves, with sweep checks | Service-hour logic |
| Rescue double entrance | Active leaf plus deliberate passive-leaf release; preserve stretcher-width opening and safe exit | Rescue event progression |
| Rescue cupboards/first aid | Existing storage interaction and recorded sound variants | Consumables and healing |
| Power entrance and cabinet/lids | Usable doors/service covers with proper local motion axes | Generator-start sequence and fault simulation |
| Blind, stretcher, trolley, dials and switches | Preserve pivots/anchors and a documented static initial pose unless a complete interaction is implemented | Carrying/folding, radio tuning, heat control and power distribution |
| Cleaning supplies and loose clutter | Static dressing, no misleading interaction prompt | Optional inspection or pickups |

Reuse StationDoor, StationCabinet, the shared focus style and existing recorded sounds where compatible. StationCabinet currently rotates around local yaw or translates by OpenOffset. The power lids rotate about source X, and some rescue controls use Y; do not feed their angles into the yaw-only path. Either orient a tested local pivot frame appropriately or add explicit arbitrary-axis support with regression checks for all existing cabinets. Paired door behavior and storage dependencies also need explicit logic; an authored pivot is not a finished interaction.

Store state through the project's established save model after auditing it. Define stable IDs, initial states, reset behavior and obstruction/retry behavior. At minimum verify a fresh launch starts in the intended closed/access-ready state. If persistent open states are supported, test save/load explicitly. Do not claim persistence from editor-map saving alone.

Emergency power remains for refuge lighting, communications and heat; it must not become a gondola-drive dependency as an accidental consequence of this import. Full power/parcel/rescue puzzles should be a later bounded design and implementation step.

## 6. Validate the complete playable checkpoint

- Verify all manifest members, hashes, actor/component transforms, material dependencies, pivots and declared replacements after map save/reopen. Check untouched actors and foliage against the fresh baseline.
- Convert the seven Blender routes into engine tests, adding each doorway, janitor reach point, cabinet approach and both entrance leaves. Use the actual runtime capsule; previous lodge checks used radius 34 cm and half-height 96 cm, while the Blender dressing probes used a shorter approximate envelope. Read current dimensions rather than copying either blindly.
- Walk the ramp, upper steps, lower stair and wrap loop both ways; turn at landings; test near rails and with relevant doors/storage open. Include stretcher clearance as geometry handling evidence separately from player walking.
- Exercise E focus, open/close, latch behavior, obstruction and retry on every new mechanism. Re-run affected old lodge door/cabinet tests, particularly if shared C++ changed.
- Review neutral lighting and actual weather/night/torch gameplay. Capture close and glancing views on both sides of each unique door/window, roof/exhaust junction, floor seam and stair connection. For suspected flicker, capture a short sequence with slight viewpoint movement, waiting for each screenshot to finish.
- Extend acoustic zones only where necessary; compare generator-room, porch, rescue and lodge transitions. Keep generator ambience tied to a defined state if implemented, not permanently layered over existing station audio by accident.
- Profile matching before/after views on the same machine/settings: game/render/GPU frame time, draw calls, texture residency and collision/interaction cost. Establish the platform/frame budget from the existing project baseline before using a hard threshold. Investigate regressions; no fabricated FPS guarantee.
- Cook/package a development build and launch it through the intended entry flow. Verify asset references, fonts/textures, native classes, collision, interactions and representative routes outside PIE.

Deliver `verification.json`, `runtime.json`, visual review images, `performance.json`, cook/launch results, and a final dependency/replacement ledger. A successful import alone does not close this phase.

## 7. Promote and retain rollback

Once the migration checkpoint passes, make a concrete promotion change set that accounts for all current R12-only work. Reconcile the current live map against the recorded baseline; do not replace a newer R12 map with an older migration snapshot. Trace the actual entry/startup travel logic and update that destination as appropriate; preserve player starts, opening sequence, gondola behavior and story triggers.

Keep the old playable map/checkpoint and asset ledger for rollback. Promotion must include required new content and any runtime code, not only the map file. Reopen and launch the promoted result, repeat critical arrival/lodge/control/west-services routes, and record the delivered commit/checkpoint. No promotion or config changes are part of this planning task.

## Execution order and checkpoints

1. Baseline + source/terrain audit → agreed exact transfer inventory.
2. Export/import orientation probe → proven coordinate and pivot contract.
3. Shared shell/platform/ground → walkable compound checkpoint.
4. Materials + three rooms + dressing → visual-fidelity checkpoint.
5. Mechanisms and sound integration → interaction checkpoint.
6. Combined reopen/runtime/performance/cook checks → release candidate.
7. Reconcile and promote → normal-game delivery.

The first implementation session should stop at the walkable compound checkpoint only if a real issue prevents progress; otherwise proceed through these gates. Each phase is resumable from manifests and produces a reviewable result. Keep a single integration owner for placement, terrain and replacements even if room export work is later delegated. No new tasks have been dispatched by this plan.

## Evidence and implementation references

- Source and latest dressing: [delivery](../../art/blender/station_dressing_01/delivery.json), [verification](../../art/blender/station_dressing_01/verification.json).
- Combined architecture/interfaces: [west-services README](../../art/blender/west_services_02/README.md) and reconciliation/roof reports in that folder.
- Local migration history: [lodge README](../../art/unreal_handoff/passenger_lodge_01/README.md), [finishing](../../art/unreal_handoff/passenger_lodge_01/finishing/README.md), [later east wall](../../art/unreal_handoff/passenger_lodge_01/east_wall/README.md).
- Proven pipeline entry points: `art/unreal_handoff/passenger_lodge_01/scripts/export_shell.py`, `import_shell.py`, `export_kitchen.py`, `install_kitchen.py`, `session.py` and the matching verification/runtime scripts. Adapt their map guards and manifests deliberately; do not replay initialization over a completed checkpoint.
- Geometry and interaction failure history: [mesh authoring lessons](../../art/MESH_AUTHORING.md).
- Epic's [FBX static mesh pipeline](https://dev.epicgames.com/documentation/unreal-engine/fbx-static-mesh-pipeline-in-unreal-engine) documents the FBX/collision workflow; the site's current default is newer than this project's UE 5.7, so local tested importer behavior takes precedence over assuming new defaults. [Nanite documentation for 5.7](https://dev.epicgames.com/documentation/en-us/unreal-engine/nanite-virtualized-geometry-in-unreal-engine?application_version=5.7) informs per-asset evaluation. No engine upgrade is proposed.

## Implementation record / September 11

Implementation is recorded in [west_services_01](../../art/unreal_handoff/west_services_01/README.md). The expanded migration map is now the configured normal-game destination; R12 remains an unchanged rollback map. That delivery's reports supersede the planning-only and pending statements in this document. The final cleaning-cupboard placeholder replacement was identified through an actual flashlight review and source-owner trace, and is included in its replacement ledger.

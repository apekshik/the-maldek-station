# Handoff 08 — furnish the bare east waiting-hall wall

Build a second, additive wall-detail package in Blender. The user specifically wants more objects on the broad bare wall between the existing visitor map and the locker corner. This is an implementation handoff, not a request for another planning-only response.

## Source and target

- Asset repository: `C:/Users/apek-anna/Developer/the-maldek-station` (the app task's default website checkout is not the asset repository).
- Read `AGENTS.md`, `art/MESH_AUTHORING.md`, and the lodge 04 README. Use `art/blender/passenger_lodge_04/Maldek_Passenger_Lodge_Integrated.blend`, scene `Lodge_Integrated`, as immutable fitted context. This supersedes lodge 03 as this task's fitting source.
- Integrated source SHA256: `bcf7e6301aecedd83688488981fd58a5a9719d685ef975210eef9eeb7f753f6c`, delivered in commit `fdd88f3`.
- User reference: `C:/Users/apek-anna/.codex/attachments/43e360cf-ba01-4126-afb3-c536dae7a55f/Screenshot 2026-09-10 at 9.45.21 AM.png`. The same camera context is `art/blender/passenger_lodge_04/previews/03_Hall.png`.
- Target is the long EAST interior wall, facing into the hall along -X, approximately world X=-10.28. The existing visitor map is centred near world Y=0.40, Z=5.68; the locker bank occupies the rear corner near Y=-7. Do not confuse this wall with the west wall that already has three posters and a community board. Survey actual evaluated faces and bounds before positioning.
- Metres, Z up, floor Z=4; preserve all current furniture, openings, control room and station layout.

## Design and inventory

Make this wall feel used by ordinary skiers and waiting passengers in the early 1990s. Add a mixed cluster of real objects, rather than another row of identical posters. Use cream enamel, petrol paint, aged pine, galvanized brackets, paper and modest glass reflections. Keep the existing visitor map legible and separate from new pieces.

Build these six primary assemblies in the currently bare run, generally Y=-1 to -5.7, fitting their final spacing to the surveyed map/locker bounds:

1. One framed illustrated ski-safety / mountain etiquette panel, approximately 0.70 × 0.95 m. Short, readable ordinary visitor guidance; no new puzzle or invented operational rules affecting gameplay.
2. Two separately framed archival station/mountain photographs or original monochrome illustrations, each approximately 0.55 × 0.40 m. Slightly stagger them as a paired group; use modest caption plates without inventing a canonical date or named historical event.
3. One shallow wall-mounted leaflet rack, approximately 0.45 × 0.60 m, maximum projection 0.16 m. Model folded leaflets, pocket lips, fasteners and a few unevenly depleted stacks. Aim for an accessible mounting height; verify approach around the existing benches.
4. One small analog thermometer/hygrometer in a period enamel or timber housing, approximately 0.22 × 0.35 m. Model the gauge face, needle, glass, rim and fixings. Static dressing only; no live weather logic.
5. One compact labelled FIRST AID wall cabinet near the locker end of the run, approximately 0.38 × 0.45 × 0.14 m. Credible sheet-metal returns, hinged leaf, latch and mounting hardware; keep its leaf separately pivoted for future use. Do not add contents, keys, collectibles or gameplay logic.

These are six assemblies because the two archival pictures are separate. Lay them out as two or three related clusters with roughly 150–250 mm breathing room where feasible. Use multiple mounting heights and shallow depth to break up the empty expanse. Leave upper wall/ceiling and some wall between groups visible; aim to occupy approximately one third of the currently blank useful display band, not every surface. Do not add another clock, visitor map, timetable or full community noticeboard. Do not place new objects on locker leaves or over existing signage.

## Ownership and construction

- Output only to `art/blender/passenger_lodge_wall_details_02/`. Collection `PLG2_East_Wall_Details`, object prefix `PLG2_`. Keep the previous wall package and integrated master unchanged.
- Deliver both an asset-only blend and an independent fitted review blend based on lodge 04. Append only the new collection for review; source context and temporary lights must be clearly excluded from delivery.
- Model visible frame thickness, backboards, mounting brackets, screw heads, paper edges/folds and controlled wear. One owner per visible surface; no coplanar overlay or wall penetration except deliberate concealed fasteners.
- Preserve existing trim. Place objects clear of it or use physically sensible mounting stand-offs; if a trim change is unavoidable, document an exact local patch proposal instead of editing the master.
- Keep new projections out of seating/locker/door approach envelopes. Use the integrated 340 mm radius, 1.8 m high walking envelope for checks. Avoid hook rails or protruding ski equipment behind seated passengers in this pass.
- Read the original wall-art handoff for artwork/provenance expectations. Original editable vector artwork is suitable for lettering and diagrams. Use online references with recorded sources/licenses; any downloaded image needs suitable reuse rights. If generated illustration is helpful, use the existing protected FAL credential workflow only; never paste credentials into scripts, messages or commits. Do not block the package on generation access: original illustrations are an acceptable fallback. Keep all text editable and deterministic.
- No Unreal import, main-master reconciliation, interaction code, clue changes or changes to other packages in this handoff.

## Delivery and acceptance

1. A fitted wall-elevation sheet showing the existing map, new assemblies, trim and locker corner with measurements.
2. Detailed editable meshes, packed textures, editable artwork, provenance and an additive placement manifest with exact world matrices, material slots, pivots and source hash. Replacement list should be empty unless explicitly justified for a local integration issue.
3. Before/after from the user's hall angle, a straight wall elevation, an oblique walking view, near views of the cabinet/rack/gauge and one dim warm review. Include existing seating so projection and scale are assessable.
4. Saved/reopened checks for evaluated mesh topology, mounting separation, packed images, readable text, cabinet-leaf sweep and combined circulation against the integrated scene. Distinguish Blender checks from actual engine tests.
5. README with assembly inventory, verification results and exact append instructions. Commit and push only this new package from an isolated asset checkout/branch; preserve unrelated changes. Report completion back with the package location and review images. Do not overwrite the lodge 04 master.

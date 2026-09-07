# Architecture redesign 02

Open `Maldek_Architecture_Redesign.blend`. This is a separate editable Blender design study; it does not overwrite revision 01 or any Unreal level.

## This pass

- Control room enlarged from 5 × 4 m to 5.8 × 5.2 m (30.16 m²). Front instruments remain beside the viewing window. Rear cabinets, cable trays, workbench and maintenance noticeboard make use of the added space.
- Upper living/radio room: 6.1 × 4 m (24.4 m²), floor 3.35 m above the control floor, 2.65 m nominal shell height. Includes a bed, pillow and blanket, bedside storage, wardrobe, writing/radio desk, microphone, logbook, chair, manuals and a pinboard. Furniture and instruments are modest geometry studies, not final hero props.
- The upper room projects 0.7 m beyond the control-room side. Transfer beams, bolted plates and knee brackets express the support arrangement; this is visual design, not an engineered structural claim.
- Rear external stair: 20 risers at 167.5 mm, 280 mm goings and 1.25 m tread width. The rear bypass walkway permits an approach to the stair foot without walking beneath the low end of the flight. Top landing turns into the rear upper doorway.
- Platforms alternate open framed grating and mostly flat steel plates. Bolts appear at panel corners, retaining clips, rail feet and structural connections. Stair nosings carry restrained yellow markings.
- Matching shell/interior studies for the 9.8 × 7.8 m waiting hall, 6 × 8 m generator room, 3 × 5 m workshop and 4 × 4 m relay hut. Waiting benches, timetable board, ticket counter, generator housings, workshop storage and relay racks establish each room's function.

Collections separate the control room, upper room, decks/stair, waiting hall, maintenance buildings and relay hut. Cameras provide the front exterior, rear stair, upper interior, building family and control interior. All five PNG views are in `renders/`.

## Review corrections

Corrected outward cladding orientation on back/left walls, extended the upper landing toward the doorway, connected its supporting posts to the deck, removed standing seams beneath the upstairs floor, kept base framing out of doorways, and moved the upper shelf away from the entrance route. Interior camera positions were reviewed visually.

`access_verification.json` records sampled stair elevations, vertical headroom, upper/lower door passages, upper floor surfaces and landing support contact. These checks are not continuous capsule sweeps. `design_manifest.json` records dimensions and openings.

## Integration boundary

The maintenance and relay positions are spaced for presentation, not final level placement. The control/hall enlargement, rear access route and upper-room silhouette must be reconciled with the evolving station map and gondola sightlines. The drive-gallery redesign, wider terrain/platform connections and full station replacement remain subsequent work. This file has no new Unreal import or game collision export; revision 01's FBX is not an export of this redesign. Blender procedural materials still need an Unreal equivalent or baking.

The existing concrete scan is packed into the file. Painted metal, steel, fabric and other finishes remain editable procedural materials. No external assets were purchased.

## Reproduce

Run `scripts/build_redesign.py` using factory-startup background Blender. It reuses construction helpers from `../visual_fidelity_01/scripts/build_sample.py` and creates only this revision. Then run `scripts/verify_access.py` against the saved redesign. Existing source files and maps are not opened for modification.

# Handoff 7 — wall displays, maps, posters and passenger information

Implement this package after reading [shared-contract.md](shared-contract.md) and `docs/design/passenger-cabin.md`. This package includes both Blender display meshes and the artwork they carry.

Output: `art/blender/passenger_lodge_wall_details_01/`; asset collection prefix: `PLG_`. Keep editable artwork, final textures, references and provenance within this package directory.

## Purpose and placement

Make the lodge feel like a former public waiting room at an early-1990s ski station: useful visitor information, local outings, ordinary notices and traces of daily use. Avoid a wall of ominous messages. Preserve blank space for future evidence and leave roughly half the community noticeboard available.

Start with a wall-elevation placement sheet and a fitted Blender overview. Inspect the current material master and its actual available wall faces, windows, doors, lockers and counter. The three `FIT_Poster_frame_*` proxies mark the intended west-wall poster zone; keep the locker bank on its approved rear wall. Preserve door swings, frame reveals, queue space, the screened restroom approach and seated headroom. Group displays into a few readable clusters rather than covering every wall.

Use this initial inventory, adjusting physical sizes to the surveyed wall space:

- Three framed period ski/travel posters in the west-wall display zone.
- One visitor route/piste map with legend and clear station identification.
- One gondola timetable and operating-information case near the platform exit, readable before boarding.
- One community noticeboard with four to six ordinary pinned items: local ski-club notice, lost property, opening hours, event or excursion notice, and a modest weather cancellation.
- Static wayfinding for restrooms, the public exit and staff-only access, positioned on fixed walls or headers so it does not require editing another task's door leaf.
- A coordinated menu artwork panel for the kitchen's display frame, plus a small lost-property information label beside its cubby.
- One simple analog wall clock and one restrained coat-hook strip if the surveyed wall space supports them. Keep hooks away from the stair/door routes; omit them rather than crowding circulation.

The visitor map must derive the station diagram from the approved layout. Show the lodge, exterior route to control's independent entrance, gondola/platform and relevant public approaches accurately. Do not draw a direct internal connection to control. Any wider mountain/piste geography not established in the project must be clearly treated as proposed fiction, not asserted canon. Verify established place names before typesetting them.

## Ownership with other packages

Own poster frames, map/timetable cases, noticeboard, mounting hardware, fixed-wall sign plaques, clock and coat hooks. Own final artwork for those surfaces.

The kitchen task owns the physical menu-board frame, counter and lost-property cubby; this task supplies correctly sized artwork/labels and a placement manifest for them. Read its delivered manifest if available; otherwise provide a provisional size that can be adapted and label the dependency. Do not build a second kitchen frame or change the counter.

The restroom task owns fixtures, mirrors, dispensers and bathroom door hardware. This task owns fixed-wall directional/identification signage only. The locker task retains number plates 01–12 and all locker-attached hardware. The windows task retains window frames/glazing. Do not duplicate these assets.

Inspect legacy source signage before placement. Interior review renders reveal an old reversed `MALDEK / ARRIVALS` label near the ceiling. Locate its exact object and provide an explicit retire/replace recommendation in the integration manifest; do not merely cover it with a new sign or delete objects by a broad name match. Source master remains untouched.

## Artwork and modeled construction

Model credible thin frames, backboards, glazing where suitable, paper thickness, mounting brackets, pins/clips and controlled edge curl. Use a few subtle overlapping notices with physically separated surfaces; avoid coplanar decals/paper that will flicker. Give glazed cases sensible roughness and glass thickness so reflections do not hide all information. Wear should follow handling, pin holes, sun exposure and edges rather than uniform dirt.

Keep critical writing as editable SVG/text or another deterministic typeset source: titles, timetable rows, map labels, menu names, locker references and any clue wording. Raster illustrations can supply decorative art underneath. Do not rely on generated text for anything the player must read. Export separate front-on textures with consistent margins and adequate resolution for inspection-distance views; document texture sizes, UV placement and texel density. Bake no scene lighting or frame shadows into flat artwork.

The user previously authorized FAL artwork generation. Unlike the mesh-only packages, this package may use it when useful. Consult the existing secure credential workflow described in `docs/design/passenger-cabin.md`; verify availability without printing or copying the credential. Do not put secrets in this package or browser code. Verify current model endpoint names and capabilities before using them; the user's phrase “GPT Image 2.5” is not evidence of an available endpoint. Prefer the already documented Nano Banana Pro workflow if suitable, or supported tooling available in the task. If unavailable, continue with original vector/typeset artwork rather than blocking the mesh work.

Use original illustrations or appropriately licensed reference-derived assets; record source URLs, license/attribution requirements, generation model/prompt and output provenance as applicable. Avoid real brand logos or unsupported real-world operating claims. The warm cream, pine green, petrol blue and ochre palette should fit the station without making every display visually identical.

## Story and interaction boundaries

Read the proposed first-clue chain in `docs/design/passenger-cabin.md`. Support its ordinary timetable/lost-property context without adding another cipher or changing the ticket/key/locker association. The ticket, key, bag and locker contents are not owned by this wall package. Preserve proposed critical wording exactly if it is reproduced; identify unresolved currency, dates, prices and geography as editorial choices in the manifest rather than inventing a new progression requirement.

Keep inspectable candidates separate with stable names and sensible origins, but do not implement interaction code, journal entries or mandatory clues. No Unreal import. Static timetable/clock dressing does not become a live gondola-status system; the existing status sign remains independent.

## Deliverables

Deliver the standalone Blender collection, fitted review copy, placement/replacement manifest, editable artwork and final textures, artwork/provenance inventory, and reproducible scripts where appropriate. Record display dimensions, mounting heights, material slots, UVs, texture filenames and exact source proxy/legacy objects to replace.

Render the west-wall cluster, map/timetable close-ups, the noticeboard, restroom wayfinding, and a full-hall eye-height view. Include normal walking-distance and close inspection-distance views to assess visual hierarchy and spelling. Review readability under neutral and dim warm lighting; clearly label temporary review lights. Verify saved/reopened geometry, surface separation, intended text content and clearance from all openings. Supply a short editorial list of provisional text or geography for later review.

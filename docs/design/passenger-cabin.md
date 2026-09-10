# Former passenger cabin — proposal 01

September 9, 2026 · For layout review; no Blender or Unreal changes in this pass.

Review the [interactive floor plan](../passenger-cabin.html). This proposal replaces the old Waiting Hall brief, not the gondola vehicle or central control. The older V2 compound map remains contextual rather than a surveyed R12 footprint.

## Shape and relationship to the station

A modest L-shaped timber lodge at the public platform level (+4 m in the station design baseline). A 14 × 8 m main room and a 6 × 6 m rear wing form a 148 m² gross footprint within a 14 × 14 m envelope. Dimensions include the schematic wall envelope, not guaranteed usable floor area. The missing 8 × 6 m corner forms a sheltered arrival court. Orient the broad windows toward the platform; put the restroom/service extension away from the dock. Keep central control adjacent and retain the hall–platform–control circulation loop.

The review diagram uses local coordinates, not Unreal world axes. Survey the current waiting hall, control openings, upper quarters supports, terrain, roof sign sightline and platform clearance in Blender before freezing the footprint. Expansion must not overwrite the drive gallery, quarters or retained access routes. Prefer expanding toward the arrival side; shorten the wing if the survey requires it.

## Room and furniture schedule

| Area | Planned contents | Placement / use |
|---|---|---|
| Waiting room, 14 × 8 m gross | 4 timber picnic tables, 8 matching benches, 24 nominal seats | Two pairs flanking a clear central route; table tops 1.8 × 0.8 m, complete bench envelope about 1.8 × 1.9 m |
| Lockers | 12 full-height doors, two banks of 6 | West wall; about 3.6 m total run, 0.5 m deep; keep 1.5 m clear in front |
| Coffee service | One 3 m counter, one 3 m back counter, 3 shelves, undercounter fridge, sink, kettle, filter-coffee urn, till, tray and snack display | Southwest of waiting room, near wing plumbing; staff aisle target 1.1 m; counter queue outside central route |
| Women's restroom, 3 × 4 m gross | 2 WC cubicles, 1 basin, mirror, dispenser and bin | Rear wing; entry off shared lobby, no direct toilet view from seating |
| Men's restroom, 3 × 4 m gross | 1 WC cubicle, 1 urinal with screen, 1 basin, mirror, dispenser and bin | Shares plumbing wall with women's room |
| Restroom lobby, 6 × 2 m gross | Direction signs, cleaning cupboard and access to both rooms | Short perpendicular turn for privacy; exact fixture clearances resolved in blockout |
| Arrival court, 8 × 6 m open notch | Boot scraper, covered entrance, 2 ski racks and umbrella stand | Keep public approach and exterior route to platform continuous |
| Information / lost property | 1 timetable case, 1 community noticeboard, 1 menu board, 1 lost-property cubby | Timetable on platform exit route; cubby at counter end |

No office desks: central control already has the operator's desk. Add two window benches only if the blockout demonstrates spare space; they are not part of the baseline count.

Design circulation targets: 1.5 m central path, 1.2 m secondary passages, 1.2 m clear main doors, 0.9 m restroom doors, 2.4 m minimum clear interior height. These are game-layout targets, not an architectural compliance claim. Draw actual door sweeps, pulled-out bench envelopes and open locker doors in Blender. Main entrance is at the south edge of the waiting room beside the wing; platform exit is on the north wall. A separate east connection maintains access toward control.

## Everyday life and exploration

Warm pine boards, worn varnish, cream plaster above dark timber wainscot, dull petrol enamel lockers, brass labels, brown quarry tile at wet thresholds and cream restroom tile. Use the established frosted upper door glass and sharp warm-gold double borders for inspection UI. Exposed roof beams, patched seat corners, cup rings and a radiator establish age without covering everything in decay. Window light, modest amber pendants and muffled machinery give this room a different mood from the platform.

Four authored inspections, proposed rather than implemented:

1. **Lost-property claim ticket at the counter:** “Blue day bag · locker 07 · spare key with attendant.” Clear first clue, readable at inspection distance and retained in the journal.
2. **Key tag 07 in the attendant's open cubby:** available without a prerequisite. Use the existing insert-and-turn interaction to open locker 07. This teaches observation, object association and a physical action without changing control/relay's temporary 1234 code.
3. **Locker 07's day bag:** ordinary lift pass and folded visitor map. The map identifies the route to central control; it is a tutorial payoff, not a new mandatory lock on progression. Later narrative evidence can replace one insert after story review.
4. **Annotated timetable:** an ordinary weather cancellation and tea-stained corner establish working life. Optional inspection, no cipher and no ominous warning.

Keep the critical ticket and key reachable on every visit; reopening the locker remains possible. No random placement, missable consumption or requirement to interpret generated text. Proposed inventory association is later implementation work: current ordinary doors do not yet require finding a key.

Supporting set dressing: 6 cups plus 2 saucers, 1 kettle, 1 coffee urn, 3 drinks cartons/bottle variants, 2 snack package variants, sugar tin, spoon jar, tea tin, cleaning cloth, mop/bucket, radiator, coat hooks, a single lost glove and folded scarf. Dress two tables lightly and leave two mostly clear. Reserve one shelf bay, one locker and half the noticeboard for later evidence. Use ordinary ski-club notices, opening hours and a staff cleaning rota; no wall of threatening messages.

## Blender build order

1. Site survey and dimensioned L-shaped blockout. Review human eye-height arrival, seating, counter, restroom doors, control connection and gondola/sign visibility. Establish separate public/staff paths before detailing.
2. Shell kit: floor, wall layers, window/door openings, L roof junction and gutter, beams, covered entrance and wet-room partitions. Apply `art/MESH_AUTHORING.md`: single surface owners, openings through every layer, no retained wall behind replacement geometry.
3. Furniture kit: one picnic-table master, one bench master with restrained variants, modular locker bank with separately pivoted doors, counter/back counter, shelves and cubby.
4. Hero pieces: rounded key bow/tag, ticket, bag, timetable case, detailed kettle and coffee equipment. Kettle is real Blender geometry, including spout, handle and lid; images supply labels/artwork only.
5. Restroom fixture kit and utility details, then restrained material wear and supporting props. Author interaction pivots, collision and readable labels independently of decorative textures.
6. Review saved/reopened Blender in neutral, night and glancing views. Only then integrate as an explicit replacement set in Unreal, preserve station systems, test walkthrough/door/locker clearances and nighttime clue legibility, and capture review shots.

## Generated artwork plan

FAL credential is stored outside the repository in `%LOCALAPPDATA%/MaldekStation/Secrets/fal-key.dpapi`, encrypted for the current Windows user. Never place credentials in HTML, source, prompts, manifests or browser requests. Future tooling must decrypt only inside a local generation process and avoid printing headers.

Use `fal-ai/nano-banana-pro` for decorative raster artwork. FAL currently lists `openai/gpt-image-2`; the requested name “GPT Image 2.5” has not been verified and is not a configured endpoint. Sources: [Nano Banana Pro API](https://fal.ai/docs/model-api-reference/image-generation-api/nano-banana-pro), [FAL model catalog](https://fal.ai/explore/search). No paid generation was run for this layout pass.

First artwork batch after layout review: one period ski travel illustration, two ordinary community notice illustrations, one snack/drinks label sheet. Request flat front-on artwork without scene lighting, frame or baked shadows; muted pine green, ochre and cream, early-1990s regional ski stop. Build final menu, prices, timetable, locker numbers and clue wording as editable typesetting over the artwork, so they remain exact and readable. Final currency, prices and dates remain to be set from story geography.

Retain model ID, prompt, seed if supplied, output dimensions and local asset path in an asset manifest; inspect spelling, artifacts and unwanted trademarks before use. Make mesh UVs/decals from reviewed images, never use a generated kettle picture as a substitute for its modeled form.

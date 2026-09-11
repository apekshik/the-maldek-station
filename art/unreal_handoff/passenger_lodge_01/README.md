# Passenger lodge migration — site fit

Work in `/Game/MaldekRefinement/PassengerLodge/Station_Lodge_Migration`.
The live `/Game/MaldekRefinement/R12/Station_R12` remains unchanged against
the SHA-256 recorded in `before.json`. Do not promote this pilot over it.

## Implemented checkpoint

- Duplicate of the current saved station, preserving all 1,063 actor transforms.
- 28 shell chunks from the integrated Blender lodge, with approved wall cuts,
  roof, cladding and trim. Bounds checked in Unreal against source metres.
- 58 deck chunks: actual open grating, expanded western promenade, guards,
  shifted sideways arrival and second bypass stair. Exact replacement lists:
  `shell_install.json` (15 old hall components) and `deck_replacements.json`
  (117 original deck, guard, structure and sideways-arrival components).
- A separate ground asset extending the western shoulder beneath the new deck,
  and a narrow recess for the bypass descent. 869 mesh vertices change; all
  vertices outside the two explicit masks stay unchanged. Source gorge mesh and
  Blender file are preserved. Native terrain beneath the recess changes only
  28 height values in one component, with texture ownership and readback checks.
- Eight shrubs relocated to nearby exterior ground, with no deletion. Their
  before/after coordinates are recorded in `vegetation_moves.json`. The closest
  relocated shrub is over 9 m from the documented arrival-path samples.

The underlying Landscape alone is not the playable ground here. The baseline
survey initially exposed the deep Landscape under the station; `ground_survey`
correctly includes `VF10_Parking_Terrain` and `VF10_Parking_Ground` as well.
Do not infer a 20 m unsupported stair from Landscape-only samples.

## Verification and limits

- Original map file hash unchanged; 929 retained actor component sets checked;
  no unexpected baseline actor transform or static-mesh changes.
- All imported geometry bounds agree within 0.2 cm; material slot labels retain
  source order (FBX sanitization only).
- 72 terrain probes across the bypass treads pass, including near both sides.
- 280 clearance/support samples pass on entry, west promenade, public platform
  and bypass using radius 34 cm and half-height 96 cm. These are editor collision
  queries, not actual character movement. The current cleanup check excludes no
  actors; the two obsolete hall doors have now been removed.
- `reopen_verification.json` records the persistence check after a full map switch.
- `playtest.json` records actual player movement up and down both stairs, including
  the top landing turns. All four tests passed with the runtime capsule dimensions.
- `previews/` contains unlit site-geometry views with existing weather. These are
  provisional color materials, not the finished Blender material migration.

## Remaining migration

1. Continue extended approach continuity review as detailed assets are installed.
2. Bake/translate the remaining furnishing materials, preserving UVs, surface
   ownership and glass treatment; integrate accumulated snow/wetness as appropriate.
3. Import the five remaining detailed furnishing packages with shared meshes/instances;
   keep every moving assembly pivot and exclude reference buildings.
4. Configure public/staff doors, bathroom doors/stalls, lockers and kitchen
   mechanisms, reusing existing interaction presentation and recorded audio.
5. Neutral/night/torch review, save/load, collision and gameplay regressions,
   performance checks, and only then promote the reviewed replacement into R12.

## Reproduction

Run `scripts/session.py` in the Unreal Python console for bounded local job
dispatch. Each request names a script in this directory; responses are local
JSON files. Survey and duplicate scripts reject the wrong map/state. Blender
exports run in background against immutable sources; `export_shell.py -- --deck`
exports circulation. `import_shell.py` accepts `kind: Shell` or `kind: Deck`.

`site_shape.py` defines the two soil masks. `export_ground.py` creates the
separate editable ground copy. `native_ground.py` checks duplicate-map heightmap
ownership, rejects stale data and reads back the patch. The editor plugin allows
only R12 and this exact migration map and requires each map to own its textures.
Its module-only Development Editor build passed during this checkpoint.

The vegetation retry script restores only its eight named actors from baseline
before retrying a partially completed move. Normal successful runs reject replay.
Do not rerun duplicate or vegetation initialization over a completed checkpoint.

## Perimeter and obsolete hall cleanup

The cleanup remains confined to the migration map. `cleanup_report.json` records
every removal and move; `cleanup_baseline.json` preserves the preceding actor
state. Run `cleanup_apply.py` only on the pre-cleanup checkpoint: it rejects replay.

- Relocated nine native pines, seven native grass clumps and one alder away from
  the expanded deck and arrival turn, placing their bases against actual ground.
- Shifted three station-side cordon trees and their wraps away from the arrival
  flight; five ribbon endpoints follow them. The main crossing anchors remain fixed.
- Moved six west-edge marker components to the new guard line.
- Removed exactly eight obsolete hall actors: two doors, the former entry light,
  and five transferred fitting assemblies containing old conduit, guttering,
  hardware and lettering. Independent control-room details are retained.

`cleanup_verification.json` supersedes the initial site-fit preservation report:
1,128 untouched actors plus 13 deliberately moved actors survive reopening, all
eight removals persist, and all 280 route samples pass. The native foliage
checkpoint verifies all 4,556 instance positions persist across the map switch;
the 16 moved instances also match the explicit change ledger. This is a
post-cleanup persistence checkpoint, not an independent pre-cleanup foliage audit.
`playtest.json` records all four post-cleanup actual-character stair traversals
passing. `foliage_audit_after.json` contains zero remaining native foliage bounds
overlaps with the documented lodge/deck review box. The module-only Development
Editor rebuild of StationMigrationTools passed after adding this exact migration
map to the native foliage-move allowlist.

Seven matching before/after views in `previews/cleanup_before` and
`previews/cleanup_after` cover the arrival flight, top turn, west and north deck,
both interior directions and bypass stair. They use Unlit for geometry review;
materials and furnishings are still at the provisional migration stage.

## Fitted windows and surface checkpoint

The shell/deck now use migration-owned finishes instead of pilot colors, and both
approved fixed windows are installed. See `windows/README.md` for material
translation choices, exact grouping, provenance and reproduction. The existing
4K plaster maps, cream/green dado, quarry tiles and Blender-baked station metals
are connected in Unreal. The window export contains 132 source components in 14
actors; the inner and frosted outer panes remain separate.

Current review evidence is in `previews/surfaces` (Lit neutral review) and
`previews/surfaces_night` (actual PIE flashlight views). Prior cleanup images above
remain historical Unlit geometry evidence. `surface_verification.json` and
`surface_playtest.json` cover the updated checkpoint. Public/staff doors,
restrooms, kitchen, seating, lockers and wall dressing are still pending import;
their source hierarchies and demonstration actions remain preserved in Blender.

## Seating checkpoint

All six detailed tables and twelve benches are now installed at their approved
780/480 mm heights and original positions. The 559 source pieces are exported as
six static assemblies with baked wood, end grain and hardware finishes. See
`seating/README.md` for grouping, texture provenance, fidelity limits and exact
reproduction. `seating/verification.json` records saved/reopened fit, dependencies,
219 interior clearance samples and 280 perimeter samples. Player traversal and
neutral/nighttime images have their own seating reports and preview folders.
The earlier surface-only images remain historical evidence. Doors, restrooms,
kitchen, lockers and wall displays are still pending import and interaction work.

## Public and staff door checkpoint

The three fitted keyed doors are now installed with separate levers, lock plugs,
latches and bottom seals. The existing angled key-drag interaction, recorded
turning/opening/closing sounds and obstruction-aware swings drive these authored
components. See `doors/README.md`, its installation and verification reports,
and neutral/nighttime previews. All three passed actual player traversal and
key interaction tests. The map saves with them closed and the keys available.
Restrooms, kitchen, lockers and wall displays remain pending; earlier reports
above describe their respective historical checkpoints.

## Restroom checkpoint

Both restrooms are furnished with the PLR package, including two entrance doors,
three cubicles with usable privacy bolts/indicators, three toilets, two basins,
urinal and supporting fixtures. See `restrooms/README.md` for source grouping,
controls, material translation and reproducible verification. The saved state is
closed and vacant. The screened hallway and existing building footprint remain.
Kitchen, lockers and wall displays are the remaining package imports.

## Kitchen checkpoint

The weathered coffee annex package is installed with fifteen independent cabinet,
drawer and appliance-door mechanisms. Press E on a front to open/close it; blocked
movement stops and can be retried. The existing staff door, service hatch and
building geometry are preserved. Sinks, beverage equipment and other appliance
functions remain decorative. See `kitchen/README.md` for collision repairs,
material translation, tests and reproduction; neutral/night reviews are in the
matching preview folders. Lockers and wall displays remain pending imports.

## Lockers and wall displays checkpoint

The last two delivered packages are installed: twelve usable lockers with
separate lock cams, and the complete delivered wall display collection, including
the coffee menu and lost-property insert. All seven packages are now represented
in the isolated migration map. See `finishing/README.md` for controls, provenance,
material translation, combined validation and remaining narrative scope. Previous
pending-package lists above describe historical checkpoints. R12 remains the
original map; promotion and a performance/cooking pass are separate steps.

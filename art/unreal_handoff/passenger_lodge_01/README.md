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
  queries, not actual character movement. They explicitly ignore the two obsolete
  hall doors, which remain pending functional replacement.
- `reopen_verification.json` records the persistence check after a full map switch.
- `playtest.json` records actual player movement up and down both stairs, including
  the top landing turns. All four tests passed with the runtime capsule dimensions.
- `previews/` contains unlit site-geometry views with existing weather. These are
  provisional color materials, not the finished Blender material migration.

## Remaining migration

1. Extended approach continuity and a check of remaining old hall foundations,
   fittings and obsolete door actors.
2. Bake/translate the detailed materials, preserving UVs, surface ownership and
   glass treatment. Replace the provisional ShellPilot/DeckPilot finishes.
3. Import the seven detailed furnishing packages with shared meshes/instances;
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

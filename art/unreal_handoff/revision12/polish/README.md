# R12 walking and torch polish

The window-sill and doorway bands were a hardware-Lumen geometry mismatch. The visible Nanite trim was much more detailed than its automatically simplified tracing fallback. The waiting-hall assembly traced against 1,794 triangles instead of its 42,296 source triangles. Disabling hardware Lumen removed the defect in an isolated comparison; disabling torch shadows or hiding glass did not.

Seventeen assemblies containing door/window trim now explicitly request 100% fallback triangles (444,428 source triangles; 444,350 after Unreal's build). Nanite remains enabled for their visible geometry. Collision, source geometry, station layout, terrain, weather and global lighting settings are unchanged by this repair. The import manifest and importer preserve this setting on reimport. `trim_fallback_repair.json` records actual rebuilt triangle counts; `shadow_close` and `shadow_final` contain the before/after evidence. Earlier `shadow_repaired` and `fallback_auto_trial.json` record an ineffective Auto-target trial, not the final fix.

Epic documents the distinction between Nanite geometry and its fallback representation: [Nanite technical details](https://dev.epicgames.com/documentation/en-us/unreal-engine/nanite-technical-details). The controlled scene comparisons establish its relevance here.

## Player controls

- **F:** toggle the flashlight.
- **Wheel up:** smoothly tighten the beam and extend its attenuation range.
- **Wheel down:** widen the beam for nearby surfaces.
- **Hold Shift:** sprint indefinitely. Release to walk. The stamina widget is collapsed.

The cone interpolates from 34 to 11 degrees and the attenuation cutoff from 18 to 60 metres. These are light settings, not a claim that every surface is visibly lit at the cutoff. Output stays near the established exposure-compatible intensity while the narrower cone concentrates it. A projected light-function material supplies a soft hotspot, spill, uneven reflector rings and a restrained central variation; the focus parameter also changes the profile. No scene illumination is baked into it. See [Epic light-function documentation](https://dev.epicgames.com/documentation/unreal-engine/using-light-functions-in-unreal-engine).

Walking presentation follows actual grounded speed: restrained vertical bob, lateral sway, held-tool lag and a small landing response. Running increases cadence and amplitude. The camera settles at rest and motion fades in the air. The collision capsule, aiming input, FOV and movement routes are untouched. `HeadBobScale` on the presentation component can be set to zero for a steady camera.

`torch/Field_Torch.blend` is a separate authored source, with a reproducible builder and FBX export. The 25 cm torch has 10,580 triangles, a ribbed grip, machined bezel, reflector, lens and switch. Its small local bounce light reveals the casing without illuminating the room. Existing hands remain. The approved VF07 Blender source is untouched.

## Assets and reproduction

The playable map remains `/Game/MaldekRefinement/R12/Station_R12`. Its R12-owned game mode now uses `BP_StationWalker_Polished`. Player assets live under `/Game/MaldekRefinement/R12/Player`; the ForestTest Blueprint assets and shared R10 optics are preserved.

1. Build the Development Editor target after pulling the native changes, then open `game/game.uproject` and Station_R12.
2. The source mesh is generated with Blender background execution of `scripts/polish_build_torch.py`.
3. Editor scripts `polish_fix_trim_fallbacks.py` and `polish_setup_player.py` rebuild the repair and player assets. Run with no PIE session. The standard R12 local dispatcher supports these scripts.
4. Run `polish_validate_player.py` for real F/wheel/Shift input and a 35-second sustained running test. `validate_behaviors.py` accepts `report: polish/behavior_validation.json`; `run_routes.py` accepts a separate report path and route names.
5. Build the packaged default map with `scripts/Build_R12.ps1 -UseDefaultMap -ReportSubdirectory polish`. Smoke-test using `scripts/Smoke_R12.ps1 -UseDefaultMap -ReportSubdirectory polish -ExpectedGameMode BP_StationGameMode_Polished_C -ExpectedPawn BP_StationWalker_Polished_C`.

## Validation evidence

- `player_validation.json`: scroll boundaries and smoothing endpoints, F toggling, focus retention, grounded walking/running, unlimited sprint beyond the old limit, return to walking, bounded bob, faster running cadence, settling and footsteps.
- `behavior_validation.json`: five physical-surface sound sets, ambience, flashlight input and idle/airborne footstep suppression.
- `routes.json`: actual player movement through the affected entrances and stair routes in both directions.
- `optics_review`: wide/mid/focused comparisons in the unchanged night scene; also shows the detailed casing and absence of the stamina display.
- `reference_validation.json`: 1,938 reachable packages, no new missing references, four Blueprints up to date and no shader errors across 242 materials. The five pre-existing Beech authoring references remain documented.
- `performance/performance_capture.json`: six camera averages of 11.52–13.30 ms (about 75–87 FPS) at 2560×1440 output with inherited TSR, without frame generation. GPU averages are 9.34–11.14 ms, about 4–8% above the prior release capture. The intervening saved lighting checkpoint means this is not an isolated measurement of fallback cost.
- `package-default-build.json` and `package-default-smoke.json`: successful Development build and default-map D3D12 startup with the polished game mode, followed by normal exit. `package-default-startup.png` was visually reviewed: detailed torch present, stamina display absent.
- `saved_audit.json`: reopened-editor verification of player defaults, optics, detailed mesh and all 17 persisted fallback builds.

The original migration's performance report remains a separate baseline; this polish does not claim to resolve its previously documented GPU regression. The full fallback repair adds tracing geometry, so its cost is measured rather than assumed free.

The parallel audio task completed a recorded-foley update during final validation. Its 62 waves, source recordings, attribution and packaging entry are preserved with the shared polished pawn. `combined_behavior_validation.json` and `combined_reference_validation.json` verify that integration; the final package is rebuilt with it. Audio-specific evidence is retained in `../recorded_foley_test/`. The movement/visual performance measurements above precede this audio-only handoff.

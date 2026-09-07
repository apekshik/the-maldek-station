# R12 doorframes, stairs, torch and gondola markers

The remaining doorway stripes were coplanar insulated wall cores overlapping the steel jamb and lintel faces. Controlled Nanite/Lumen comparisons reproduced the defect with those rendering paths disabled. The export repair recesses only coincident wall-core faces 4 mm into the core: 42 cores in 12 architectural assemblies. Approved VF07 Blender source, doorway dimensions and authored collision boxes are unchanged. See `core_recess.json`, `source_openings.json`, `ab/` and `after/`.

Stair presentation now uses a critically damped world-height spring, updated after character movement. The camera and held torch share the same correction; walking bob is reduced on steps. Collision still follows individual treads. Teleports, airborne movement and long frames reset the correction, which is bounded relative to MaxStepHeight. `GroundHeightResponse` defaults to 18. Arrival, quarters and internal service stairs passed in both directions with full walking input and no falling frames. `stair_comparison.json` records 84–88% suppression of per-frame height second differences versus the capsule on identical frames. This is a discontinuity measurement, not a physical acceleration or subjective comfort score; quantized clock samples are not used to infer acceleration.

The focused torch endpoint increases from 1.0 to 1.35 lumens (35%); the wide endpoint remains 1.2. Existing cone, range, optical profile, wheel controls and F toggle remain in use.

Ten red lens markers sit on the surveyed gondola roof, grouped into one noncolliding mesh attached to the existing roof actor. Two short-range, non-shadowing lights provide faint spill. The existing gondola transform and controller are preserved. `marker_layout.json` records roof contacts and pivot; `setup.json` records saved settings. The separate Blender marker source and FBX are included.

## Reproduction

1. Run `trim2_source_audit.py` and `trim2_recess_cores.py` with Blender in background from the approved VF07 source. The latter regenerates only the affected FBXs and handoff records, preserving collision mappings.
2. Run the established `import_stage.py` through the R12 dispatcher for Architecture with the exact asset names in `core_recess.json`.
3. Run `trim2_build_markers.py` in Blender, then `trim2_setup.py` through the editor dispatcher to import markers, bind materials and save player/map settings.
4. Build Development Editor. Capture the control jamb from source eye position [-3.25,-0.8,5.65] toward [-2.65,0,6.05]. Run `run_routes.py` with full_speed and camera_trace for the three stair routes in both directions; use `trim2_compare_stairs.py` to analyze the traces.
5. Test wheel focus, F toggle, sustained sprint, idle footsteps and camera settling with `polish_validate_player.py`, output `trim2`, focused_intensity 1.35. The concurrent opening experience remains enabled; test scripts wait for its input hold to finish.

The saved level also retains the concurrent opening/audio work. Old stage acceptance remains historical; the supplementary review and refreshed Architecture audit cover this repair. Package and runtime result JSON files provide the actual validation outcomes. No new full-route GPU benchmark is claimed for this pass.

## Final verification

- Six full-speed stair traversals and eight doorway/boarding traversals passed. Gondola stayed parked.
- Runtime player checks passed, including measured focused intensity 1.35, wheel limits, F toggle, sustained sprint, idle silence and camera settling.
- Development Editor and packaged Development builds passed. Default-map packaged startup passed on D3D12; the startup image was reviewed.
- Reference validation found no new missing references and no material shader errors. Five pre-existing Beech authoring references remain recorded separately.
- The structural audit uses actor identities and transforms read from the untouched `adc092e` map in the verification checkout. Older migration inventory predated user lighting changes and deleted lights; comparing against it would incorrectly flag those edits. Current compiled modules were copied into ignored binary folders only to read this checkpoint.
- A NullRHI attempt at the final editor-specific audit crashed in LevelEditor; the audit was rerun in the reopened interactive editor. The package smoke test did not crash.

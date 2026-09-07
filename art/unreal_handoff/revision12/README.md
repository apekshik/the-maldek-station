# VF07 → Unreal R12 migration

All 328 approved VF07 assemblies are integrated in `/Game/MaldekRefinement/R12/Station_R12`. The map is selected for editor and game startup. See `RELEASE_REVIEW.md` for measured results, reproduction instructions and the explicitly retained GPU performance limitation. The migration history is preserved on `codex/vf07-unreal-r12`; final remote verification is recorded separately.

## Preserved checkpoint

- Before migration, local `main`, remote `main`, the fresh verification checkout and `pre-vf07-unreal-migration` were verified at `d713a3c5e7189bc3c5f59cc12396d3428a84b96c`.
- The remote camera-tour commit was merged without rewriting the existing local history.
- Required LFS objects were uploaded and retrieved in `C:/Users/apek-anna/Developer/maldek-checkpoint-verification`; LFS object/pointer verification passed.
- Approved VF07 SHA-256: `e2ce19363f35f7fbef1860f5d5591e53ccf0b97d989085153b631a82558724dd`.
- Unsaved Blender review edits were captured separately. Original Blender and Unreal revisions remain available.
- Gaea's compatible local vendor plugin is intentionally excluded; see the pre-migration checkpoint dependency report for installation requirements.

## Implemented transfer

- Created `/Game/MaldekRefinement/R12/Station_R12` from the saved forest map and matched all 214 original actor transforms.
- Recorded explicit replacement components and preserved actor identities in `replacement_inventory.json`.
- Exported evaluated, triangulated VF07 assemblies with material slots, metre pivots, source-object lists, bounds, collision groups and SHA-256 hashes in `handoff_manifest.json`.
- Separated the retained parking/car from the old combined arrival mesh. Forest approach remains a separate retained actor.
- Compared the bridge against R11: 221 retained objects are byte-identical in evaluated geometry; two junction footings move 8 cm; the removed pieces belong to the station junction.
- Baked reusable 2K base-color, DirectX normal and ORM textures at an 8-metre repeat, with graph-based deduplication. Surface normals contain the evaluated bump detail; base color contains no scene lighting.
- Built R12 master materials and named instances, separate indoor/exterior weather treatment, explicit texture overrides, and existing footstep physical-material bindings.
- Verified a one-metre asymmetric orientation probe and five real VF07 samples. Imported bounds agree within 0.000031 cm. The player-sized capsule passes the doorway center and stops at both jambs.
- Prepared graded road/apron convex collision following the actual faces, rather than rectangular envelopes around the paths.
- Prepared forest-relative terrain changes and a masked Landscape underlay clearance workflow.
- Accepted the pilot's neutral/night appearance, glass transparency, doorway collision and shader compilation (`pilot/acceptance.json`). Parking material bindings are complete.
- Verified R12-owned Landscape heightmaps. Within the actual VF07 terrain change mask, minimum underlay clearance is 0.837 m; no Landscape height edits are required (`landscape_delta.json`).
- Imported 189 circulation assemblies, including the preserved bridge. The bridge was brought forward because its superseded junction guard blocked the new east terrace.
- Preserved 86 cross-sections of the forest approach exactly, including their UVs, and aligned its final bend to the approved south landing access. The old whole approach component is replaced explicitly, so its obsolete end does not remain underneath.
- Moved the parking PlayerStart one metre clear of the retained car's authored collision. Its class, orientation, capsule and movement settings remain inherited; the exact transform exception is recorded in `actor_adjustments.json`.
- Runtime circulation checks cover all 14 applicable VF07 routes in both directions, plus the entire bridge and parking/forest/arrival connection. Earlier failed east-terrace and forest-end results are superseded by the targeted passing reports; the final full-station results below supersede these intermediate checks.

## Integrated validation

- All three imported stages passed their saved bounds, material, collision and replacement audits after the two export-only numerical repairs.
- All 18 approved VF07 routes passed in both directions. Additional room, water, forest and bridge routes bring the passing total to 54 directional tests (`independent_route_summary.json`).
- The visible gondola stayed stationary throughout those tests. Flashlight input, live ambience, surface-specific footsteps and idle/airborne silence passed (`behavior_validation.json`).
- All six defect views, quarters, lower floor, water terrace and whole station were reviewed in neutral and production night lighting (`final_visual_review.json`). Final water-night images supersede the earlier overexposed trial captures. Temporary inspection lights were removed.
- After reopening, all 138 authoritative foliage instances matched the saved inventory: three clearance adjustments and 135 untouched transforms (`foliage_persistence.json`).
- The Development Editor and game targets compiled successfully; the final explicit-map Development package built and exited normally. Default-map packaging and startup are recorded in `package-default-build.json` and `package-default-smoke.json`.

## Validation and performance status

- Continuous parking-to-station-to-water/relay/bridge tours pass in both directions, approximately 308 seconds each. The corrected generator aisle also passes separately.
- Both inherited Blueprints are up to date, all 235 R12 material interfaces compile, and there are no new missing references. Five pre-existing Beech authoring-graph references remain documented.
- Six paired views average 75–87 FPS; retained walking routes average 75–85 FPS at 2560×1440 output with inherited automatic TSR. Service GPU captures show 1552×873 internal resolution in both baseline and R12. No frame generation is used.
- Mean and p95 frame-time budgets pass; frame-time changes remain under 10%. **GPU resource increases remain above 10% in three views and reverse bridge walking, reaching 19.1%.** The diagnostic alternatives and the decision to retain the approved fidelity are explicit in `gpu_cost_review.json`; this GPU threshold is not claimed to pass.
- No measured frames exceed 50 ms. Two isolated R12 outliers at 39–42 ms remain included; see `hitch_review.json`.
- Package startup, default promotion and final remote verification are recorded in their named JSON reports and the final release review; consult those rather than earlier diagnostic runs.

## Reproduction order

Run Blender scripts from this directory's `scripts` folder using Blender 5.0 in background mode. They never save over the approved source:

1. `export_full.py`
2. `export_parking_split.py` (requires the Unreal retained-slot audit)
3. `refine_collision_exports.py`
4. `align_forest_arrival.py`
5. `repair_export_junctions.py` (bakes the intended water-access shear into vertices; separates two coplanar hidden beam faces from the finished quarters floor by 3 mm)
6. `prepare_fixture_handoff.py` (ordinary Python; resolves the finite obsolete fixture list to exact actor/component identities)
7. `consolidate_export_copy.py`
8. `bake_surfaces.py -- handoff_manifest.json`
9. `audit_glass_topology.py` (classifies closed building panes separately from single-surface gondola glass)

Build the Development Editor target to enable the editor-only `StationMigrationTools` module. Start the editor with `-ExecCmds="py <repository>/art/unreal_handoff/scripts/r12_session.py"`. The local dispatcher accepts a unique job ID and a script name from `revision12/scripts` in `revision12/request.json`; it has no network listener. A dispatcher response saying `started` is not a completed validation result—read the script's report.

`build_materials.py` and `import_stage.py` accept a `dry_run` job flag. Import stages are `Circulation`, `Architecture`, and `Infrastructure`; later stages require acceptance of the earlier stage. After building materials, run `optimize_closed_glass.py` to create the closed-pane material copies and persist the named-slot overrides before importing or rerunning the stages. No broad actor-name deletion is used. Old combined mesh components are cleared only through the explicit manifest, while their actor roots remain as anchors.

The fixed-camera benchmark forces a real 2560×1440 PIE render target, records engine frame timing without generated frames, and samples texture memory once per second. Earlier captures with a stale stat counter, editor throttling, different initialized weather, or per-frame memory-query overhead are retained under `diagnostics` and must not be used as the final performance comparison.

The full independent route report has 54 directional tests. Its two initial water-access failures are superseded by `routes_junction_repairs.json`, which validates the repaired intended ramp in both directions and rechecks the quarters interior. `export_junction_repairs.json` records the exact export-only corrections; the approved source hash remains unchanged. The original 18 VF07 routes pass in both directions. Continuous-tour, final visual, package and performance evidence are separate named reports.

## Rollback

Restore the previous map values recorded in `default_map_promotion.json` and select the preserved forest level. The checkpoint tag, source level and shared R04–R11 assets provide rollback without rewriting Git history.

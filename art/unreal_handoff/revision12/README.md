# VF07 → Unreal R12 migration

Work is on `codex/vf07-unreal-r12`. The playable station has **not yet been replaced or promoted**. This file records implementation status, not final acceptance.

## Preserved checkpoint

- Local `main`, remote `main`, fresh verification checkout and `pre-vf07-unreal-migration` resolve to `d713a3c5e7189bc3c5f59cc12396d3428a84b96c`.
- The remote camera-tour commit was merged without rewriting the existing local history.
- Required LFS objects were uploaded and retrieved in `C:/Users/apek-anna/Developer/maldek-checkpoint-verification`; LFS object/pointer verification passed.
- Approved VF07 SHA-256: `e2ce19363f35f7fbef1860f5d5591e53ccf0b97d989085153b631a82558724dd`.
- Unsaved Blender review edits were captured separately. Original Blender and Unreal revisions remain available.
- Gaea's compatible local vendor plugin is intentionally excluded; see the pre-migration checkpoint dependency report for installation requirements.

## Implemented so far

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

## Gates still open

- Circulation, architecture and infrastructure imports, with saved stage acceptance reports.
- All 18 approved routes in both directions with the actual player, plus continuous forest/bridge/water/maintenance traversal.
- Final defect-view, furnishing, glass, weather, audio and flashlight review.
- Blueprint/reference validation, editor reopen, packaged Development smoke test and default-map promotion.
- Performance comparison, regression fixes, final merge/push and fresh-checkout verification.

## Reproduction order

Run Blender scripts from this directory's `scripts` folder using Blender 5.0 in background mode. They never save over the approved source:

1. `export_full.py`
2. `export_parking_split.py` (requires the Unreal retained-slot audit)
3. `refine_collision_exports.py`
4. `consolidate_export_copy.py`
5. `bake_surfaces.py -- handoff_manifest.json`

Build the Development Editor target to enable the editor-only `StationMigrationTools` module. Start the editor with `-ExecCmds="py <repository>/art/unreal_handoff/scripts/r12_session.py"`. The local dispatcher accepts a unique job ID and a script name from `revision12/scripts` in `revision12/request.json`; it has no network listener. A dispatcher response saying `started` is not a completed validation result—read the script's report.

`build_materials.py` and `import_stage.py` accept a `dry_run` job flag. Import stages are `Circulation`, `Architecture`, and `Infrastructure`; later stages require acceptance of the earlier stage. No broad actor-name deletion is used. Old combined mesh components are cleared only through the explicit manifest, while their actor roots remain as anchors.

The fixed-camera benchmark forces a real 2560×1440 PIE render target, records engine frame timing without generated frames, and samples texture memory once per second. Earlier captures with a stale stat counter, editor throttling, different initialized weather, or per-frame memory-query overhead are retained under `diagnostics` and must not be used as the final performance comparison.

## Rollback

Until promotion, the existing default maps are unchanged. Afterwards, restore the previous default-map settings and select the preserved forest level. The checkpoint tag, source level and shared R04–R11 assets provide rollback without rewriting Git history.

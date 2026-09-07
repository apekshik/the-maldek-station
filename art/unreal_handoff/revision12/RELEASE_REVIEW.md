# VF07 station migration — R12 release review

The approved container/concrete station is now the playable R12 level. Expanded rooms, furnished quarters, continuous open grating borders, sideways arrival, lower service circulation, water infrastructure and the detailed parked gondola are integrated with the current forest scene. The existing bridge span and inherited player/audio/weather behavior remain intact.

## Acceptance evidence

- All 328 assemblies are imported with named materials, authored collision and an explicit replacement ledger. The handoff contains 5,027,642 export triangles and 40 reusable 2K texture sets (120 maps).
- All 18 approved VF07 routes pass both ways. The 54-test full suite plus the separate generator aisle checks pass; the complete connected tour also passes both directions without jumping, crouching or teleporting between destinations.
- Continuous tour: forward 307.6 seconds; reverse 307.6 seconds. Visible gondola transforms stayed stationary.
- The six reported defect views, quarters, lower floor, water terrace and whole station were inspected under neutral and production night lighting. Inspection lights were removed before saving.
- Flashlight input, live ambience, all five footstep audio sets and idle/airborne silence pass. Both affected Blueprints compile; all 235 R12 material interfaces have no shader errors.
- Reopening preserves all 138 foliage instances: three deliberate clearance relocations and 135 untouched transforms.
- Development Editor/game builds, cooking, packaged R12 startup and packaged default-map startup pass.

## Fixed-view performance

RTX 5070 Ti 16 GB; 2560×1440 output with inherited automatic TSR (1552x873 internal resolution in both service-view GPU captures); identical project settings, initialized Snow/night and six camera transforms; no frame generation. Values are measured engine frames. CPU is raw game-thread timing, which can include waiting. All-zero render/RHI counters are reported as unavailable in the JSON.

| View | Before FPS | R12 FPS | Before / R12 CPU ms | Before / R12 GPU ms | R12 p95 / p99 frame ms | Draw-call change |
|---|---:|---:|---:|---:|---:|---:|
| bridge | 78.7 | 75.2 | 12.70 / 13.30 | 8.94 / 10.08 | 15.14 / 16.08 | +17.8% |
| control | 78.5 | 78.6 | 12.74 / 12.72 | 8.44 / 9.10 | 13.52 / 14.57 | -14.5% |
| dock | 79.3 | 77.3 | 12.61 / 12.93 | 8.03 / 9.09 | 14.04 / 15.37 | +8.0% |
| forest | 77.5 | 76.9 | 12.90 / 13.00 | 9.84 / 10.75 | 14.25 / 15.63 | +17.4% |
| service | 89.4 | 87.0 | 11.18 / 11.50 | 7.25 / 8.63 | 13.74 / 14.82 | +16.2% |
| station | 78.4 | 76.4 | 12.75 / 13.08 | 9.15 / 9.95 | 14.82 / 16.10 | +19.2% |

All fixed views and paired walking routes meet the 60 FPS mean and p95 frame-time budgets, with less than 10% frame-time change. The separate GPU resource threshold is **not fully met**: bridge +12.8%, dock +13.2%, service +19.1%, and reverse bridge walking +11.2%. These increases remain after investigation. The release retains the approved fidelity with this explicitly recorded performance limitation; see gpu_cost_review.json for the tested alternatives. No claim of eliminating these GPU regressions is made.

## Walking performance

| Retained path | Direction | Before FPS | R12 FPS | Before / R12 GPU ms | R12 p99 frame ms | R12 frames >50 ms |
|---|---|---:|---:|---:|---:|---:|
| Retained forest walking benchmark | forward | 76.3 | 75.9 | 9.08 / 9.62 | 15.30 | 0 |
| Retained forest walking benchmark | reverse | 77.0 | 75.9 | 8.76 / 8.87 | 15.29 | 0 |
| Retained bridge walking benchmark | forward | 86.3 | 85.0 | 7.18 / 7.63 | 17.33 | 0 |
| Retained bridge walking benchmark | reverse | 77.5 | 74.6 | 9.27 / 10.31 | 16.00 | 0 |

Across the fixed views, R12 process RAM averages 9.69–9.72 GiB, streaming textures 0.73–0.93 GiB, and nonstreaming textures 3.89–3.89 GiB. The texture streaming pool is 0.98 GiB. These are measured residency/process counters, not total VRAM consumption.

The paired walking paths use the same preserved forest and bridge geometry in both levels. Full per-frame samples, streaming texture residency, process RAM, draw calls, percentiles and hitch locations are retained in the JSON reports. Texture residency is not total device VRAM usage.

## Changes kept within R12

The latest forest terrain received only the explicit local VF07 delta. The final forest-path bend joins the sideways arrival; 86 earlier cross-sections and their UVs remain exact. The R12 Landscape underlay is owned independently and has sufficient clearance without further height edits. Superseded road/apron layers and precisely identified mesh components are retired through the manifest.

The bridge comparison preserves 221 source objects exactly, with only the approved junction pieces and two footing adjustments. The gondola retains its audited pivot and boarding alignment. Existing controller/spline configuration stays unchanged; the visible cabin remains parked.

Two export-only numerical fixes are recorded: bake the intended water-ramp shear into vertices, and recess two hidden support top faces 3 mm below the quarters floor to remove coplanar flicker. The approved VF07 source file retains its original SHA-256.

Fourteen closed building panes across seven assemblies now cull redundant backfaces; all ten single-surface gondola panes remain two-sided. Geometry, collision and the approved glass appearance remain intact.

Four restrained practical lights and relocated inherited entrance/cabin lights follow the new fixtures. The nearby inherited yard light is calibrated to remove a fog glare hotspot. Global weather, exposure and sky settings remain inherited. R12-owned copies of the retained rock material persist Nanite usage without modifying shared forest materials.

## Open and reproduce

Open `game/game.uproject` in Unreal 5.7. Both editor and game defaults select `/Game/MaldekRefinement/R12/Station_R12`. The level inherits `BP_ForestGameMode` and `BP_ForestWalker`.

Run `scripts/Build_R12.ps1 -UseDefaultMap` to build, cook and archive Development for Windows. The local package is `game/Saved/R12Package/Windows/game.exe`. Run `scripts/Smoke_R12.ps1 -UseDefaultMap` for the bounded startup smoke test. See README.md for Blender export/import order and the dispatcher workflow.

The import manifest, material bindings, exact actor/component replacement inventory and integration ledger are in this directory. Review images are in `reviews/final` with final water-night overrides in `reviews/final_water` and glass checks in `reviews/closed_glass`; matched before/after camera captures are in `baseline` and `final`.

## Retained dependencies and rollback

The local GaeaUnrealTools 2.0.0.15 vendor plugin remains intentionally excluded from Git; a new authoring machine needs its compatible UE 5.7 installation. Five pre-existing missing Beech authoring-graph branch references remain documented; placed foliage assets and the packaged level are valid, and no new missing references were introduced.

Rollback uses `pre-vf07-unreal-migration` at `d713a3c5e7189bc3c5f59cc12396d3428a84b96c`, the preserved `Forest_Approach_Test` level and the previous map values in `default_map_promotion.json`. Original R04–R11 assets and the approved Blender source remain available. No history rewrite is required.

## Remote delivery verification

Release commit `cf773e9c81eeccc28f53adf58f9cd6efc50fbcc3` was pushed to main and retrieved in the independent verification checkout. All 3534 LFS files are hydrated; 1151 actual R12 files (1,680,398,430 bytes) match their committed SHA-256 OIDs. Git LFS fsck and the separate source/328-FBX/120-texture checks pass. The previously verified baseline LFS cache was reused; missing migration assets were fetched from origin.

The editor also reopened through its default-map setting and verified the saved closed-glass slot bindings. The final documentation commit adds these verification receipts without changing playable assets.

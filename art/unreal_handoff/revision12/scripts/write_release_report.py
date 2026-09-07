"""Produce the review document from measured acceptance reports."""

import json

from pathlib import Path

b=Path(__file__).resolve().parents[1]

def read(name):return json.loads((b/name).read_text(encoding='utf-8-sig'))

p=read('performance_comparison.json');w=read('movement_performance_comparison.json');tour=read('routes_continuous.json')

assert p['accepted'] and w['accepted'] and tour['success']

for name in ['package-default-build.json','package-default-smoke.json','reference_validation.json','foliage_persistence.json']:assert read(name)['success'],name

assert read('package-default-visual.json')['accepted']
assert read('editor_release_reopen.json')['success']
remote=read('remote_verification.json');assert remote['success']

lines=['# VF07 station migration — R12 release review','',

'The approved container/concrete station is now the playable R12 level. Expanded rooms, furnished quarters, continuous open grating borders, sideways arrival, lower service circulation, water infrastructure and the detailed parked gondola are integrated with the current forest scene. The existing bridge span and inherited player/audio/weather behavior remain intact.','',

'## Acceptance evidence','',

'- All 328 assemblies are imported with named materials, authored collision and an explicit replacement ledger. The handoff contains 5,027,642 export triangles and 40 reusable 2K texture sets (120 maps).',

'- All 18 approved VF07 routes pass both ways. The 54-test full suite plus the separate generator aisle checks pass; the complete connected tour also passes both directions without jumping, crouching or teleporting between destinations.',

f"- Continuous tour: forward {tour['results'][0]['elapsed_seconds']:.1f} seconds; reverse {tour['results'][1]['elapsed_seconds']:.1f} seconds. Visible gondola transforms stayed stationary.",

'- The six reported defect views, quarters, lower floor, water terrace and whole station were inspected under neutral and production night lighting. Inspection lights were removed before saving.',

'- Flashlight input, live ambience, all five footstep audio sets and idle/airborne silence pass. Both affected Blueprints compile; all 235 R12 material interfaces have no shader errors.',

'- Reopening preserves all 138 foliage instances: three deliberate clearance relocations and 135 untouched transforms.',

'- Development Editor/game builds, cooking, packaged R12 startup and packaged default-map startup pass.','',

'## Fixed-view performance','',

'RTX 5070 Ti 16 GB; 2560×1440 output with inherited automatic TSR (1552x873 internal resolution in both service-view GPU captures); identical project settings, initialized Snow/night and six camera transforms; no frame generation. Values are measured engine frames. CPU is raw game-thread timing, which can include waiting. All-zero render/RHI counters are reported as unavailable in the JSON.','',

'| View | Before FPS | R12 FPS | Before / R12 CPU ms | Before / R12 GPU ms | R12 p95 / p99 frame ms | Draw-call change |',

'|---|---:|---:|---:|---:|---:|---:|']

for name,row in p['cameras'].items():

 a,z=row['baseline'],row['r12'];lines.append(f"| {name} | {a['mean_fps']:.1f} | {z['mean_fps']:.1f} | {a['game_ms']['mean']:.2f} / {z['game_ms']['mean']:.2f} | {a['gpu_ms']['mean']:.2f} / {z['gpu_ms']['mean']:.2f} | {z['frame_ms']['p95']:.2f} / {z['frame_ms']['p99']:.2f} | {row['percent_change']['draw_calls']:+.1f}% |")

lines += ['', 'All fixed views and paired walking routes meet the 60 FPS mean and p95 frame-time budgets, with less than 10% frame-time change. The separate GPU resource threshold is **not fully met**: bridge +12.8%, dock +13.2%, service +19.1%, and reverse bridge walking +11.2%. These increases remain after investigation. The release retains the approved fidelity with this explicitly recorded performance limitation; see gpu_cost_review.json for the tested alternatives. No claim of eliminating these GPU regressions is made.', '', '## Walking performance','', '| Retained path | Direction | Before FPS | R12 FPS | Before / R12 GPU ms | R12 p99 frame ms | R12 frames >50 ms |','|---|---|---:|---:|---:|---:|---:|']

for row in w['routes']:

 a,z=row['baseline'],row['r12'];lines.append(f"| {row['name']} | {row['direction']} | {a['mean_fps']:.1f} | {z['mean_fps']:.1f} | {a['gpu_ms']['mean']:.2f} / {z['gpu_ms']['mean']:.2f} | {z['frame_ms']['p99']:.2f} | {len(z['hitches_over_50ms'])} |")

lines += ['', 'Across the fixed views, R12 process RAM averages %.2f–%.2f GiB, streaming textures %.2f–%.2f GiB, and nonstreaming textures %.2f–%.2f GiB. The texture streaming pool is %.2f GiB. These are measured residency/process counters, not total VRAM consumption.' % tuple([min(r['r12'][k]['mean'] for r in p['cameras'].values())/2**30 if mode=='min' else max(r['r12'][k]['mean'] for r in p['cameras'].values())/2**30 for k,mode in [('process_physical_bytes','min'),('process_physical_bytes','max'),('streaming_texture_bytes','min'),('streaming_texture_bytes','max'),('nonstreaming_texture_bytes','min'),('nonstreaming_texture_bytes','max'),('texture_pool_bytes','max')]]), '', 'The paired walking paths use the same preserved forest and bridge geometry in both levels. Full per-frame samples, streaming texture residency, process RAM, draw calls, percentiles and hitch locations are retained in the JSON reports. Texture residency is not total device VRAM usage.', '',

'## Changes kept within R12','',

'The latest forest terrain received only the explicit local VF07 delta. The final forest-path bend joins the sideways arrival; 86 earlier cross-sections and their UVs remain exact. The R12 Landscape underlay is owned independently and has sufficient clearance without further height edits. Superseded road/apron layers and precisely identified mesh components are retired through the manifest.',

'',

'The bridge comparison preserves 221 source objects exactly, with only the approved junction pieces and two footing adjustments. The gondola retains its audited pivot and boarding alignment. Existing controller/spline configuration stays unchanged; the visible cabin remains parked.',

'',

'Two export-only numerical fixes are recorded: bake the intended water-ramp shear into vertices, and recess two hidden support top faces 3 mm below the quarters floor to remove coplanar flicker. The approved VF07 source file retains its original SHA-256.',

'',

'Fourteen closed building panes across seven assemblies now cull redundant backfaces; all ten single-surface gondola panes remain two-sided. Geometry, collision and the approved glass appearance remain intact.', '',

'Four restrained practical lights and relocated inherited entrance/cabin lights follow the new fixtures. The nearby inherited yard light is calibrated to remove a fog glare hotspot. Global weather, exposure and sky settings remain inherited. R12-owned copies of the retained rock material persist Nanite usage without modifying shared forest materials.',

'',

'## Open and reproduce','',

'Open `game/game.uproject` in Unreal 5.7. Both editor and game defaults select `/Game/MaldekRefinement/R12/Station_R12`. The level inherits `BP_ForestGameMode` and `BP_ForestWalker`.',

'',

'Run `scripts/Build_R12.ps1 -UseDefaultMap` to build, cook and archive Development for Windows. The local package is `game/Saved/R12Package/Windows/game.exe`. Run `scripts/Smoke_R12.ps1 -UseDefaultMap` for the bounded startup smoke test. See README.md for Blender export/import order and the dispatcher workflow.',

'',

'The import manifest, material bindings, exact actor/component replacement inventory and integration ledger are in this directory. Review images are in `reviews/final` with final water-night overrides in `reviews/final_water` and glass checks in `reviews/closed_glass`; matched before/after camera captures are in `baseline` and `final`.',

'',

'## Retained dependencies and rollback','',

'The local GaeaUnrealTools 2.0.0.15 vendor plugin remains intentionally excluded from Git; a new authoring machine needs its compatible UE 5.7 installation. Five pre-existing missing Beech authoring-graph branch references remain documented; placed foliage assets and the packaged level are valid, and no new missing references were introduced.',

'',

'Rollback uses `pre-vf07-unreal-migration` at `d713a3c5e7189bc3c5f59cc12396d3428a84b96c`, the preserved `Forest_Approach_Test` level and the previous map values in `default_map_promotion.json`. Original R04–R11 assets and the approved Blender source remain available. No history rewrite is required.','']

lines += ['## Remote delivery verification','',f"Release commit `{remote['verified_release_commit']}` was pushed to main and retrieved in the independent verification checkout. All {remote['all_lfs_files_hydrated']} LFS files are hydrated; {remote['r12_lfs_working_files_hash_verified']} actual R12 files ({remote['r12_bytes_hash_verified']:,} bytes) match their committed SHA-256 OIDs. Git LFS fsck and the separate source/328-FBX/120-texture checks pass. The previously verified baseline LFS cache was reused; missing migration assets were fetched from origin.",'','The editor also reopened through its default-map setting and verified the saved closed-glass slot bindings. The final documentation commit adds these verification receipts without changing playable assets.','']
(b/'RELEASE_REVIEW.md').write_text('\n'.join(lines),encoding='utf-8')

print('Wrote RELEASE_REVIEW.md')

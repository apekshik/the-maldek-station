# West services: Unreal integration

The assembled parcels office, rescue hut and lower auxiliary-power room are installed in `/Game/MaldekRefinement/PassengerLodge/Station_Lodge_Migration`, together with the furnished janitor closet and rescue shelving. This map retains the previously integrated passenger lodge. The original furnished Blender master is unchanged.

## Content and ownership

`exports.json` is the authoritative import manifest: 1,566 renderable source objects in 101 localized mesh groups, including 17 independently moving mechanisms. It records source membership, pivot frames, material slots, bounds, hashes and blocking roles. The 50 materials include eight procedural finishes baked to 2K base-color/normal atlases. Existing station geometry and materials were not globally reimported or restyled.

`WestServices_EngineAdjusted.blend` is the editable station copy with the rescue shelf repositioned and the generator fuel line routed clear of its cover. Collision-only edge insets are metadata on the parcels hinge and exact boxes in the export manifest. `West_Site_Ground.blend` preserves the fitted ground source separately.

The upper rooms remain at station Z=4.6 m, the old promenade at 4.0 m and the lower platform at 1.2 m. Eighteen obsolete west-edge guard pieces were removed through three localized deck replacements; their retained source members are recorded in `deck_patch_exports.json`.

## Terrain and forest

The custom ground beneath the compound was surveyed and fitted to a continuous bank. Only the bounded west-services area changes; the old ground asset remains available. The lower deck has ground/support clearance instead of terrain protruding through the floor. `ground_changes.json` contains exact vertex changes, with before/after engine surveys.

The native foliage move ledger contains 394 initial changes (14 tall trees relocated, remaining entries reseated or cleared with the ground work) and 13 additional grass-edge relocations. Twenty-eight smaller pines form staggered west, south and north screening outside the circulation footprint. Full transformed foliage bounds are audited against the platform, upper approach and stairs. Native foliage instance identities are preserved.

Day review images use temporary neutral directional illumination; gameplay-night images use the actual weather and player flashlight. Temporary review lights are removed without saving them. The forest masks the immediate downslope bank while retaining distant mountain views.

## Controls and scope

Press E while aiming at a new door, cabinet, tray or service lid. Mechanisms stop on a blocking object and can be retried. Doors save closed and accessible. Secure trays require the wire door to be open. The generator's service covers open, but start/fault simulation, parcel quest logic, medical-item consumption and persistence of open states across game sessions are separate narrative systems, as specified in the approved plan. Props and panel markings remain authored environmental detail.

The integration uses the existing StationCabinet runtime class and recorded station movement sounds. No shared C++ interaction behavior or global rendering quality settings were changed for this import.

## Reproduction and rollback

Use the supplied FBXs, textures and `exports.json` with `scripts/install.py` in the migration map. Its placement, material-slot and source-hash assertions protect the import contract. `baseline.json` and `baseline_backup/Station_Lodge_Migration.umap` record the pre-integration checkpoint. Ground, deck and native foliage scripts have separate manifests and ledgers; do not replay an initial relocation over an already modified map without restoring its baseline.

`export.py` records the initial full bake; `export_collision_patch.py` records the later generator/seal repair. The final supplied manifest also includes the measured parcels hinge/latch collision insets. The supplied final assets are the repeatable engine import inputs. `save_adjusted_source.py` regenerates the editable adjusted source from the untouched furnished master.

Validation and normal-game promotion results are recorded below after the release checks finish.

## Verification results

- Ten actual-character walking routes passed, including reverse ramp and stair routes (`traversal_runtime.json`). Static capsule queries had conservative stair-contact failures; real character stepping resolved those routes without suppressing structural collision.
- All 17 mechanisms passed full open/close (`mechanism_runtime.json`), real E-key focus/open/close (`focus_runtime.json`) and actual pawn obstruction/retry (`safety.json`). The focus-only camera test disables pawn collision to isolate aiming/input; the separate safety and walking tests use the real capsule.
- Final save/reopen passed: 1,279 retained baseline actors, 101 imported groups, all 4,556 native foliage instance identities and expected positions, original furnished-source hash and R12 map hash (`verification.json`). The temporary peek-test start was deliberately restored to the original R12 arrival start. Transient Landscape grass component names are excluded from identity checks because Unreal regenerates those components after loading; native foliage instances are checked independently.
- Conservative full foliage-bounds audit found zero conflicts, including the 28 new screening pines (`foliage_conflicts.json`).
- The original solid cleaning-cupboard placeholder was removed from one shared shell chunk while preserving its five wall/privacy members (`janitor_patch_install.json`).
- The existing sheltered-storm audio actor now includes the three new rooms. Room-center weights are 1; porch and lower outdoor walkway weights are 0 (`entry_acoustics.json`). No independent generator sound loop was layered over the existing ambience.
- Paired 1600x1000 PIE samples measured 16.32 ms at the compound, 14.77 ms looking west, and 14.59 ms in rescue with the additions visible. Compared with the same scene with the new actors hidden, median frame-time changes were +0.06, +0.18 and +0.25 ms. This is a local rendering comparison, with terrain/foliage and all actor ticks held constant, not a historical whole-map benchmark or an FPS guarantee. See `performance.json`; render-thread values reported near zero are not used as meaningful timing evidence.
- Normal startup retains `/Engine/Maps/Entry`, then travels to the migration map. `DefaultGame.ini` cooks both that map and R12; `DefaultEngine.ini` opens the expanded station for editing. Config backups and the untouched R12 map provide rollback. `r12_reconciliation.json` found no new actors or placement changes since the lodge baseline.

## Windows package

Development BuildCookRun succeeded (exit 0; 2m40s). Launch `game/Saved/WestServicesPackage/Windows/game.exe` from the repository. The executable reaches the normal Maldek Station menu. The first attempt to build was blocked by the active editor Live Coding session; the editor was saved and closed, then the normal build succeeded.

The final standalone travel/interaction smoke test is pending: Windows Security opened a network-access prompt, and the computer-use tool cannot target its PickerHost dialog. It rejects clicks into the covered game. The user has been asked to click Cancel; no network permission was granted by this integration. See `package-launch.json`. All earlier runtime interaction/traversal results are PIE checks, not a claim that this last standalone test passed.

## Packaged loading crash repaired / September 11

The first real Begin shift attempt exposed an async-loading crash in `AStationCabinet`: its constructor called `UWidgetComponent::SetMaterial`, which updated a dynamic material and reached the renderer from `FAsyncLoadingThread`. The crash stack is retained in `package-crash-before-fix.log`. The constructor now retains the material reference; `BeginPlay` applies it on the game thread, following the existing StationDoor pattern. This is a subsequent shared C++ fix, superseding the earlier no-runtime-code-change statement.

A fresh Development package built successfully. Clicking Begin shift in that executable loaded the expanded map, completed readiness in 4.4 seconds and started the opening without the assertion (`package-launch-after-fix.log`). The game was left running for the user. This verifies the packaged loading regression; it does not replace the earlier PIE interaction suite with a claim of full standalone interaction testing.

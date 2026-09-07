# Forest approach test

Open `/Game/MaldekRefinement/ForestTest/Forest_Approach_Test` in Unreal 5.7. This is a separate copy of saved R11. The source station map and shared building assets are not edited.

The study uses European Beech, Goat Willow and European Aspen from the existing Megaplant library, planted in groups outside the 2.5 m approach corridor. The project's installed ProceduralVegetationEditor plugin is enabled because these assets reference its master materials and wind data.

The test includes a wider, undulating terrain shoulder, a rough soil material, scanned rock patches, and six small warm route-marker fixtures. The existing player and flashlight are inherited from R11. Hazel and Rowan have not been imported.

Reproduction order: run `build_forest_terrain.py` in Blender, then `import_forest_terrain.py` and `build_forest_test.py` in the test level's Unreal Python environment. The initial `build_forest_test.py` can create the level from R11 when no test level exists. All scripts are in `../scripts/`. Generation uses a fixed seed.

Validation and screenshots are stored here. This is an art-direction prototype, not a packaged performance validation. Skeletal foliage is not yet converted into a production foliage scattering setup. Ground plants and leaf-litter dressing remain a subsequent pass.

## Completed first pass

45 trees (29 beech, 10 willow, 6 aspen), 15 scanned rock patches, 6 route markers, and 35 simple trunk collision proxies. Willow remains passable. The 57.6 m approach passed 29 movement checkpoints with the actual character; sampled floor deviations stayed below 1 cm. The test was repeated after the flashlight adjustment and passed again.

The test-only BP_ForestWalker/BP_ForestGameMode expands flashlight reach to 15 m and its outer cone to 42 degrees, with intensity 1.2 in the inherited lighting setup. Main R10/R11 player assets remain unchanged. Route lights were raised to 0.18. Reproduce these final adjustments with finish_forest_test.py followed by tune_forest_flashlight.py.

The files play_flashlight_on/off.png were captured through the editor screenshot API during PIE and should not be used to assess the actual flashlight beam. gameplay_on/off.png use the game viewport command instead. The live viewport was also visually checked with the flashlight illuminating the path.

R11 source map remained last modified at 2026-09-06 20:12:06 local time. No production performance claim is made. The enabled vegetation plugin is experimental in UE 5.7. The prototype soil shader and coarse terrain remain suitable for direction testing, not final environment art.

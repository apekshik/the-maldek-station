# Forest test audio

The Forest_Approach_Test map now has a stronger forest wind bed (volume multiplier 0.07 to 0.35), weather master 0.6, and a night insect loop at 0.1. This changes in-game audio, not the computer's master volume. No music score was added.

BP_ForestWalker inherits the new native SurfaceFootstepComponent. It plays local first-person steps from actual grounded movement distance: 145 cm per walking step, increasing to 190 cm at full running speed. The faster movement still produces a faster cadence. Steps are suppressed while stationary, airborne, teleporting, or pushing against a wall without moving. Five samples per surface avoid immediate repeats and use small pitch/volume variations.

Physical surface IDs in DefaultEngine.ini: 1 Soil, 2 Gravel, 3 Metal, 4 Concrete, 5 Wood. Test-local material instances associate the existing visual materials with these surfaces. Complex traces select the material underfoot on meshes containing several materials. The bridge's simple walking collision supplies a metal fallback through grating gaps. Unassigned surfaces fall back to soil; new environment assets should receive explicit physical materials.

Audio variants are in /Game/MaldekRefinement/ForestTest/Audio/Steps. The component's five sound arrays and volume are editable on the player blueprint. Material and sound assignments are isolated to the test map/player; original R11 map and shared visual materials are untouched.

Build: Development Editor via Unreal Build Tool. Reproduce asset wiring with ../scripts/setup_forest_audio.py. Run ../scripts/test_forest_audio.py for fixtures, actual path/bridge surface checks, idle/airborne suppression, and cadence validation. Test fixtures are removed before saving. Results: audio_validation.json; recorded mix: footstep_mix.wav.

Source recordings and processing notes: ../../audio/footsteps/README.md. Metal and gravel are layered prototype composites; a final foley pass can replace those samples without changing the surface system.

Validation completed: all ten cases passed after the bridge collision fallback fix. Five surface fixtures, actual gravel path, actual metal bridge, idle suppression, airborne suppression, and running cadence. Measured cadence: 2.28 steps/s walking and 2.94 steps/s running. Both ambience actors reported playing. The 9.024-second captured path/bridge mix peaks at 0.152 full scale with zero clipped samples. This is a first-pass mix; final foley and indoor/outdoor ambience transitions remain future sound-design work.

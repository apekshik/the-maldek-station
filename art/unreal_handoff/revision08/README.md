# R08 - upper-floor wall lamps

Open `/Game/MaldekRefinement/R08/BlockOut_R08`. [Render gallery](SHOTS.md).

The two R07 upper-platform spotlights spread light across the whole floor without visible fixtures. An inherited point light above the gondola also produced an unsupported white glow. R08 disables those three sources and adds two hooded wall lamps above the control-room and waiting-hall entrances. Each has a mounting plate, housing, guard, luminous diffuser and conduit to the roof.

The two lamps use 1.5 and 1.2 lumens under this scene's existing exposure, compared with 13 and 10 for the former test spots. Their outer cones are 34 degrees, their reach is 4.2 metres, and they aim down and slightly out onto the thresholds. Reduced volumetric scattering (0.12) keeps them from becoming large glowing fog cones. Both use 3600 K light. The source intensity values are specific to the current exposure; they are not intended as real-fixture photometric specifications.

The lower-deck and relay lighting settings are inherited from R07. Fog volumes and moon intensity are unchanged. The saved time is explicitly 23:00: R07's saved 05:57 setting produced a much brighter dawn sky when reopened in a fresh editor. These captures therefore show the wall lamps in a reproducible night setting.

Validation saves and reloads the map, checks that the old sources are off and the two new lights retain their reduced settings, and traces the wall faces behind both mounts. Decorative fixture parts use the NoCollision profile. The three 2560x1440 screenshots use the saved lighting without inspection fill lights or exposure overrides. Performance at 1440p/60 FPS has not been measured.

Run `../scripts/capture_r08.py` with R08 open to apply, verify and capture the pass. The construction script updates named actors and can be rerun without duplicating them. R07 remains available for comparison.

# Sound, camera and practical light pass

Saved in Station_R12 and BP_StationWalker_Polished. No native code or global lighting changes.

- Footstep component volume: 0.8 -> 2.0 (+7.96 dB). All 62 existing recorded surface samples retained.
- Camera: HeadBobScale 0.7 -> 1.5; IdleSwayScale 1 -> 2; WalkSwayCm 0.9 -> 1.8; RunSwayCm 1.65 -> 3. Breathing displacement increases 4.29x. Existing stair smoothing remains.
- Two warm ceiling panels in the adjacent office/waiting hall, with downward practical lights.
- Two small red lenses over the tall bridge pillars, above the crosshead. Emission is 15% of the gondola marker material; spill is 0.003 lumens within 45 cm.

Validation: 28 PIE player checks passed; 52 footsteps during walking/running; lateral travel 5.4 cm walking and 9 cm running. The 21-second mixer recording peaks at 0.711 with zero clipped PCM samples. This is a signal check, not a claim of subjective listening approval. Night screenshots were inspected: office diffuser visible, red tower markers small at bridge distance. No collision added, minimum office headroom 3.032 m. All 725 existing actor transforms preserved. Saved-property verification passed; no dirty map packages.

Files: before.json, setup.json, verified.json, player_validation.json, mix_analysis.json, walking_mix.wav, views/*.png.

Reapply with scripts/sensory_refine_setup.py via the existing editor dispatcher, only after acquiring the shared editor. The script is idempotent. Do not rerun before.json audit over the original baseline. No packaged executable rebuild was done in this pass; changes are in the Unreal project. The forest task retains ownership of the shared map and will preserve this pass in subsequent terrain work.

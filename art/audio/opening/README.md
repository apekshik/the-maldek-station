# Demo opening

The current R12 player sees the game fade in from black over the first two seconds. MALDEK STATION appears directly over the forest from 2.2–3 seconds, holds, and fades out from 4.8–6 seconds. Movement and looking are held for those six seconds and released on completion or EndPlay.

After a five-second gap, lower-screen instructions fade in from 11–13 seconds as plain text over the game, with no background panel. F toggles the flashlight; scrolling up tightens the beam and down widens it. Each line turns a muted green when used. After both actions, the prompt fades out (minimum 17 seconds total); otherwise it automatically clears at 33 seconds. It does not capture the mouse or change input mode.

Actual light toggles play distinct recorded mechanical clicks. Focus adjustment does not play a switch click. Clicks and control acknowledgements run through the same pawn functions used by the F and mouse-wheel bindings.

The selected intro is A, Dark Cavern Ambient by Paul Wortmann (CC0): a 35-second excerpt with a two-second entrance and eight-second exit, played once per opening. Near the station, B, Dark Ambient Drone #2 by Tsorthan Grove (CC BY 4.0), fades in over five seconds. It uses the creator's continuous loop. If A is still playing, it fades out over the same transition. B begins a 12-second fade to silence 60 seconds after approach and never retriggers on boundary reentry. Existing environmental ambience continues.

After user playtesting, A's runtime volume increased from 0.55 to 1.75 (+10.05dB) and B from 0.45 to 1.4 (+9.86dB). The original source preparation remains unchanged. Flashlight clicks now use a 0.85 source peak and 1.0 runtime multiplier (+10.8dB combined over the prior 0.35/0.7 mix).

Sources and edits are documented in `sources.json`; credits are staged with the game in `Content/AudioCredits/Opening.txt`. The Freesound sources are public high-quality MP3 previews of real flashlight recordings. Selected atmosphere originals are in `art/audio/auditions/2026-09-07/originals`. Audio processing is limited to trimming, conversion, gain and fades.

Runtime settings are on `StationOpeningComponent` in `BP_StationWalker_Polished`: opening, switch and station sounds and volumes, Station Approach Location and Radius. The approach is a 16-meter sphere centered at the surveyed forest arrival endpoint (station-local -13.5, -19.5, 0 meters), converted through the existing station origin. It is checked after the six-second input hold. The opening is opt-in so older maps retain their existing behavior. Automated movement tests should wait until its Elapsed reaches 6 seconds or disable Enable Opening on a test pawn.

Editor install script: `art/unreal_handoff/revision12/scripts/install_opening.py`.
PIE validation: `test_opening.py` with mode `interactive` or `timeout`.
Approach audio validation: `test_station_audio.py`; evidence in `revision12/station_audio/`.
Reports, title/hint captures and game audio captures: `art/unreal_handoff/revision12/opening/`.

Selected A/B validation (2026-09-07): editor build passed; 10 approach/loop checks and 18 opening/flashlight checks passed. The default-map Development package built and passed startup smoke. Captured approach output is non-silent with peak 0.221 (no clipping). Capture runs require the temporary editor launch override `-ini:Engine:[Audio]:UnfocusedVolumeMultiplier=1.0`; normal background-muted captures are not audible evidence. The packaged game's background audio setting is unchanged.

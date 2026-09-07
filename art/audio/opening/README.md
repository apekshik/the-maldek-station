# Demo opening

The current R12 player gets a centered MALDEK STATION title on a dark full-screen card. The title fades in from 0.35–1.65 seconds, holds, fades from 3.6–5.1 seconds, and reveals the level from 4.3–6 seconds. Movement and looking are held for those six seconds and released on completion or EndPlay.

At 6.2 seconds a lower-screen prompt fades in: F toggles the flashlight; scrolling up tightens the beam and down widens it. Each line turns a muted green when used. After both actions, the prompt fades out (minimum 12 seconds total); otherwise it automatically clears at 28 seconds. It does not capture the mouse or change input mode.

Actual light toggles play distinct recorded mechanical clicks. Focus adjustment does not play a switch click. Clicks and control acknowledgements run through the same pawn functions used by the F and mouse-wheel bindings.

The intro atmosphere is a 14-second licensed Nox sound excerpt with a slow entrance and exit, played once per opening. Existing environmental ambience continues. No random stingers or jump scares are added.

Sources and edits are documented in `sources.json`; credits are staged with the game in `Content/AudioCredits/Opening.txt`. The Freesound sources are public high-quality MP3 previews of real flashlight recordings. The Nox source comes from the previously downloaded Essentials archive. Audio processing is limited to trimming, conversion, gain and fades.

Runtime settings are on `StationOpeningComponent` in `BP_StationWalker_Polished`: Enable Opening, Opening Atmosphere, Atmosphere Volume, Switch On/Off and Switch Volume. The opening is opt-in so older maps retain their existing behavior. Automated movement tests should wait until its Elapsed reaches 6 seconds or disable Enable Opening on a test pawn.

Editor install script: `art/unreal_handoff/revision12/scripts/install_opening.py`.
PIE validation: `test_opening.py` with mode `interactive` or `timeout`.
Reports, title/hint captures and game audio captures: `art/unreal_handoff/revision12/opening/`.

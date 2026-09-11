# Lodge camera and recorded-audio refinement

The platform/gondola door uses key camera offset (-18,35,14), reversing the horizontal offset to keep the inserted key and keyhole clear of its inward jamb. Three full key interactions pass visibility, E entry, drag/reverse/cancel, unlock/swing and threshold crossing checks in `key_runtime.json`. The default remains (18,35,14) for other doors.

Forty-five edited recordings are imported under PassengerLodge/AudioRefine. The twelve lockers, fifteen kitchen mechanisms, sixteen access/restroom doors and new first-aid cabinet use family-specific take banks. Native door travel sounds now play once per movement rather than restarting each time a short recording ends. Opening, closing and close-impact selection avoid immediately repeating the same recording when alternatives exist.

Surface 6 is Tile. Quarry flooring uses PM_Tile, with six boot-on-tile takes; concrete uses a different six-take boot bank on the player blueprint. Both are filtered to remove harsh upper transients and reinforced with low-frequency energy from their original recordings. Other floor banks and walking cadence are preserved.

StationLodgeAcoustics adds an 87-second recorded indoor wind loop, filtered to a low, sheltered howl. Three interior boxes cover the hall, coffee annex and restrooms while excluding the courtyard and roof. Boundary transitions fade smoothly; the layer follows the existing weather actor's wind intensity. The existing exterior storm remains in place.

## Verification

The native editor module builds successfully. `runtime.json` checks weather transitions, interior coverage/courtyard exclusions, three opening/closing cycles for each storage recording family, and actual tile/concrete walking with the expected surface IDs. `audio_quality.json` checks all 45 PCM edits and three real engine-output captures for nonzero levels and clipping. Initial background-editor captures were silent; they were replaced by verified foreground captures. The concrete test uses an isolated temporary pad, removed afterward.

Engine captures: `Sheltered_storm_game.wav`, `Tile_steps_game.wav`, `Concrete_steps_game.wav`. Source credits, SHA-256 hashes, reproducible edits and audition banks are in `art/audio/lodge_refine_01`. Subjective final loudness can be reviewed using these recordings or directly in the lodge; signal measurements are not a substitute for listening.

Run `install_audio_refine.py` through the existing dispatcher to reproduce assignments, then `test_key_refine.py` and `test_audio_refine.py`. Keep Unreal foreground when capturing its audio output. No original R12 map replacement is performed.

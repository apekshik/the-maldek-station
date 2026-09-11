# Recorded police-tape tears

Source: “tearing-duct-tape.aif” by alienistcog, Freesound 125304.
https://freesound.org/people/alienistcog/sounds/125304/
CC0 1.0: https://creativecommons.org/publicdomain/zero/1.0/
The source author describes actual duct tape being torn, peeled and handled.
The public HQ MP3 preview is retained; source URL and SHA256 are in sources.json.

Three recorded excerpts are prepared as 48 kHz mono PCM16 WAVs. edits.json records
exact ranges and gains. Only trimming, DC removal, resampling, level adjustment,
and short edge fades were applied. No generated sounds.

The native StationPoliceTape actor chooses a variation at actual seam failure.
Simultaneous breaks share a 120 ms cooldown; merely approaching or retreating
cannot play the tear. Audio is spatialized at the seam, full volume within 2 m,
with 12 m falloff. The level uses TearVolume 1.3 and a small randomized pitch range.

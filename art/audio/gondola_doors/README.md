# Recorded gondola-door sound bank

Real recordings downloaded from Freesound's public high-quality previews. All three are CC0 1.0. Authors, source/download URLs, hashes and edits are recorded in `sources.json`; the original MP3s are retained.

| File | Recording | Intended role |
|---|---|---|
| `wav/Gondola_Door_Open.wav` | iamaviolin, Berlin S-bahn, Zoom H4N | Opening slide, 3.529 s |
| `wav/Gondola_Door_Close.wav` | iamaviolin, same location/recorder | Closing slide and stop, 1.776 s |
| `wav/Metal_Track_Alternate.wav` | wlabarron, old metal-track door | Alternative weathered mechanical texture, 11.989 s |
| `wav/Cabin_Door_Sequence_Audition.wav` | Opening and closing placed on the review timeline | 17-second timing audition, with silence for the dwell |

`prepare.py` makes mono 48 kHz PCM16 WAVs, removes DC offset, adjusts constant gain and applies 4 ms edge fades. No audio is synthesized, no artificial noise is added, and the pitch is unchanged. Opening/closing WAVs are packed into the Blender study. Game import, spatial attenuation and mixing against the terminal machinery remain for the later integration pass.

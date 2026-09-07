# Footstep audio sources

Kenney — Impact Sounds 1.0 (CC0): https://kenney.nl/assets/impact-sounds
Original license: kenney/License.txt. Downloaded 2026-09-06.

TinyWorlds — Different steps on wood, stone, leaves, gravel and mud (CC0):
https://opengameart.org/content/different-steps-on-wood-stone-leaves-gravel-and-mud
Downloaded 2026-09-06. Uses gravel.ogg. The author credits original recordings to pdsounds.org.

prepare.py converts selected recordings to mono 48 kHz PCM WAV and balances peaks. Gravel combines the gravel recording with five distinct shoe impacts. Metal combines five light metal impacts with shoe impacts; these are prototype composites rather than recordings of boots on the station's particular grating. Soil uses five grass footsteps, concrete and wood use five recorded footsteps each. sources.json records each output's source files. Runtime adds subtle pitch/volume variation and prevents immediate sample repeats.

Existing forest wind and insect audio comes from the project's Ultra Dynamic Sky assets; those remain under the user's existing asset license.

# Recorded player foley

Replaces the earlier Kenney-based footsteps and constructed gravel/metal composites with actual footstep recordings. This pass changes audio assets and the current R12 pawn's sound banks; it does not change locomotion, terrain, lighting, or buildings.

| Runtime bank | Recorded surface | Variations |
| --- | --- | --- |
| Soil | Leaves, grass, dirty ground (six each) | 18 |
| Gravel | Gravel | 10 |
| Metal | Nox Metal V1 walking takes | 15 |
| Concrete | swuing concrete footsteps, mastered by congusbongus | 9 |
| Wood | Wood | 10 |

Nox outdoor recordings and Iochi Glaucus fabric are CC0. Concrete recordings are CC BY 3.0. Full attribution, original links, and modification notices are in `game/Content/AudioCredits/RecordedFoley.txt`, staged as a loose file by the packaging configuration. Per-take filenames, original file hashes, trim positions, and gain are in `sources.json`.

`prepare_recordings.py` only edits source recordings: mono conversion, sample-rate conversion, silence trimming, short fades, bank-level gain, and a quiet fabric recording mixed 80 ms after contact. It performs no synthesis. Clothing is baked into each footstep so it follows the existing grounded movement gate and nonrepeating sample choice without a native rebuild. Fabric stems and dry footsteps are retained for rebalancing. Set the fabric peak in that script (currently 0.035) and regenerate/reimport to adjust it independently; it is not yet a runtime clothing-volume control.

The 62 runtime waves are in `wav/`; originals are in `originals/`; dry edits are in `dry/`; clothing edits are in `cloth/`. The full 988 MB Nox archive is a local ignored download cache, not part of the game. Only selected recordings are imported.

`recorded_foley_preview.wav` is an offline source/mix preview in this order: forest floor, gravel, metal, concrete, wood, with four takes per surface and a pause between groups. It is not an in-game recording. Runtime validation and the in-game capture are written under `art/unreal_handoff/revision12/recorded_foley_test/`.

Install from the R12 editor dispatcher with `install_recorded_foley.py`; run `test_recorded_foley.py` after installation. The install report records previous pawn bank references for rollback. The earlier ForestTest pawn remains unchanged; the current default R12 pawn receives this update.

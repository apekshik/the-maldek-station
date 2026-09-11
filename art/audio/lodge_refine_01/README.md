# Recorded lodge audio refinement

45 edited recordings: separate concrete and tile boot banks (six takes each), room and steel access doors, locker doors, drawers, cupboard doors, fridge doors and an 87-second sheltered-wind loop. Playback selects a different take from the previous one within each mechanism bank.

All sounds are edits of recordings, not synthesized/generated effects. `download.py` retains source downloads and hashes; `prepare.py` reproduces 48 kHz mono PCM edits, EQ, level normalization, edge fades and the wind crossfade. Exact ranges and gains are in `edits.json`. Low-pass filtering removes brittle high-frequency transients; a low-frequency copy of the same recording adds body. The loop follows lodge occupancy and the existing weather actor's wind intensity.

## Sources

- wind: [Kinoton / 815100](https://freesound.org/people/Kinoton/sounds/815100/), CC0. Original download and SHA-256 recorded in sources.json.
- drawer: [maaaks / 521214](https://freesound.org/people/maaaks/sounds/521214/), CC0. Original download and SHA-256 recorded in sources.json.
- wooddrawer: [FOSSarts / 740297](https://freesound.org/people/FOSSarts/sounds/740297/), CC0. Original download and SHA-256 recorded in sources.json.
- cupboard: [wlabarron / 509108](https://freesound.org/people/wlabarron/sounds/509108/), CC0. Original download and SHA-256 recorded in sources.json.
- locker: [kyles / 450785](https://freesound.org/people/kyles/sounds/450785/), CC0. Original download and SHA-256 recorded in sources.json.
- fridge: [sethlind / 265024](https://freesound.org/people/sethlind/sounds/265024/), CC0. Original download and SHA-256 recorded in sources.json.
- tile: [IENBA / 834027](https://freesound.org/people/IENBA/sounds/834027/), CC0. Original download and SHA-256 recorded in sources.json.
- concrete: [florianreichelt / 459964](https://freesound.org/people/florianreichelt/sounds/459964/), CC0. Original download and SHA-256 recorded in sources.json.
- room: [launemax / 250024](https://freesound.org/people/launemax/sounds/250024/), CC0. Original download and SHA-256 recorded in sources.json.
- fridge_alt: [SpliceSound / 218334](https://freesound.org/people/SpliceSound/sounds/218334/), CC0. Original download and SHA-256 recorded in sources.json.

Steel-door excerpts reuse MathewHenry recordings 700682 and 700705 from `../doors/recorded/originals`, with the existing package provenance. No new license restrictions are introduced.

`*_audition.wav` files concatenate the prepared takes for listening. Runtime behavior and signal measurements are recorded in `../../unreal_handoff/passenger_lodge_01/audio_refine`. Numerical checks establish levels and playback routing; final subjective balance remains reviewable in-game.

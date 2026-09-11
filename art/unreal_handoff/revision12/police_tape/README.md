# Runtime crisscross police cordon

Map: `/Game/MaldekRefinement/R12/Station_R12`.
Assets: `/Game/MaldekRefinement/R12/PoliceTape`.
Native actor: `game/Source/game/Variant_Horror/StationPoliceTape.{h,cpp}`.

The crossing is fitted to forest approach sample 80, between two newly grounded
beech trees. Three yellow/black strands form an irregular crisscross. Six more
spans continue along existing trees on both sides. The perimeter follows those
trees rather than copying the small closed loop in the Blender review stage.

The actor simulates centreline chains at a fixed 120 Hz and draws two-sided
spline-mesh ribbons with continuous lettering UVs. Capsule contact loads the
strands; sustained moving contact and 36 cm seam displacement permit a controlled
tear. The torn ends continue simulating. Retreat cannot tear by proximity, and
walking back does not reset the opening. New PIE sessions reset the actor.
There is no invisible path-blocking collider or hand animation.

Ribbon-to-ribbon contact uses thin approximate proxies, not full Chaos Cloth
surface collision or calibrated plastic fracture. Local trunk/ground envelopes
bound the loose ends. Simulation work is bounded per frame and sleeps beyond
50 m. This is a gameplay prototype, not a certified performance target.
Three real tape-tearing excerpts from alienistcog (Freesound 125304, CC0) play at
seam failure. A 120 ms gate prevents simultaneous breaks from stacking. See
art/audio/police_tape for the source recording, license, and edit manifest.

Reproduce: export `SM_Tape_RuntimeSegment` and the trunk wrap using Blender study
03's `scripts/export_runtime.py`; compile gameEditor; run
`../scripts/police_tape_install.py` in a fully loaded, idle R12 editor. Startup
uses `police_tape_boot.py` to defer placement until the editor has initialized.
An immediate-startup placement attempt crashed before level changes were saved;
deferred placement succeeded. The local ignored backup is pre-install only.

`installation.json` records live placement and surveyed heights. Play tests cover
retreat, forward walking, reverse traversal with state preservation, and sprinting
with a 30 FPS cap. `playtest.json` records results; caps are requested limits,
not measured sustained frame rates. `views/` holds actual game captures. The
inspection capture uses a temporary PIE-only light, removed at the end.

Source design and material reference: `art/blender/police_tape_03/README.md` and
`art/blender/police_tape_01/README.md`. These assets use original lettering art.

## Bark fitting

Twelve individual wraps replace the uniform ring. `wrap_fit/survey.json` records
actual tree assets, scale, rotation, and each attachment height. Blender study 03
`fit_wraps.py` sections the exported bark (excluding foliage), creates a convex
taut ribbon envelope across nine slices over its full width, and includes a
15 mm source-space allowance (27 mm at the two middle trunk bulges) for differences
between exported and rendered bark. This is an art-directed fit, not a physical
contact measurement. Import with `police_tape_fit_install.py`, then join the
strands with `police_tape_fit_anchors.py`. The main installer runs both when the
fitting manifest exists. Anchors extend inside the bark envelope, preventing
open gaps at the wrap joins. Mesh import uses the standard round-trip orientation;
mirrored/rotated diagnostic variants were discarded.

The editable fitted meshes are also saved in wrap_fit/Maldek_Bark_Fitted_Wraps.blend; the grid layout is for inspection, with export-origin notes on each object. views/fitted_wrap_closeup.png is the final in-game attachment check.

## Later reveal at the station approach

The crossing was moved 26.15 m toward the station, to path sample 80, about 7.38 m
from the end of the footpath at the stairs. Its width and interaction are unchanged.
The two crossing trees and fitted bands moved together, with fresh ground traces.
Six matching trees carry the side spans; the former perimeter trees remain in the
forest. The parking navigation sign spotlight is disabled (zero intensity and
visibility off). `relocation/` contains the before-state, placement, and captures.
The main installer preserves this placement once its manifest is present.

Audio installation: police_tape_audio_install.py imports and assigns the three variations and attenuation asset after building gameEditor. The play test records tape_crossing_mix.wav and checks sound events on retreat, crossing, return, and sprint.

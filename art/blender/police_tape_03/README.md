# Crisscross cordon physics study

`Maldek_Crisscross_Cordon.blend` replaces the parallel crossing with two opposing
diagonals and a third oblique strand. The eight-span perimeter from study 02 is
preserved. Review trees/foliage remain placeholders. No live Unreal map changed.

Play frames 1–144 at 24 fps. The three strands now share one simulation, with
gravity, wind, anchors, torso/trunk/floor contact and ribbon contact. Ribbon
contact uses thin anisotropic centreline proxies: nearby projected footprints
separate in depth, permitting lateral sliding without welding the crossings.
It is an approximation, not continuous collision of full cloth surfaces; it
does not model plastic friction, adhesion, self-collision or calibrated fracture.
The 6 mm contact envelope is numerical clearance, not the tape's film thickness.

Forward movement loads and opens the three controlled seams at frames 58–59.
The loose ends remain simulated. The idle and retreat cases produce no tears.
A contact-disabled comparison differs by up to 0.414 m across the full motion,
showing that coupling affects the result; that number is not an accuracy metric.
`physics_check.json` records these runs. `verification.json` checks finite mesh
positions and a clear central 1.3 m walking gap at frames 96 and 144.

Reproduce with Python/NumPy `scripts/simulate.py`, then Blender 5.0 background
`scripts/build.py`. The build saves the editable source, 18 static crossing/wrap
FBXs, three stills, and 48 preview frames. Use Python/Pillow
`scripts/encode_preview.py` for the six-second GIF. Perimeter exports remain in
study 02; the complete perimeter geometry is included in this Blender file.

The mesh animation is baked shape keys; FBXs contain only the intact geometry.
No hand animation or audio. Unreal runtime solver, frame-rate testing, final tree
fitting and actual game collision verification remain a separate integration.

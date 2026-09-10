# Passenger lodge shell polish

A separate fitted shell review built from the lodge 03 master. No assigned windows, doors, furniture, restroom fixtures, kitchen equipment or wall-display meshes are replaced. The approved room footprint and all opening dimensions remain fixed. Source master and other packages are unchanged.

## Changes

- Cream upper walls and muted green lower paint, with restrained scanned plaster detail replacing the broad procedural mottling. World-scaled planar UVs use the scan's 3.2 m width.
- Protective skirting, dado and cornice trim. Contiguous construction segments are joined; actual door openings remain clear. Trim stops short of opening boundaries for final frame integration.
- A 300 mm quarry-tile floor shader with grout and shallow bump; no walking-surface displacement. This floor treatment is procedural, not a downloaded scan.
- Closed the original 70 mm wall-head gap beneath the roof envelope. Added shallow ceiling members and a quieter roof-underside enamel finish. The roof remains an envelope; drainage, pitch and flashing are not finalized.

## Downloaded texture

[Plastered Wall 04](https://polyhaven.com/a/plastered_wall_04), by Rob Tuytel / Poly Haven, released under [CC0](https://polyhaven.com/license). The 4K diffuse, OpenGL normal and roughness maps are included in `textures/`. `texture_sources.json` records download URLs, hashes and physical scale. The scan is blended subtly beneath paint; it is not used as an unpainted concrete finish. Textures use relative paths in the saved Blender file.

## Review and integration

Open `Maldek_Lodge_Shell_Polish.blend`, scene `Shell_Polish_Review`. Review lights are temporary and clearly named `PLSH_Review_Light`; do not treat them as installed fixtures. Rendered hall and hallway views use the same unfinished furniture/fixture context as lodge 03.

`shell_manifest.json` lists shell material changes and source bounds. Integration should apply the material/UV changes only to those shell objects and append `PLSH_Shell_Trim`; do not wholesale replace a newer master. Roof underside changes are separately named. Check trim endpoints against the final door/window frames and kitchen hatch when their packages arrive. If another package has edited a wall core, preserve that repair and transfer the finish with its updated geometry.

Rebuild using Blender `--background --python art/blender/passenger_lodge_shell_01/scripts/build.py`, then run `scripts/verify.py`. Verification checks source preservation, unchanged shell bounds, texture availability on reopen, new mesh topology and the existing sampled floor/headroom, stair and right-landing routes. This is not Unreal collision or lighting validation.

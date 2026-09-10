# Fitted windows and shell surfaces

This migration checkpoint installs the two approved fixed, three-bay window
assemblies in `Station_Lodge_Migration`. It also replaces the shell/deck pilot
colors with 18 migration-owned surface graphs. No public door, locker or kitchen
mechanism is installed by this checkpoint.

## Ownership and placement

`exports.json` records all 132 evaluated window meshes from the integrated master,
grouped by assembly/material into 14 actors and 12 mesh assets. Two matching
groups share an asset; the other groups retain their distinct exported geometry.
Both assembly origins remain at the approved rough jamb/sill. The 6 mm inner
clear pane and 6 mm outer opal pane remain separate from the metalwork and seals.
These windows are fixed; there are no animated hinges to flatten or replace.

The source's 4 mm concealed core/reveal separation, sill falls, drains, packers,
beads and seals survive evaluated export. No new opening cut or wall relocation
is performed. The existing exit opening between the two windows stays clear.
The Blender master is read-only throughout the export.

## Materials

- Painted plaster keeps its original 4K CC0 Poly Haven maps and 3.2 m planar UVs.
  The green band ends 1.05 m above the floor, matching the integrated source.
- Quarry flooring uses 300 mm square tiles, 4 mm mortar and the authored palette.
  Tile color randomization is translated to Unreal and is not pixel-identical.
- Station paints, galvanized steel and other inherited VF06/VF07 finishes reuse
  the existing Blender-baked BaseColor, ORM and DirectX normal texture sets.
  Source-metre triplanar projection supports the combined pilot meshes without
  changing their geometry or inventing new UVs. Existing texture assets are read
  but not modified. The first UE-noise trial looked marbled and was replaced.
- Frosted outer panes use a local nine-sample screen-color filter. This preserves
  blurred silhouettes, with rough surface reflections; it is a screen-space
  approximation, not a physical volumetric glass simulation. Inner panes retain
  a separate low-opacity clear material. Bright lamps can show discrete filter
  lobes at close range; the nighttime review records this approximation honestly.

No global renderer setting, live-map material or weather setting is changed.
Accumulated snow/wetness integration is still a later material/weather pass.
Full furnishing migration and moving interactions remain later checkpoints.

## Reproduction and evidence

From the repository root, run `scripts/material_audit.py` and
`scripts/export_windows.py` in background Blender. In the bounded Unreal
dispatcher run `install_surface_materials.py`, then `install_windows.py`.
Use `verify_surfaces.py` with `reopen: true` for persistence and route checks.
Review scripts are `review_surfaces.py` (temporary neutral lights, removed on
completion) and `review_surface_night.py` (actual PIE flashlight views).

Reports live one directory above this file: `surface_materials.json`,
`surface_verification.json`, `surface_review.json`, `surface_night_review.json`.
`install.json` contains imported bounds checks; `before.json` records the
pre-window actor transforms. Review images are in `previews/surfaces` and
`previews/surfaces_night`. All engine work stays in the isolated migration map.

After saving and reopening, all 1,141 pre-window actor transforms persisted,
all 86 shell/deck material bindings matched, all 18 material shaders passed,
both sides of all six window bays blocked collision traces, and all 280 route
samples passed. The source live map hash remained unchanged. Neutral views
and actual-character exit traversals in both directions passed review; the
character retained its 34 cm radius and 96 cm half-height collision capsule.
The traversal results are recorded in `../surface_playtest.json`. Neutral views
cover the facade, hall, restroom approach, deck and window sill/head/reveals.
Three nighttime camera positions with three small shifts each show no observed
reveal flicker or crossing faces in the sampled images. The cleaning-cupboard
blockout in the restroom approach remains part of the pending furnishing work.

During bulk mesh-thumbnail saving the editor reported D3D12 E_OUTOFMEMORY
(`material_memory_error.txt`). The graphs had already saved. After restarting,
`install_surface_materials.py` with `resume: true` validated the saved graphs
and skipped identical mesh bindings; the subsequent reopen verification passed.

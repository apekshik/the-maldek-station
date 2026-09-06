# Millford V2 — cliff revision 02

Open `millford_v2_cliff_02.blend` in Blender 5.0.1. Revision 01 remains intact in the parent directory. This revision is based on the saved revision 01 file; it does not include subsequent unsaved edits in the live Blender window.

## What changed

- A sculptable 181 × 181 vertex terrain mesh creates the forest hillside, northern gorge and eastern relay spur. Terrain is graded beneath rooms, stairs and paths. The relay sits on a terrain pad rather than floating in space.
- The lower drive gallery has open north and east sides, a reduced west parapet and a grated apron extending to Y = 11.5 m. The flywheel is visible as a rim, spokes and axle near the open edge. The motor is moved beside it.
- Upper grated dock fingers extend toward the gorge. Steel girders, posts, braces and concrete anchors give the overhang a structural vocabulary.
- The gondola is now **3.1 × 6.0 m**, with its boarding end retained at Y = 5.05 m. Move the `Gondola_MOVE_THIS` parent, whose pivot is (0, 8.05, 4) m.
- All three flights retain their established rise/run but use open steel grating treads and side stringers. Thin collision plates support walking without filling the visible space below each tread.
- Weathered concrete, painted steel, galvanized grating, warm practical lights, fog and 250 linked placeholder conifers establish the setting.

## Inspect

Use `02_Full_Shell` for the environment and saved cameras. `01_Cutaway` and `03_Lower_Level` hide forest and fog for editing. Collections 15–18 contain terrain, forest, atmosphere and cliff anchors. Render previews are in `previews/`: exterior, player-height view beneath the gondola, and the site/relay approach.

This is an architectural and atmosphere study. The procedural conifers are placeholders; terrain needs art sculpting and localized rock detail. Mechanical connections, cable rigging, acoustics and gameplay are not simulated. The open gallery establishes views and an outdoor soundscape opportunity; actual wind, forest and machinery audio belongs in the engine pass.

## Export and checks

`exports/` contains 17 FBXs with fixed architecture at a shared origin, separate doors and gondola, plus a metre scale cube. `export_manifest.json` records pivots and bounds. Terrain, trees and atmosphere remain Blender-only; stage terrain separately as UE Landscape or a dedicated terrain mesh, not a single convex hull. Blender node materials need rebuilding in Unreal.

`validation_report.json` checks 673 route/stair samples for floor support, 2 m headroom and approximate body clearance, including terrain in the geometry probes and the new exposed apron route. It also checks the operator sightline and independently re-imports all 17 FBXs for bounds and collision-hull counts. These are sampled geometric checks; a UE5 capsule and movement playtest is still pending.

Read `ASSET_RESEARCH.md` for the external mesh shortlist and the CC0 textures actually used.

## Rebuild

Run from the repository root in a separate background Blender process. The generator overwrites revision 02, so save hand edits under another filename first.

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background art/blender/millford_v2_blockout_01.blend --python art/blender/scripts/revise_cliff_02.py
/Applications/Blender.app/Contents/MacOS/Blender --background art/blender/revision_02/millford_v2_cliff_02.blend --python art/blender/revision_02/scripts/validate_and_export.py
```

The HTML floorplan remains the earlier schematic; this Blender revision is the current dimensional and terrain study.

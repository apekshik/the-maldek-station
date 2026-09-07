# Millford V2 — dimensional blockout 01

Before new mesh work, read [Mesh authoring lessons](../MESH_AUTHORING.md) for surface ownership, opening clearances and the confirmed R12 z-fighting fixes.

Editable source: `millford_v2_blockout_01.blend` · Blender 5.0.1 · September 6, 2026

This is the first architectural interpretation of the V2 website diagram. It resolves floor heights, stair runs, openings and the operator's window into geometry. It is a blockout for iteration, not final art or a tested UE5 level.

## Open and inspect

Open the `.blend` in Blender. It starts in an orthographic cutaway view with material colors. Viewport overlays are off for a clean opening view; Shift–Option–Z on macOS (Shift–Alt–Z on Windows) toggles them for editing. The top-right View Layer menu contains:

- **01_Cutaway:** roofs hidden; edit the upper rooms and compound.
- **02_Full_Shell:** ceilings and canopy included; inspect enclosure and headroom.
- **03_Lower_Level:** upper rooms hidden; inspect the drive, generator and stair vestibule.

Collections 01–14 contain named, editable parts. Roofs are isolated in collection 13. Collections 90–93 contain presentation geometry, scale figures, labels and cameras; they are excluded from the FBX exports. The hidden wireframe `Control_Glass` is a placement guide, also excluded from export; the first pass uses open window geometry rather than an opaque placeholder pane.

Select the `Gondola_MOVE_THIS` empty to move the entire gondola, including its roof. The two door placeholders have hinge origins and are saved open. Other doorways remain open apertures for the initial walkthrough.

The saved cameras are overview, plan, operator eye, return from the fuel yard, and lower service. Preview PNGs are in `previews/`. The operator-eye image deliberately hides the human standing at the camera location.

## Dimensions and changes from the website

One Blender unit is **one metre**. +X is east, +Y is north toward Maldek, +Z is up. Lower finished floor is Z = 0 m; upper finished floor is Z = 4 m. Dimensions below are nominal footprints between wall centerlines; clear space is reduced by the 220 mm wall thickness.

| Space | Initial footprint / elevation |
|---|---|
| Control room | 5 × 4 m / +4 m |
| Waiting hall | 7 × 6 m / +4 m |
| Main platform envelope | 16 × 7 m / +4 m, with stairwell and gondola bay removed |
| Drive gallery | 8 × 7 m / 0 m |
| Generator room | 8 × 6 m / 0 m, including enclosed stair vestibule |
| Fuel yard | 7 × 6 m / 0 m |
| Overlook | 6 × 4.5 m / +4 m, plus approach links |
| Relay hut | 4 × 4 m / +2 m |
| Gondola | 3.1 × 3.8 m floor, 2.3 m shell height |

The booth is intentionally smaller than the website's 8 × 8 m schematic. A 3 m wide north window gives the operator a direct view of the gondola opening. Public rooms have 3.1 m to their roof underside; the drive has at least 3.65 m beneath the upper floor structure, subject to local equipment.

All three flights have **24 risers of 166.7 mm**, **23 goings of 280 mm**, and **1.6 m tread width**. They rise 4 m over a 6.44 m horizontal run. These are prototype dimensions, not a building-code claim. The arrival stairs descend to a lower landing, then a short sloping link reaches parking.

The internal stair uses an open slot beside the dock. Its foot enters a small enclosed vestibule before reaching the drive room; this avoids entering directly onto raised treads. The overlook connection goes around the high end of that stairwell, preserving headroom. These are deliberate refinements of the diagram's abstract connectors.

The forest route skirts the south end of the exterior stair rather than cutting through the flight. The exterior paths and site base remain coarse. The base is a presentation plinth, not finished terrain, and is not exported. Supports indicate the raised structure; foundation engineering and final slope integration remain to be designed. The original HTML V1 and V2 drawings have not been rewritten to match this dimensional pass.

## FBX handoff

`exports/` contains 16 FBX files:

- Fixed architecture split into named chunks, with vertices baked relative to a **shared world origin**. Place these fixed chunks at the same actor transform, initially location 0 / rotation 0 / scale 1.
- Two separate door files with hinge-relative geometry.
- A separate gondola file, including the roof, relative to its movement pivot.
- A centered 1 m cube for the first scale check.

Each file contains **one render mesh** and its named `UCX_` convex collision pieces. Keeping one render mesh per file avoids the multi-mesh custom-collision limitation described in Epic's [FBX static mesh pipeline documentation](https://dev.epicgames.com/documentation/en-us/unreal-engine/fbx-static-mesh-pipeline-in-unreal-engine). Door apertures are composed of separate convex wall segments, so collision does not fill the doorway. Stair treads use individual convex boxes. Thin handrail geometry is supplemented by simplified guard volumes where supplied; this remains prototype collision, not a final safety enclosure.

Export settings are recorded in `scripts/validate_and_export.py`: metre scene, unit scaling enabled, FBX Units Scale, -Y forward / Z up, selected meshes only, face smoothing, no animation, and triangulation on export copies. Blender writes FBX 7.4; this is not a claim to match Epic's documented FBX SDK version. A UE5 import test is still required.

### First UE5 check

1. Import `SM_Scale_1m.fbx` and verify it measures **100 cm** on each side at actor scale 1. Resolve any axis or unit mismatch here before importing the station.
2. Import the fixed chunks into a dedicated blockout folder, using their custom collision and disabling automatically generated collision if it would replace the supplied hulls. Inspect the collision overlay on a doorway and a stair flight.
3. Place the fixed chunks at the common origin. Inspect alignment of the upper platform, lower drive and stairs.
4. Add the doors and gondola separately. `export_manifest.json` records their source Blender pivot positions in metres. Confirm axis conversion before applying those positions in Unreal; the manifest intentionally does not pretend to be an engine-tested placement script.
5. Walk from booth to gondola, through the hall loop, down the internal stair, through the generator, and back via the exterior stair. Test the actual player capsule, step height, slope limit, camera height and movement speed.
6. Check the operator view from approximately 1.65 m eye height. Test whether the short routes feel useful before extending the forest route.

The material colors are placeholders. Texture UVs, lightmap UVs, final normals/bevels, LODs, production collision optimization, lighting and interactions remain for later passes. Do not treat this export as production-ready scenery.

## Validation

`validation_report.json` records the actual sample count and results. The final run checks 629 samples. The script tests floor support (allowing a maximum 220 mm deviation at small path joints), 2 m headroom, radial body clearance with a 280 mm radius at two body heights, each stair flight, and a ray from the operator's eye to the gondola. It also independently re-imports every FBX, compares bounds, and checks the number of collision hulls.

These checks are geometric samples, **not** continuous capsule sweeps or a substitute for UE5 CharacterMovement testing. The first check caught a blocked window sightline; the opening was widened before export. The final round-trip error is recorded in metres for each file.

## Iteration

Save hand-edited versions under a new revision name, e.g. `millford_v2_blockout_02.blend`. The builder is destructive to its own new scene and overwrites revision 01 outputs; it must be run in a separate background process, never against unsaved work.

From the repository root:

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup --python art/blender/scripts/build_millford.py
/Applications/Blender.app/Contents/MacOS/Blender --background art/blender/millford_v2_blockout_01.blend --python art/blender/scripts/validate_and_export.py
```

For the next design pass, prioritize the control-room proportion, the two stair approaches, and the feeling of returning from the yard. Terrain, roof silhouette and machinery detail should follow the first engine walkthrough.

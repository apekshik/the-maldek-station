# Millford / Maldek — rainy night revision 03

Open `millford_v2_night_03.blend`. Earlier revisions remain intact. The scene is based on the saved revision 02, not unsaved changes in another Blender window.

## Layout

The relay moves from (26, 1, 2) to **(48, 13, 3) metres**, approximately 25 m farther into the landscape. A wooded shoulder screens its approach. Two continuous Catmull–Rom path strips replace the separate ramp blocks and square joints. The terrain is graded beneath their full width, with a broad eastern shoulder replacing the accidental crater inside the former loop. The northern cliff beneath the gondola remains exposed.

The approach and return paths retain separate connections to the fuel yard and overlook. `route_points.json` stores the sampled curves. These are editable mesh strips in collection 09; regenerate the curve from the control points in `scripts/revise_night_03.py` in the parent Blender directory. Path material is wet gravel, not paving slabs.

The gondola line now extends roughly 380 m to a distant **Maldek terminal silhouette**, with sagging twin cables and three support structures. An overlook telescope points along the route. The far terminal is a composition and navigation landmark, not a second playable level or engineered cableway.

## Trees actually imported

The scene uses the three authored LOD2 variants from [Pine Tree 01, Poly Haven](https://polyhaven.com/a/pine_tree_01), modeled by Rico Cilliers with photography by Rob Tuytel. Poly Haven assets are [CC0](https://polyhaven.com/license). The 1K Blender source and its 18 accompanying maps were downloaded from the official API URLs and verified against the published MD5 hashes. Source metadata is in `assets/pine_tree_01.files.json`.

Trees use linked mesh data with varied scale and rotation. The selected texture maps are packed in the delivered file. These trees are substantially more detailed than revision 02's procedural placeholders. Even LOD2 is relatively dense; an Unreal handoff needs foliage instances, appropriate LOD/culling and a performance pass. The source download remains in `assets/` for reproducibility.

## Rain and night

Blender establishes the visual target: wet concrete/steel clear coats and variable roughness, warm interior light, cool dock lamps, local volumetric mist, lighter distant haze and static wind-slanted rain streaks. Rain is a still-render study, not an animated weather simulation. The existing gondola blockout remains angular; it is not yet a detailed reproduction of the supplied reference.

Saved cameras / preview files:

- `platform_rain.png`: low viewpoint beside the platform, looking toward the gondola.
- `control_room_night.png`: operator-height window view.
- `relay_terrain.png`: wider view of the relocated relay and continuous shoulder.
- `cable_route.png`: overlook view along the cable toward Maldek.
- `relay_daylight_layout.png`: separate daylight proof for inspecting the terrain and continuous paths. The saved scene retains its night lighting.

Use the Full Shell view layer for these renders. The Cutaway and Lower Level layers hide forest, fog and the distant route to make editing easier.

For the playable version, rebuild moving rain and impact splashes with Unreal's [Niagara](https://dev.epicgames.com/documentation/unreal-engine/tutorials-for-niagara-effects-in-unreal-engine), tune wet materials under the actual game lighting, and stage atmospheric depth with [Volumetric Fog](https://dev.epicgames.com/documentation/en-us/unreal-engine/volumetric-fog-in-unreal-engine). Rain sound, roof shelter/occlusion and weather transitions belong in that pass. This split lets the Blender renders guide the intended appearance while Unreal determines performance and player readability.

## Validation / handoff

`validation_report.json` records floor, headroom and approximate body-clearance samples, including the new relay route and actual terrain. These are sampled geometry checks, not continuous player-capsule sweeps. Revision 03 has no new FBX package; revision 02 exports do not include this terrain, relocated relay, new paths or distant terminal. Validate the changed layout in UE before relying on gameplay timing.

Rebuild from the repository root, in a separate background process. This overwrites revision 03; save manual edits under a new filename first:

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background art/blender/revision_02/millford_v2_cliff_02.blend --python art/blender/scripts/revise_night_03.py
/Applications/Blender.app/Contents/MacOS/Blender --background art/blender/revision_03/millford_v2_night_03.blend --python art/blender/revision_03/scripts/validate.py
```

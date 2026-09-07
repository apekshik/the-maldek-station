# Map to mood — short rendering demo

Separate film workspace based on the unchanged revision 03 scene. It does not use or modify the concurrent model-refinement files.

## Edit

16 seconds, 1280 × 720, 24 fps, silent H.264 MP4. The first six seconds show the actual HTML 2D plan, HTML 3D blockout and user-supplied Blender material-preview capture. These three documentary stills have subtle editorial push-ins. The remaining ten seconds contain four actual Cycles camera animations, 60 rendered frames each:

1. Front three-quarter exterior: gentle approach across the cliff face.
2. Platform: low dolly toward the gondola, with wet foreground reflections.
3. Control booth: short lateral move through the window composition, shallow foreground focus.
4. Pine reveal: lateral movement behind foreground branches, focus held on the station.

`deliverables/maldek_map_to_mood.mp4` is the assembled edit. The four numbered MP4s are clean individual shots without titles. `shots.json` records camera coordinates, focal lengths and aperture settings. `proofs/` contains checked camera endpoints and browser captures. `references/` preserves the supplied angles.

## Render choices and limits

- Blender 5.0.1, Cycles OptiX, RTX GPU, 48 samples with denoising, fixed seed.
- Exposure lifted from −0.35 to +0.15 in the film scene for small-screen readability. No architectural geometry or source materials changed.
- One linked instance of an existing Poly Haven pine is staged for the fourth shot only. Source trees and station layout are unchanged.
- Rain streaks, people, gondola and forest remain static source-scene elements; this is a camera-motion environment study, not animated weather or gameplay footage.
- Night atmosphere is intentionally dark. Spatial references guide composition rather than being exact camera matches.
- The current scene omits the operator mannequin in the booth render, keeping the window view unobstructed.
- Source pine asset attribution and CC0 provenance are in `../revision_03/README.md`.

## Reproduce

From the repository root, run Blender in a separate background process:

```powershell
& 'C:/Program Files/Blender Foundation/Blender 5.0/blender.exe' --background art/blender/revision_03/millford_v2_night_03.blend --python art/blender/render_demo/scripts/render_demo.py -- proof
& 'C:/Program Files/Blender Foundation/Blender 5.0/blender.exe' --background art/blender/revision_03/millford_v2_night_03.blend --python art/blender/render_demo/scripts/render_demo.py -- render
```

The renderer resumes existing numbered frames. Use a fresh output folder if changing camera or render settings; otherwise stale frames would mix with new frames. The saved demo Blender file contains all four named cameras; each camera's move uses frames 1–60. Foreground-pine visibility is selected by the script per shot.

Run `scripts/assemble.py` with Python containing Pillow and imageio-ffmpeg. Assembly verifies all 240 source frames exist, produces clean clips and builds the titled edit. No posting to social media is performed.

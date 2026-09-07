# Control room — visual fidelity sample 01

Editable asset: `Maldek_Control_Art_Sample.blend`. This is an isolated art sample, built from the measured control-room dimensions in `art/unreal_handoff/revision11/station_layout.blend`. No existing Blender source or Unreal map was changed.

## Review

- `renders/01_Assembly.png`: daylight assembly and material relationships.
- `renders/02_Player_detail.png`: glazing, corrugation, thresholds and real grating at close range.
- `renders/03_Night_material_study.png`: Blender lighting study with interior and entrance practicals. This is not an Unreal screenshot.

The control-room footprint is 5 × 4 m. The original 3 × 1.4 m north window, 1.2 × 2.4 m north doorway and 1.2 × 2.4 m west doorway are preserved. The sample origin is the room's southwest floor corner; translating by (-8, -4, 4) metres returns the architecture to its source Blender location. The wraparound deck, foundations and guard arrangement are proposed sample geometry; integrate with the evolving platform layout before replacing any level assets.

The sample includes continuous insulated wall cores, folded sheet cladding with thickness, structural posts, roof slab and overlapping edge caps, concrete upstands, framed glazing with seals and sill, open metal decking, retaining clips, underside joists, fasteners, conduit, drainage pipe, ventilation, signage and practical-light housings. The water-tower reference informs industrial assembly details; no water tower has been modeled in this pass. Interior equipment remains simple presentation geometry.

Cladding, steel and galvanized finishes use editable procedural Blender shaders. Concrete reuses the repository's `revision_02/assets/concrete_floor` scan, with reduced saturation. Images are packed into the Blender file. No new marketplace assets were purchased or downloaded.

## Validation and handoff

`verification_and_export.json` records 421 passing sampled rays through door/window apertures and against wall/roof enclosure. These are shell checks, not continuous player-capsule sweeps. The FBX round-trip bounds difference was below 0.000001 m.

`exports/SM_VF01_Control_Sample.fbx` contains evaluated render geometry and 22 named UCX collision hulls. Collision includes smooth proxies for the grated floor. The export has 101,532 vertices and 99,301 polygons before engine triangulation. It is a detailed review asset; modular splitting, performance budgeting and guard collision remain integration work.

FBX does not reproduce the procedural Blender materials. Material names and base parameters are in the verification manifest; recreate or bake these shaders for Unreal. The initial UV set is metre-scale box projection, not a packed lightmap atlas. Engine scale/orientation, shader appearance and gameplay collision have not yet been validated in Unreal. Do not replace live station meshes with this single combined sample.

## Reproduce

Run `scripts/build_sample.py` in a separate factory-startup background Blender process. It builds only this sample and renders three views. Then open the saved sample in a separate background Blender process and run `scripts/verify_export.py`. That script exports and reimports its own FBX without modifying the saved editable file.

Visual references: `art/metal-container-based-building.png`, `art/metal-container-based-buildings-set.png`, and `art/water-tower.png` supplied by the user.

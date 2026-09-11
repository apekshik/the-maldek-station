# Maldek parcels office — standalone editable package

`Maldek_Parcels_Office.blend` contains only `WSP_ASSETS`, in metres, at local origin. `Maldek_Parcels_Fitted_Review.blend` places that collection inside the frozen west-services scene. Reference architecture, cameras and lights must never be exported as parcels assets.

Assembly adds **(-37.45, -5.00, 4.60)** exactly once, with identity rotation and unit scale. The east orientation empty is deliberately off-centre at (6.4, 1.85, 0.1); +X points through the door toward the porch, +Y points toward the gondola. Use the full matrix in `assembly.json`.

## Contents and operation

- Pine shelving has four numbered bays at each of two deposit levels, plus two higher storage levels. Five independent belongings occupy 01, 03, 05, 06 and 08; three deposit bays and the upper shelves remain empty. All eight deposit anchors sit 1.5 mm above real shelf tops. The old suitcase is the hierarchy `WSP_Belonging_1`; moving or hiding that hierarchy does not modify shelving.
- The east counter has an open kneehole, lockable sliding drawer, original analog scale, paper-tag stack/dispenser, ruled ledger, pencils, string spool and stamp pad. The scale sits forward of the shutter sweep.
- The south cabinet has an actual wire front, keyed closure, open interior and three individually removable trays. Its hinged door opens before trays extend in the demonstration animation.
- The trolley is parked along the south edge, outside the central handling rectangle. Four casters have swivel pivots and separate axle pivots. The test envelope is 0.8 × 1.2 × 1.1 m.
- The entrance hinges inward toward the south side. The latch and key cylinder have separate pivots; exterior and interior hardware follow the same mechanism. Finished clearance between seals is approximately **1.324 × 2.223 m**, above a 12 mm threshold. Threshold slope/accessibility refinement and actual engine capsule handling remain integration gates.
- The fixed glazed sash has independently hinged internal shutters. The whole window fits the fixed aperture. Frames own the visible reveals; casings cover concealed butt contacts. No shell patch is necessary and no shell geometry is supplied in the asset file.

Frame 1 is closed/rest; frame 40 is open; frame 80 returns to rest. The secure door opens during frames 1–20, holds through 60, then closes. Trays extend 20–40 and retract 40–60. All moving assemblies remain separate and editable. Animation is demonstration data, not runtime behavior.

The guaranteed operator aisle is the 1.25 m strip X [3.00, 4.25], Y [3.25, 4.70]. It remains outside the fully extended drawer and handle. `operator_aisle_verification.json` checks that whole strip against closed geometry and sampled mechanism swept bounds. The adjacent 2.2 m handling zone is available in normal transit state; open cabinet use is a separate interaction.

`assembly.json` contains the exact four-name deletion list from the frozen master. Delete **only** those objects in later assembly, or replace only `WS_PARCELS_PROXY`. No rescue/power objects, shared shell, original meshes, runtime files or maps were modified. `collision.json` describes preliminary boxes in actual attachment-pivot space and sampled moving bounds. Do not box-fill shelf/cabinet openings. Engine collision must be built and tested later.

## Reproduce

Use Blender 5.0.1 background processes. Each script resolves paths from its own location and writes only this package directory. Run from any directory with absolute script paths:

1. `blender -b -t 4 --python <package>/scripts/inspect_reference.py`
2. `blender -b -t 4 --python <package>/scripts/build.py`
3. `blender -b -t 4 --python <package>/scripts/verify.py`
4. `blender -b -t 4 --python <package>/scripts/review.py`
5. `blender -b -t 2 --python <package>/scripts/verify_fitted.py`
6. `blender -b -t 2 --python <package>/scripts/collision_recipe.py`
7. `blender -b -t 2 --python <package>/scripts/check_surfaces.py`
8. `blender -b -t 4 --python <package>/scripts/review_extra.py`
9. `blender -b -t 2 --python <package>/scripts/finalize.py`

The review builder supports an optional `-- 05_tag_station` to render a selected named shot. It always reconstructs and saves the fitted review from the immutable master plus this asset file. `-- save_only` saves that review without matching any render shot.

## Evidence and limits

`reference_inspection.json` records the actual saved scene's proxy and relevant shell bounds. The source SHA-256 is checked against the master `delivery.json`. `verification.json` records evaluated manifold/degenerate-face checks, UV presence, dimensions/material slots per mesh, required anchors and sampled movement bounds after reopening the asset file. `fitted_verification.json` reopens the saved fitted file and checks removed proxies, frame/shell triangle intersections, major entrance/drawer/shutter sweeps and conservative walking/trolley boxes against the real shared structure.

Neutral review images cover the porch, both entrance sides, threshold, rear shelving, counter/window, tag station, secure cabinet closed/open and removal of the suitcase. Review-only room lights provide visibility; they are not an authored lighting installation.

Geometry checks are sampled Blender evidence, not an engine collision certification. The triangle checks target the important opening and mechanism interfaces; they do not prove every possible decorative-surface pair. Final integration must perform Unreal neutral/night/torch and moving glancing-angle reviews, save/reopen checks and actual capsule/trolley traversal. Shared architectural refinement belongs to the later integration task. FBX export, material bakes/atlases, engine import orientation, LODs and collision tuning remain outstanding. The asset meshes have independent usable smart UV islands; a production lightmap/atlas unwrap has not been authored. Font lettering stays editable as Blender text and must be converted in an export copy.

`surface_verification.json` additionally scans evaluated rectangular faces across objects for same-facing coplanar overlap. This caught casing corner overlaps, sash joins and tray rims during authoring; the delivered joints meet without those overlaps. The scan excludes rotated/curved/text faces and is not a general arbitrary-mesh theorem. Flexible weather seals intentionally contact the closed leaf and are excluded from physical blocking/sweep failures. Far-away context is hidden from rendering in the fitted review to reduce render cost; its objects remain in that copy.

## Materials and references

All geometry, lettering and material graphs are original. Materials are Blender procedural/constant shaders, including directional pine/kraft variation. No downloaded photographs or third-party textures are embedded or redistributed, so there are no external texture paths to pack.

The working arrangement adapts desk, paperwork and pigeonhole logic described by [Railway Archive](https://www.railwayarchive.org.uk/the-offices), and modest parcels/lost-luggage identification from [Cumbria Archives image 3925](https://www.sankeyphotoarchive.uk/collection/view/?id=8960). The [Harcourt photographic record](https://www.victorianrailways.net/photogallery/northmid/harcourt/harcourt.html) and [Rushden station rooms](https://www.rhts.co.uk/transport-museum/find-out-more/) remain supporting references, not dimensional or historical-accuracy claims. No archival artwork was copied into a texture.

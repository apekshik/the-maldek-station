# Windows handoff and model refinement plan

September 6, 2026. Planning handoff only: no model changes were made for this request.

## Starting point and intent

Snapshot `830a3f0` contains the V1/V2 website, Blender revisions 01–03, render previews, source assets, generation scripts, validation reports and older FBX exports. It was applied on top of the newer GitHub history, preserving the UE5 scaffold. Blender/FBX files use Git LFS alongside Unreal assets and maps. Local Blender backup saves and Python caches are excluded.

Open `art/blender/revision_03/millford_v2_night_03.blend`. Read its `README.md`. Keep it as the baseline; create `revision_04/millford_v2_detail_04.blend` for the next pass. The current file includes the open drive gallery, six-metre gondola, relocated relay, continuous paths, textured pine forest, distant Maldek silhouette and rainy night lighting.

The target is a convincing assembled industrial place at player-eye distance. Spend geometry on silhouette, edge highlights, depth and visible connections. Use textures/decals for fine surface variation. Avoid a whole-scene overhaul or detail that disappears in the actual camera. Preserve the accepted layout and gritty concrete/metal character.

## Windows setup

For a new checkout, install Git with Git LFS, then run:

```powershell
git lfs install
git clone https://github.com/apekshik/the-maldek-station.git
cd the-maldek-station
git lfs pull
git lfs fsck
```

For an existing clean checkout, use `git pull --ff-only` followed by `git lfs pull`. If local changes or history divergence prevent that, preserve them and inspect the divergence; do not reset away Windows work. The upstream history had already been rewritten before this handoff.

The `.blend` must be a real binary file, not a short LFS pointer. The delivered scene packs its textures; verify no missing-image warnings or pink materials on Windows. Source assets are retained under revisions 02 and 03. The Mac checkout skipped downloading the newly discovered Unreal LFS assets; the Windows `git lfs pull` step hydrates them.

Use Blender 5.0.1 initially to match the saved scene. Enable the RTX 5070 Ti in **Preferences → System → Cycles Render Devices → OptiX**, then choose **Cycles → GPU Compute** in Render Properties. Verify the device is available and a small render works with the installed driver. These two settings are separate; the Mac source scene/generator uses CPU rendering. See the [Blender GPU rendering documentation](https://docs.blender.org/manual/en/5.0/render/cycles/gpu_rendering.html).

Render the existing platform camera first at the saved 1400 × 930 / 40 samples. Record render time, device, memory usage and visual issues. Compare against `revision_03/previews/platform_rain.png` before changing lighting or samples. After the baseline, try 1920-pixel output and 128 samples for presentation, keeping denoising; tune from measured noise and memory use rather than assuming higher samples fix geometry.

The existing Unreal project is `game/game.uproject`, associated with **UE 5.7**. It includes a BlockOut map, a gondola-system asset and UltraDynamicSky content. Inspect their actual state on Windows before creating replacement systems. They have not been opened or validated during this Mac session.

A supplementary [eight-shot map tour](revision_03/tour/README.md) was rendered after the handoff snapshot. Use it for context; close-up neutral/material audit captures are still the first modeling step.

## First action: screenshot and reference audit

Existing renders already show the main weaknesses: the gondola reads as a sharp rectangular shell; rail intersections look like intersecting bars; concrete slabs have little assembly detail; lamps are luminous boxes; equipment and controls remain primitive forms. The next session should capture fresh screenshots of the actual objects before editing, rather than rely only on the atmospheric views.

Create `revision_04/audit/before/` and matching `after/` captures. Use the same camera, focal length, exposure and framing for each pair. Capture a neutral/clay view, a grazing-light material view and the relevant night view. Keep viewport captures distinguishable from final renders.

| Subject | Required view | Questions to answer |
|---|---|---|
| Gondola | Front three-quarter, side, boarding threshold, hanger | Which corners need rounding? Where do skin, frame, glazing and hardware meet? |
| Railing/stairs | Player eye, one post base, stair-to-landing joint | Can we read tubing, fasteners and attachment to the deck? |
| Platform | Low grazing angle and top-down joint layout | Is surface relief believable? Do drainage and material boundaries make sense? |
| Canopy/structure | Underside and post/beam connection | Does the roof have thickness, edges, brackets and plausible connections? |
| Drive equipment | Flywheel/motor at service distance | Which few housings, mounts and cables convey machinery? |
| Control room | Operator view and desk detail | Do controls, casing edges and window trim read beyond primitives? |
| Relay/terrain | Doorway, path shoulder and foundation | Are joins grounded and readable without adding clutter? |
| Cable route | Existing overlook view | What actually survives at that distance? Keep remote detail coarse. |

Use the supplied `docs/assets/reference/gondola-red-docked.png` as the primary mood/shape target. Collect a few real reference views per selected object, with source links and notes about construction, silhouette and scale. Online photos are references, not automatically licensed textures. Capture or download reference imagery only where permitted; record licenses for any meshes incorporated.

## Ranked implementation passes

### 1. Gondola silhouette and component layers

Largest focal object in both platform and control-room views. Keep the accepted length and boarding opening. Round the main body corners selectively; add a shallow roof crown/lip, inset window frames, rubber-like seals, lower skirt and a readable sill. Add a small repeated set of panel seams, handles and fasteners where assembly calls for them. Improve the hanger with a few brackets/pivot forms.

Start with silhouette and frame depth before rivets. Use modest geometry bevels with angle-aware shading; inspect existing modifiers to avoid doubling bevels. Preserve crisp panel planes. [Blender's bevel modifier](https://docs.blender.org/manual/en/4.4/modeling/modifiers/generate/bevel.html) documents the relevant geometry controls. [Doppelmayr/CWA cabin imagery](https://www.doppelmayr.com/en/cwa-cabins/) is useful for studying frame/glazing/body separation; adapt those observations to the older red industrial reference rather than copying a modern cabin design.

### 2. One coherent railing and stair hardware kit

Build one post/base, one rail span, one corner and one stair transition. Replace square-looking rail stock where tubular construction fits. Add visible tube ends/caps, base plates, a few bolt heads and either welded collars or clamp fittings. Use the same construction family across the dock and service stairs, with coherent material treatment. Keep existing routes and guard extents.

[Kee Safety's modular railing system](https://www.keesafety.com/safety-railings/kee-klamp) provides a clear reference for how separate tubes and fittings form an assembly. Its [component catalogue](https://www.keesafety.com/media/a21h2w1n/kee-safety-components-catalog.pdf) is a useful visual source for flanges and connectors. This is visual reference, not a claim that our blockout is structurally certified. Also revisit the Fab mesh shortlist in `revision_02/ASSET_RESEARCH.md`; use a purchased kit only if its format, license and style fit. No further asset purchase is required to begin.

### 3. Platform surface and slab edges

Give concrete a small number of meaningful joints, chamfered edges, inset access covers and drainage details. Add broad, very shallow mesh variation where it improves grazing highlights—start around 2–5 mm over roughly metre-scale spans as an artistic trial, then inspect from player height. Mask thresholds, stair connections and equipment pads to retain alignment. Keep collision simple and recheck walking routes after any change affecting feet.

Separate broad shape from fine roughness: mesh relief for visible profile changes, bump/normal detail for aggregate, roughness masks for damp patches and puddles. Concrete should not acquire random metal rivets; fasteners belong on bolted plates, covers and steel assemblies. Avoid uniform noisy displacement or a blanket mirror-like wet coating. Use slab/joint photos to guide composition; [NRMCA's Concrete in Practice index](https://www.nrmca.org/association-resources/research-and-engineering/cip/) identifies relevant jointing and finishing references, not a specification for this suspended platform.

### 4. A few secondary objects, after the first three pass review

Replace lamp cubes with simple shades, stems, lenses and mounting plates. Add roof edge trim/gutters, beam end plates and selected brackets visible from below. Refine the motor with a housing, end caps, mounting feet and cable conduit; add a few casing seams, switches and labels to the control desk. Reuse a small detail library. Keep distant structures and hidden equipment simple.

## Review gates and scope control

Complete one representative gondola corner/window, one railing span/base and a small platform patch first. Compare neutral and night before/after captures. Expand only when the improvement is visible in the existing cameras. Suggested detail sizes are starting points, not measured construction specifications.

A pass is successful when edges catch light naturally, assemblies read as connected parts, material scale is coherent and silhouettes remain clean. Reject rounded-over slab shapes, lumpy steel, excessive rivets, stretched textures and wetness that makes every material look identical. Keep the frame focused on the gondola and route; clutter is not the goal.

Track object/triangle count, linked-instance reuse, render time and GPU memory for each batch. Keep modifiers editable in the source. Check normal orientation, intersections, texture packing and the camera sightlines. Re-run route/headroom checks when geometry near the player changes. The existing 982 samples are a baseline, not continuous capsule testing.

## Unreal handoff after the visual pass

Revision 03 has no refreshed FBX package. Revision 02 exports are older than the relocated relay and new paths. The current exporter builds geometry from raw mesh vertices; update it to export evaluated modifier results and preserve UVs/normals before expecting new bevels and surfacing to survive the handoff. Keep source objects editable and bake export copies only.

Retain metre units, the gondola movement parent/pivot and common-origin fixed chunks. Export simple collision separately from decorative relief and hardware. Check the 1 m scale cube, door/stair collision and operator sightline in UE5. Inspect the existing weather setup before implementing rain, splashes, wetness and sound. Blender remains the look-development source; final player readability and performance are assessed in the engine.

## First Windows session deliverables

1. Verified LFS checkout and GPU baseline render.
2. Before-image audit/contact sheet with a short ranked issue list and reference links.
3. Revision 04 containing only the three representative refinements above.
4. Matching after-images and brief measurements; decide what to propagate next.

Continue with this instruction: “Read art/blender/WINDOWS_HANDOFF_AND_REFINEMENT_PLAN.md, verify the Windows checkout and RTX render setup, capture the baseline audit, and begin the three representative refinements. Preserve revision 03 and the existing UE5 project.”

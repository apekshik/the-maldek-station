# Millford refinement 04 — first four-area pass

Open `millford_v2_refinement_04.blend`. This is independent of `revision_03` and `revision_04/millford_v2_detail_04.blend`, which remain the rendering-demo baseline. Existing Unreal files are untouched.

## What changed

- **Gondola:** corrected misplaced glass and vertically oriented rub strips; built a rounded crown roof and drip lip, framed windows with separate seals/glass, paneled lower skins, horizontal rub rails, entry handles, sill, undercut skirt and a bolted hanger saddle/pivot. The accepted boarding opening and movement parent remain.
- **Control room:** replaced the console's render box with a plinth, folded enclosure, sloped panel, three analog gauges with ticks and needles, switches, emergency stop, service doors and latches. Added window trim, conduit, clamps and a junction box; reduced oversized wall bump.
- **Lower drive:** separated the intersecting motor/wheel placeholders into a finned motor, terminal box, coupling, reducer, output shaft, bearing, grooved wheel, brake and mounted bases. Cross supports connect the motor feet to the skids.
- **Platform:** panelized render surfaces with recessed seams, restrained 1.5 mm relief, finer aggregate response, a recessed hatch and grated drain. Replaced upper platform guard stock with tubes, sockets, collars, base plates and shared hex fasteners. Grated dock edges receive toe plates.

This is an assembly-detail pass, with intentionally restrained weathering. The new concrete is less uniformly glossy than the original. Local wetness, exposed corner weathering and rain-responsive materials can be tuned in the next art review.

## Inspect

The `CAM_R04_Gondola`, `CAM_R04_Controls`, `CAM_R04_Drive` and `CAM_R04_Platform` cameras bookmark the four areas. The original night cameras are retained. Details remain in the original named subject collections, with `R04_` object names and editable bevels, normals, glass thickness and recess modifiers.

The opened review window starts in an isolated gondola material view. **Numpad /** exits local view to return to the complete scene. Other subject collections can be isolated in the same way.

`audit/before/` and `audit/after/` contain matching Cycles images. Four isolated studio material pairs and two night-camera pairs are provided. These are renders, not screenshots. `REVIEW.md` presents the pairs. Construction research and its application are in `REFERENCES.md`.

## Verification

- The preserved revision 03 SHA-256 matches the pre-edit hash (see `build_report.json`).
- Reused all **982 route/clearance samples** from revision 03, now evaluating modifiers and including new decorative meshes except glazing. No issues; operator-to-gondola sightline clear. This remains sampled geometry validation rather than an Unreal capsule playtest.
- Reviewed isolated before/after renders, then corrected window-end gaps, mounting support and wheel silhouette smoothness.
- Reviewed the original platform and operator night cameras with unchanged framing and lighting. After renders took 9.642 and 10.095 seconds at 1400 × 930 / 40 samples on this run. Concurrent GPU activity makes these observations unsuitable as a controlled performance comparison.
- Visible evaluated triangle totals: gondola 52,100; control room 26,228; lower drive 22,920; upper platform 104,516. These include existing visible geometry in each collection. See `mesh_statistics.json`.
- New bolts reuse mesh data by size/area. The scene remains an editable Blender look-development asset; small repeated pieces should be instanced or consolidated for the eventual game export.

## Limits and next review

Earlier shell/platform meshes remain hidden as simple collision proxies. New drive solids are included in geometric checks. The evaluated FBX package and first Unreal integration are now in `art/unreal_handoff/`; open `/Game/MaldekRefinement/Maps/BlockOut_R04` in Unreal. See that handoff README for collision, gondola and supplemental terrain checks. The drive assembly is an artistic layout, not a complete engineered ropeway or animated belt system. Door operation, glazing collision, production LODs and game performance remain future work.

Review the body/window proportions, console height/readability, drive assembly spacing, and concrete/steel finish balance before adding more small detail. Secondary lamps, the remaining site railing family, full weathering and cable reeving have not been expanded in this pass.

## Reproduce

Run scripts in a separate Blender process, with `revision_03/millford_v2_night_03.blend` as input for `scripts/refine.py`. It writes this revision's named output file, so save manual edits under a new filename before regenerating. `scripts/audit.py -- before|after` renders the file loaded by Blender; `scripts/night.py -- before|after` renders the saved night cameras. `scripts/validate.py` validates whichever scene is loaded, writing results here.


# Shared authoring contract

Repository: `C:/Users/apek-anna/Developer/the-maldek-station`.

Read repository `AGENTS.md` and `art/MESH_AUTHORING.md` before modeling. Current approved layout/material source:

`art/blender/passenger_lodge_03/Maldek_Passenger_Lodge_Materials.blend`

Working scene: `05_Material_Study`. Hide `PL03_Removable_Roof` for interior work. Read its README, `material_report.json` and `verification.json`. Source SHA-256 recorded at handoff: `b9d78ed0d7c5c50bc28a8fb6a0d63f1c86fa83d3144c6a7eae50476ee9607796`. Verify the actual source before work; report any mismatch and inspect its changes rather than blindly using stale dimensions.

The source is a material mockup, not a finished building. Layout dimensions come from `art/blender/passenger_lodge_01/scripts/build.py`; source-relative placement comes from lodge 02. Existing source reference geometry may contain obsolete fittings: inspect ownership before reusing an object. Relevant render scripts and images are in lodge 03.

## Fixed layout and style

- Blender coordinates are metres, Z up; finished lodge floor is Z=4. Source local layout maps to station by `(x - 24.1, -depth + 4, z + 4)`. These are not Unreal transforms.
- Main hall is 14 × 11.2 m; six picnic tables and twelve benches remain. Preserve lockers on the current rear wall, the screened restroom hallway and enclosed coffee annex.
- Preserve existing control/quarters, gondola, platform, grated floor, corrected stairs and rails. Keep level right-side access at the top of the bypass stair open. No internal door to control.
- Warm early-1990s visitor station: practical metalwork, petrol paint, galvanized steel, cream enamel, pine and restrained wear. Avoid generic sci-fi detailing or blanket damage.
- Reuse station materials where appropriate. Baked textures/export-ready materials are later integration work; clearly identify any procedural Blender-only materials.

## Parallel file ownership

Use only the output directory assigned by your handoff. Append reference geometry or copy the source into that directory for fit checks; never save over lodge 01/02/03, another package, the live map or existing door studies. Do not alter shared source mesh data indirectly through linked collections.

Keep finished assets in the named package collection. Mark retained source context as reference-only and exclude it from delivery exports. Keep movable leaves, handles and hardware separate, with real hinge pivots and sensible local origins. A local asset origin plus a documented source-scene assembly transform is preferred over undocumented recentering.

If a reveal or clearance needs a master-wall change, demonstrate it in the package review copy and supply a narrowly scoped patch manifest/script. Do not change the master. Opening-specific core/reveal patches belong to that opening's task; no task owns a whole shared wall.

## Deliverables and verification

Deliver an editable `.blend`, reproducible authoring/verification scripts, README, replacement manifest and review renders in your package directory. Include:

- Original proxy names replaced; new object/collection names, dimensions, material slots, assembly transforms and moving-part pivots.
- Any required wall/cladding patch, stated exactly and confined to your openings.
- Close neutral-light renders from both sides, player-height fitted context, and useful mechanism poses. Use temporary review lights if necessary and label them.
- Saved/reopened geometry checks for topology, surface ownership, openings and relevant reach/swing/walking clearance. Distinguish proxy layout checks from actual engine collision.
- A concise list of remaining integration work and limitations.

Work on the Blender package now; do not start Unreal, import assets, modify runtime logic, install sounds or claim PIE validation. The live editor is shared with other tasks. No new image generation is required for these mesh packages. Never copy API credentials into scripts, handoffs or commits.

Respect unrelated working-tree changes. The user wants completed work pushed to the remote: stage only your package, inspect the staged diff, then commit/push using the repository's current workflow. Do not switch shared checkout branches or run destructive cleanup while other tasks are working. If a concurrent push intervenes, coordinate instead of rewriting another task's changes.

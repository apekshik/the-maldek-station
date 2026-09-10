# Combined station blockout 02

`Maldek_Combined_Station_Blockout.blend` is a separate Blender placement study built from lodge 01 and its appended VF07 reference. Unreal and the source files are unchanged.

The working scene is `04_Combined_Station_Blockout`. Earlier interior/reference scenes remain available. The lodge moves to (-24.1, 4, 4) metres in the Blender station coordinate system: expansion goes west/north of the old hall, shifting the south arrival flight and turn 1.5 m west. A 2 m strip between lodge and control forms the bypass. This is a blockout placement, not an approved Unreal transform.

The old waiting hall, public deck and affected guards/supports are excluded from this scene. Retained east rails/supports are linked back unchanged. Old hall fittings intersecting the new footprint are retired only in this scene; other objects from their collections are relinked. Replacement deck rectangles avoid the new lodge floors and stair landing; west perimeter rails follow the enlarged footprint. The relocated arrival stair, control, quarters, gondola and machinery remain reference geometry. New deck material is a solid placeholder for later grating/plate detailing.

The second stair runs along the right side of the bypass, with a turning upper landing. Its lower tie-in is provisional and requires terrain/service-yard verification before integration. Support probes and route samples are recorded in `fit_report.json`; do not interpret source preservation as complete collision validation.

Review the combined overview and plan before detailed shell work. Rebuild using Blender 5.0 `--background --python art/blender/passenger_lodge_02/scripts/build.py` from the repo root. Before Unreal integration, resolve all reported route failures, lower landing fit, structural ground contact, roof/quarters clearance and the actual player capsule. Earlier web-plan dimensions are design intent; this file is the first source-relative fit study.

Validation is in `verification.json`: saved/reopened new meshes and sampled route floor/headroom checks. A 2 mm contact patch resolves rays exactly on a shared slab boundary. The original grating stair is preserved, not re-certified by these point-ray tests. The second stair has a 2 m upper landing; its lower approach remains a separate terrain-fit task before final placement approval.

## Edge refinement

The west promenade is reduced from 7.35 m to 5.35 m. The original arrival assembly moves 1.5 m west in the combined scene, with its deck opening and guards following it. An obsolete projecting deck tab is removed. The right stair now has a full opening through every replacement deck slab, including the east platform footprint. Both lower stair approaches require terrain-fit review before integration. Source reference scenes retain their original geometry.

Rebuild the refined version with scripts/build.py, then scripts/finish_edges.py, then scripts/verify.py (each through Blender --background --python). The finish pass rebuilds intermediate guard posts and re-probes the moved outer supports against terrain.

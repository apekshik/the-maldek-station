# R06 — snowy cliff and forest study

Level: `/Game/MaldekRefinement/R06/BlockOut_R06` (Unreal Engine 5.7).

The R05 station and integration were checkpointed in commit `0658a2e` before this pass. R05 and the original BlockOut remain available. This pass modifies a separate level and new R06 assets.

## Cliff

The shape follows the north-facing gorge described in `art/blender/scripts/revise_night_03.py` and the refined Blender scene. The broad fill immediately in front of the lower deck is removed, revealing a gorge approximately 23.5 metres below the lower floor. The relay shoulder and both paths stay in place.

The existing Gaea landscape also occupied the gorge, so its R06 heightmap is locally lowered underneath the new terrain. Exactly 2,800 height pixels are changed. RG height data made a byte-exact round trip through Unreal before import; the rest of the landscape is retained. Collision traces after reopening R06 confirm the drop rather than an invisible old landscape shelf. This pass establishes the visual and collision geometry of the fall; it does not add a fall-death trigger.

## Trees

The project already has Megaplant species, including skeletal Aleppo pine variants. For this static environment study we reused the three Poly Haven CC0 pine variants from the Blender scene. Attribution/source metadata remains in `art/blender/revision_03/README.md` and its assets folder. Each variant was reduced to 18% of the Blender mesh triangle count before export, then given four Unreal LODs. The 160 trees are foliage instances with varied scale/rotation and 120–180 metre culling, placed clear of paths, the gondola corridor, and the immediate station footprint. Their alpha-masked foliage uses the source texture; upward-facing surfaces receive snow shading. Tree collision and wind animation are not part of this pass.

## Winter atmosphere

The existing Ultra Dynamic Sky and Weather actors are retained; their Fog value is 6.5. Landscape snow coverage is restored with a subdued blue-grey tint. The local terrain uses slope-based snow, leaving the cliff face darker, and exposed roofs, upper platform and overlook receive matching snow shading. This is an appearance study: a complete weather transition, shelter accumulation and precipitation pass is deferred.

## Checks and limits

Reopening the saved level retained all 160 foliage instances, the fog settings, and the carved landscape collision. Reports: `reload_verification.json`, `cliff_validation.json`, `heightmap_import.json`, `tree_lods.json`. R05's previous path checks remain relevant, but a complete new gameplay traversal is still needed. No 1440p/60 FPS performance claim is made from these still captures. Terrain transitions and snow materials remain suitable for iteration rather than final art.

`final_renders` contains current views; `first_renders` contains intermediate diagnostic views. PNG height data in this folder is encoded terrain data, not a color photograph.


The extra 10_cliff_inspection image uses temporary fill lights to make the gorge geometry legible. Those lights are removed after capture and are not saved in the level. The normal night view into the gorge is deliberately very dark.

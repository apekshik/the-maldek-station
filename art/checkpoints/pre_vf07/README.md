# Pre-VF07 migration checkpoint

Saved 2026-09-07 before replacing any playable station geometry.

- `unreal_saved.json`: saved Forest_Approach_Test actor/component inventory (214 actors), transforms, parents, mesh/material and collision bindings.
- `Unsaved_VF06_Review.blend`: copy of the unsaved open VF06 review. The approved VF07 source remains unchanged.
- `blender_dependencies.json`: read-only audit of 23 Blender sources; no unpacked missing external images or missing linked libraries.
- `development_editor_build.log`: Win64 Development Editor build succeeded with UE 5.7.

## Dependencies and exclusions

Use Git LFS to retrieve `.blend`, `.fbx`, `.uasset`, and `.umap` files. Unreal Engine 5.7 and its enabled ModelingToolsEditorMode, StateTree, GameplayStateTree, and ProceduralVegetationEditor plugins are required. Editor scripting uses PythonScriptPlugin and EditorScriptingUtilities.

Gaea2Unreal 2.0.0.15 is installed locally in `game/Plugins/GaeaUnrealTools` with UE 5.7 compatibility adjustments. Its licensed vendor source stays excluded by `.git/info/exclude`; install an equivalent compatible plugin separately on another machine. The engine-level copy also exists locally. This checkpoint does not claim to distribute that dependency.

Existing credential, cache, build-product, `.blend1`/`.blend2`, local generated H3 output and vendor-plugin exclusions are preserved. The empty FAL_KEY example is a template, not a credential.

The R12 migration starts only after main and LFS have been pushed and a separate checkout verifies retrieval. Its rollback tag is `pre-vf07-unreal-migration`.

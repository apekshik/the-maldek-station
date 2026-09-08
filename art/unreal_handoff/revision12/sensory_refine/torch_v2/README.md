# Stronger idle, louder feet, and reference-led flashlight

Current saved pawn: footstep volume 3.5 (+4.86 dB over the previously approved 2.0); idle sway 5.0 (2.5 times the approved 2.0). HeadBobScale 1.5, WalkSwayCm 1.8, RunSwayCm 3.0 and GroundHeightResponse 18 remain unchanged.

The held assembly now follows the actual additive camera view transform, with independent hand movement scaled to 0.15. Camera motion no longer makes the flashlight drift in the opposite direction. The oversized spherical GlovedThumb placeholder is hidden when using the detailed torch. The old spherical switch is replaced by a flat switch in the new mesh.

Reference: https://maglite.com/products/ml300l-led-2-cell-d-flashlight (official product photo inspected). The model follows its 231.8 mm length, 38.1 mm barrel and 57.15 mm head proportions, with original in-game markings. Field_Torch_V2.blend retains named editable parts and an export mesh. The FBX has 56,308 triangles. Seven material slots, no collision. Source and prior torch remain available.

Validation: native gameEditor build succeeded; final player checks passed with unchanged walk/run lateral travel (~5.4/9 cm), strong idle displacement, steady collision capsule and unchanged aiming input. Maximum relative torch translation was 0.123 cm during the sampled idle/walk/run sequence. Focus, toggle and sprint checks pass. The final in-game screenshot was inspected. Saved pawn values were verified before a clean restart. Map was not modified in this pass.

Audio: 4.0 was auditioned, then trimmed to 3.5 for headroom. The final mixed recording contains 48 near-full-scale samples out of 1,878,016 (peak 0.99985); this is not a claim of clip-free output or subjective listening approval. The intermediate stronger/walking_mix.wav was muted by Unreal's background-focus setting and must not be treated as evidence of silence in gameplay. The final recording used a temporary launch-only UnfocusedVolumeMultiplier=1, removed by reopening the editor normally afterward.

Reproduction: build_field_torch_v2.py in Blender; compile native editor; import_field_torch_v2.py via owned Unreal dispatcher; sensory_refine_validate.py with output sensory_refine/torch_v2/final, idle_max 2.8, idle_min_range 3.8, check_held true. Finish with saved-property verification. Packaged executable not rebuilt; forest and door tasks retain ownership of their concurrent map/content work.

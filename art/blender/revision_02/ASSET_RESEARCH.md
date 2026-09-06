# Industrial deck and stair asset research

Reviewed September 6, 2026. No marketplace mesh has been purchased, downloaded or installed. The current fitted stairs, grating, trees and terrain are authored study geometry.

| Option | Fit for this station | Access / integration |
|---|---|---|
| [Modular Industrial Catwalks Set — Universal Constructor](https://www.fab.com/listings/522128db-02fa-44f3-8a18-359a6bc291f5?lang=en) | Strongest coherent family: floors, rails, beams, stairs, ladders and trusses; customizable paint, rust, steel and dirt. Modular grid. | Fab listing supplies Unreal Engine format; license/purchase required. Treat as a potential UE replacement kit, not a verified Blender source pack. |
| [Industrial Stairway — lyoshko](https://www.fab.com/listings/515d5191-62c6-44d6-9ad0-37baadef8066) | Walkways, supports and stairs share a customizable material. Smaller focused alternative. | Unreal Engine format; license/purchase selection required. Not imported. |
| [Industrial Stairs — BlenderKit](https://www.blendkit.com/asset-gallery-detail/f7d34191-665f-45ad-9308-91f6b55f5c72/) | Free-listed Blender stair model worth evaluating for close-up detail and stringer construction. | BlenderKit account/add-on download flow. Exact asset license and suitability must be checked before incorporating it. |

Recommendation: choose one rail/stringer/grating family across the service level. Use weathered concrete for fixed slabs and retaining foundations; dark painted steel for supports and stairs; galvanized grating for walking surfaces; oxide-red sheet steel for the gondola. Cohesion comes from construction and shared surface treatment, not making every part concrete.

## Assets actually incorporated

Downloaded 1K diffuse, roughness and displacement maps from Poly Haven, checked against the API-provided MD5 hashes, and packed them into the Blender file:

- [Concrete Floor](https://polyhaven.com/a/concrete_floor)
- [Rusty Painted Metal](https://polyhaven.com/a/rusty_painted_metal)

Poly Haven publishes its assets under [CC0](https://polyhaven.com/license). Source maps and API metadata are retained in `assets/`. Displacement maps drive shader bump, not additional geometry. These surfaces are a material-direction study; final UVs, weathering masks and Unreal materials remain to be built.

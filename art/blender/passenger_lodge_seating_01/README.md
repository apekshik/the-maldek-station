# Passenger lodge seating kit

Editable six-table / twelve-bench package for handoff 05. Open `Maldek_Passenger_Lodge_Seating.blend` in Blender 5.0.1. It opens fitted to the approved lodge, with the removable roof hidden. The source master is unchanged.

## Contents and ownership

- `PLS_Seating_Kit`: delivery collection, six identifiable `PLS_Group_01` through `06` floor-origin assemblies, 559 mesh objects sharing 17 meshes (542 linked uses beyond the first). Five table planks and two planks per bench; rounded 6 mm finished edges, transverse bearing rails, splayed timber legs, upper spines, lower stretchers, diagonal braces, thin flat floor shoes, petrol steel ties and galvanized hex heads with annular washers. One underside mending strap on group 03's north bench.
- `REFERENCE_ONLY_Source_Context_DO_NOT_EXPORT`: local fitted context. Never include in a furniture export. It preserves the source walls, lockers, service furniture, access routes and station structures. All 90 old table/bench components are removed from this review copy only.
- `REVIEW_ONLY_Lights_Cameras_Human`: temporary neutral softboxes, six cameras and a seated scale block figure. Exclude from export. No moving mechanisms, hinges, wall patches or character delivery.
- `replacement_manifest.json`: exact removed names and source collections/bounds, every new object's parent, dimensions, local transform, mesh and material slots, and all group transforms.
- `source_inventory.json`: the 90 actual inspected source pieces, including material-pass planks and earlier leg/support proxies.
- `verification.json`: saved/reopened evaluated topology, packed textures, context preservation, footprint routes, floor contact and seated-reference checks.
- `REFERENCES.md`, `texture_api.json`, `textures/`: online construction references, CC0 texture provenance and three packed-and-external stained-pine PBR maps.

## Dimensions and fit

All coordinates are Blender metres, Z up. Group roots are at the tabletop XY centre, Z=4. All root rotations are zero; scale is one. Children retain useful local component origins. The first group supplies the reusable table/two-bench base; all other groups share its meshes, except the single repair strap.

| Group | Root X | Root Y | Root Z |
| --- | ---: | ---: | ---: |
| 01 | -19.2 | 2.5 | 4 |
| 02 | -13.2 | 2.5 | 4 |
| 03 | -19.2 | -0.7 | 4 |
| 04 | -13.2 | -0.7 | 4 |
| 05 | -19.2 | -3.9 | 4 |
| 06 | -13.2 | -3.9 | 4 |

Table top envelope is 1.8 x 0.8 m, with a 0.78 m upper surface. Each bench is 1.8 x 0.35 m, upper surface 0.48 m. Both heights are a proposed 30 mm reduction from the mockup: this brings feet closer to the floor while preserving the 300 mm seat-to-table difference. Each top is 45 mm thick, with 4 mm board gaps. Benches remain at local Y +/-0.775; the whole group stays inside the original 1.8 x 1.9 m footprint. No group was relocated.

The middle seating bay has at least 1.195 m between supports, 95 mm above the scale figure's 640 mm knee envelope to the 735 mm tabletop underside, and a 200 mm horizontal gap from bench front to table edge. The centre spine and stretchers stay inward of the figure's knees/feet. The 1.75 m-equivalent figure is an approximate proportion check, not an anthropometric certification. Benches have narrow footprints inherited from the mockup; assess tipping and load stability before physical manufacture.

## Materials and review

The pine uses Poly Haven's scanned stained-pine color, roughness and OpenGL normal maps, with restrained normal strength and a light varnish response. Eight single-board atlas strips vary knots and scratches between linked objects. End faces have a separate, stain-matched procedural growth-ring material. Station petrol paint and galvanized metal are reused. The atlas selection, procedural end grain and station materials need baking/export conversion later; this is not an engine-ready material claim.

The six PNG reviews show isolated oblique and reverse sides, low underside construction, a fitted player-height view at 1.65 m, an overhead view of all six groups, and a seated-reference side view. Temporary lighting and roof removal are deliberate review conditions. `scripts/render.py` reopens the saved package and changes visibility for each render without saving those temporary states.

## Reproduce

Set `MALDEK_SOURCE_REPO` to a checkout containing the approved lodge 03 source if it is not at the handoff path. From the asset repository, run these in order with Blender:

```text
blender --background --python art/blender/passenger_lodge_seating_01/scripts/inspect_source.py
blender --background --python art/blender/passenger_lodge_seating_01/scripts/build.py
blender --background --python art/blender/passenger_lodge_seating_01/scripts/verify.py
blender --background --python art/blender/passenger_lodge_seating_01/scripts/render.py
```

Textures are already included. To retrieve the identical files, run `scripts/download_textures.ps1`. The builder refuses a changed source SHA-256. It only writes into this package directory. The shared source must match `b9d78ed0d7c5c50bc28a8fb6a0d63f1c86fa83d3144c6a7eae50476ee9607796`.

## Verification limits and integration

Saved/reopened checks evaluate every unique mesh for closed manifold edges, nonzero face areas and positive volume; assert removal of all original seating pieces; compare every retained source object's world transform and mesh geometry/material slots; verify all six furniture bounds and ground contacts; check all 72 brace-to-spine/stretcher surface intersections; reject seated-figure/furniture AABB penetrations; and check sampled 0.6 m-wide routes against conservative full furniture footprints. Intentional concealed timber joints and hardware contacts are not boolean-unioned. Topology is per component, not a claim that the whole furniture assembly is one watertight solid.

Remaining integration: accept the proposed height correction, bake materials and atlas variations, decide merge/instance export granularity, create collision and LODs, then validate actual Unreal capsule routes, seating animation/reach and lighting after integration. No Unreal, live map, runtime interaction, sitting animation or PIE validation was performed. Architectural openings and cladding need no change for this kit.

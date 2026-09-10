# Passenger lodge lockers 01

Twelve individually identified sheet-metal lockers on the approved rear hall wall. The original 300 x 500 x 1850 mm bodies and 320 mm pitch are preserved. Doors have real punched vents, folded edges, split hinge sleeves, a pull and mechanical keyed cam lock. Each empty cavity has a shelf and hook. Plinths, top caps and rear wall straps finish the bank.

## Files and review

- `Maldek_Passenger_Lodge_Lockers.blend`: editable fitted review; scene `PLL_Fitted_Review`, asset collection `PLL_Lockers`. Saved closed at frame 1, roof hidden. Original layer exclusions remain hidden in the review copy.
- `PLL_Asset_Only.blend`: appendable collection library containing only `PLL_Lockers`; append this collection for integration. No master context or review lighting is included.
- `replacement_manifest.json`: all 96 exact proxy replacements, new object names, parents, local positions, dimensions, material slots, assembly transforms and camera settings.
- `verification.json`: saved/reopened topology, source preservation, vent and clearance evidence.
- `previews/`: closed full bank, player-height approach with 04/05/06 open, keyed pull close-up, open cavity and neutral rear attachment view. Rear view deliberately hides context to expose mounting straps; all other views retain fitted context. All added lights are temporary review lights, not installed fixtures.

Frame 1 is closed and latched. Lock cams turn 90 degrees about their local Y axes by frame 8. Leaves remain closed through frame 10. At frame 50 lockers 04, 05 and 06 stand open at 100 degrees; at frame 100 all doors are open. These are demonstration poses, not gameplay or puzzle decisions.

## Placement and capacity

Blender metres, Z up, floor Z = 4. Unit i (zero based) has assembly translation `(-14.1 + i*0.32, -7.0, 4.0)`, no rotation or scale. Local assembly origin is the lower rear left corner. The body bank bounds are X -14.10 to -10.28, Y -7.00 to -6.50, Z 4.00 to 5.85. Local mapping from the layout is `(x-24.1, 4-depth, z+4)`; these are not Unreal transforms.

Every door pivot is `(0.014, 0.528, 0.086)` relative to its assembly, local +Z swing from 0 to +100 degrees. The front sheet is 1.5 mm thick; rear folds make a 15 mm deep leaf. The front/header clearances are intentional, not duplicate dark backing faces. Cams have independent pivots at `(0.224, -0.036, 0.904)` relative to the door pivot. Pins and sleeve segments share the hinge axis but occupy distinct axial spans.

The lower cavity has a conservative clear envelope 272 x 450 x 1298 mm. A 230 x 400 x 500 mm compact soft daypack fits analytically. Typical rolling carry-on luggage does not fit through this narrow opening. No width expansion into circulation was made. The hook and upper shelf suit small personal belongings; all twelve lockers remain empty.

Rear straps bridge the existing approximately 200 mm stand-off to the rear wall. Their anchors extend slightly into the wall as installation fasteners. No wall/cladding patch is required. Structural anchoring design remains an integration detail.

## Source ownership

Source: `art/blender/passenger_lodge_03/Maldek_Passenger_Lodge_Materials.blend`, SHA-256 `b9d78ed0d7c5c50bc28a8fb6a0d63f1c86fa83d3144c6a7eae50476ee9607796`, matching the handoff.

Exactly 12 bodies, 12 doors, 12 number texts, 12 added handles and 48 added vent proxies are removed from the review copy. The complete exact list and original bounds are in the manifest. `FIT_Locker_approach` is a layout guide, not a body replacement. Other station lockers, table planks, benches, walls, restroom geometry and other packages are preserved. `REFERENCE_ONLY_Source_Context` and `REVIEW_ONLY_Cameras_Lights` must never be included in a delivery export.

Repeated panels share mesh data. Three door material/mesh variants are shared by four lockers each; numbers, assembly parents, door parents, keyed plugs and cam parts retain independent identities. There are no linked master datablocks. Spare individual component origins are their local construction centres; moving assembly origins are physical pivots.

## Materials and age

Station galvanized metal, warm enamel and structural steel are reused. Petrol paint has restrained cloudy fading, lower-edge grime, sparse edge abrasions and fine roughness. The three door variants offset the texture in both directions to reduce obvious repetition.

Created using **Painted Metal 012** from ambientCG / Lennart Demes, licensed CC0 1.0. Only its 1K roughness map is retained and packed in both blends. Source: https://ambientcg.com/view?id=PaintedMetal012 ; license: https://docs.ambientcg.com/license/ . `textures/sources.json` records the download URL and file hash. Its rust/color maps are not used.

These Blender material graphs include procedural micro-bump, object-coordinate masks and the packed image. They require UVs/baking or deliberate engine material recreation before export. The light galvanized interior and schematic nickel/brass lock material are package-local materials. There is no geometry displacement or uniform rust blanket.

## Reproduce

Use Blender 5.0.1. Set `MALDEK_ASSET_REPO` if the source repository is elsewhere (default `C:/Users/apek-anna/Developer/the-maldek-station`). Run from any directory using absolute script paths:

```text
blender --background --python scripts/build.py
blender --background --python scripts/weather.py
blender --background --python scripts/verify.py
blender --background --python scripts/verify_context.py
blender --background --python scripts/render.py
```

The `scripts/` paths above are relative to this package. The retained texture is already included; `scripts/download_texture.py` can retrieve it again with Python. `build.py` fails on a source-hash mismatch. It writes only this package. `weather.py` should follow a fresh build. Verify and render reopen the saved package and do not save over it.

## Verification and remaining integration

All 11,936 retained context objects match the source exactly for checked world transforms, mesh vertices/faces, material slots and text (`context_verification.json`). The saved/reopened release passes evaluated mesh manifold/degenerate-face checks, exact replacement removal, source SHA preservation and ray checks through the punched door vents. Neighboring moving assemblies pass 10,201 conservative convex-hull angle pairs (0–100 degrees in one-degree increments). A separate triangle-level sweep checks an unlocked leaf assembly against its own carcass every two degrees, excluding intentional hinge contact joints. Repeated unit geometry makes this representative of all twelve units.

The maximum moving front envelope is approximately Y -6.195 m. The nearest approved bench begins at Y -4.850 m, leaving approximately 1.345 m of aisle. The privacy screen and restroom approach remain behind/west of this sweep. These are Blender geometry checks, not engine collision or continuous physical simulation. Concealed sheet joints, fasteners and welded supports meet/intersect deliberately; no universal arbitrary-mesh coplanarity guarantee is claimed.

Remaining work: UVs and baked/export materials, mesh grouping/LOD budget, collision shapes, engine scale/orientation confirmation, per-locker interaction wiring, sound, actual capsule/reach checks and Unreal neutral/night/torch review. No Unreal import, live map change, puzzle choice or PIE validation was performed.

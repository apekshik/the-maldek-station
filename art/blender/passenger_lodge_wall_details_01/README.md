# Wall displays and visitor information

Editable standalone collection: `Maldek_Passenger_Lodge_Wall_Details.blend`, scene `PLG_Delivery`, collection `PLG_Wall_Details` (233 objects). `Maldek_Passenger_Lodge_Wall_Details_Fitted.blend` retains an independent reference copy of the material master and exact kitchen menu/cubby context. Append only `PLG_Wall_Details` for later integration. Source and other packages were not saved or changed. No Unreal work is included.

## Review and construction

Start with `textures/wall_elevations.png` or its editable SVG. `renders/11_Overview_neutral.png` shows the surveyed fit; `01_West_cluster`, `09_West_walk` and both hall views establish normal viewing distance. `02_Timetable_close`, `03_Map_close`, `04_Community_close` and `12_Poster_inspection` cover readable faces. `05_Restroom_approach` and `08_Wayfinding_hall` show fixed-header signs. `13_Poster_mounting_rear` isolates backboard/bracket ownership; `14_Case_maintenance` explodes the screw-retained glass for an illustrative maintenance view. Cases are not hinged. `10_Clock_close` shows the separate hands at 10:10.

Neutral and dim warm versions of the timetable, board and eye-height hall view use clearly named `PLG_TEMP_*` review lights, not installed lighting. Interior renders have the source roof on; only the overhead has it hidden. Inspection views hide source context. The fitted file initially hides the removable roof for editing. `render_manifest.json` records cameras and review state. Rendering does not resave the package.

| Assembly | Outer width × height | Source-world mounting centre | Front normal |
|---|---|---|---|
| Poster 1 / 2 / 3 | 0.75 × 1.05 m | X -23.901; Y 1.425 / -0.575 / -2.575; Z 5.675 | +X |
| Community board | 1.55 × 1.10 m | (-23.901, -4.8, 5.66) | +X |
| Timetable case | 0.84 × 1.16 m | (-18.30, 3.80, 5.65) | -Y |
| Visitor map case | 1.44 × 1.18 m | (-10.30, 0.40, 5.68) | -X |
| Clock | diameter 0.37 m | (-23.895, -0.575, 6.65) | +X |
| Menu print only | 2.07 × 0.355 m | (-21.60, -6.968, 6.53) | +Y |
| Cubby label only | 0.44 × 0.055 m | (-19.630, -6.596, 5.156) | +Y |

All values are metres, Blender Z up; lodge finished floor is Z=4. Each root has an explicit assembly matrix in `replacement_manifest.json`; local X is artwork-right, local Y is up, local Z is outward. Child geometry uses local origins. Clock hands pivot at the axle on local Z. There is no unrecorded recentering or Unreal transform conversion.

Frames have thin backboards, separate paper, beveled rails, steel mounting brackets and screw heads. Cases use 2 mm glazing with roughness 0.12 and IOR 1.45, clear of the print. Paper is 0.35 mm thick with up to 4 mm controlled corner curl. Five separately named pinned notices leave over half the usable pinning field available; two overlap with measured separation. Small historical pin puncture marks dress the unused side without filling it. Coat hooks are intentionally omitted to keep blank wall and circulation clear.

Age follows handling and exposure: margin specks, fine edge abrasions, a faint timetable tea ring, frame-edge scuffs, discontinuous ledge dust and old pin marks. Cork color/roughness use ambientCG Cork001 with a warm-brown tint. Reused source pine and fine procedural bump remain Blender materials requiring later baking. Wear does not obscure critical text. `scripts/weathering.py` is deterministic.

## Replacement and artwork ownership

Retire only `FIT_Poster_frame_1`, `FIT_Poster_frame_2`, `FIT_Poster_frame_3` and obsolete `FIT_Menu_placeholder`. The old reversed near-ceiling lettering is exactly `Service_lettering.001`, body `MALDEK / ARRIVALS`, bounds X -13.43766 to -12.36726, Y 0.19240 to 0.19360, Z 6.67392 to 6.75792. Retire that object during integration. Do not broadly match `Service_lettering`; preserve control and gondola-status signage. These exact objects are merely hidden in the fitted reference copy.

Replace kitchen text `PLK_Menu_Editable` and `PLK_Cubby_Label` with the supplied inserts. Keep `PLK_Menu_Board`, every physical menu frame part and `PLK_Cubby_Label_strip`. The delivered kitchen manifest determines both insert sizes and placements. This package adds no counter, cubby or menu frame. Fixed plaques sit above the public/platform/restroom/staff openings, never on another package's leaves. No wall, cladding, reveal or opening patch is required; `wall_patches` is explicitly empty.

Every front texture has a matching editable SVG with deterministic text in `artwork/`; the authoring program is `scripts/artwork.py`. `artwork/inventory.json` lists exact writing, pixels, physical sizes and texel density. Front UVs cover [0,1] across each print; other faces use paper-edge material, with independent thickness. Artwork is flat color with physical aging marks, no baked lighting or frame shadows. Typography uses Windows Arial and Georgia at generation time; fonts themselves are not redistributed. For other systems supply equivalent licensed fonts and visually review the SVG rendering.

The map derives lodge/annex rectangles from approved layout dimensions and control from surveyed `Control_Floor` and north door returns. Its platform route goes outside before reaching the independent north control entrance at about (-3.3,0.2). There is no internal lodge-control link. It is a schematic station visitor map, not a wider piste survey. Only established Maldek naming is used; mountain poster illustrations are expressly invented scenery.

## Verification and reproduction

Run with Python 3 + Pillow and Blender 5.0.1, from any working directory:

1. `python scripts/download_materials.py` only if restoring the bundled CC0 material maps.
2. `python scripts/artwork.py` to regenerate SVGs and textures.
3. `blender --background --python scripts/survey.py` for a fresh source inventory.
4. `blender --background --python scripts/build.py` for both blends. Set `MALDEK_SOURCE` to the approved material master's path when elsewhere. Its SHA-256 must match the contract.
5. `blender --background --python scripts/verify.py` for saved/reopened checks.
6. `blender --background --python scripts/render.py` for review images; optional `PLG_VIEWS` is a comma-separated fitted camera-name filter. Isolated inspection views always render.
7. `python scripts/check_artwork.py` verifies SVG text, texture sizes and review outputs.

`verification.json` records evaluated manifold topology, positive volumes, degenerate-face and exact duplicate-face checks, packed images, identical assembly matrices in both saved files, six padded opening envelopes and 331 sampled route positions. Actual overlapping-paper samples retain at least 0.35 mm separation. Checks compare this package with the approved proxy layout. They are not engine collision, capsule traversal or arbitrary polygon-intersection proofs. Mesh authoring found degenerate bevel slivers on submillimetre scuffs; removing those unnecessary bevels resolved them before final verification.

Source hash remains `b9d78ed0d7c5c50bc28a8fb6a0d63f1c86fa83d3144c6a7eae50476ee9607796`. Shared master, other packages, source blend and Unreal are preserved.

## Editorial and integration remainder

The printed 09:00 first departure, half-hour interval and 16:30 last departure are provisional story choices, not a live operating system. Menu choices, club/walk notices and weather cancellation are ordinary proposed dressing. Prices, currency and calendar dates are deliberately absent pending story decisions. The critical ticket sentence and 07 key/bag association are not reproduced or changed; no clue objects or interaction code are included. The existing gondola status sign stays independent.

Before Unreal integration: approve editorial schedule, bake procedural materials, establish export/collision budgets, append only this collection and apply the exact retire list. Fit against final neighboring packages, recheck routes and header clearances with the actual player capsule, and review text/glass under engine night/torch lighting. No import, runtime interaction, journal or PIE validation is claimed.

## Artwork and material provenance

All poster illustrations, diagrams, notices and lettering are original deterministic vector artwork, not downloaded brands or generated lettering. `materials/provenance.json` records Cork001 source URLs, CC0 license, source hashes and tint usage. See [ambientCG Cork001](https://ambientcg.com/view?id=Cork001) and [license](https://docs.ambientcg.com/license/).

FAL's supported endpoints were checked on 2026-09-10: [Nano Banana Pro](https://fal.ai/docs/model-api-reference/image-generation-api/nano-banana-pro), [GPT Image 2](https://fal.ai/models/openai/gpt-image-2). GPT Image 2.5 was not assumed. The existing protected credential could not be decrypted with the documented workflow, so no authenticated model request or paid generation was sent. This package uses the handoff's original-vector fallback. No credential or decrypted data is included.

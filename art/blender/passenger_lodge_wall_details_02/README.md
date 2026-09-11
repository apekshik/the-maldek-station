# East waiting-hall wall dressing

Append `PLG2_East_Wall_Details` from **Maldek_East_Wall_Details.blend** into a future integration copy. The package is additive: replacement and wall-patch lists are empty. **Maldek_East_Wall_Details_Fitted.blend** is an independent lodge 04 review copy, not a replacement integrated master. Its `PLG2_REFERENCE_ONLY` context must not be appended/exported. No lodge 04 or Unreal integration was performed.

The immutable source is `passenger_lodge_04/Maldek_Passenger_Lodge_Integrated.blend`, scene `Lodge_Integrated`, SHA-256 `bcf7e6301aecedd83688488981fd58a5a9719d685ef975210eef9eeb7f753f6c`. This supersedes lodge 03. The new fitted scene is `PLG2_Fitted_Review`; the asset-only scene is `PLG2_Delivery`. Metres, Z up, floor Z=4. Source context, furniture, trim, artwork, lockers and doors are preserved.

## Six primary assemblies

| Root | Size, width × height | Mount centre XYZ, metres | Construction |
|---|---|---|---|
| PLG2_Safety | 0.70 × 0.95 | -10.300, -1.12, 5.78 | Pine frame, backboard, paper, illustrated etiquette |
| PLG2_Archive_A | 0.55 × 0.40 | -10.300, -2.10, 6.10 | Petrol frame, monochrome platform study, caption plate |
| PLG2_Archive_B | 0.55 × 0.40 | -10.300, -2.40, 5.46 | Pine frame, monochrome mountain/gondola study, caption plate |
| PLG2_Leaflet_rack | 0.45 × 0.60 | -10.322, -3.23, 5.18 | Six shallow pockets, rolled lips, 16 folded leaflets, one depleted pocket |
| PLG2_Climate_gauge | 0.22 × 0.35 | -10.300, -4.03, 5.91 | Twin analog faces, separate needles, steel rims, thin glass, timber housing |
| PLG2_First_aid | 0.38 × 0.45 | -10.300, -5.02, 5.61 | Empty returned sheet-metal cabinet, hinged leaf and turn latch |

The collection has 172 objects including the six roots. Local X points toward world -Y, local Y points up world +Z, and local Z points outward world -X. `placement_manifest.json` records every object's world matrix, dimensions, material slots and parent. Root origins are wall-facing assembly centres; no recentering or Unreal-axis conversion is hidden.

The 1.623 m² of new assembly rectangles occupy 25.7% of their 4.44 × 1.42 m bounding display band, intentionally at the sparse end of the roughly-one-third brief to preserve space beside the map and lockers. Heights vary, the archival pair is staggered, and upper wall remains visible. `textures/elevation.png` and `artwork/elevation.svg` show measured placement, existing map, dado and locker corner. There is no second map, clock or full noticeboard.

The dado projects to X=-10.292 at Z=5.03–5.07. Rack stand-offs bridge it: the back clears it by 30 mm, while the complete rack projects 150 mm from the wall, below the 160 mm limit. Feet/fixings lie above and below the rail. No trim cutting or master-wall patch is required. The rack bottom is 0.88 m above floor; leaflet tops vary with depletion. A dedicated route reaches its front around the bench ends. The first-aid approach stops to the latch side, clear of the open leaf.

## Materials and artwork

The original illustrations, safety text, leaflet covers, labels and instrument scales are editable SVG and deterministic Pillow output from `scripts/artwork.py`. `artwork/inventory.json` contains exact wording, physical print sizes, PNG resolution, full-rectangle UV mapping and texel density. Twelve print designs plus the separate placement elevation are supplied. Printed faces use [0,1] UVs; edges/back faces have a separate paper material. Paper has real thickness, with folded leaflet ridges and varied stack depths.

The two archival images are **original monochrome illustrative studies**, not historical documentary photographs. Their captions assert no date or named event. The safety text is ordinary advisory dressing and introduces no gameplay rule. The first-aid cabinet is empty and has no key, contents or collectibles. Instrument readings are static dressing at approximately 18°C / 50% RH, with no live weather connection.

Materials reuse the integrated station's aged pine and match cream enamel, petrol paint, dull galvanized steel and cream paper. Roughness varies across enamel. Edge rubs, paper-margin abrasions, ledge dust, depleted-pocket dust and tiny latch wear remain localized. New procedural roughness and inherited pine need baking before an engine export; flat print textures are already packed. Existing master material graphs are not modified. All new and reused required images are packed in the asset-only blend.

`provenance.json` identifies the immutable source, original artwork authorship, fonts used for deterministic typesetting and material reuse. No external image or unlicensed photograph was downloaded. No FAL generation or credential access was needed for this package. Windows Arial and Georgia are used at generation time; font files are not redistributed.

## Review

`renders/01_Before_user_angle.png` and `02_After_user_angle.png` use exactly the lodge 04 `03_Hall` camera: position (-22.7, 2.4, 5.65), target (-14, -5.7, 5.1), 22 mm lens. This is the wider view corresponding to the user's cropped screenshot. The same source furniture, camera and lighting are used on both sides; only the new collection is toggled. Existing seating remains visible for scale.

Other renders: `03_Wall_elevation`, `04_Oblique_walk`, close views `05_Leaflet_rack`, `06_Climate_gauge`, `07_First_aid`, `08_Cabinet_open`, `10_Archive_pair`, `11_Safety`, and `09_Dim_warm`. The roof stays on. `render_manifest.json` records camera and cabinet poses. `PLG2_TEMP_KEY` and inherited review lamps are temporary review illumination. Render scripts reopen and never resave the fitted file.

## Verification and reproduction

Run Python with Pillow and Blender 5.0.1:

1. `python scripts/artwork.py`
2. `blender --background --python scripts/survey.py`
3. `blender --background --python scripts/build.py`
4. `blender --background --python scripts/verify.py`
5. `blender --background --python scripts/render.py`
6. `python scripts/check_artwork.py`

Scripts resolve outputs relative to themselves. `build.py` accepts `MALDEK_SOURCE` for an alternative path to the same immutable source hash. Use `PLG2_VIEWS` with comma-separated render names for a selective rerender. Both delivery files remain closed at frame 1. Frame 40 opens the new cabinet to 95 degrees; the cabinet hinge is `PLG2_Cabinet_LeafPivot`, local (-0.184, 0, 0.131), rotation about local Y/world Z. Apply only this new pivot's pose when reviewing against the integrated master; changing the master's timeline also poses other packages.

`verification.json` verifies saved/reopened evaluated mesh manifoldness, positive volume, degenerate faces, packed images, identical asset world matrices in both files, unchanged source hash and unchanged reference transform/mesh-count/material signature. It tests new meshes against evaluated integrated wall/trim/furniture BVHs, minimum wall stand-off and rack depth. The cabinet leaf is sampled every 5 degrees through 95 degrees against fixed cabinet pieces and surrounding context; intended hinge mating hardware is excluded.

Combined circulation replays all 15 lodge 04 public/restroom/kitchen routes plus three east-wall walking/approach routes, with a 340 mm radius and 1.8 m height. Public/restroom/locker doors are open; kitchen cabinets are closed. Each route is checked with the new cabinet both closed and open. `routes_input.json` preserves the exact paths. These are conservative Blender convex-hull and sampled surface checks, not Unreal collision, continuous motion simulation or gameplay testing.

Remaining integration work: append only this new collection into an explicitly authorized master revision; establish export grouping/LODs, bake procedural materials, author engine collision and verify actual player traversal and night/torch text visibility. The first-aid pivot and separate gauge needles support future editing without implementing interactions.

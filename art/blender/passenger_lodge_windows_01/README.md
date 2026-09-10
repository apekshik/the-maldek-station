# Passenger lodge fixed windows — PLW 01

Two fitted, three-bay metal windows replace the frosted layout proxies in an editable review copy of the approved lodge. Finished geometry is in **PLW_Assets**, with separate **PLW_Window_01** and **PLW_Window_02** collections. Open `Maldek_Passenger_Lodge_Windows.blend`, scene `05_Material_Study`.

The custom construction uses hollow petrol-painted profiles, warm enamel reveals and returns, galvanized sloping sill pans with end dams and drip folds, separate glazing beads and EPDM seals, restrained slotted bead fixings, setting blocks and 6/12/6 mm insulated glazing. Rear bedding and four support packers per window bridge the frame-to-pan joint. The outer pane has a rough translucent finish matching the approved frosted intent. See [construction references](references/README.md) for manufacturer details and their specific application.

## Fitted dimensions

All coordinates are **Blender metres, Z up, +Y toward the gondola**. Dimensions below describe authored geometry, not structural specifications.

| Item | Window 01 | Window 02 |
|---|---|---|
| Replaced proxy | `FIT_Frosted_window_placeholder` | `FIT_Frosted_window_placeholder.001` |
| Rough opening world X | -22.700 to -18.900 | -15.500 to -11.700 |
| Rough opening world Z | 4.900 to 6.600 | 4.900 to 6.600 |
| Assembly root translation | (-22.700, 4.000, 4.900) | (-15.500, 4.000, 4.900) |
| Root rotation / scale | (0,0,0) / (1,1,1) | (0,0,0) / (1,1,1) |

| Common detail | Dimension |
|---|---|
| Rough opening | 3800 × 1700 mm |
| Sill above finished floor Z=4 | 900 mm |
| Source core depth | 180 mm, Y=3.820–4.000 |
| Source cladding bounds | Y=4.003–4.032 |
| Frame outer size, W × H × depth | 3760 × 1630 × 110 mm |
| Perimeter face / mullion face | 70 / 60 mm |
| Hollow profile wall | 3 mm |
| Glazing per bay, W × H | 1158.67 × 1482 mm |
| Glazing thickness | 6 mm clear + 12 mm cavity + 6 mm frosted |
| Clear view inside gaskets per bay | approximately 1126.67 × 1450 mm |
| Sheet reveal thickness / core clearance | 2 / 4 mm |
| Sill fall | 30 mm outward over 316 mm; 5.42° |
| Sill nose | Y=4.120, 88 mm beyond cladding peaks |
| Overall trim/hood envelope W × H × depth | 3882 × 1769 × 321 mm |
| Sill drains | Two 24 × 8 mm exterior slots per bay, plus top feeds |

The root origin is the west rough jamb / outer core plane / rough sill. Component origins are local geometry centres. Both assemblies are fixed; there are no moving-part pivots or gameplay mechanisms. Exact names, world bounds, local origins and per-object material slots are in [replacement_manifest.json](replacement_manifest.json).

## Replacement and surface ownership

Source: `art/blender/passenger_lodge_03/Maldek_Passenger_Lodge_Materials.blend`. The measured SHA-256 matches the handoff: `b9d78ed0d7c5c50bc28a8fb6a0d63f1c86fa83d3144c6a7eae50476ee9607796`.

**No master-wall patch is required.** Both original openings already pass through all relevant core and corrugated layers. Replace only the two proxy objects with the corresponding PLW collections at their recorded root transforms. Do not cut, replace or suppress any shared wall segment. `scripts/build.py` reproduces the full replacement in the package review copy; its source-hash guard stops an unreviewed source revision from silently changing the fit.

The package owns the visible new jamb/head linings and sill pan. A 4 mm concealed gap separates the linings from the source core. Head linings finish above the jambs with a 1 mm joint. The jamb lower edges follow the sill end dams, avoiding overlapping corner sheets. Returns cover the installation seams, including a folded rear sill return closing the underside behind the interior architrave. The dark exterior perimeter seal intentionally intersects corrugation peaks behind the cover trim; this is a concealed filled joint, documented by the surface audit, not a competing exposed core/reveal face. Metal profiles, glass, beads and gaskets remain separate editable meshes.

The existing public exit at X=-17.7 to -16.5 retains its full 1.2 m proxy width. The room layout, doors, roof, original control windows, gondola and platform geometry remain unchanged. Reference context is retained under **PLW_REFERENCE_ONLY__DO_NOT_EXPORT**; review cameras and temporary lights are under **PLW_REVIEW_ONLY__DO_NOT_EXPORT**. Export only **PLW_Assets**.

## Material slots

Each mesh has one explicit slot, with the per-object assignments recorded in the manifest.

| Slot material | Use | Integration note |
|---|---|---|
| `VF06_Petrol_paint` | Profiles and glazing beads | Reused station procedural finish |
| `VF06_Warm_enamel` | Reveals and cover returns | Reused station finish |
| `VF06_Galvanized` | Pans, drip hoods, spacer bars and fixings | Reused station procedural finish |
| `PLW_EPDM_Charcoal` | Gaskets, setting blocks, bedding, packers | Principled rough dark rubber |
| `PLW_IGU_Edge_Seal` | Concealed insulating-unit edge seal | Principled dark sealant |
| `PLW_Clear_Glass_6mm` | Interior pane | Roughness 0.08, transmission 1.0, IOR 1.52 |
| `PLW_Opal_Glass_6mm` | Exterior pane | Roughness 0.38, transmission 0.85, IOR 1.52 |

Procedural station finishes and Blender transmission need an engine material pass or baking. Optical settings approximate the frosted design intent; they are not measured product properties.

## Review and verification

- [Review gallery](review.html): fitted views of both sides, matched before/after facade beside control, sill/head details and all 16 corner views.
- Four fitted close-ups use a camera elevation of Z=5.65 m (1.65 m above the floor) and retain the roof.
- The facade comparison uses identical cameras and unchanged source lighting. Close and corner views add labelled temporary neutral softboxes.
- [verification.json](verification.json): saved/reopened evaluated topology, source geometry preservation, source-to-asset surface intersections, wall-opening rays, pane thickness, drainage feed/outlet checks and exit encroachment checks.
- [source_survey.json](source_survey.json): original object bounds, materials, visibility and wall layers.

Reproduce from the repository root, using Blender 5.0:

```powershell
& 'C:\Program Files\Blender Foundation\Blender 5.0\blender.exe' --background --python-exit-code 1 --python art/blender/passenger_lodge_windows_01/scripts/survey.py
& 'C:\Program Files\Blender Foundation\Blender 5.0\blender.exe' --background --python-exit-code 1 --python art/blender/passenger_lodge_windows_01/scripts/build.py
& 'C:\Program Files\Blender Foundation\Blender 5.0\blender.exe' --background --python-exit-code 1 --python art/blender/passenger_lodge_windows_01/scripts/verify.py
& 'C:\Program Files\Blender Foundation\Blender 5.0\blender.exe' --background --python-exit-code 1 --python art/blender/passenger_lodge_windows_01/scripts/render.py
& 'C:\Program Files\Blender Foundation\Blender 5.0\blender.exe' --background --python-exit-code 1 --python art/blender/passenger_lodge_windows_01/scripts/detail_views.py
python art/blender/passenger_lodge_windows_01/scripts/gallery.py
```

The checks apply to the saved Blender package. Unreal import, LODs, collision, player traversal, night/torch lighting and export axis/unit validation remain integration work. No live map or runtime logic was modified, and no PIE validation is claimed. This is a visual construction asset, not a manufacturer-certified or structurally engineered window system.

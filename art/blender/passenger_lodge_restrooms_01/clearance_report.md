# Saved-file topology and clearance report

Overall result: **PASS**. 273 evaluated asset meshes; 24,872 evaluated polygons. All have zero non-manifold edges and zero degenerate faces.

All 5 patched context meshes are manifold. Source hash remains unchanged.

## Walking and operating clearance

All routes use the approved layout's 0.34 m radius, 1.8 m high envelope. Distances below are from the sampled center path to the nearest evaluated convex footprint, not a claim of engine collision clearance.

| Route | Minimum distance | Margin beyond 340 mm radius | Closest component |
|---|---:|---:|---|
| Screened_hall | 530.0 mm | 190.0 mm | FIT_Full_height_privacy_screen |
| Women_entry | 357.0 mm | 17.0 mm | PLR_Women_Entry_Stop |
| Women_basin | 390.5 mm | 50.5 mm | PLR_Women_B_Stall_Leaf |
| Women_A_stall | 349.0 mm | 9.0 mm | PLR_Women_A_Stall_Stop |
| Women_B_stall | 349.0 mm | 9.0 mm | PLR_Women_B_Stall_Stop |
| Men_entry | 360.0 mm | 20.0 mm | PLR_Men_Entry_Lever_-1 |
| Men_basin | 354.0 mm | 14.0 mm | PLR_Men_Entry_Leaf |
| Men_A_stall | 349.0 mm | 9.0 mm | PLR_Men_A_Stall_Stop |
| Urinal | 355.0 mm | 15.0 mm | PLR_Men_Urinal_shell |

785 path samples. All 28 floor rays found the retained finished floor. All 18 waiting-hall sightlines to the fixture targets were blocked by retained source walls.

The stall standing positions also clear the closed leaf while the outward swing moves away from the occupant. The source cubicles remain compact. Final engine collision must preserve the small gate margins; do not use over-sized box colliders on hardware.

## Pivots and door poses

World coordinates below are metres, Z up. All leaves are closed at frame 1 and at their working open angle at frame 40. The entrance axes sit behind the leaf planes, on the opening side, so the inner corners clear the shared wall.

| Pivot | World X, Y, Z | Leaf width | Open Z angle |
|---|---|---:|---:|
| PLR_Women_Entry_Pivot | -13.202, -9.252, 4.020 | 0.896 m | +85 degrees |
| PLR_Men_Entry_Pivot | -11.202, -9.252, 4.020 | 0.896 m | +90 degrees |
| PLR_Women_A_Stall_Pivot | -15.660, -11.328, 4.150 | 0.780 m | +90 degrees |
| PLR_Women_B_Stall_Pivot | -14.310, -11.328, 4.150 | 0.780 m | +90 degrees |
| PLR_Men_A_Stall_Pivot | -12.710, -11.328, 4.150 | 0.780 m | +90 degrees |

94 sampled door poses passed leaf/hardware-versus-fixed-geometry checks. The door sweep regions are mutually separated. Hinge mating pieces and the corresponding mechanical stop are intentional contacts and excluded from collision failure counts.

Both nominal 0.900 x 2.200 m openings passed 267 reveal rays each. Door leaves and hardware reduce the working passage locally; the radius checks above include that reduction.

## Replacement and surface ownership

13 exact proxies are replaced; 280 asset objects are inventoried. The new closed rear cubicle panels, door assemblies and ancillary hardware are additions within the approved envelopes. No hall lockers, hall furniture or privacy-screen walls were changed.

See `replacement_manifest.json` for every original proxy, its replacement parts and the five opening-specific patches; `asset_inventory.json` provides dimensions, material slots, parent relationships and assembly matrices.

The finished steel liners own the entrance reveals. The concealed wall boundaries are notched only below the recessed headers, leaving 4 mm separation behind the liners. Face trims cover the joints from both sides.

## Limits

Blender-only saved/reopened checks. No Unreal import, collision cook, PIE, accessibility certification or structural/plumbing engineering is claimed. The curved fixtures use closed shells and capped shared-vertex pipe meshes. Multiple physically connected components intentionally remain separate editable meshes.

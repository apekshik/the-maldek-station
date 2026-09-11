# East waiting-hall wall integration

Installed the additive `PLG2_East_Wall_Details` delivery collection from `art/blender/passenger_lodge_wall_details_02`. The fitted review building was not exported. The integrated Blender master is unchanged.

Six assemblies bring a safety poster, two archival illustrations/captions, a six-pocket leaflet rack with sixteen folded leaflets, a twin analog climate gauge and an empty first-aid cabinet into the Unreal lodge. Thirty engine meshes retain the source placement. A 4K wood/enamel/steel atlas preserves procedural surfaces; twelve original print textures retain source UVs and resolution. The gauge readings remain decorative.

The first-aid door uses native StationCabinet interaction, opens 95 degrees in Unreal, and closes with E. Its printed face and separate latch follow the hinge. Cupboard recording variants are used for this small cabinet. No contents or pickup/inventory behavior were added. The latch remains a separately editable part attached to the door.

`collision_repair.json` records a 7 mm inset of the rectangular collision's hinge edge to avoid the mating hinge pins and knuckles. Meshes, visible seams and the pivot were not moved. `collision_probe.json` identifies the exact source components; the repaired probe is clear.

## Reproduce and check

Run Blender with `../scripts/export_east_wall.py`, then execute `install_east_wall.py` in the open migration map through the existing dispatcher. Import requires the completed audio-refinement assets. `verify_east_wall.py` saves/reopens, checks all preserved actors, placement, dependencies, 21 combined interior routes and the perimeter. `test_east_wall.py` exercises real E input and walks the three new approaches with the cabinet open. `review_east_wall.py` creates temporary neutral lights and removes them after nine review captures. Night/torch views come from the actual PIE test.

Delivery map: `/Game/MaldekRefinement/PassengerLodge/Station_Lodge_Migration`. The original R12 map remains unchanged. All mechanisms are saved closed, roof visible, without temporary test pads or review lights. Source package provenance and editable artwork are retained beside the blend files.

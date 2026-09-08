# Terminal drive / separate Blender study

The existing lower machinery in VF07 originates in `revision_04_refinement/scripts/refine.py`: finned motor, reducer, output shaft and a 1.83 m rim with a brake caliper. The newly installed upper terminal had a bullwheel and bearing frame but no connection to that lower drive. They currently read as two unrelated mechanisms.

This editable study proposes one continuous power path: motor -> input service brake -> reduction gearbox -> guarded vertical shaft -> upper angle gearbox -> tilted bullwheel. The small lower wheel should become a brake disc/coupling rather than another rope-turning wheel. Two safety calipers act on a disc rigidly attached to the bullwheel, independently of the transmission. This is a replacement machinery layout proposal, not a bolt-on shaft aligned to the old room coordinates.

At Maldek, the free return bullwheel and its bearings sit on a carriage guided along the rope direction. A hydraulic cylinder reacts against the fixed frame to maintain tension. Its hydraulic power pack does not propel the cabin. Only Millford has the main propulsion motor in this concept.

The one cabin shuttles on one side of the rope loop and reverses before its grip reaches either terminal bend. The other rope run is empty. It does not require a second cabin, and the cabin never travels around the bullwheel. The game currently animates the cabin, not rope material transport or terminal rotation.

## Geometry and limits

- Preserved current lateral/vertical rope separation: 2.35 m / 2.955 m. Bullwheel plane is tilted to join these tangents; pitch diameter about 3.775 m, 180-degree wrap, rope diameter 64 mm.
- At 3.5 m/s the bullwheel rotates about 17.7 rpm; an illustrative 1,500 rpm motor would need about 84.7:1 overall reduction. This establishes a speed relationship, not motor power or gearbox capacity.
- Weathered matte paint, exposed dull metal, oxidized base plates, independent bearings, foundation anchors and torque reaction members are modeled. Shaft guard is shown open for inspection; full operating enclosure and maintenance access remain to be detailed.
- This is a layout study. Rope traction, D/d suitability, brake torque, bearing loads, gear selection, hydraulic travel/force, structural capacity and exact station retrofit are not yet validated. Rendered internal shaft continuity does not certify mechanical capacity.
- `Maldek_Terminal_Drive_Study.blend` remains separate from Unreal. No replacement import was performed. Current approved route, terrain and cabin geometry are preserved.

Run `blender -b --python scripts/build.py` to rebuild the source and both renders. `verification.json` records dimensions and speed calculation. `overview.png` compares drive and return assemblies; `drive_detail.png` shows the transmission.

## Manufacturer references consulted 2026-09-08

- [LEITNER drive system](https://www.leitner.com/en/products/ropeway-components/detail/leitner-drive-system/): electric motor, planetary reduction, separate braking systems, overhead/underground and drive/tension arrangements.
- [Doppelmayr ropeway FAQs](https://www.doppelmayr.com/files/sites/default/data/_general_content/pdfs/2020_Urban_FAQs_ENG.pdf): station motor acts on the bullwheel; carriers are hauled and braked by the rope.
- [Doppelmayr maintenance training](https://service.doppelmayr.com/training/course-list/detail/maintenance-assistance-3385/): bullwheel coupling, brakes, hydraulic systems and guided tension carriage.

The angled transmission and dimensions here are our game design proposal, not a copied manufacturer system.

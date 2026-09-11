# Millford service cassette — Blender review

Open `Millford_Service_Cassette.blend`. Model is in metres, nominal 100.4 × 63.8 × 12.1 mm. Named editable shell halves, smoked window, two six-tooth through-hubs, wound magnetic tape, guide rollers, pressure pad, five screws per side, capstan openings, record-protection pockets, and original two-sided service labels. Fonts packed. Studio is a separate collection.

`previews/01_hero.png` is the main review; front, rear and underside views are also included. Rebuild with Blender 5.0 background mode and `build_cassette.py`.

References: [Duplication cassette shell guide](https://www.duplication.com/cassette-selection-guide.php), [Recording the Masters blank cassette specifications](https://www.recordingthemasters.com/blank-cassettes). Nominal dimensions are a modelling target, not an IEC conformance claim. Labels are original fictional station artwork.

Status: Approved and imported to `/Game/Inspection/Cassette/SM_ServiceCassette`. Saved inspectable actor `Inspection_Cassette_Pickup_Hood` sits flat beside the meter on the yellow pickup in Station_R12. The editable Blender master remains intact. `export_cassette.py` creates the combined, centered FBX with geometry labels; Unreal materials are authored by `cassette_install.py`.

Placement includes 6 cm of vertical correction above the collision-derived position: an in-game height comparison showed the thin prop was hidden by the visible hood before this correction. Re-running the installer preserves that correction.

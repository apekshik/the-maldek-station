# Revision 03 — outward platform bands and front cantilever

Open `Maldek_Architecture_Redesign.blend`. Earlier revisions remain unchanged.

The station platform now has three continuous bands measured outward from the combined building envelope: 0.60 m open grating, 2.40 m solid steel promenade, and 0.65 m outer open grating. Plate seams are small assembly joints, not alternating grate panels. Both grille bands have real holes; support beams sit below the walking surface. Rear infill joins the staircase to the surrounding promenade. The broad side route passes outside the landing columns.

The upper living/radio room grows to 6.1 × 5.7 m (34.77 m²), projecting 1.2 m beyond the control-room front and 0.7 m beyond its side. Its floor is now at 3.65 m. The original overlapping control roof is replaced by a continuous transfer slab meeting the lower walls and upper floor, with perimeter fascia and front knee brackets. Only the exposed rear/left roof strips remain. Radio furniture moves toward the new front windows.

The rear stair remains in place, adjusted to the new floor height: 20 risers at 182.5 mm, 280 mm goings, 1.25 m tread width. Deck guards scale to approximately 1.2 m high with the revised stair/landing geometry.

`verification.json` records measured slab/floor contact, sampled stair and landing support, headroom, 1.2 m diameter clearance along the broad promenade, and coverage samples distinguishing solid panels from open grating. Solid-panel coverage is sampled away from panel joints. These are Blender checks, not Unreal capsule sweeps or structural engineering validation.

Five review images are in `renders/`. The primary image shows the new front projection and platform bands. Service-building locations remain presentation placements. The larger platform and upper room have not been placed into the Unreal station; site fit, gondola clearance and gameplay collision remain integration work.

Run `scripts/build_revision.py` in factory-startup background Blender to rebuild this revision. It derives from revision 02 and its revision 01 helpers. Then run `scripts/verify_revision.py` against the saved file. No marketplace assets were purchased.

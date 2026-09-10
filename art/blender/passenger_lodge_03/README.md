# Passenger lodge material mockup

This separate Blender file develops the approved lodge/platform layout with the station's existing VF06 petrol paint, galvanized steel, structural steel and warm enamel materials. The source lodge 02 file is preserved.

Exterior wall segments receive closed corrugated metal skins outside their cores. Original door/window openings are respected. The flat removable roof envelope receives sheet-metal seams and fascia; roof drainage, insulation, flashing and final roof form remain a later architectural pass.

The replacement deck, bypass treads and landings use real open grating, with framed panels, bearing bars and recessed crossbars. Opaque proxy slabs are removed. The right-hand landing route remains open, and guards retain the approved stairwell footprint. New grating uses 65 mm bearing-bar spacing and 100 mm crossbar spacing in this visual mockup; engineering and game collision remain separate work.

All six tables, twelve benches, lockers, counter, prep zone and restroom components remain. Table and bench tops are now individual pine planks; lockers have metal handles and vent details. Frosted windows use transmissive rough glass. Small coffee appliances, sanitary fixtures and poster frames remain materialized proxies, not finished detailed assets.

Build with Blender `--background --python art/blender/passenger_lodge_03/scripts/build.py`, then run `scripts/verify.py` the same way. Verification reopens the result, checks new mesh topology, sampled floor/headroom routes, open grating apertures and the right landing route. These are Blender checks; no Unreal import or playtest is claimed.

Review cameras cover the full exterior, roof-hidden cutaway, grating detail and the corrected staircase. Hide `PL03_Removable_Roof` to work inside the lodge. The file opens with the roof visible.

Additional review views: scripts/render_review.py renders the front beside control, the opposite arrival-side overview, two interiors and a lower front-platform perspective. The roof stays on. Interior views use temporary warm area lights for readability; these lights are not installed fixtures and are not saved into the source. additional_views.json records camera positions and source-file preservation.

Restroom review: scripts/render_restrooms.py supplies the approach from the waiting hall, hallway views in both directions, and a restroom interior. These roof-on renders use temporary review lighting and preserve the source file; restroom_views.json records camera positions. Fixtures and partitions are still mockup assets.

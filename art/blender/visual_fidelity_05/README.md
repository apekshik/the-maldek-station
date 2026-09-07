# Revision 05 — wider platform bands

Open `Maldek_Architecture_Redesign.blend`. Revision 04's water tower, utility details, interior furnishings and architecture are retained.

From the buildings outward, the main platform now uses **1.8 m inner grating, 3.6 m solid plate, and 1.95 m outer grating**, for a total depth of **7.35 m**. Both grating bands are three times revision 04's widths; the solid band is 50% wider. The same proportions apply to generator/workshop and relay aprons. Girders, deck supports and outer guards follow the new perimeter.

Service buildings and the water tank move 8 m east to clear the larger main platform. The relay hut and tank also move 5 m north to keep the enlarged generator apron out of their footprints. Wide connecting decks link the revised assemblies. These are presentation/layout studies, not final terrain placement. Main buildings and the upper room retain their previous dimensions.

`verification.json` checks inherited main circulation, stairs, upper floor junction and the new front band coverage. `wide_platform_verification.json` checks new connections and the side band coverage. These are sampled Blender geometry checks, not full Unreal capsule sweeps or structural validation.

The previous revision's documented limitations still apply: no new Unreal import, final site-fit review, complete water distribution system, game ladder interaction or performance pass. Seven render views are in `renders/`.

Rebuild using `scripts/build_wide_platform.py` in factory-startup background Blender, then run `scripts/verify_wide_platform.py` on the saved file. Earlier revision files remain unchanged.

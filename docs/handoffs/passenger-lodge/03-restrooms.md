# Handoff 3 — complete restroom mesh package

Implement this package after reading [shared-contract.md](shared-contract.md).

Output: `art/blender/passenger_lodge_restrooms_01/`; asset collection prefix: `PLR_`.

Own both restroom entrance-door assemblies, all cubicle partitions and stall doors, toilets, urinal, washbasins and supporting restroom hardware. The lodge-door task does not own any bathroom door.

Keep the screened hallway separating the waiting hall from the restrooms. Design-intent restroom annex is 6 × 6 m: local X=8–14, depth 11.2–17.2; world approximately X=-16.1 to -10.1, Y=-13.2 to -7.2. Inspect actual wall and clearance geometry. Two restroom entrance openings in the hallway partition have nominal 0.9 × 2.2 m clearances at local X=10–10.9 and 12–12.9, depth 13.02.

Current proxies are not finished fixtures: `FIT_Women_Basin`, `FIT_Men_Basin`, `FIT_Women_A_WC`, `FIT_Women_B_WC`, `FIT_Men_A_WC`, `FIT_Urinal` and cubicle side panels. The user correctly sees no recognizable sinks yet. Replace these with actual modeled basins and fixtures.

Build two women's cubicles and one men's cubicle plus the urinal/privacy divider, following the approved program. Stall doors must be their own design: practical painted/laminated panels, raised bottom clearance, supporting feet, top bracing where appropriate, hinges, latch with occupancy indicator, stop and coat hook. Determine working door widths and swings from the existing cubicle envelopes; do not shrink usable circulation to fit decorative hardware.

Add recognizable basins with bowl interiors, rims, faucets, drains, traps/supply connections, mounting, mirrors, soap and drying provision. Add toilet bowls/cisterns/seats, urinal and flush plumbing, paper dispensers and modest bins. Model visible construction sensibly; do not spend geometry on invisible mechanisms.

Keep the hallway navigable and entrance sightlines screened. Do not invent an expanded bathroom footprint or move hall lockers. Show both entry-door swings and every stall-door swing in context; allow access to each basin and cubicle. Supply a topology/clearance report, entrance and stall pivots, exact proxy replacements and any opening-specific patches. Render hallway both ways and each restroom interior with temporary review lighting clearly identified.

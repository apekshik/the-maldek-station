# Handoff 6 — passenger belongings lockers

Implement this package after reading [shared-contract.md](shared-contract.md).

Output: `art/blender/passenger_lodge_lockers_01/`; asset collection prefix: `PLL_`.

Own the twelve-locker bank on its approved rear hall wall, including carcasses, doors, hardware, interiors, numbering and base/top finishing. Preserve its location and count. Do not relocate the bank to the poster wall, alter restroom access or own public architectural doors.

Inspect `FIT_Locker_*` bodies and doors in `PL02_Fitted_Lodge_Geometry` plus `PL03_Locker_Handle*` and `PL03_Locker_Vent*` additions in `PL03_Furniture_Details`. Existing number text may be hidden in the material study. Enumerate and replace the complete assemblies, including redundant handles/vents, in the review copy. Do not remove table planks or other assets from that shared source collection.

Layout intent: twelve units at local X=10+i×0.32, depth 10.5; body nominally 0.30 m wide, 0.50 m deep and 1.85 m tall. Use the shared coordinate mapping and actual source bounds. Preserve the bank footprint and walking aisle. Verify usability for ordinary passenger bags; document any proposed dimension change instead of silently expanding into circulation.

Model folded sheet-metal carcasses, real door thickness, recessed frame lips, seams, hinges, louvres, handles and a simple period-appropriate mechanical keyed lock. The door/key studies may be used as style references; do not edit those source assets or reuse oversized architectural-door hardware unchanged. Include a plausible plinth or feet, top cap, wall attachment and restrained number plates 01–12.

Give doors separate objects with correct hinge pivots and simple open/closed poses. Build interior shelves, hooks and a clean storage cavity visible when opened. Prefer one reusable unit and restrained paint/wear variants over twelve unrelated models. Reuse the station petrol-painted metal and sensible galvanized hardware; avoid futuristic digital locks and uniform heavy rust.

Show several neighboring doors open at once and check their interaction with each other, the aisle and restroom approach. The eventual key/inventory puzzle is not specified: preserve individually identifiable lockers and lock parts for later logic, but do not choose which locker contains evidence, add a code mechanic or install game interactions. Leave most compartments empty.

Deliver the full fitted bank, player-height approach, a closed-door hardware close-up and an open-unit interior view. Provide exact source replacements, transforms, door pivots, opening angles, material slots, instance strategy and saved/reopened geometry/clearance checks. No master-scene or Unreal changes.

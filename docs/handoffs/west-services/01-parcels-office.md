# Handoff 01: luggage and parcels office

Implement this standalone Blender package now. Read [shared contract](shared-contract.md) and [references](references.md) first. Work only in `art/blender/west_services_parcels_01/`.

## Purpose and composition

A one-operator luggage / parcels office serving daytime visitors and storing objects recovered during overnight gondola inspections. Normal on Night 1. The office must support tagging, depositing, retrieving and comparing individual belongings later. Build readable physical organization, not a generic pile of luggage.

Clear interior station bounds: X [-37.25,-31.65], Y [-4.8,-.1], floor 4.60; ceiling zone begins 7.30. The south room is the parcels office. Use local origin (-37.45,-5,4.60) and collection `WSP_ASSETS`. Replace only `WS_PARCELS_PROXY`, whose exact members are in the master manifest. Shared walls and slab stay reference-only.

## Model scope

- East entrance: inward-opening door assembly with operable latch/key cylinder, threshold, frame and weather seals. Preserve >=1.30 x 2.15 m finished opening. Provide hinges and moving collision envelope, not just a rotated static door.
- East window: practical timber/painted-metal sash with glass and a working internal shutter; fit its fixed rough opening. It sits over the public-facing counter zone.
- Sorting counter near the east window with lockable clerk drawer, paper-tag dispenser, ledger location and small mechanical parcel scale. Keep the entrance-to-central-aisle route open.
- Rear open shelving in the west proxy reservation: distinct numbered bays with believable shelf spans and brackets. Build shelves as actual shelves, not the solid proxy cabinet. Mix bags, wrapped parcels and one old suitcase; leave several empty bays for future arrivals.
- Secure lost-property cabinet toward the south wall: visible wire mesh or glazed door, keyed closure and separate removable trays. Avoid a second wall of lodge-style lockers.
- Small luggage trolley with turning wheels and a parking position outside the walking/stretcher route. Paper tags, pencils, string spool, stamp pad and concise original signage. No photographic archive image used as a texture without rights.

## Working arrangement and interaction contract

Keep a 1.2 m operator aisle and a 2.2 m handling zone inside the entry. A 0.8 x 1.2 m trolley must be able to turn from the porch into the room in the fitted review. The shell's porch is a shared circulation route, not counter storage.

Named empties: `WSP_TAG_STATION`, `WSP_LOG_LEDGER`, `WSP_DEPOSIT_01` through `WSP_DEPOSIT_08`, `WSP_SECURE_CABINET`, `WSP_TROLLEY_PARK`. Deposit anchors must be above real support surfaces with independent props. Supply dimensions/approach direction and reach height in assembly.json. No gameplay scripts yet.

## Review and finish

Use references 1-4 for archival desk/shelving/counter logic, adapting it to existing alpine materials. Render exterior on the porch, doorway open/closed, inside toward rear shelves, reverse toward window, and close-ups of tag station and secure cabinet. Demonstrate a suitcase deposited and removed without rebuilding shelving.

Follow all contract delivery checks: saved/reopened .blend, evaluated topology, clear openings, door/drawer sweeps, surface ownership, texture provenance, proxy replacement list and assembly transform. Do not replace the shared shell to accommodate fittings. Flag a narrowly scoped opening patch if necessary. Unreal work and final shared-building polish happen later.

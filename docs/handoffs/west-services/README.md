# West services: three independent modeling handoffs

The combined Blender blockout is ready for three separate modeling tasks. This package does not automatically create or dispatch them.

Start with [shared contract](shared-contract.md) and [reference research](references.md).

1. [Luggage / parcels office](01-parcels-office.md)
2. [Rescue hut](02-rescue-hut.md)
3. [Emergency power room](03-emergency-power.md)

## Blender plan

Open `art/blender/west_services_01/Maldek_West_Services_Blockout.blend`, scene `West_Services_Combined`. This adds the western service building to the integrated lodge 04 context. All three spaces have proxy furnishings, real rough door/window openings and common access geometry. Hide `WS_SHARED_ROOF` for upper-room inspection. `WS_REVIEW_ONLY` holds cameras and origins, never export assets.

The current blockout establishes the footprint and interfaces. The detail tasks own rooms' fittings and openings, not three competing copies of the shared building. Read the master README and verification limitations before relying on terrain fit or collision.

## Paste into each future task

> Implement `docs/handoffs/west-services/01-parcels-office.md`. Read its shared contract and references, then complete the standalone Blender package, fitted review renders, assembly manifest and saved/reopened verification. Preserve the shared master and other tasks' files.

Use the same prompt with `02-rescue-hut.md` and `03-emergency-power.md` for the other two tasks. Each has an exclusive directory and collection.

## Later single integration task

1. Verify the blockout hash in its `delivery.json` and each package's source declaration. Read all three assembly/replacement manifests before appending.
2. Open a new derived master, `art/blender/west_services_02/`; preserve west_services_01 and lodge 04. Append only WSP_ASSETS, WSR_ASSETS and WSE_ASSETS with their stated transforms. Never combine whole fitted-review scenes.
3. Retire only each corresponding proxy collection and apply narrowly scoped, reviewed reveal/penetration patches. Keep a reconciliation ledger of exact source hashes, replaced objects, transforms and surface owners.
4. Refine the shared structural shell once: timber construction, slab/base transitions, soffits, drainage, roof ridge/eaves, supports and common guard joints. Incorporate the power exhaust sleeve route. Fit foundations and lower access to the then-current terrain; do not treat inherited Blender terrain as a live survey.
5. Check combined routes: existing arrival and west promenade; steps/porch to both rooms; trolley ramp; stretcher transfer; lower stair to power controls; doors/cabinets in working states. Inspect cross-package intersections and openings from both sides.
6. Render neutral exterior, upper cutaway, all three rooms, ramp/steps and lower access; save/reopen and record verification. Only then prepare Unreal export groups, units, pivots, collision, materials and runtime interaction ownership.
7. Unreal acceptance is separate: verify imported orientation using asymmetric landmarks, actual capsule routes, neutral/night/torch surfaces, small viewpoint changes and saved/reopened persistence. No package may claim these checks from Blender alone.

Gameplay proposals retained for later: recovered objects accumulate in labeled parcel bays; the rescue room can be prepared for an expected passenger; emergency power restores only refuge/communications/lights. Night 1 remains entirely mundane. No horror events or runtime systems are implemented by these mesh tasks.

## Completed assembly / September 11

All three room packages are complete and assembled in `art/blender/west_services_02/Maldek_Station_West_Integrated.blend`, scene `Station_West_Services_Integrated`. The integrated master retains their exact placement roots, separate mechanisms and material slots. See `art/blender/west_services_02/README.md`, `reconciliation.json` and `verification.json` for delivery checks and source hashes.

The user's follow-up also adds a continuous lower platform around the building, a wider west-door/stair-foot area, perimeter guards/supports and loose storage clutter on the spare sides. The power wall sleeve and roof-exhaust interface are resolved in the derived master. The original blockout and all standalone packages remain preserved. Unreal integration remains a separate phase.

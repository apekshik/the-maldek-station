# Maldek Station — integrated west services

Open **Maldek_Station_West_Integrated.blend**, scene **Station_West_Services_Integrated**, in Blender 5.0.1. This is the new combined authoring master: the existing passenger lodge / station context plus all three completed west-services packages, common architectural finish and the enlarged lower platform. Source masters and standalone deliveries are unchanged.

## What is assembled

| Package | Collection | Objects including pivots/text | Placement |
|---|---|---:|---|
| Luggage / parcels | WSP_ASSETS | 388 | (-37.45,-5,4.60) |
| Rescue / first aid | WSR_ASSETS | 343 | (-37.45,0,4.60) |
| Emergency power | WSE_ASSETS | 244 | (-37.45,-5,1.20) |

All three tasks reported completion. The actual editable-file hashes match their delivery manifests, and their saved-file verification reports pass. The 975 appended objects retain their hierarchies, material slots, editable mechanisms and local coordinates under one placement root per package. No fitted-review scene or duplicate room shell was appended. Exact hashes, transforms and retired proxy names are in `reconciliation.json`.

## Platform and common finish

The former short lower walkway is replaced by a continuous platform at Z=1.20 m, surrounding the entire 6 x 10 m building. Its outside bounds are X [-40.45,-28.95], Y [-7.5,10.6]. Four nonoverlapping slabs join the retained building base slab. The west door side is 3 m wide, the south/east bands 2.5 m, and the north area accommodates the bottom of the service stair plus a route around its low underside.

The perimeter has new guards, beam supports and piers fitted to the inherited Blender terrain. The lower door approach is clear. Pallets, three rough crates, spare boards, short pipe lengths and a covered bundle occupy the south/east spare areas. These are independent loose props, with no new gameplay requirement attached.

Common upper walls have exterior timber battens/bands and cream interior faces. The roof has seams, ridge trim, gutters and downpipes. The package's south exhaust-wall sleeve patch is applied once. A separate roof bore, low flashing, terminated roof seam and standoff socket resolve the exhaust at the overhang without altering the power package.

`roof_patch.json` records these interfaces. `roof_interface_probe.json` contains only the two intended wall/socket standoff contacts; the exhaust tube, roof panel, seam and flashing no longer have interfering surface intersections. These are game-mesh construction details, not an engineered installation certification.

## Review and mechanisms

The file opens at frame 1 with the compound overview and closed upper-room mechanisms. Frame 40 demonstrates the parcels mechanisms and rescue-ready pose; frame 80 shows rescue equipment open. Power mechanisms remain separately editable at their authored pivots; `scripts/review.py` sets its service doors open for appropriate views without baking changes into the saved master. These source demonstration states are not runtime interactions.

Hide `WS_SHARED_ROOF` for an upper-room cutaway. `WS02_WRAP_PLATFORM`, `WS02_STORAGE_CLUTTER` and `WS02_SHARED_FINISH` separate new circulation, loose dressing and shared finish. `WS02_ASSEMBLY_ROOTS` holds package placements. All `*_REVIEW_ONLY` collections are review metadata, not export assets.

`previews/` contains 12 views: compound, wrap platform, upper cutaway, lower plan, arrival, each room, shared porch, lower entrance, spare-side clutter and roof interface. Exterior overview/plan images use Blender workbench; room and detail images use temporary neutral Cycles lighting. They are not Unreal screenshots or the final game lighting.

## Verification

`verification.json` reopens the final saved master and checks:

- All three immutable package hashes, exact object presence/rest transforms and material slots.
- Retained station-context transforms and removal of all declared proxies/obsolete lower rails.
- Evaluated manifold / nondegenerate topology for 1,384 west-services meshes (combined delivered, retained and newly authored meshes).
- Exhaust wall-patch persistence.
- Six walking routes / 755 samples: retained promenade, ramp into parcels, steps into rescue, shared porch, lower service entry and full lower-platform loop. Support includes the existing grating's foot-sized sampling method; body checks use a 0.34 m radial envelope and 1.8 m head height.

All checks pass. Routes use an explicit transit state: doors open, parcel storage trays closed, rescue stretcher deployed. The rescue route follows the package's recorded clearance path around the passive door and stretcher. Its independent 435-sample stretcher handling evidence remains in the rescue delivery. Detailed package sweeps and handling checks are retained rather than claimed as newly repeated engine tests.

`delivery.json` records the final master hash. These are sampled Blender geometry checks, not continuous rigid-body collision or Unreal capsule tests. Foundation lengths use inherited R11 Blender terrain. Current Unreal terrain fit, export/LOD/atlas choices, material baking, collision setup and neutral/night/torch traversal remain the subsequent engine-integration phase.

## Reproduce

Use separate Blender background processes, sequentially, from the game repository:

1. `blender -b -t 4 --python art/blender/west_services_02/scripts/integrate.py`
2. `blender -b -t 4 --python art/blender/west_services_02/scripts/finish_interfaces.py`
3. `blender -b -t 4 --python art/blender/west_services_02/scripts/verify.py`
4. `blender -b -t 4 --python art/blender/west_services_02/scripts/roof_probe.py`
5. `blender -b -t 4 --python art/blender/west_services_02/scripts/review.py`

Integration always starts from frozen west_services_01 and verifies the source/package hashes. Interface finishing runs once after a fresh integration build. Review scripts reopen without saving. Do not run finishing repeatedly against an already-finished file. No source Blender package, live map, game code, checkout branch or external publication is modified by this delivery.

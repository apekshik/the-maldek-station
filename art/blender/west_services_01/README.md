# Western passenger support building — combined blockout

Open **Maldek_West_Services_Blockout.blend** in Blender 5.0.1, scene `West_Services_Combined`. The scene includes the integrated passenger lodge 04 and its station context, plus the new raised parcels / rescue building and lower emergency power room. The original lodge file is preserved.

## Layout

- Building footprint: 6 x 10 m, west of the existing promenade, X [-37.45,-31.45], Y [-5,5].
- Upper finished floor: Z=4.60 m, 0.60 m above the existing deck. Parcels is the south room, rescue the north room, separated by one shared wall.
- Lower finished floor: Z=1.20 m; concrete enclosure beneath both rooms. Emergency power is distinct from the station's main drive power.
- East porch: 2 m gross width, four 150 mm steps at the north end, 7.2 m long 1:12 trolley ramp at the south end and a 2 m bottom landing.
- Lower access: 16 x 175 mm risers / 350 mm goings, descending west along the north side to a lower west service walk. Doorway is on the west wall.
- Shared low roof, ceiling/gable closure, guardrails, slab/support blockout, real rough door/window/louvre apertures and furniture/equipment reservations are included.

Metres, Z up; +Y gondola side, -X west. These are Blender station coordinates, not Unreal transforms.

## Collections and review

`WS_SHARED_STRUCTURE` owns common architecture/access; `WS_SHARED_ROOF` can be hidden for an upper-room cutaway. `WS_PARCELS_PROXY`, `WS_RESCUE_PROXY` and `WS_POWER_PROXY` are explicitly replaceable fitting reservations. `WS_REVIEW_ONLY` contains five cameras and the three local assembly origin markers. The default camera shows the compound.

`previews/` provides the combined station, west building, upper cutaway, arrival/ramp approach lower entrance, porch at eye height and lower equipment reservation. These are neutral Blender workbench blockout views, not game screenshots or final materials. Dark objects in the rooms are intentional volume reservations, not completed furniture. Reference photography is linked in the research catalogue, not packed as unauthorized game textures.

## Handoffs

[Three work packages](../../../docs/handoffs/west-services/README.md), [shared contract](../../../docs/handoffs/west-services/shared-contract.md), [12-reference research catalogue](../../../docs/handoffs/west-services/references.md).

Each future task creates an isolated asset package, with its own door/window assemblies and room details. Shared walls/floors/roof stay with one later integrator. Exact proxy inventories and source hash are in `manifest.json`; package transforms and clear openings are in the shared contract. No new Codex tasks were dispatched by this planning pass.

## Reproduction and verification

Run Blender `--background --python art/blender/west_services_01/scripts/build.py`, then `scripts/verify.py` using its full repository-relative path. The builder starts from immutable lodge 04, writes only this derived package and renders five views. Run `scripts/review_extra.py` for two additional interior/eye-height views. The verification script reopens the saved file and writes `verification.json` plus the delivery SHA-256 in `delivery.json`.

`survey.json` records the inherited western context bounds. `manifest.json` records preserved transforms and exact retired west-boundary rails; replacement guards follow the new level changes. `terrain_support.json` records support toes fitted 0.35 m into the inherited Blender terrain. No original context mesh is modified; only the listed rail objects are retired in the derived scene.

Verification covers new closed-mesh topology, saved source hash, retained object transforms and sampled supporting-floor/body/headroom checks for five walking routes. It does not certify continuous collision, finalized furniture/door swing or stretcher handling. Those are explicit detail-package and later Unreal acceptance requirements.

## Remaining integration work

This is the structural and circulation blockout requested for delegation. Room fittings, door/window details, refined timber construction, roof drainage/joints, material polish, export grouping and engine collision are subsequent work. Support lengths use inherited R11 Blender terrain, not a survey of current Unreal terrain. Final terrain fit and actual player traversal must be reviewed before importing.

The power handoff must resolve proper intake/discharge duct routing, engine removal access and exhaust sleeve details. The present machine and pipe shapes are reservations, not an engineered installation. Baseline scene has no horror events or runtime changes. Existing arrival, lodge, control and main equipment are retained.


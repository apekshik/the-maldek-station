# Handoff 02: small rescue hut

Implement this standalone Blender package now. Read [shared contract](shared-contract.md) and [references](references.md) first. Work only in `art/blender/west_services_rescue_01/`.

## Purpose and composition

A modest unattended rescue / first-aid room where an operator can prepare shelter for a returning passenger. Warm, organized and maintained. It is not a hospital, staffed rescue headquarters or horror scene. The unsettling possibilities come later from who fails to arrive.

Clear interior station bounds: X [-37.25,-31.65], Y [.1,4.8], floor 4.60; ceiling zone begins 7.30. The north room is the rescue hut. Local origin (-37.45,0,4.60), collection `WSR_ASSETS`. Replace only `WS_RESCUE_PROXY`; exact names are in master manifest.

## Model scope

- East entrance: paired inward-opening leaves, frame, seals, threshold and practical latch hardware. Finished clear opening >=1.50 x 2.15 m with both leaves open. Provide independent active/passive leaf pivots; hold-open hardware should not obstruct the transfer route.
- East window in the fixed aperture, with simple internal privacy blind. Preserve some view of the platform when standing; glass and blind are separate.
- One narrow cot in the reserved west-central position and a separate folding rescue stretcher stored on properly supported wall brackets. Show straps, carrying handles, fabric tension and hinge logic. Do not use the cot as the only transport device.
- Blanket cupboard, first-aid cabinet, modest first-aid bag, splints, rope bag, hooks, boot tray and a chair. Organize equipment by use; no crowded surgical trolley or modern monitor.
- Small electric heater near the north wall, grille and physical thermostat. Preserve clearance from textiles. Its emergency circuit supplies modest refuge heat, not the whole lodge.
- Wall radio/telephone point with analog controls, readiness checklist, pencil, simple room sign and a restrained first-aid symbol. Original art only. Avoid protected organizational branding.

## Handling and future gameplay

Demonstrate a 2.2 x 0.75 m stretcher passing through the east doorway and turning into a usable position with doors held open. Keep an approximately 2.2 m turning zone at the entrance. Document the sampled path including corners and clearances; a person-only route test does not prove stretcher access. The 1:12 ramp and porch are shared, reference-only geometry.

Named empties: `WSR_STRETCHER_STOW`, `WSR_STRETCHER_READY`, `WSR_BLANKET_PLACE`, `WSR_HEATER_CONTROL`, `WSR_READINESS_CARD`, `WSR_RADIO_POINT`. Supply reachable control heights and orientations. Prepare normal empty and ready-for-arrival arrangements as named poses/collections without changing architecture. No missing-person evidence, paranormal props or medical instructions are required.

## Review and finish

References 5-8 establish equipment relationships and practical construction. Modern product photographs are shape references; this asset must fit the station's analog/early-1990s vocabulary. Render from the porch, both sides of the door, room toward cot, equipment cupboard open, stretcher folded/deployed, and a neutral overhead handling view.

Follow the contract's editable source, transforms, exact proxy replacement, packed texture/provenance, moving-part and saved/reopened checks. Do not author a second floor, party wall or roof. Final engine capsule/stretcher interaction, actual lighting and gameplay remain integration work.

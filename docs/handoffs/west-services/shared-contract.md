# Shared authoring contract: west services

Read `AGENTS.md`, `art/MESH_AUTHORING.md`, this contract, `references.md`, then the assigned handoff. Repository: `C:/Users/apek-anna/Developer/the-maldek-station`.

## Frozen assembly source

`art/blender/west_services_01/Maldek_West_Services_Blockout.blend`, scene `West_Services_Combined`. This derives from integrated passenger lodge 04; the original is unchanged. Consult `art/blender/west_services_01/manifest.json` for the exact source hash, retired west guard names and proxy inventories. Consult `verification.json` for actual checks and limitations. Do not substitute an older lodge 01/02 shell.

Units: metres, Z up, +Y toward gondola side, -X west. Objects in the master are in station coordinates. Upper floor Z=4.60, lower floor Z=1.20. Do not convert to centimetres inside Blender.

| Package | World origin for local authoring | Output collection | Exclusive output directory |
|---|---|---|---|
| Parcels | (-37.45,-5,4.60) | WSP_ASSETS | art/blender/west_services_parcels_01 |
| Rescue | (-37.45,0,4.60) | WSR_ASSETS | art/blender/west_services_rescue_01 |
| Power | (-37.45,-5,1.20) | WSE_ASSETS | art/blender/west_services_power_01 |

For asset-only local authoring subtract the listed origin once. Integration adds it once, with identity rotation and unit scale. Alternatively keep world coordinates and explicitly declare identity assembly transform. Never mix both conventions. Supply matrix and asymmetric orientation marker in `assembly.json`. Preserve child world transforms if changing hierarchy; do not translate parent and child twice.

## Ownership

Master owns `WS_SHARED_STRUCTURE` and `WS_SHARED_ROOF`: foundation, slabs, all walls including party wall, roof, porch, ramp, stairs, common rails and supporting members. These are blockout architecture with real openings. None of the three packages duplicates a building shell, floor, roof, shared wall, ramp or staircase. A later integration pass refines that shared architecture once.

Each room package owns its own entrance door/frame/threshold, its windows, interior fittings and room signage. Power owns both lower louvres, equipment, service doorway, exhaust and service penetrations. Each package replaces only its corresponding `WS_*_PROXY` collection, including its provisional lettering. No other package may touch those names. Delete proxies only in your review copy; supply the deletion list for later assembly.

Rough openings are fixed; finished frames must fit inside them while maintaining the clear opening target. Assign the visible reveal to your frame and recess any concealed shell face in a narrowly scoped patch. Document exact mesh/object/face changes and replayable patch script, not a replacement copy of the entire master wall. Existing shared walls are 0.20 m upper / 0.25 m lower. No blanket offset, duplicate wall skins or solids across openings.

## Interfaces and circulation

- Upper porch X [-31.45,-29.45], Y [-5,5], floor 4.60. Keep 1.8 m usable width and doorway approaches clear. Doors open inward; hinges must be authored for that motion.
- Parcels east rough doorway: Y [-3.9,-2.4], Z [4.6,6.95], wall X [-31.65,-31.45]. Finished clear target >=1.30 x 2.15 m.
- Rescue east rough doorway: Y [1.2,2.9], same Z/wall. Finished clear target >=1.50 x 2.15 m, paired leaves if appropriate.
- Parcels east window: Y [-1.8,-.4], Z [5.6,6.65]. Rescue east window: Y [3.35,4.45], same Z.
- Power west rough doorway: Y [1.4,3.0], Z [1.2,3.5], wall X [-37.45,-37.2]. Finished clear target >=1.40 x 2.10 m. Removable frame/machine-handling plan to be documented.
- Power west louvre holes: Y [-3.8,-2.3], Z [1.8,2.9]; Y [-.8,.7], Z [2.3,3.4]. Detail task must distinguish intake/discharge and prevent short-circuit routing; may request a precise alternate-wall aperture if justified. No airflow through occupied rooms.
- Exhaust riser reservation is south of the building near (-35.2,-5.3), top approximately 8.8. Keep it clear of the public porch and windows. Task owns properly connected sleeves, insulation, brackets and cap; existing tubes are route proxies.
- Keep room doors, drawers, electrical switches, shutters and other moving parts separate with actual pivots. Record closed/rest/open states and swept bounds.

## Style and gameplay

Warm practical alpine visitor station; old infrastructure maintained into early 1990s, analog interaction. Pine, cream, petrol enamel, galvanized hardware, local contact wear. Procedural Blender materials must be identified as such. Do not add runtime behavior, horror events, new story facts, digital displays or branded copied art. Supply named interaction anchors for later gameplay.

## Required delivery

Editable asset-only .blend; fitted review .blend or reproducible fitted review builder; scripts; README; `assembly.json`; exact proxy replacement list; material slots; dimensions and pivots; close neutral renders and player-height context; open/closed mechanism views; saved/reopened geometry validation. Pack permitted textures, retain provenance, and exclude reference context/cameras/lights from asset exports. Keep UVs usable and identify any later baking/LOD work.

Check evaluated mesh topology and cross-object surface ownership; inspect all opening sides and thresholds. Test conservative 0.34 m radius / 1.8 m tall walking envelopes. Rescue also tests a 2.2 x 0.75 m stretcher handling envelope. Do not claim engine collision verification from Blender. Unreal neutral/night/torch, glancing moving views, save/reopen and actual capsule traversal remain integration gates under MESH_AUTHORING.md.

Only write your assigned package directory. Do not edit the shared master, other deliveries, live maps, game code or the checkout branch. Do not create user-owned tasks or dispatch messages automatically. Completed packages are to be assembled later by one integration task. Respect unrelated working-tree changes. Do not infer permission to publish or push from historical handoffs for unrelated work.

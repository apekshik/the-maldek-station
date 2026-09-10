# Passenger lodge — Blender layout 01

Open `Maldek_Passenger_Lodge_Layout.blend`. This is the first editable blockout of the approved six-table lodge, not a finished architectural asset. One unit is one metre; local X runs across the room, -Y runs from platform facade toward the rear annexes, and floor top is Z=0. Final station placement is deliberately uncommitted.

The main scene contains the complete 217.8 m² gross program: six table tops and twelve benches, twelve numbered lockers, poster placeholders, serving hatch and enclosed prep room with appliance proxies, public lost-property cubby, two restrooms and screened hall. Wall openings have real voids, door sweeps are gold, and sampled walking routes are green. Furniture and fixture names support later replacement with detailed meshes. Roof envelopes are in a separately hidden collection so the layout can be reviewed; they are not final roof construction. Window inserts currently mark frosted-glass volumes with an opaque proxy material.

`02_Protected_Site_Study` contains retained floor anchors and arrival/forest route corridors from the VF07 source layout. It is a source reference, not a live Unreal survey. No existing pathway, station asset or Unreal map was modified. There is no claimed terrain clearance or approved placement for the larger lodge. Before merging the lodge with the station, survey the latest map and expand its footprint outward while preserving the established approach. The context scene intentionally does not guess a building transform that could obstruct the route.

Review images: top plan, cutaway, player entry, coffee workspace and restroom approach. `layout_report.json` records the room program and sampled 0.34 m radius horizontal clearance checks against solid blockout proxies. `verification.json` records reopening, evaluated manifold checks and counts. These are layout checks, not a continuous physics sweep or Unreal movement test.

## Detail sequence

1. Review this room blockout at player height; resolve any layout changes now.
2. Survey and freeze the station placement, deck edges and protected path clearances.
3. Author shell construction: roof pitches, structural frame, wall build-up, window/door reveals, ceilings and utility routes. Follow `art/MESH_AUTHORING.md` for surface ownership and openings.
4. Replace picnic-table/bench proxies with one detailed master set and controlled wear variants. Then lockers with hinges, doors, vents, numbers and the key mechanism.
5. Detail service counter, cabinetry, kettle, coffee urn, microwave, fridge and washing facilities. Keep all working/door envelopes intact.
6. Detail restroom partitions, fixtures and signage, then posters, exact menu/timetable text and the inspection objects. Generate decorative artwork only after dimensions and UVs are fixed.
7. Materials, restrained wear, lighting, sound and final Blender review; then export/import and test Unreal. No phase is marked finished merely because a proxy exists.

Rebuild from repo root with Blender 5.0 background `--python art/blender/passenger_lodge_01/scripts/build.py`, then run `scripts/verify.py` in a separate Blender process. Earlier station and lodge plans remain the design reference.


## Existing station included

`03_Existing_Station_Reference` appends the actual VF07 station scene, including platform plates/grating, railings, stairs, control, quarters and terrain. Imported source mesh transforms are checked unchanged and the original .blend is not modified. This replaces reliance on simple reference boxes when judging the design against existing architecture.

A linked instance of the new lodge is staged west of the station at (-43, 0, 4) metres for side-by-side comparison. **This is a staging position, not its proposed final location or a connected platform.** Edit lodge geometry in `01_Lodge_Layout`; the reference-scene instance follows those edits. Work toward the existing control/platform by replacing only the identified waiting-hall/deck parts after a route-protection and site-fit pass. Do not move the established approach to make the staged instance fit.

Run `scripts/add_station_reference.py` after the blockout build and before `scripts/verify.py`. It adds the reference scene and sixth review image. The saved file opens on that reference scene. `station_reference.json` records provenance and preservation checks. This remains the VF07 source baseline, not a fresh export of all subsequent Unreal dressing changes.

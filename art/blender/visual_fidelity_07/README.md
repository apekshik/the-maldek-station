# Maldek station — circulation cleanup 07

Open `Maldek_Station_Cleanup.blend` in Blender 5.0.1. This is a separate, editable revision of VF06 addressing the six screenshot issues. Earlier revisions and Unreal assets are preserved.

## Changes

- Removed the inherited railing through the control doorway. Moved a timetable board that also obstructed the waiting-hall rear entrance.
- Rebuilt the public deck with real open grating against the control facade and around the outer perimeter, including the gondola-side connection and east terrace. Removed obsolete solid backing slabs and bridge-junction guards. The gondola boarding opening remains intentional.
- Filled the former arrival stair slot across the rear platform. A 1.8 m wide stair now climbs west along the outside edge, meets a turning landing, and leads onto the promenade. The waiting-hall entrance is reached across the completed deck.
- Moved the quarters stair clear of both building shells. Its 1.6 m wide flight has an open lower approach and a separate upper turning landing to the existing door at +7.65 m.
- Replaced overlapping lower-yard slabs and paths with one service apron. Both descending stairs end on flush grating landings recessed into that apron. Refreshed the internal stair treads with the same fine grating used in the new stairs.
- Cut and blended the terrain away from the service stair, apron and road approaches. The service road and relay routes have separate apron connections; the returning route has a proper opening in the terrace guard.
- Routed the water main below the service apron and along the service edge, with its shutoff mounted on the lower building wall.
- Shifted one canopy support out of the walking strip and added its connection bracket. Rebuilt affected deck foundations and grounded the bridge backstay anchors after terrain grading.

The principal deck bands remain **1.8 m grating → 3.6 m solid plate → 1.95 m grating**, measured outward from the waiting hall. Local dock and stair connections adapt to their actual footprints. The control room, quarters, lower drive and gondola floor bounds remain unchanged from VF06. This revision inherits VF06's alignment to the audited Unreal R11 layout; its expanded decks and local terrain grading are proposed Blender changes.

## Review

Ten cameras and their rendered images are in `previews/`: connected station, sideways arrival, control doorway, quarters stair, service descent, dock border, water/routes, platform plan, whole site, and the view up the quarters stair. The saved project opens on the complete station camera. Forest dressing is omitted to expose the geometry.

`verification.json` records **18 passing routes, 805 sampled positions and 9,505 mesh rays**, plus six passing anchor/surface checks. Cross-sections test declared clear widths at four body heights; five lateral headroom probes extend to 2.10 m above each sampled floor. Foot patches check contact with actual visible floor/grating meshes. Declared widths range from 0.8 m at the quarters doorway to 1.4 m within the new 1.8 m stairs. The report identifies the width for each route.

These are sampled Blender geometry checks and visual reviews, not a complete continuous capsule sweep or Unreal playtest. No Unreal import, collision rebuild, material baking or engine performance validation was performed. Before replacing level assets, transfer the changed terrain and access geometry together and validate player movement in Unreal.

## Rebuild

Run these in separate Blender background processes, from the repository root:

```powershell
& 'C:/Program Files/Blender Foundation/Blender 5.0/blender.exe' --background --factory-startup --python art/blender/visual_fidelity_07/scripts/build_cleanup.py
& 'C:/Program Files/Blender Foundation/Blender 5.0/blender.exe' --background --factory-startup --python art/blender/visual_fidelity_07/scripts/verify_routes.py
& 'C:/Program Files/Blender Foundation/Blender 5.0/blender.exe' --background --factory-startup --python art/blender/visual_fidelity_07/scripts/render_review.py
```

The builder loads VF06 and writes only VF07. It reuses mesh helpers from VF01, VF02 and VF06. `layout.json` records the authored deck rectangles, walking routes, pipe centerline and preserved anchors. One Blender unit is one metre; +X east, +Y toward the cable route, +Z up. Main platform +4.00 m; service apron 0.00 m; quarters +7.65 m.

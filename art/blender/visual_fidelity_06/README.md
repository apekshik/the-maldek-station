# Maldek — integrated station study 06

Open **Maldek_Integrated_Station.blend** in Blender 5.0.1. This is a separate editable project combining the reviewed VF05 architecture with the actual R11 station layout and terrain. Earlier Blender projects and Unreal maps are untouched.

## What changed

- Enlarged 5.8 × 5.2 m control room at the real dock, with electrical cabinets, controls, workbench, pipes, vents and glazing. The existing 9.8 × 7.8 m waiting hall footprint is retained.
- Furnished living/radio quarters at +7.65 m, reached by a rear stair. The upper room projects 1.2 m toward the dock. The west canopy ends at a flashed junction clear of its transfer floor.
- Deck bands run outward from the buildings: **1.8 m open grating → 3.6 m plate → 1.95 m open grating**. They wrap the waiting hall and rear circulation, stopping at the gondola bay and stair openings. Existing confined dock and stair connections retain their footprint.
- The actual 3.1 × 6 m gondola keeps its movement pivot, boarding opening and alignment. Added bench cushions, grab rails, door track, lights, rub strips, fasteners and markings complement the inherited cabin details.
- The 8 × 7 m lower drive gallery retains its machinery. Added overhead pipes, task lighting, inspection plates, service markings, lockers and a repair bench. The former generator footprint remains lower-level service space.
- The separate R11 generator, workshop, relay hut, diesel yard and connecting routes remain in their actual locations. Replacement shells follow the container material style and preserve route-facing doors.
- A braced water tower sits on a separate service terrace near (21, -18), with a graded approach and supply pipe. The terrace includes a proposed local terrain cut; it is not part of the existing Unreal landscape.

## Review views

Images in `previews/`:

1. `01_Integrated_Station.png` — main dock, public platform, upper room and lower gallery.
2. `02_Whole_Site.png` — station, service buildings, relay and connecting routes.
3. `03_Dock_Approach.png` — close view from the dock.
4. `04_Lower_Drive.png` — machinery, service access and lower-floor details.
5. `05_Rear_Arrival.png` — arrival descent, broad deck bands and quarters stair.
6. `06_Service_Yard.png` — water terrace and existing diesel yard.
7. `07_Public_Plan.png` — labeled public floor, roofs/upper room hidden for review.
8. `08_Lower_Plan.png` — labeled lower-floor arrangement.
9. `09_Station_Section.png` — clipped section/elevation comparing floor levels.
10. `10_Quarters.png` — living/radio room interior.

The saved Blender project contains the complete geometry; the render script applies temporary visibility changes for plans and section views.

## Source and verification

The live read-only Unreal audit identified `/Game/MaldekRefinement/ForestTest/Forest_Approach_Test`, using the R11 station, R10 dock/hall and inherited R04 architecture chunks. `live_unreal_audit.json` records mesh paths and actor transforms. Fixed station chunks share location (-44282.305975, 18474.707549, 9898.5) cm and yaw 180°. The gondola is separately placed at the existing movement pivot.

Geometry sources: `art/unreal_handoff/revision11/station_layout.blend` and its separate `terrain_grid.json`. The older terrain embedded in the layout file was replaced with that current terrain grid in this study. VF05 parts are appended into named VF06 collections; the previous showroom decks are not carried across.

`verification.json` records **88 passing checks**: unchanged measured anchors and original visible stair treads, protected deck voids, and floor/headroom point samples at doors, cabin entry and service aisles. These are Blender geometry checks, not an Unreal capsule walkthrough or collision certification. Service-path finishes are lifted 12 mm to avoid coincident faces on the existing hardstanding.

One Blender unit is one metre. +X east; +Y toward the cable route; +Z up. Main public floor +4.00 m; lower drive 0.00 m; quarters +7.65 m; remote maintenance -1.00 m; relay +3.00 m.

## Rebuild and handoff

Run `scripts/audit_sources.py` to refresh source inventories, then `scripts/build_integrated.py`, `scripts/verify_integrated.py`, and `scripts/render_review.py` in separate background Blender processes. The live audit script must run inside Unreal's editor Python context and only writes the JSON audit.

This revision is a design and mesh study. **No Unreal import has been performed.** Procedural Blender materials still need an Unreal material/baking pass; collision, LODs, performance, terrain transitions and gameplay connections require engine validation before replacing level assets. Forest dressing is omitted from review renders so the architecture remains visible.


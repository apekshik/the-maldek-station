# Station gorge: nighttime terrain pass

The current R12 map contains the local cliff, solid western platform shoulder,
172 additional descending pines and 12 embedded rock masses. Distant Gaia mountain
composition, station position, lighting, weather, fog, doors and audio are retained.

## Terrain and access

The local change mask is x (-96,111), y (-15,170) metres relative to the station.
The western shoulder occupies x (-26,-4), y (-15,9.5), reaching 3.48 m below the
3.72 m slab underside. It leaves the arrival stairs and lower gallery clear.
At x=-7, heights at y=7,20,30,40,60,90 are approximately 3.20,-21.26,-53.17,
-64.78,-71.57,-81.46 m. The crest is irregular and returns to the existing valley.

The mesh source is station_gorge.blend, exported as SM_Station_Gorge_Terrain.fbx.
The live edit uses gorge_native_probe.py and gorge_native_apply.py, backed by
bounded CPU access in the editor-only StationMigrationTools module. The probe
reads current merged/base heights. The apply rejects stale source data and touches
only 34,593 height values within the local rectangle. Normals and collision update
through the landscape edit layer pipeline.

gorge_dress.py grounds affected vegetation and adds deeper trees and rocks.
gorge_crest_trees.py adds twelve nearer treetops below the deck edge.
gorge_verify.py checks thirteen live collision points, merged height readback,
and 790 unaffected actor transforms. gorge_capture.py uses existing scene lighting.
Transient pointer addresses are excluded from transform comparison.

## Correction to the earlier failed workflow

The old landscape_before.png was completely blank RGBA (all channels zero),
despite the export API reporting success. The earlier pixel preservation report
did not validate preservation of actual landscape data. Full imports using that
image were invalid and repeatedly exhausted memory. Those attempts were rolled
back before resuming this pass.

gorge_install.py is disabled and gorge_heightmap.py now rejects blank exports.
Do not use retained landscape_gorge.png, landscape_applied.json, or the old
heightmap_report.json as current installation evidence. They describe the retired
attempt. Current evidence: native_probe.json, native_applied.json,
verification.json, dressing.json, crest_trees.json and review images.

## Latest rollback

Station_R12_ca7d494_before_resume.umap preserves the complete pre-pass map,
including latest physical-key/keypad doors, recorded turn audio and F6 marker.
Earlier backups predate those features and must not be used for a current rollback.
Do not overwrite this backup or restore it over subsequent user edits.

## Daylight review

The user requested a brighter Ultra Dynamic Sky inspection (Time Of Day 1300).
That review exposed the rectangular mesh join and reimport material slots.
The mesh was extended 74 m, its full perimeter was matched to native ground
(658 samples; maximum mismatch 0.000087 m), and every section was assigned the
correct material. A 3 m masked edge blend softens the overlay/landscape material
transition. Source: gorge_blend_edges.py, gorge_prepare_edge_patch.py,
gorge_mesh_refresh.py and gorge_edge_material.py. Final terrain evidence is
native_edge_patch.json and native_edge_applied.json. The original night settings
are recorded in night_sky_settings.json and restored after inspection.

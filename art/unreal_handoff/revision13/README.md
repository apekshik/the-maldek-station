# Approved service-area port

VF08 generator/fuel design and VF09 concrete/grating cleanup are installed in
`/Game/MaldekRefinement/R12/Station_R12`. R13 is the asset revision; the playable
map name and project startup configuration remain R12.

The port includes the 10 × 10 m generator hall, connected workshop, detailed
diesel engine/alternator/radiator, hoist, switchgear, exhaust and ventilation,
horizontal fuel tank, emergency filling equipment, continuous apron, framed
grating, recessed foundations, water-main reroute and local terrain grades.
Fuel-transfer equipment is visual geometry; this does not implement refuelling
gameplay.

## Integration

- 22 imported assemblies replace 41 explicitly identified R12 mesh components.
  Original actors remain for reference stability. A partially replaced water
  assembly retains its valve pieces in a separate R13 asset.
- Existing R12 baked materials are reused. New indoor variants exclude exterior
  weather effects; oxide-red fittings use an evaluated Blender bake.
- Four ceiling lights and one south bulkhead light align with modelled fixtures.
  Five obsolete service-area lights are disabled. Generator audio follows the
  new machine position; current audio, player and global weather changes remain.
- Only 1,663 changed terrain vertices are merged into the current R12 surface.
  Landscape collision probes show at least 4.57 m underlay clearance at these
  vertices, so no Landscape heightmap is modified. A blank render-target export
  was rejected, never imported; collision probes provide the usable evidence.
- One pine intersected the enlarged workshop and was relocated to adjacent
  terrain; the remaining 137 painted trees retain their locations.

## Validation and evidence

`integration_ledger.json` records FBX hashes, actor identities, material slots,
collision hulls and bounds validation (under 0.2 cm error).
`play_routes.json` records all 11 routes passed in both directions with ordinary
player movement, including workshop, fuel access, grating borders and approach
ramp. The gondola remained stationary. These are traversal tests, not a 60 FPS
performance certification.

`reviews/` contains 1440p production-night and temporary inspection-light views;
the inspection light and overrides are removed afterward. `reviews/openings/`
contains rapid close-ups with small viewpoint changes at the three doorway
constructions. `saved_verification.json` records the final reloaded-map check.

Source: `art/blender/visual_fidelity_09/Maldek_Service_Apron_Refinement.blend`.
`scripts/export_assets.py` preserves later R12 work outside the service area;
do not replace the whole current map with the older full Blender scene.

## Reproduction

Run `scripts/export_assets.py` and `scripts/bake_red.py` with Blender 5.0.
With Station_R12 loaded and PIE stopped, run `scripts/import_service.py` in
Unreal's Python environment, followed by `scripts/environment.py` on first
installation. R12 dispatcher bridge scripts and the route/capture job files
record the verification entry points. Coordinate editor ownership before use.
Do not rerun the environment/foliage snapshot after later layout work without
first reviewing those later changes.

Mesh solids use Nanite with full fallback geometry for faithful traced detail;
thin pipework and grating use three conventional LODs. Measure the expanded
service area in a later performance pass before claiming the 1440p/60 FPS target.

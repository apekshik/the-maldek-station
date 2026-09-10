# Station expansion around the passenger lodge

September 9, 2026. **Station placement proposal; lodge program approved.** No Unreal actors or Blender meshes changed in this planning pass. [Current compound map](../floorplan.html#v3) · [Approved lodge](../passenger-cabin.html).

## Basis and limits

The approved lodge is 217.8 m² gross: a 14 × 11.2 m hall, a 5 × 5 m coffee annex and a 6 × 6 m restroom wing. Six tables and twelve benches are required. The hall, serving hatch, separate restroom corridor, southeast lockers, west posters and solid control-facing wall remain as approved.

R12 records establish the public floor at +4 m, lower service level at 0 m, and living/radio quarters at +7.65 m. Existing generator, workshop, fuel yard, water terrace and relay destinations must be retained. These elevations are local design datums, not Unreal world Z. The older V1/V2 website drawings and V2 3D model remain explicitly historical; they are not the basis for measuring the current site.

V3 is a metre-scaled placement study at 20 drawing units/metre for the central compound. The lodge outline follows its approved dimensions. Control's 6 × 5 m rectangle and the other retained envelopes are placeholders pending a current mesh survey. The remote route box and lower-level inset show connections only. No claimed before/after displacement is derived from the historical map.

## Placement decision

Keep the gondola dock, cable axis, drive machinery and control booth as anchors. Expand the public deck west and toward the arrival side, rather than moving the cable alignment to accommodate furniture. Place the lodge west of control, with its platform exit facing the dock apron and its entrance court facing the approach. The 14 m hall width is visibly larger than control; its southward depth and annexes determine the new arrival edge.

The new platform envelope is a proposal, not a requirement to fill the entire site with a single slab. Break it into the boarding platform, a 3 m clear covered lodge frontage, and supported arrival/bypass terraces. Keep a 3 × 3 m landing at the lodge's north exit. Rework west/south supports, edge drainage, guardrails, roof seams and lamps together. Keep the gondola sign and boarding sequence visible from the lodge exit and final stair landing. Do not put columns in the gondola door sweep or boarding path.

## Circulation and changes

| Element | Proposed treatment | Connection / clearance target |
|---|---|---|
| Public stair | Relocate toward the lodge entrance court | 4 × 6 m switchback reservation; 1.8 m clear flights and landings; nominal +4 m rise |
| Final approach | Reroute only the station-end segment after terrain survey | Existing parking/forest route → lower stair landing; retain established start/checkpoints |
| Arrival terrace | Extend to meet the new court | Stair top → 3 m wide court → lodge entrance; 1.5 m clear through-route |
| Lodge platform frontage | Extend west from the retained boarding platform | 3 m clear covered strip; no coffee queues on boarding route |
| Exterior bypass | Add along lodge's east edge | 2 m clear path from arrival terrace to platform; control remains reachable when lodge is closed |
| Control | Retain booth and actual keypad door | Exterior approach only; survey exact door side and align final path accordingly |
| Service stair | Keep eastern service corridor; adapt top landing if necessary | Platform ↔ lower gallery/yard without crossing the new public stair |
| Quarters access | Retain independent upper-level connection | Preserve headroom, supports and access to +7.65 m; do not place lodge roof through it |
| Remote routes | Retain relay, bridge, overlook and water destinations | Adjust near-station ties only where apron perimeter changes |

For the nominal 4 m rise, begin the public stair study with 24 risers of about 167 mm in two flights. Resolve exact riser/tread count and landings from the measured level difference. The reservation is not a tested stair mesh. Verify capsule turning, rail offsets, headroom and the player's downward view at both landings. Do not leave the old stair or collision under the new terrace when implementing the replacement.

Public loop: approach → stair → court → lodge → apron → exterior bypass → court. Control is a branch from the apron through its keypad entrance, never a passenger through-route. Staff access to coffee remains off the court. The service loop remains distinct below/east of the public areas.

## Ground and structural implications

The wider lodge needs a terrain/support survey before choosing a slab, piers or retaining wall. Preserve machinery clearance beneath the dock and the lower service route; no broad foundation collision box may block either. Determine where the new west terrace meets ground and where it needs independent support. Provide deliberate roof runoff and walkway drainage so the enlarged roof does not shed onto the stair. Check sightlines from the incoming path to the gondola status sign after choosing roof pitches.

## Build sequence

1. Export/read current station bounds and all door/route landing transforms. Include terrain, dock, control, quarters, service stairs, bridge and water connection. Overlay this proposal; document required offsets instead of using historical web geometry as truth.
2. Block out the lodge at full approved size with the new apron, court, bypass and both stair corridors. Resolve terrain and support ownership under `art/MESH_AUTHORING.md` before detail work.
3. Walk parking → lodge → dock, parking → external keypad → control, platform → lower service yard, and all retained remote connections. Test with lodge closed. Review night sign visibility and roof/quarters clearance.
4. Freeze site transforms and architectural shell only after those checks. Build furniture and details inside the validated envelope.
5. Integrate as an explicit replacement set: old waiting-hall shell, obsolete stair/landing segments, affected deck/rail/roof pieces and their collision. Retain cable machinery, control security, checkpoints and remote buildings. Save/reopen and retest routes after Unreal import.

V3 makes the station changes reviewable; it does not assert terrain feasibility, current collision clearance or a final construction footprint.

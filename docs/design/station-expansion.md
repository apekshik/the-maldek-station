# Station expansion around the passenger lodge

September 9, 2026. **Station placement proposal; lodge program approved. Stair/terrace correction based on saved R12 and Blender references.** No Unreal actors or Blender meshes changed in this planning pass. [Current compound map](../floorplan.html#v3) · [Approved lodge](../passenger-cabin.html).

## Basis and limits

The approved lodge is 217.8 m² gross: a 14 × 11.2 m hall, a 5 × 5 m coffee annex and a 6 × 6 m restroom wing. Six tables and twelve benches are required. The hall, serving hatch, separate restroom corridor, southeast lockers, west posters and solid control-facing wall remain as approved.

R12 records establish the public floor at +4 m, lower service level at 0 m, and living/radio quarters at +7.65 m. Existing generator, workshop, fuel yard, water terrace and relay destinations must be retained. These elevations are local design datums, not Unreal world Z. The older V1/V2 website drawings and V2 3D model remain explicitly historical; they are not the basis for measuring the current site.

V3 is a metre-scaled placement study at 20 drawing units/metre for the central compound. The lodge outline follows its approved dimensions. Control's 6 × 5 m rectangle and the other retained envelopes are placeholders pending a current mesh survey. The remote route box and lower-level inset show connections only. No claimed before/after displacement is derived from the historical map.

## Placement decision

Keep the gondola dock, cable axis, drive machinery and control booth as anchors. Expand the public deck west and toward the arrival side, rather than moving the cable alignment to accommodate furniture. Place the lodge west of control, with its platform exit facing the dock apron and its entrance court facing the approach. The 14 m hall width is visibly larger than control; its southward depth and annexes determine the new arrival edge.

The new platform envelope is a proposal, not a requirement to fill the entire site with a single slab. Break it into the boarding platform, a 3 m clear covered lodge frontage, a 7.35 m broad west promenade, and continuous arrival/bypass terraces. Keep a 3 × 3 m landing at the lodge's north exit. Rework west/south supports, edge drainage, guardrails, roof seams and lamps together. Keep the gondola sign and boarding sequence visible from the lodge exit and final stair landing. Do not put columns in the gondola door sweep or boarding path.

## Circulation and changes

| Element | Proposed treatment | Connection / clearance target |
|---|---|---|
| Public stair | Sideways climb along outer edge, then turn onto promenade | 1.8 m clear flight, 2 m turning landing; nominal +4 m rise; no head-on approach |
| Second deck descent | Proposed along the outer right/east side of bypass | Flush landing; connect below after terrain survey; separate from retained service stair |
| Final approach | Reroute only the station-end segment after terrain survey | Existing parking/forest route → lower stair landing; retain established start/checkpoints |
| Arrival terrace | Extend to meet the new court | Stair top → 3 m wide court → lodge entrance; 1.5 m clear through-route |
| Lodge platform frontage | Extend west from the retained boarding platform | 3 m clear covered strip; no coffee queues on boarding route |
| Exterior bypass | Add along lodge's east edge | 2 m clear path from arrival terrace to platform; control remains reachable when lodge is closed |
| Control | Retain booth and actual keypad door | Exterior approach only; survey exact door side and align final path accordingly |
| Service stair | Keep eastern service corridor; adapt top landing if necessary | Platform ↔ lower gallery/yard without crossing the new public stair |
| Quarters access | Retain independent upper-level connection | Preserve headroom, supports and access to +7.65 m; do not place lodge roof through it |
| Remote routes | Retain relay, bridge, overlook and water destinations | Adjust near-station ties only where apron perimeter changes |

The earlier head-on switchback stair reservation is superseded. Match the existing arrival: a straight flight climbs sideways to the left along the outside deck edge, meets a flush 2 m turning landing, and turns onto the promenade. Retain the 1.8 m clear flight target. The public platform and both upper stair landings must meet without a gap or stair slot through the rear deck. The new stair location/length is still subject to terrain fit.

Run the second proposed stair parallel to the outer right/east side of the bypass, attached to the platform edge. Ascending players travel north, then turn left across a flush upper landing into the bypass. It does not project south from the bypass end. Keep the lower tie-in to the approach/service network. It is distinct from the retained machinery/service stair. Thus the proposal contains two accesses down from the lodge deck plus the existing service access; it does not duplicate the service stair under a new name.

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

## Reference correction / September 9 evening

The editor was not running during this review; no live scene survey is claimed. Examined the saved Unreal [sideways arrival inspection](../assets/station-sideways-arrival.png), `art/blender/visual_fidelity_07/README.md`, its `layout.json`, and the R12 `independent_route_summary.json`. The latter records passed Arrival, Arrival turn onto platform, and Completed rear hall approach routes. The image is a historical in-game reference of the relevant architecture, not a fresh capture of current dressing.

Blender route evidence: Arrival runs from approximately (-14.01, -16.35, 0) to (-21.45, -16.35, 4), a westward climb. The turning route then runs from (-21.6, -16.35, 4) to (-18, -14.3, 4). These are Blender source coordinates; do not paste them into Unreal. The documented deck bands are 1.8 m grating + 3.6 m solid plate + 1.95 m grating = 7.35 m. Use that established breadth on the revised west promenade, rather than the previous thin strip.

The map now shows continuous deck beneath the arrival court, flush stair heads, a leftward arrival flight/turn and the proposed bypass descent. These source-informed corrections supersede the previous V3 stair arrangement. Before mesh changes, still survey current saved scene geometry and both new lower landing elevations.

## Combined Blender fit study

Passenger lodge 02 fits the six-table layout beside the existing control building, extends the deck west to a 7.35 m promenade, and retains the original arrival stair and turn. The 2 m bypass connects to a proposed side stair with a 2 m upper landing. Source geometry remains available in the earlier reference scene. See art/blender/passenger_lodge_02/README.md and its fit_report.json for placement, source preservation and sampled-route evidence. The lower stair approach, final structure and Unreal player collision still require validation before integration.

Edge refinement: west promenade reduced to 5.35 m; arrival assembly and turning opening moved 1.5 m west. The right-hand stair now cuts through all replacement deck surfaces, and an obsolete projecting deck tab is removed. Lower terrain connections remain provisional.

## West passenger-support extension / September 11

The user approved both a luggage/parcels office and a small rescue hut, raised above a dedicated emergency power room. The combined Blender blockout is now at `art/blender/west_services_01/Maldek_West_Services_Blockout.blend`, derived from integrated passenger lodge 04. See its README, saved-file verification and [three detail handoffs](../handoffs/west-services/README.md).

The proposal adds a 6 x 10 m structure west of the retained promenade, upper floor +4.60 m and lower floor +1.20 m. Both upper rooms share a covered porch with four steps and a 1:12 trolley/stretcher ramp. The lower room has a separate exterior stair and west service entrance. Existing lodge/control/dock geometry stays fixed. Only the derived scene's west boundary guard is replaced at the new connections.

The three later packages own their individual room fittings and opening assemblies; one integrator owns common walls, slab, roof and access. Emergency power supplies refuge heat, lights and communications, explicitly excluding the gondola drive. This is a Blender authoring proposal with inherited terrain references; current Unreal terrain, capsule traversal and engine integration remain unverified.

## Integrated west services and lower wrap platform / September 11

The completed parcels, rescue and emergency-power meshes are now combined with the existing station in `art/blender/west_services_02/Maldek_Station_West_Integrated.blend`. This is the current Blender assembly for the west extension, superseding its proxy fittings. A lower platform at +1.20 m now wraps the whole building, with a 3 m west doorway band, access around the service-stair foot and loose south/east storage clutter. Common timber/roof finish and the exhaust wall/roof connections are included. See the integrated package's README and verification report. Source files remain preserved; live Unreal terrain and collision are still separate integration work.

## Interior dressing / September 11

Latest combined Blender master: art/blender/station_dressing_01/Maldek_Station_Furnished.blend. The cleaning cupboard placeholder is now open storage with tools and supplies. Rescue wall shelves and an emergency-power spares rack/tool board add room dressing. See the package README, manifest, previews and verification.json. Earlier integrated masters remain intact; Unreal integration is still pending.

## Unreal transfer plan / September 11

See [the detailed integration plan](west-services-unreal-integration.md). It extends the existing furnished lodge migration with the west compound and final dressing, using a fresh engine/terrain baseline, bounded export groups, interaction adapters, runtime/cook checks and a later reconciled promotion. Planning only; no game asset or map changes in this step.

## Unreal implementation / September 11

The west compound and final dressing are now installed in `Station_Lodge_Migration`, including fitted ground, relocated native foliage, 28 screening pines, usable room doors/storage and sheltered-storm audio zones. The solid old cleaning-cupboard placeholder is replaced by the furnished open carcass. Normal game travel and editor startup now target this expanded map, with the original R12 map retained for rollback. See the [integration delivery](../../art/unreal_handoff/west_services_01/README.md) for current checks, source ownership and package results. Earlier pending/planning notes above describe historical checkpoints.

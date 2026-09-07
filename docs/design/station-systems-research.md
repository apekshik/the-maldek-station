# Millford: a working station and a place to live

September 7, 2026. Research and discussion proposal, not an approved scope change.

## Baseline reviewed

Baseline: repository revision `adc092e`. Reviewed VF06/VF07 construction notes and scripts, the R12 handoff manifest, R12 README and release review, and the older GDD/zone definitions. The Unreal editor was not opened for this review; geometry presence and release behavior are based on those records, not a fresh engine inspection.

R12 documents three elevations: lower drive/service level at 0 m, public platform/control level at +4 m, and furnished living/radio quarters at +7.65 m. It already includes a separate generator building, workshop, diesel yard, relay routes, and water tower/service terrace with supply pipe and wall shutoff. The older two-level web map and v0.1 GDD are behind this baseline. Do not propose these existing structures as missing additions.

The release describes a stationary visible gondola during validation. Imported machinery and passed walking routes do not establish functioning station simulation.

## Choose the ropeway family before adding terminal machinery

Our send–wait–receive premise fits a small reversible aerial tramway particularly well. LEITNER describes aerial tramways with one or two cabins moving back and forth; its detachable systems instead release cabins from the rope in stations. This is a recommendation for the fictional engineering, not a conclusion that the current rig already implements it. [LEITNER: types of ropeway](https://www.leitner.com/en/company/useful-information/types-of-ropeway/).

Use the reversible configuration to preserve the identity of one familiar returning cabin. Decide the carrying/hauling rope arrangement and drive/tensioning locations before further cable mechanism modeling. A drive can be located at either terminal; locating it at Millford is a useful creative choice because it gives the player physical access. LEITNER identifies service/safety brakes and geared or gearless drive variants. Its illustrated geared installation includes a diesel-hydraulic emergency drive. These are reference configurations, not universal specifications. [LEITNER: drive system](https://www.leitner.com/en/products/ropeway-components/detail/leitner-drive-system/).

Do not automatically add detachable-cabin conveyor trains or a large cabin garage. Those belong to a different operational scale/configuration. LEITNER's garaging reference shows external storage, inclined conveyors and integrated maintenance platforms for detachable installations. It is useful both visually and as a boundary on scope. [LEITNER: garaging systems](https://www.leitner.com/en/products/ropeway-components/detail/leitner-garaging-system/).

## Comparison and proposed scope

“Not established” means absent from the reviewed operational specification; it is not proof that no small prop exists anywhere in the project. Proposed interactions and sonic behavior below are game design, not prescribed maintenance procedures.

| System | Current evidence | Proposed addition or clarification | Player/atmosphere value |
|---|---|---|---|
| Cable drive | Gallery, motor and brake geometry; GDD mentions wheel/tensioner | Coherent motor-to-drive-wheel connection, guarded mechanism, local readings and readable operating states | Learn the acceleration, running and stopping sounds; verify a panel reading locally |
| Tensioning | GDD specifies adjustment; complete mechanism/location not established | Choose a tensioning arrangement appropriate to the ropeway; show its travel/pressure locally | Slow movement and occasional machinery sounds, rather than a knob needing constant adjustment |
| Recovery drive | No distinct recovery system established | Independent reduced-speed recovery capability as a late-game interaction | Restore the ability to retrieve the cabin without restoring ordinary operation |
| Electricity | Separate generator, diesel reserve, breakers | Clarify fuel transfer, generator cooling/exhaust, distribution and limited battery-backed circuits | Partial outages; lights/radio can survive a stopped drive |
| Water | Tower, terrace, supply main and shutoff already present | Establish refill source, pumping if required, level indication, frost protection and distribution to fixtures | A periodic fill sound, a meaningful valve, and a supply the operator actually uses |
| Heat/hot water | Operational chain not established | Compact boiler/heating cupboard, radiators and hot-water provision | Warm refuge, pipe ticks, drying clothes; cooling is gradual after failure |
| Wastewater/drainage | Operational chain not established | Washroom, waste pipe, plausible site treatment; roof gutters, surface drains, optional low-point sump | Rain produces visible consequences; most components remain environmental |
| Communications | Radio/phone and separate relay hut | Distinguish dispatch radio, terminal communication and local announcements by function/power path | Cross-check conflicting information; familiar voices and speaker clicks |
| Weather and stops | Weather ambience exists; operating consequences not established | Wind instrument, local weather indication and understandable departure/hold conditions | Weather changes decisions without requiring a large new area |
| Maintenance logistics | Workshop, lockers and service access exist | Sparse functional spare parts, inspection tags, lubricants, work light and delivery traces | Explain how repairs happen and how the station survives beyond this shift |
| Operator's home | Furnished upper living/radio quarters exist | Verify/add kitchenette, washroom, dry-clothes area and a few optional personal routines | Attachment to a place worth restoring; quiet time with agency |
| Emergency provision | Specific provision not established | First-aid cabinet, emergency lighting, rescue equipment storage and a believable callout plan | Evidence of a wider organization without implementing mountain rescue gameplay |

Doppelmayr's training identifies drives, bullwheels, tensioning, service/emergency brakes, bearings, couplings and gearboxes as distinct areas of maintenance. This supports a richer machinery assembly, but not making all of them recurring player chores. [Doppelmayr: drives and hydraulics](https://service.doppelmayr.com/training/course-list/detail/advanced-course-in-drives-and-hydraulics-135/).

For monitoring references, Doppelmayr shows brake status, wind values, operating mode and alerts together. Translate these functions into the game's analog panel rather than copying modern screens. [Doppelmayr: operating console reference, pp. 8 onward](https://www.doppelmayr.com/wp-content/uploads/2022/11/DM_WIR202_ENG.pdf).

For building services, these are choices for our remote residential station, not equipment every gondola terminal universally contains. A pumped well is one possible source; an elevated tank is storage and pressure provision, not a source by itself. [EPA: water wells](https://www.epa.gov/privatewells/learn-about-private-water-wells). A boiler and water-fed radiators provide a coherent heating concept. [DOE: heating guide](https://www.energy.gov/sites/default/files/2013/11/f5/hvac_guide.pdf). If we choose onsite wastewater treatment, a conventional septic concept includes both tank and drainfield, with site suitability still to be resolved. [EPA: septic systems](https://www.epa.gov/septic/how-septic-systems-work).

## Spatial recommendation

Keep the control room, dock and hall close. Put building services in the existing lower/service spaces; retain the separated generator, water and relay destinations. Use the upstairs quarters as the personal retreat. Add at most one short branch to a water intake/pump enclosure if the chosen refill source and a tested scene justify the journey. A wellhead or delivery fill point may achieve the same believability without another building.

Extend the implied world through a service road, delivery pad, maintenance records and cables/pipes that continue beyond the playable boundary. Additional square footage should earn its place through a different view, sound environment, decision or relationship to the station. The R12 release already records an approximately five-minute complete connected validation tour; this is not player pacing data, but warns against assuming the map has no traversal cost.

## Make normal operation rewarding and legible

Three scales of sound:

- Continuous while enabled: generator/extraction, electrical hum, distant weather. Localize and filter through structures.
- Cyclic: pump runs, thermostat/relay clicks, radio calls, departure and arrival sequences.
- Personal: kettle, spoon, chair, boots, page turning, a small radio the player can switch off.

Spatial quiet is essential even while the station runs. The quarters should contain muffled machinery through the floor and tiny domestic sounds. The platform exposes weather and line noise. The generator yard masks detail. The relay path gradually removes the station from hearing. Avoid a uniformly loud ambient loop.

Give sound a causal relationship to state. A drive stop removes cable motion but leaves auxiliary systems. A generation failure leaves wind, rain, cooling metal, perhaps a battery-powered radio. An eventual disappearance of even those independent sounds can communicate a supernatural event because the player has learned what an ordinary outage sounds like.

Example scene: the operator fills a kettle; the water system begins its familiar refill cycle. Later the same pump runs while every known tap is closed. The player can check tank level, a leak, and the upstairs washroom. Most such investigations should initially have understandable causes. Reserve the impossible for a moment earned by that knowledge.

The station must also work well for stretches. Allow the player to finish a useful inspection, dry their coat, eat, listen to a weather bulletin, or watch an uneventful arrival. Optional rituals create attachment without hunger/thirst meters. Successful repairs should buy quiet time instead of immediately spawning another fault.

## Production boundary

Implement deeply: line movement/stopping, electrical supply, communications, and one combined water/heating storyline. Give other systems believable visible consequences and a few interactions. Use passive detail for waste treatment, major servicing, stock deliveries and specialist rescue.

Automation can reduce asset and setup labor. It does not remove the writing, pacing, audio and testing cost of each new player obligation. Evaluate additions by how much they help the player understand and care for Millford.

## Reference viewing shortlist

1. [LEITNER drive assemblies](https://www.leitner.com/en/products/ropeway-components/detail/leitner-drive-system/) — motor/frame/brake relationships, maintenance access and drive variants.
2. [Bartholet aerial tramways](https://www.bartholet.swiss/en/ropeway-systems/aerial-tramways/) — a second manufacturer's tramway imagery for cabin/terminal scale and configuration comparisons.
3. [LEITNER garaging](https://www.leitner.com/en/products/ropeway-components/detail/leitner-garaging-system/) — understand the machinery and footprint we need only if choosing detachable circulation.
4. [Doppelmayr control-room photographs](https://www.doppelmayr.com/wp-content/uploads/2022/11/DM_WIR202_ENG.pdf) — operator sightlines and instrument grouping; translate to period-ambiguous analog equipment.
5. [Doppelmayr maintenance services](https://www.doppelmayr.com/en/customer-support/services/) — gear units, bearings and inspection context for workshop dressing.

References are linked for study; no photographs or meshes have been licensed or imported as game assets.

## Discussion update: machinery, records and sound

User direction accepted September 7: imply the water refill source through additional pipework; make the drive a substantially more imposing, coherent assembly matched to the existing cabin; develop cable-support towers individually and carry them into Unreal; prioritize the weak generator area and then the communications hut; retain the current cabin/storage treatment; emphasize older machinery with distinct audible operation. The user reports that line supports exist in Blender but are absent in Unreal; verify the current engine actor inventory before scheduling imports. No model or engine edits were made in this ideation pass.

### Drive and line-support modeling brief

Make the full machinery assembly monumental through the drive wheel, reduction gearbox, bearing supports, concrete foundations and guarded service access. Do not merely scale the motor. The reviewed VF06 gallery is 8 × 7 m; test a sectional blockout against its service aisles, the cabin hanger/boarding envelope and the actual cable route. Establish wheel orientation, rope approach/return and shaft connection between levels before detailing. Preserve earlier Blender revisions.

Use an older geared electric drive as the proposed visual/audio direction. “Slow” describes the visible output wheel and deliberate start/stop behavior; the motor and gearbox need distinct speeds and sound layers. Older equipment should remain dependable in its normal state. Persistent grinding should not become a healthy baseline.

The [LEITNER drive page](https://www.leitner.com/en/products/ropeway-components/detail/leitner-drive-system/) provides illustrated geared and gearless configurations; use the geared assembly as a functional reference, not a claim of period authenticity. [Doppelmayr's Rotorua maintenance report](https://service.doppelmayr.com/news/detail/customer-service-mission-in-new-zealand/) documents a motor/gearbox exchange, bullwheel bearing work and hydraulic servicing, reinforcing that these are separable assemblies.

Create a near support tower with concrete feet, structural legs/bracing, head assembly, access ladder and inspection platform; use simpler variants down the line. Keep its proportions linked to terrain, cabin clearance and rope geometry. [LEITNER's line reference](https://www.leitner.com/en/products/ropeway-components/detail/leitner-line/) and [technical brochure](https://www.leitner.com/fileadmin/userdaten/00-home/Ordner-Facelift/PDF_s_Logo_neu/Strecke/The_LEITNER_Line_.pdf) show tower and maintenance-access construction. Their roller-bank references must not be copied indiscriminately onto a reversible tramway: the selected carrying/hauling arrangement determines the tower head. Treat final ropeway configuration as unresolved until the mechanical section is approved.

### Generator area

Bring its construction/material language up to the main station's quality, with distinct functional assemblies: diesel engine and alternator on a base, fuel connection, cooling airflow and exhaust route, electrical cabinets, task lighting, and a usable inspection aisle. Repeat the station's door hardware, conduit supports, signage and material treatment. Make aging legible through repairs and service wear rather than uniform dirt. Keep controls readable outside the noisiest position. This is the first environment redesign priority identified by the user.

### Communications: proposed fictional architecture

The control room is the everyday operator interface: dispatch radio, terminal handset, indicator lamps and logbook. The remote hut houses a powered line junction/repeater, local battery supply, test handset and isolation controls. Its location is explained by the incoming mountain communication route and antenna siting; its actual separation should match the chosen technology. This is a game-specific architecture, not a universal ropeway layout.

Ordinary calls happen at the desk. The hut allows the player to test the mountain side separately from the station feeder, check local supply and reconnect or isolate a failed path. It is not a second desk that automatically tells the truth. A successful repair persists until a meaningful authored change.

Example: desk handset fails, dispatch radio remains available. At the hut the mountain-side test works, isolating an ordinary feeder fault. A later transmission on a deliberately disconnected feeder violates a procedure the player understands. Retain a working independent source so investigation remains possible.

### Records: proposed interaction design

Use one carried shift notebook that becomes the formal station log when placed at the desk. Two tabs/pages: current shift and equipment reference. Provide a brief glossary/site schematic in the reference section, not a second separately maintained inventory.

Automatically capture only what the operator has actually observed or received: time, cycle, instrument reading and communications transcript. The player selects their operational conclusion or intended follow-up. Avoid mandatory typing, repetitive transcription and omniscient detection of unseen faults. A useful entry reads: “22:14 / Cycle 03 / Desk line silent; dispatch radio working / Mountain junction not checked / Car held.” After a local test, update the finding and resolution without asking for another identical writing animation.

Separate observed facts, interpretation, and unresolved questions visually. Known concerns remain visible; no universal checklist of all possible hidden faults. Keep notebook use brief and readable with text scaling, and let communications be reviewed. Prototype it in first person to decide whether time continues while reading; do not let access to necessary information become a dexterity penalty.

Player-authored conclusions should stay dependable. If a supernatural document event occurs, prefer an older station archive page or an explicitly detectable alteration; preserve an independent record of discoveries.

### Audio-first playable scene

Prototype one full healthy departure/transit/arrival before detailed machinery modeling. Each event belongs to a source and a state: contactor click, brake mechanism, motor rise, gearbox tone, wheel/rope movement, cabin suspension/body sounds, deceleration, docking and latch. Synchronize these to actual animation; define a small number of recognizable cues rather than filling every moment.

The generator has a different sound identity and responds to load separately. Walls and closed doors filter sound; metal floors can carry muted machinery vibration. The notebook never substitutes for hearing these relationships. Significant cues need optional descriptive captions and should not depend entirely on stereo hearing.

Test from control room, gallery, quarters and relay path. Can the player distinguish line running, line stopped with power available, generation failed, and an unexplained loss of independent environmental sound? Can they identify a normal arrival without looking? Do repairs restore a reassuring sound and buy quiet time? Use these observations to revise the models, acoustic boundaries and interaction timing together.

### Selected drive reference and emergency recovery

The user explicitly selected page 13 of [Doppelmayr WIR 202](https://www.doppelmayr.com/wp-content/uploads/2022/11/DM_WIR202_ENG.pdf#page=13) as a retained drive-design reference. Local copy: [Doppelmayr WIR 202 drive reference](references/Doppelmayr-WIR202-drive-reference.pdf), page 13. The PDF is stored with Git LFS; on a checkout that filters LFS downloads, retrieve it with `git lfs pull --include="docs/design/references/*.pdf" --exclude=""`. The selected page compares a geared AC-motor assembly, Sector Drive and Direct Drive. Favor the upper geared assembly for our proposed older machinery: a large red wheel below a substantial service frame, with motor, transmission, cabinet and guarded access above. Preserve the other configurations as comparison references. This is a modern manufacturer's functional reference, not evidence of historical appearance or a dimensioned design for our cabin.

Emergency drive is now an accepted core gameplay direction for a later emergency, with exact implementation still proposed. It should recover a stranded cabin through an alternate drive path when the normal drive is unavailable. Keep it distinct from the station generator: it supplies mechanical recovery capability, not automatic restoration of every building circuit. Reference the diesel-hydraulic emergency-drive configuration linked earlier; the selected comparison image alone does not specify our emergency machinery.

Proposed authored sequence: secure/hold the line, investigate the normal-drive fault, go to the machinery, select the recovery arrangement through simplified labeled controls, start the auxiliary drive, supervise a slower return from a local position, stop and inspect the recovered cabin, and record the outcome. This is fictional interaction design, not real operating instructions. The sequence must not imply releasing safety brakes to let the cabin run uncontrolled or repairing moving machinery.

The effort comes from leaving the overview, preparing equipment, cross-checking limited local information and attending the slow recovery. Avoid repetitive button mashing or requiring the player to hand-crank the entire ropeway. If using hold-to-run interaction, offer an equivalent accessible toggle and reliable stop behavior. Give the local position enough arrival indication to operate coherently; any loss of the platform sightline should be a deliberate, legible tradeoff.

Teach or demonstrate recovery once in a controlled context before the crisis. During the crisis, let the learned procedure genuinely succeed and change the situation. Maintain partial systems where justified, such as battery-backed communication, rather than silencing everything on the first outage. Auxiliary engine, hydraulic and slow rope-motion layers form a distinct recovery sound state; returning to normal operation restores the familiar soundscape.

# VF08 — generator hall and horizontal diesel tank

Open `Maldek_Generator_Fuel_Refinement.blend`. The entire VF07 station remains available for context, with this area's replacements organized in eight named VF08 construction collections and a separate presentation collection. The file opens on the generator/fuel-yard camera.

## Design

- Generator hall expanded from 6 x 8 m to **10 x 10 m**, with 4.4 m internal wall height. Its west entrance stays at the previous service-path connection. Workshop becomes **4 x 6 m** east of the hall, joined through a 1.6 m opening. The surrounding terrain is graded locally to accommodate the enlarged footprint.
- Roughly **5.15 x 2 m generator skid** replaces the 2.4 x 1.2 m placeholder. Separate modeled components include six rocker covers and injector lines, crankcase inspection covers, oil sump, filters, turbo/intake, alternator and terminal box, radiator/fan guard, vibration mounts and fasteners.
- Room systems include an exhaust riser and silencer, open-ended radiator discharge duct, a separate intake louver, switchgear, cable tray, local controls/emergency stop, a day tank, overhead hoist, service markings, and sheltered light housings. The workshop has a bench, tool board and parts shelves.
- Horizontal **6.5 m long, 2.2 m diameter tank** borrows the water tower's blue paint, circumferential bands and galvanized fittings. Dished ends, two profiled saddles with anchor fittings, bolted manway, normal vent, emergency relief fitting, level dial, identification plate, containment kerbs and feed/return lines replace the small cylinder placeholder.
- A ground-level filling cabinet outside the containment area has capped connections, a spill tray, manual transfer pump and suction hose. It is an authored interaction location; actual refueling gameplay is not implemented.

The generator's proportions are inspired by industrial diesel sets; the station's electrical load and required runtime have not been calculated. Dimensions are art and circulation decisions, not an installation specification. The tank is visibly separate from the water system.

## Construction and preservation

Materials reuse VF06's petrol paint, service green, dark structural steel, galvanized fittings and cream enamel. New surfaces have real thickness and recessed wall-core edges. Old remote shells/equipment were removed by evaluated location rather than object origin, which catches folded sheets whose origins sit at zero. The previous approach mesh is clipped beneath the replacement entrance landing so there is a single floor owner.

The source is the approved `visual_fidelity_07/Maldek_Station_Cleanup.blend`, which supplied the R12 migration. R12 subsequently received engine/export-only opening and material fixes. This study does **not** replace those corrections: future import should transfer only the VF08 area and its scoped terrain/route changes. Do not wholesale replace the current Unreal map from this Blender file. The currently modified VF06 file and Unreal assets were not edited.

## Review and checks

`previews/01_Generator_and_Fuel.png`: exterior, larger hall and horizontal tank.

`02_Generator_Interior.png` and `04_Machine_Service.png`: player-height equipment and circulation views.

`03_Fuel_Filling.png`: tank construction and emergency filling station.

`05_Plant_Cutaway.png`: temporary roof/front-wall cutaway to expose the room layout. The saved Blender file retains all walls and roofs.

`verification.json` records evaluated mesh/curve floor and body-clearance samples through the entry, both generator-side aisles, cross aisle, workshop, fuel exit and emergency fill approach. It also checks preserved main-station floor anchors. These are sampled Blender checks, not a continuous capsule sweep or Unreal playtest. No new assets have been imported, baked, collision-certified or performance-tested in Unreal.

Rebuild with Blender 5.0.1: run `scripts/build_generator.py`, `scripts/verify_layout.py`, then `scripts/render_review.py` in separate background processes. Builders write only VF08. `source_audit.json` and `build_report.json` preserve the source inventory, replaced object names, dimensions and source checksum.

## Reference notes

[Cat C18 generator dimensional sheet](https://emc.cat.com/n/api/pubdirect?media_string_id=LEHE1773-06.pdf) provides industrial equipment proportions: separate engine/alternator, radiator and substantial base. The authored machine is not a replica or a claim about the required station capacity.

[Highland Tank horizontal tank construction](https://www.highlandtank.com/app/data/literature/G_LIT_Aboveground-Horizontal-Tanks.pdf) and [support systems](https://www.highlandtank.com/accessory/support-systems/) informed the horizontal vessel, two saddles, inspection clearance and vents. [Tank accessories](https://www.highlandtank.com/options-and-accessories/) informed the separate fill/containment fittings. These references informed visual plausibility, not an engineered fuel-system design.

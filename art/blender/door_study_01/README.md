# Control door — design study 01

Open `Maldek_Control_Door_Study.blend` in Blender 5.0. This is an editable design proposal, with a copy of the existing control building for context. Source building files and Unreal assets are unchanged.

## Design

The station's VF06 petrol paint, warm enamel, structural steel and galvanized materials are reused directly from the VF10 source. Per the user's direction, the door has a broad frosted-glass upper panel: light and indistinct forms pass through, while surface roughness obscures fine detail. The 45 mm steel leaf includes replaceable stainless kick plates, mechanical levers on both sides, latch/strike hardware, three articulated hinges, EPDM seals, enamel identification and localized scuffs. Both skins are continuous around the real 1.02 × 0.88 m cut-through opening. The 8 mm glazing uses a transmissive rough-glass shader with a fine etched surface, not an opaque white panel.

The measured control opening is 1.300 m wide by 2.400 m high. Its existing threshold rises 24 mm; the leaf starts at 34 mm, leaving 10 mm bottom clearance. Side and head reveals are 6 mm. This is a game-specific adaptation of industrial personnel-door construction, not a manufacturer replica or certified doorset.

## Review

- `previews/01_Closed.png`: exterior material and silhouette.
- `previews/02_Open.png`: 105-degree opening and warm enamel interior.
- `previews/03_Hardware.png`: lever, lock and strike detail.
- `previews/04_In_building.png`: copy of the existing control building, neutral lighting.
- `previews/05_Interior.png`: closed interior face.
- `previews/06_Frosted_transmission.png`: backlit abstract silhouette 0.6 m behind the glass, to review partial visibility. Test objects are in a separate, disabled presentation collection and are not door assets.

The timeline holds closed at frames 1–30 and open at 90–120. `D01_HINGE_PIVOT` owns the moving leaf; fixed hinge sections, seal and strike remain stationary. This is a review animation, not a game interaction implementation. Toggle `91_Existing_control_building` on and `03_Review_frame` off to inspect the measured fit with the actual source reveal; the studio frame is only a display substitute. The source transform is recorded in `design_manifest.json`.

## Internet references

Viewed 2026-09-07. Product photographs and technical pages were used as visual references; no third-party meshes or textures are redistributed.

- [Bloxwich personnel door](https://www.bloxwichdoorgear.com/acatalog/BCP22024-Standard-Shipping-Container-Personnel-Door-1270.html): insulated steel construction, 45 mm leaf, stainless hinges, seals and hardware.
- [Bloxwich goal-post frame](https://www.bloxwichdoorgear.com/acatalog/BCP22027-Shipping-Container-Personnel-Door-Goal-Post-Frame-1251.html): independent rectangular frame within corrugated cladding.
- [BigSteelBox personnel doors](https://www.bigsteelbox.com/modifications/personnel-man-doors/): outward-opening personnel access in container architecture.
- [Inpro stainless kickplate specification](https://www.inprocorp.com/globalassets/resource-documents/stainless-steel-kickplates_specifications_448_rev_6.pdf): replaceable screw-mounted lower protection.

## Validation and next phase

`source_openings.json` records the source reveal bounds. `verification.json` checks saved/reopened evaluated geometry, the cut through both skins, closed fit and a sampled clear route in the open study assembly. These are Blender checks only. Final acceptance requires the project's `art/MESH_AUTHORING.md` Unreal checks after design approval.

Before game integration: decide the visual design; adapt handing and sizes to each entrance; check full swing against walls, furniture and walkways; create export UVs and baked materials; optimize/join moving parts; author separate frame/leaf collision; implement opening, obstruction handling, interaction prompts and sound; validate in neutral and night/torch lighting with the actual player capsule. Do not add a second threshold or reveal over existing building parts. Existing R12 core recess repairs must be preserved during any later building export.

Rebuild from the repository root with Blender background `--python art/blender/door_study_01/scripts/build_door.py`, then run `review_frost.py` and `verify_door.py` in separate Blender processes. These scripts write only this study directory.

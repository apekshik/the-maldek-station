# Maldek — weathered central pylon / study 02

Keep the single gondola. The revised pylon has one central passenger lane through an open twin-leg portal. The overhead beam sits above the working rope, with a single suspended twelve-sheave train and a side maintenance deck. Four small rollers above the head carry a bare return rope; they are not a second passenger lane.

This is an original visual concept based on the tubular construction and rope hardware references in study 01. It does not change the production gondola system, cabin assets, or live Unreal level.

## Appearance

Faded grey-green paint and dulled galvanized steel replace polished silver. World-scaled procedural materials add broad discoloration, fine surface variation, vertical rain streaks, and heavier patina at flanges, bolts and foundation fins. Amber markings are faded. Red markers remain restrained.

## Cabin fit

The approved cabin body is appended from `visual_fidelity_07/Maldek_Station_Cleanup.blend` solely as a study reference. A small side-clearing upper hanger is added to this copy. The reference cabin is offset 10 cm from the rope centre, with the adapter bringing its suspension onto the central rope. Neither the production cabin nor its controller is edited.

The front render places the cabin in the portal. The three-quarter render places it just before the roller train. See `clearance.json` for sampled mesh-intersection checks. These are static Blender checks and do not replace the actual Unreal rig/spline and movement validation.

## Deliverables

- `Maldek_Weathered_Central_Pylon.blend` — editable pylon, procedural finishes, reference cabin, six cameras.
- `fbx/SM_Maldek_Central_Pylon.fbx` — pylon geometry only; cabin, adapter, cable samples and studio are excluded.
- `renders/01_full_pylon.png` — complete silhouette.
- `renders/02_crosshead.png` — central head and approaching cabin.
- `renders/03_base_detail.png` — weathered finishes and bases.
- `renders/04_front_clearance.png` — cabin centred in the portal.
- `renders/05_hanger_detail.png` — study adapter.
- `renders/06_night.png` — night material/marker study.
- `scripts/build.py` — reproducible generator and renders.
- `scripts/verify_clearance.py` — evaluated-mesh passage checks.

The pylon is approximately 45.12 m overall, with a working cable height of 42.327 m. Foundation centre spacing is 9.2 m. Shaft lengths and footings remain subject to actual terrain placement.

Blender procedural weathering is not automatically carried by FBX. Bake it or recreate the node recipe in Unreal before judging the imported finish. The first twin-passenger-lane study is preserved separately in `pylon_study_01`.

## Reference context

[LEITNER line](https://www.leitner.com/en/products/ropeway-components/detail/leitner-line/) informed modular tubular legs, joints and sheave assemblies.

[Doppelmayr reversible aerial tramways](https://www.doppelmayr.com/en/systems/reversible-aerial-tramways/) and [Funifor rope-system brochure](https://www.doppelmayr.com/wp-content/uploads/2022/11/FUF_Funifor_ENG.pdf) informed the distinction between a passenger track and the mechanical rope system. This compact central portal is our scene-specific design, not a replica of those installations.

The original broader task still includes route/terrain alignment and a larger, brighter distant-station silhouette. Those edits remain pending Unreal access and integration.

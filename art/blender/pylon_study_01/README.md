# Maldek — modern twin tubular pylon study 01

Standalone Blender design study for the long gondola route. The existing station and live Unreal map are unchanged by this package.

## Design

- Two gently tapering circular steel shafts: 2.10 m diameter at the base, 1.42 m at the top.
- 42.327 m cable contact height; 43.63 m overall marker height.
- 9.20 m foundation centre spacing; 14.20 m rope gauge at the head.
- Four shaft sections with bolted flange joints, separate concrete pedestals and base stiffeners.
- Twelve 550 mm running-diameter sheaves per lane, paired rocker beams, detection housings and lifting points.
- Inboard grating walkways, guardrails, access ladders, electrical enclosures and modest red marker lenses.
- Satin silver shafts, graphite crosshead, galvanized hardware and small amber identification bands.

The wide head is a visual study. Actual route gauge, cable tangents, terrain footings and gondola hanger clearance must be surveyed before integrating it. Do not scale the complete tower vertically: regenerate shaft lengths while retaining the sheave diameters, walkway proportions and head geometry.

## Files

- `Maldek_Modern_Twin_Pylon.blend`: editable named components, metric units, four cameras, independent studio lighting.
- `fbx/SM_Maldek_Twin_Pylon_42m.fbx`: consolidated evaluated geometry, origin centred between foundations, metres converted by FBX unit metadata.
- `renders/01_full_pylon.png`: whole structure with a 1.8 m person for scale.
- `renders/02_crosshead.png`: rollers, walkways, rocker beams and markers.
- `renders/03_base_detail.png`: foundations, flange joints, electrical enclosures and ladder.
- `renders/04_night.png`: subdued blue light and red markers.
- `scripts/build.py`: reproducible generator, asset export and Cycles renders.
- `manifest.json`: dimensions, sources and evaluated mesh count.

Studio ground, cables, cameras, lights and scale figure are excluded from the FBX. Render lighting does not modify production sky or exposure.

## Reference basis

[LEITNER line and special towers](https://www.leitner.com/en/products/ropeway-components/detail/leitner-line/) establishes the visual vocabulary: modular circular shafts, conical transitions, flanges, special two-leg structures and distinct roller batteries. The linked manufacturer photographs informed the equipment arrangement.

[LEITNER special tower technical sheet](https://www.leitner.com/fileadmin//userdaten/00-home/Ordner-Facelift/PDF_s_Logo_neu/Strecke/The_LEITNER_Line_specialtowers.pdf) describes round-tube sections and flange construction in taller multi-leg supports.

[Doppelmayr WIR 199, D-Line](https://www.doppelmayr.com/wp-content/uploads/2022/11/DM_WIR199_ENG.pdf) gives a 550 mm sheave diameter, used for the roller detail proportions. The complete pylon is an original art design, not a replica of either manufacturer's product.

Local reference JPGs retain their original manufacturer ownership and are reference material only; they are not included in the exported mesh.

## Unreal follow-through

The route audit found a 585.8 m travel spline and a remote station around 1.4 km away. No current imported route pylon actors were found. The read-only `route_refine_survey.py` is staged separately; run only after the forest task releases the editor. Use the terrain survey to decide tower count/heights and whether the visual route and movement spline should be reconciled together. The distant marker's present 14 × 8 × 4 m box and three small window emitters still need the requested scale/visibility pass.

Before release, verify FBX centimetre bounds and material slots, ground every footing, inspect sheave/rope contact and gondola swept clearance, then review actual night visibility in Unreal and save/reopen the level.
